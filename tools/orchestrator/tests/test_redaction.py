from orchestrator.utils.redaction import REDACTED, redact_value


def test_redacts_secret_shaped_key() -> None:
    value = {"api_key": "sk-live-abc123"}
    assert redact_value(value) == {"api_key": REDACTED}


def test_redacts_bearer_token_value_by_pattern() -> None:
    value = {"message": "calling with Bearer abc.def-123 attached"}
    result = redact_value(value)
    assert "abc.def-123" not in result["message"]
    assert REDACTED in result["message"]


def test_leaves_non_secret_values_untouched() -> None:
    value = {"status": "completed", "count": 3}
    assert redact_value(value) == value
