from pathlib import Path

from orchestrator.locks import change_lock
from orchestrator.state import candidates, ops_transaction, quant_research


def _repository_root() -> Path:
    test_path = Path(__file__).resolve()
    for parent in (test_path, *test_path.parents):
        if (parent / ".git").exists():
            return parent
    raise AssertionError("repository root not found from test path")


def test_default_roots_resolve_to_repository_root(monkeypatch):
    for variable in ("OPS_ROOT", "QUANT_RESEARCH_ROOT", "PHASE_AGENT_ROOT"):
        monkeypatch.delenv(variable, raising=False)

    expected = _repository_root()

    assert ops_transaction.root_dir() == expected
    assert quant_research.root_dir() == expected
    assert change_lock.root_dir() == expected
    assert candidates.root_dir() == expected
