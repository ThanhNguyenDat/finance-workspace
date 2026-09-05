from orchestrator.utils import config as config_module
from orchestrator.utils.config import load_config


def test_load_config_returns_empty_dict_when_file_missing(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(config_module, "CONFIG_PATH", tmp_path / "does-not-exist.yaml")
    assert load_config() == {}


def test_load_config_parses_yaml_file(tmp_path, monkeypatch) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "claude:\n  accounts:\n    - /a/one\n    - /a/two\n", encoding="utf-8"
    )
    monkeypatch.setattr(config_module, "CONFIG_PATH", config_file)
    assert load_config() == {"claude": {"accounts": ["/a/one", "/a/two"]}}


def test_load_config_ignores_non_mapping_yaml(tmp_path, monkeypatch) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text("- just\n- a\n- list\n", encoding="utf-8")
    monkeypatch.setattr(config_module, "CONFIG_PATH", config_file)
    assert load_config() == {}
