from datetime import date, datetime, timezone
from decimal import Decimal


def utc_value(value):
    #Convert datetime values to UTC. Keep dates as ISO strings
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()

    if isinstance(value, date):
        return value.isoformat()

    return value


def json_value(value):
    #Keep Decimal precision and convert dates/timestamps safely
    if isinstance(value, Decimal):
        return str(value)

    return utc_value(value)


def first_value(record, names):
    #Return the first non-null value from the given column names
    for name in names:
        value = record.get(name)

        if value is not None:
            return value

    return None


def normalize_record(record, category, account_id, collection_time):

    #Map one Snowflake record into the common assessment format.
    # Usage and billing periods

    start = first_value(
        record,
        [
            "START_TIME",
            "QUERY_START_TIME",
            "USAGE_START",
            "CHARGE_PERIOD_START",
            "ChargePeriodStart",
            "USAGE_DATE",
        ],
    )

    end = first_value(
        record,
        [
            "END_TIME",
            "QUERY_END_TIME",
            "USAGE_END",
            "CHARGE_PERIOD_END",
            "ChargePeriodEnd",
            "USAGE_DATE",
        ],
    )

    billing_start = first_value(
        record,
        [
            "BILLING_PERIOD_START",
            "BILLING_PERIOD_START_TIME",
            "BillingPeriodStart",
        ],
    )

    billing_end = first_value(
        record,
        [
            "BILLING_PERIOD_END",
            "BILLING_PERIOD_END_TIME",
            "BillingPeriodEnd",
        ],
    )

 # Record and resource information  

    record_id = first_value(
        record,
        [
            "QUERY_ID",
            "WAREHOUSE_ID",
            "TASK_ID",
            "DATABASE_ID",
            "SCHEMA_ID",
            "STAGE_ID",
            "TABLE_ID",
            "TAG_ID",
            "ID",
        ],
    )

    resource_id = first_value(
        record,
        [
            "RESOURCE_ID",
            "WAREHOUSE_ID",
            "DATABASE_ID",
            "SCHEMA_ID",
            "STAGE_ID",
            "TABLE_ID",
        ],
    )

    resource_name = first_value(
        record,
        [
            "RESOURCE_NAME",
            "WAREHOUSE_NAME",
            "TASK_NAME",
            "DATABASE_NAME",
            "SCHEMA_NAME",
            "STAGE_NAME",
            "TABLE_NAME",
            "ServiceName",
        ],
    )

    resource_type = first_value(
        record,
        [
            "RESOURCE_TYPE",
            "WAREHOUSE_TYPE",
            "SERVICE_TYPE",
            "ServiceCategory",
        ],
    )


    # Consumed quantity

    quantity = first_value(
        record,
        [
            "CONSUMED_QUANTITY",
            "CREDITS_USED",
            "BYTES_TRANSFERRED",
            "STORAGE_BYTES",
            "USAGE",
            "ConsumedQuantity",
        ],
    )

    unit = first_value(
        record,
        [
            "CONSUMED_UNIT",
            "UNIT",
            "ConsumedUnit",
        ],
    )

    # Fallback for datasets where the unit is not explicitly provided
    if unit is None:
        if record.get("CREDITS_USED") is not None:
            unit = "credits"
        elif record.get("BYTES_TRANSFERRED") is not None:
            unit = "bytes"
        elif record.get("STORAGE_BYTES") is not None:
            unit = "bytes"

    # Pricing quantity

    pricing_quantity = first_value(
        record,
        [
            "PRICING_QUANTITY",
            "PRICING_QUANTITY_VALUE",
            "PricingQuantity",
        ],
    )

    pricing_unit = first_value(
        record,
        [
            "PRICING_UNIT",
            "PRICING_QUANTITY_UNIT",
            "PricingUnit",
        ],
    )

    # Cost and pricing fields


    list_unit_price = first_value(
        record,
        [
            "LIST_UNIT_PRICE",
            "LIST_PRICE",
            "ListUnitPrice",
        ],
    )

    list_cost = first_value(
        record,
        [
            "LIST_COST",
            "ListCost",
        ],
    )

    contracted_cost = first_value(
        record,
        [
            "CONTRACTED_COST",
            "ContractedCost",
        ],
    )

    effective_cost = first_value(
        record,
        [
            "EFFECTIVE_COST",
            "EffectiveCost",
        ],
    )

    billed_cost = first_value(
        record,
        [
            "BILLED_COST",
            "BilledCost",
        ],
    )

    currency = first_value(
        record,
        [
            "BILLING_CURRENCY",
            "CURRENCY",
            "CURRENCY_CODE",
            "BillingCurrency",
        ],
    )

    
    # Service, SKU and allocation information

    service = first_value(
        record,
        [
            "SERVICE_NAME",
            "SERVICE_TYPE",
            "PRODUCT_NAME",
            "ServiceName",
        ],
    )

    sku = first_value(
        record,
        [
            "SKU",
            "SKU_NAME",
        ],
    )

    tags = first_value(
        record,
        [
            "TAGS",
            "TAG_REFERENCES",
            "ALLOCATION",
            "ALLOCATION_TAGS",
        ],
    )

   
    # Source update timestamp

    source_update_time = first_value(
        record,
        [
            "X_UPDATEDAT",
            "UPDATED_AT",
            "LAST_UPDATED",
            "LAST_UPDATE_TIME",
            "x_UpdatedAt",
        ],
    )

    # Preserve every original source field.
    # This is important for auditability and fields that are not
    # applicable to the common normalized schema.
    clean_record = {
        key: json_value(value)
        for key, value in record.items()
    }

  
    # Common normalized schema

    return {
        "Platform": "Snowflake",

        "Billing account or organization identifier": account_id,

        "Sub-account identifier": first_value(
            record,
            [
                "SUB_ACCOUNT_ID",
                "SUBACCOUNT_ID",
                "SubAccountId",
            ],
        ),

        "Source category": category,

        "Source record identifier": json_value(record_id),

        "Resource identifier": json_value(resource_id),

        "Resource name": resource_name,

        "Resource type": resource_type,

        "Service or product": service,

        "SKU": sku,

        "Usage start and end": {
            "start": utc_value(start),
            "end": utc_value(end),
        },

        "Billing period start and end": {
            "start": utc_value(billing_start),
            "end": utc_value(billing_end),
        },

        "Consumed quantity and unit": {
            "quantity": json_value(quantity),
            "unit": unit,
        },

        "Pricing quantity and unit": {
            "quantity": json_value(pricing_quantity),
            "unit": pricing_unit,
        },

        "List unit price": json_value(list_unit_price),

        "List cost": json_value(list_cost),

        "Contracted cost": json_value(contracted_cost),

        "Effective cost": json_value(effective_cost),

        "Billed cost": json_value(billed_cost),

        "Currency": currency,

        "Tags or allocation metadata": json_value(tags),

        "Source update time": utc_value(source_update_time),

        "Collection time": collection_time,

        "Additional source metadata": clean_record,
    }