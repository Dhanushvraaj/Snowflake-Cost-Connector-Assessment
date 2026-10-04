from src.main import classify_error


def test_permission_error():
    assert classify_error("Insufficient privileges to operate on view") == "permission_denied"


def test_missing_view():
    assert classify_error("Object does not exist") == "unavailable_in_account"


def test_other_error():
    assert classify_error("Connection timed out") == "failed"
