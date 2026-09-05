from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from orchestrator.cli import _shared


def test_explicit_change_produces_nested_path():
    path = _shared.resolve_log_path("codex-exec", "my-change")
    assert path == _shared.LOGS_ROOT / "my-change" / "codex-exec.log"


def test_omitted_change_falls_back_to_adhoc_date(monkeypatch):
    class _FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 1, 1, 1, 0, tzinfo=tz)  # 01:00 VN time

    monkeypatch.setattr(_shared, "datetime", _FixedDatetime)

    path = _shared.resolve_log_path("claude-exec", None)

    assert path == _shared.LOGS_ROOT / "adhoc-2026-01-01" / "claude-exec.log"


def test_adhoc_fallback_uses_vn_local_date_not_utc_date(monkeypatch):
    # 2026-01-01 01:00 +07:00 is still 2025-12-31 18:00 UTC -- confirms the
    # VN-local date (Jan 1), not the UTC date (Dec 31), is used.
    class _FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            base = datetime(2026, 1, 1, 1, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
            return base.astimezone(tz) if tz else base

    monkeypatch.setattr(_shared, "datetime", _FixedDatetime)

    path = _shared.resolve_log_path("codex-exec", None)

    assert path == _shared.LOGS_ROOT / "adhoc-2026-01-01" / "codex-exec.log"


@pytest.mark.parametrize(
    "bad_value", ["Has_Underscore", "UPPER", "-leading-hyphen", ""]
)
def test_invalid_change_name_is_rejected_by_argparse(bad_value):
    parser = _shared.build_arg_parser("codex-exec", "test")
    with pytest.raises(SystemExit):
        parser.parse_args(["prompt", "--change", bad_value])


def test_valid_change_name_is_accepted():
    parser = _shared.build_arg_parser("codex-exec", "test")
    args = parser.parse_args(
        ["prompt", "--change", "bootstrap-orchestrator-exec-commands"]
    )
    assert args.change == "bootstrap-orchestrator-exec-commands"
