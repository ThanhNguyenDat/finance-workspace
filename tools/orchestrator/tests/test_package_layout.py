from __future__ import annotations

from pathlib import Path

import tomllib

PROJECT = Path(__file__).parents[1]
SOURCE = PROJECT / "src/orchestrator"


def test_operator_entrypoints_live_under_cli_package() -> None:
    with (PROJECT / "pyproject.toml").open("rb") as handle:
        scripts = tomllib.load(handle)["project"]["scripts"]

    for name, target in scripts.items():
        assert target.startswith("orchestrator.cli."), (name, target)


def test_reusable_provider_modules_are_grouped() -> None:
    assert (SOURCE / "core/io.py").is_file()
    assert (SOURCE / "core/fingerprint.py").is_file()
    assert (SOURCE / "core/redaction.py").is_file()
    assert (SOURCE / "providers/sdk.py").is_file()
    assert (SOURCE / "providers/results.py").is_file()
    assert (SOURCE / "providers/availability.py").is_file()
    assert (SOURCE / "runners/lifecycle.py").is_file()
    assert (SOURCE / "runners/quant.py").is_file()


def test_package_root_contains_no_implementation_modules() -> None:
    assert {path.name for path in SOURCE.glob("*.py")} == {"__init__.py"}
