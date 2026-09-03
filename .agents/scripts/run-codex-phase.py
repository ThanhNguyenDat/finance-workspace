#!/usr/bin/env python3

from _bootstrap import bootstrap

bootstrap()

from phase_agent_orchestrator.run_codex_phase import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
