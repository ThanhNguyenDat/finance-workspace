#!/usr/bin/env python3

from _bootstrap import bootstrap

bootstrap()

from phase_agent_orchestrator.cli.phase_agent_state import main  # noqa: E402
from phase_agent_orchestrator.io import run_cli  # noqa: E402
from phase_agent_orchestrator.state.candidates import PREFIX  # noqa: E402


if __name__ == "__main__":
    run_cli(main, PREFIX)
