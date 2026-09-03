from __future__ import annotations

import tomllib
from pathlib import Path


PROJECT = Path(__file__).parents[1]
SOURCE = PROJECT / "src/phase_agent_orchestrator"


def test_operator_entrypoints_live_under_cli_package() -> None:
    with (PROJECT / "pyproject.toml").open("rb") as handle:
        scripts = tomllib.load(handle)["project"]["scripts"]

    for name, target in scripts.items():
        assert target.startswith("phase_agent_orchestrator.cli."), (name, target)


def test_reusable_provider_modules_are_grouped() -> None:
    assert (SOURCE / "providers/sdk.py").is_file()
    assert (SOURCE / "providers/results.py").is_file()
    assert (SOURCE / "providers/availability.py").is_file()
    assert (SOURCE / "runners/lifecycle.py").is_file()
    assert (SOURCE / "runners/quant.py").is_file()
