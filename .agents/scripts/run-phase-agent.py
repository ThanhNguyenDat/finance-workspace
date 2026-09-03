#!/usr/bin/env python3

from _bootstrap import bootstrap

bootstrap()

from phase_agent_orchestrator.run_phase_agent import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
