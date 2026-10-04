import csv
import json
import logging
import os
from datetime import datetime, timezone, date
from decimal import Decimal

import snowflake.connector
from dotenv import load_dotenv

from .config import DATASETS, FOCUS_DATASET
from .normalize import normalize_record

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)

        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, date):
            return obj.isoformat()

        return super().default(obj)


def connect():
    load_dotenv()
    required = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise ValueError("Missing environment variables: " + ", ".join(missing))

    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    )


def discover_views(cursor, schema):
    """Return the view names visible in a Snowflake usage schema."""
    try:
        cursor.execute(f"SHOW VIEWS IN SCHEMA SNOWFLAKE.{schema}")
        rows = cursor.fetchall()
        names = set()
        for row in rows:
            # SHOW VIEWS returns name in column 2 for the current connector.
            if len(row) > 1:
                names.add(str(row[1]).upper())
        return names, None
    except Exception as exc:
        return set(), str(exc)


def collect_view(cursor, schema, view, batch_size):
    """Collect all rows from one Snowflake view in batches."""

    if view.startswith("SNOWFLAKE."):
        full_view_name = view
    else:
        full_view_name = f'SNOWFLAKE.{schema}."{view}"'

    sql = f"SELECT * FROM {full_view_name}"

    cursor.execute(sql)

    columns = [column[0] for column in cursor.description]
    records = []

    while True:
        rows = cursor.fetchmany(batch_size)

        if not rows:
            break

        for row in rows:
            records.append(dict(zip(columns, row)))

    return records


def classify_error(message):
    text = message.lower()
    if "not authorized" in text or "insufficient privileges" in text:
        return "permission_denied"
    if "does not exist" in text or "unknown table" in text:
        return "unavailable_in_account"
    return "failed"


def timestamp_range(records):
    starts = []
    ends = []

    start_keys = (
        "START_TIME",
        "QUERY_START_TIME",
        "USAGE_START",
        "CHARGE_PERIOD_START",
        "ChargePeriodStart",
        "BillingPeriodStart",
        "USAGE_DATE",
    )

    end_keys = (
        "END_TIME",
        "QUERY_END_TIME",
        "USAGE_END",
        "CHARGE_PERIOD_END",
        "ChargePeriodEnd",
        "BillingPeriodEnd",
        "USAGE_DATE",
    )

    for record in records:
        for key in start_keys:
            value = record.get(key)
            if isinstance(value, datetime):
                starts.append(value)
                break

        for key in end_keys:
            value = record.get(key)
            if isinstance(value, datetime):
                ends.append(value)
                break

    earliest = min(starts).isoformat() if starts else None
    latest = max(ends).isoformat() if ends else None

    return earliest, latest


def main():
    os.makedirs("output/raw", exist_ok=True)
    os.makedirs("output/normalized", exist_ok=True)

    batch_size = int(os.getenv("FETCH_BATCH_SIZE", "1000"))
    conn = None

    try:
        conn = connect()
        cursor = conn.cursor()

        cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_REGION()")
        account_id, region = cursor.fetchone()
        logging.info("Connected to Snowflake account %s (region redacted in saved evidence)", account_id)

        discovered = {}
        discovery_errors = {}
        for schema in ("ACCOUNT_USAGE", "ORGANIZATION_USAGE", "BILLING"):
            views, error = discover_views(cursor, schema)
            discovered[schema] = views
            if error:
                discovery_errors[schema] = error

        datasets = DATASETS + [FOCUS_DATASET]
        coverage = []
        evidence = {
            "connection": "success",
            "account": "REDACTED",
            "region": "REDACTED",
            "categories_investigated": len(datasets),
            "datasets": [],
        }

        for schema, view, category in datasets:
            logging.info("Checking %s.%s", schema, view)
            status = "failed"
            explanation = ""
            records = []

            if schema in discovery_errors:
                status = "failed"
                explanation = "Could not discover views in this schema: " + discovery_errors[schema]
            elif view not in discovered.get(schema, set()):
                status = "unavailable_in_account"
                explanation = "View was not found during SHOW VIEWS discovery."
            else:
                try:
                    records = collect_view(cursor, schema, view, batch_size)
                    status = "collected" if records else "empty"
                    if not records:
                        explanation = "View exists, but returned no records at collection time."
                except Exception as exc:
                    status = classify_error(str(exc))
                    explanation = str(exc)

            collection_time = datetime.now(timezone.utc).isoformat()
            normalized = [
                normalize_record(record, category, str(account_id), collection_time)
                for record in records
            ]

            safe_name = f"{schema.lower()}_{view.lower()}"
            with open(f"output/raw/{safe_name}.jsonl", "w") as raw_file:
                for record in records:
                    json.dump(record, raw_file, cls=Encoder)
                    raw_file.write("\n")

            with open(f"output/normalized/{safe_name}.jsonl", "w") as normalized_file:
                for record in normalized:
                    json.dump(record, normalized_file, cls=Encoder)
                    normalized_file.write("\n")

            earliest, latest = timestamp_range(records)
            coverage.append({
                "Category or dataset name": f"{schema}.{view}",
                "Purpose": category,
                "Status": status,
                "Number of records": len(records),
                "Earliest source timestamp": earliest,
                "Latest source timestamp": latest,
                "Required permission or capability": "ACCOUNTADMIN; some organization data may require organization-level access",
                "Explanation": explanation,
            })
            evidence["datasets"].append({
                "dataset": f"{schema}.{view}",
                "category": category,
                "status": status,
                "records": len(records),
            })

        with open("output/coverage_report.json", "w") as file:
            json.dump(coverage, file, indent=2)

        with open("output/coverage_report.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=coverage[0].keys())
            writer.writeheader()
            writer.writerows(coverage)

        with open("output/execution_evidence.json", "w") as file:
            json.dump(evidence, file, indent=2)

        logging.info("Finished. Results are in the output folder.")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
