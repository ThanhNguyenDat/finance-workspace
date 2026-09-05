import pytest

from orchestrator.cli import codex_exec
from orchestrator.utils import config as config_module


@pytest.fixture(autouse=True)
def _isolate_orchestrator_config(monkeypatch, tmp_path, tmp_path_factory):
    """Prevent this machine's real env vars / config.yaml / log file from
    leaking into tests.

    Individual tests that want to exercise env-var, config-file, or log-file
    behavior call monkeypatch.setenv(...) / monkeypatch.setattr(...) or pass
    an explicit `log_path=` themselves afterward, which overrides these
    defaults for that test. The default log path is isolated to its own
    directory (not the test's own `tmp_path`) so tests asserting "no file
    appears in --cwd" aren't tripped up by the log file landing there too.
    """

    monkeypatch.delenv("ORCHESTRATOR_CLAUDE_ACCOUNTS", raising=False)
    monkeypatch.delenv("ORCHESTRATOR_CODEX_ACCOUNTS", raising=False)
    monkeypatch.setattr(config_module, "CONFIG_PATH", tmp_path / "unused-config.yaml")
    log_dir = tmp_path_factory.mktemp("orchestrator-logs")
    monkeypatch.setattr(codex_exec, "DEFAULT_LOG_PATH", log_dir / "codex-exec.log")
