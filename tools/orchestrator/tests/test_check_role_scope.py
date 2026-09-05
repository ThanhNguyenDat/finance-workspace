from orchestrator.cli._shared import check_role_scope


def test_role_in_scope_returns_none() -> None:
    assert check_role_scope("plan", ["plan", "verify"]) is None


def test_role_outside_scope_returns_a_message() -> None:
    message = check_role_scope("implement", ["plan", "verify"])
    assert message is not None
    assert "implement" in message
    assert "plan, verify" in message


def test_no_role_returns_none_regardless_of_scope() -> None:
    assert check_role_scope(None, ["plan"]) is None


def test_empty_scope_returns_none_regardless_of_role() -> None:
    assert check_role_scope("implement", []) is None
