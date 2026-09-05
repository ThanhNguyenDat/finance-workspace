from orchestrator.utils import config as config_module
from orchestrator.utils.config import configured_scope


def test_returns_empty_list_when_config_file_absent() -> None:
    assert configured_scope("claude") == []


def test_returns_scope_list_when_present(tmp_path, monkeypatch) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "claude:\n  scope:\n    - plan\n    - verify\n    - final_verify\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(config_module, "CONFIG_PATH", config_file)
    assert configured_scope("claude") == ["plan", "verify", "final_verify"]


def test_returns_empty_list_when_scope_is_absent_for_section(
    tmp_path, monkeypatch
) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text("claude:\n  accounts:\n    - /a\n", encoding="utf-8")
    monkeypatch.setattr(config_module, "CONFIG_PATH", config_file)
    assert configured_scope("claude") == []


def test_returns_empty_list_when_scope_is_not_a_list(tmp_path, monkeypatch) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text("claude:\n  scope: plan\n", encoding="utf-8")
    monkeypatch.setattr(config_module, "CONFIG_PATH", config_file)
    assert configured_scope("claude") == []
