from datetime import datetime, timezone
from decimal import Decimal

from src.normalize import normalize_record, utc_value


def test_warehouse_record():
    record = {
        "WAREHOUSE_ID": "W1",
        "WAREHOUSE_NAME": "COMPUTE_WH",
        "START_TIME": datetime(2026, 10, 2, 10, 0),
        "END_TIME": datetime(2026, 10, 2, 11, 0),
        "CREDITS_USED": Decimal("0.228345277"),
    }
    result = normalize_record(record, "Compute", "ABC", "2026-10-03T00:00:00+00:00")
    assert result["Source record identifier"] == "W1"
    assert result["Consumed quantity and unit"]["quantity"] == "0.228345277"
    assert result["Consumed quantity and unit"]["unit"] == "credits"
    assert result["Resource name"] == "COMPUTE_WH"


def test_bytes_record():
    record = {"BYTES_TRANSFERRED": Decimal("123.456")}
    result = normalize_record(record, "Transfer", "ABC", "now")
    assert result["Consumed quantity and unit"]["quantity"] == "123.456"
    assert result["Consumed quantity and unit"]["unit"] == "bytes"


def test_utc_conversion():
    value = datetime(2026, 10, 2, 10, 0, tzinfo=timezone.utc)
    assert utc_value(value).endswith("+00:00")
