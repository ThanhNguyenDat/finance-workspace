#!/usr/bin/env python3

from _bootstrap import bootstrap

bootstrap()

import sys  # noqa: E402

from phase_agent_orchestrator.run_phase_agent_command import main  # noqa: E402


if __name__ == "__main__":
    print("run-claude-command: compatibility entrypoint; routing through phase agents", file=sys.stderr)
    raise SystemExit(main())
