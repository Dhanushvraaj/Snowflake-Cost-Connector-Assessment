# Snowflake Cost Connector

A small Python connector for the Snowflake cost and usage assessment.


# 1. Setup

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 
```

Copy the environment file:

```bash
cp .env.example .env
```

Put your Snowflake account, username and password in `.env`.

# 2. Run tests

Tests do not need Snowflake credentials:

```bash
python -m pytest -q
```

# 3. Run the connector

```bash
python -m src.main
```

The connector creates:

text
output/
  raw/                 raw JSONL records
  normalized/          normalized JSONL records
  coverage_report.json coverage report
  coverage_report.csv  easy-to-read coverage report
  execution_evidence.json
```

# Status meanings

- `collected`: the view was available and returned records
- `empty`: the view was available but returned no records at collection time
- `permission_denied`: the view could not be read because of permissions
- `unavailable_in_account`: the view was not found during discovery
- `failed`: another collection error occurred


# Notes

Snowflake ACCOUNT_USAGE data can have reporting latency. Therefore a view can be available but empty during a particular run.

The connector uses `fetchmany()` so it does not intentionally stop after the first 100 records.

Decimal values are written as strings in JSON when needed so their precision is not lost.

Timestamps are converted to UTC when they contain timezone information.

FOCUS is investigated separately because availability depends on account capabilities and organization-level access.
