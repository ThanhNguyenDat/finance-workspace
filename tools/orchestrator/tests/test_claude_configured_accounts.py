from orchestrator.providers.claude import configured_accounts
from orchestrator.utils import config as config_module


def test_no_env_var_or_config_file_means_one_ambient_attempt() -> None:
    # conftest.py's autouse fixture already isolates env vars and CONFIG_PATH.
    assert configured_accounts() == [None]


def test_env_var_is_parsed_and_expanded(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv(
        "ORCHESTRATOR_CLAUDE_ACCOUNTS", "~/.claude, ~/.claude-personal-02"
    )
    assert configured_accounts() == [
        str(tmp_path / ".claude"),
        str(tmp_path / ".claude-personal-02"),
    ]


def test_config_file_used_when_env_var_unset(tmp_path, monkeypatch) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "claude:\n  accounts:\n    - /a/one\n    - /a/two\n", encoding="utf-8"
    )
    monkeypatch.setattr(config_module, "CONFIG_PATH", config_file)
    assert configured_accounts() == ["/a/one", "/a/two"]


def test_env_var_takes_precedence_over_config_file(tmp_path, monkeypatch) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "claude:\n  accounts:\n    - /from/config\n", encoding="utf-8"
    )
    monkeypatch.setattr(config_module, "CONFIG_PATH", config_file)
    monkeypatch.setenv("ORCHESTRATOR_CLAUDE_ACCOUNTS", "/from/env")
    assert configured_accounts() == ["/from/env"]
