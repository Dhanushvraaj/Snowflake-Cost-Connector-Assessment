
DATASETS = [
    ("ACCOUNT_USAGE", "METERING_HISTORY", "Compute and warehouse consumption"),
    ("ACCOUNT_USAGE", "METERING_DAILY_HISTORY", "Compute and warehouse consumption"),
    ("ACCOUNT_USAGE", "WAREHOUSE_METERING_HISTORY", "Compute and warehouse consumption"),
    ("ACCOUNT_USAGE", "QUERY_METERING_HISTORY", "Query/resource attribution"),
    ("ACCOUNT_USAGE", "QUERY_ATTRIBUTION_HISTORY", "Query/resource attribution"),
    ("ACCOUNT_USAGE", "STORAGE_USAGE", "Storage consumption"),
    ("ACCOUNT_USAGE", "DATABASE_STORAGE_USAGE_HISTORY", "Storage consumption"),
    ("ACCOUNT_USAGE", "STAGE_STORAGE_USAGE_HISTORY", "Storage consumption"),
    ("ACCOUNT_USAGE", "TABLE_STORAGE_METRICS", "Storage consumption"),
    ("ACCOUNT_USAGE", "DATA_TRANSFER_HISTORY", "Data transfer"),
    ("ACCOUNT_USAGE", "INTERNAL_DATA_TRANSFER_HISTORY", "Data transfer"),
    ("ACCOUNT_USAGE", "SERVERLESS_TASK_HISTORY", "Serverless/managed feature consumption"),
    ("ACCOUNT_USAGE", "SERVERLESS_ALERT_HISTORY", "Serverless/managed feature consumption"),
    ("ACCOUNT_USAGE", "SERVERLESS_FLEX_TASK_HISTORY", "Serverless/managed feature consumption"),
    ("ACCOUNT_USAGE", "SERVERLESS_EXPERIMENT_HISTORY", "Serverless/managed feature consumption"),
    ("ACCOUNT_USAGE", "ANOMALIES_DAILY", "Anomalies and optimization"),
    ("ACCOUNT_USAGE", "BUDGET_DETAILS", "Budgets and limits"),
    ("ACCOUNT_USAGE", "PRIVACY_BUDGETS", "Budgets and limits"),
    ("ACCOUNT_USAGE", "TAGS", "Tags/allocation"),
    ("ACCOUNT_USAGE", "TAG_REFERENCES", "Tags/allocation"),
    ("ACCOUNT_USAGE", "BILLING_DOCUMENTS", "Billing/spend"),
    ("ORGANIZATION_USAGE", "RATE_SHEET_DAILY", "Pricing/rates/currency"),
    ("ORGANIZATION_USAGE", "USAGE_IN_CURRENCY_DAILY", "Pricing/rates/currency"),
    ("ORGANIZATION_USAGE", "REMAINING_BALANCE_DAILY", "Commitments/balances"),
    ("ACCOUNT_USAGE", "BLOCK_STORAGE_HISTORY", "Storage consumption"),
    ("ACCOUNT_USAGE", "BACKUP_STORAGE_USAGE", "Storage consumption"),
    ("ACCOUNT_USAGE", "SNAPSHOT_STORAGE_USAGE", "Storage consumption"),
    ("ACCOUNT_USAGE", "STORAGE_REQUEST_HISTORY", "Storage consumption"),
    ("ACCOUNT_USAGE", "STORAGE_LIFECYCLE_POLICIES", "Storage optimization"),
    ("ACCOUNT_USAGE", "STORAGE_LIFECYCLE_POLICY_HISTORY", "Storage optimization"),
    ("ACCOUNT_USAGE", "ICEBERG_STORAGE_OPTIMIZATION_HISTORY", "Storage optimization"),
    ("ACCOUNT_USAGE", "ARCHIVE_STORAGE_DATA_RETRIEVAL_USAGE_HISTORY", "Storage consumption"),
    ("ACCOUNT_USAGE", "INTERNAL_STAGE_NETWORK_ACCESS_HISTORY", "Data transfer"),
    ("ACCOUNT_USAGE", "STAGES", "Storage consumption"),
    ("ACCOUNT_USAGE", "POSTGRES_STORAGE_USAGE_HISTORY", "Storage consumption"),
]

# FOCUS is checked separately because it is normally an organization-level

FOCUS_DATASET = (
    "BILLING",
    "FOCUS_COST_USAGE_V1_3",
    "FOCUS-compliant cost and usage data"
)
