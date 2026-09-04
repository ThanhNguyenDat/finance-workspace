"""Process entry point for the local Agent Transcripts MCP server.

Thin wrapper so `project.scripts` keeps every entry point under
`orchestrator.cli`; the reusable server/tool definitions live in
`orchestrator.mcp_server.agent_transcripts`.
"""

from __future__ import annotations

from ..mcp_server.agent_transcripts import main as _main


def cli() -> None:
    _main()
