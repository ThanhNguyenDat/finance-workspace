"""Local MCP server for the "Agent Transcripts" Claude Artifact.

Runs over stdio on this machine, registered by the viewer in their own
Claude app as a local ("host:") MCP server — see
`tools/orchestrator/artifacts/README.md` for the registration steps and
current caveats (only reachable from inside the Claude app, by this
artifact's owner). Read-only: it reads through the same
`export_transcript._export` normalization export-transcript and
prepare-transcript-docs already use, and never touches coordinator state.
"""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from ..cli.export_transcript import _export
from ..coordinator.db import CoordinatorDB

server = MCPServer(name="agent-transcripts")


@server.tool(
    description=(
        "Return the normalized attempt transcripts for one coordinator "
        "session id, or one change_name grouping every session under it "
        "(e.g. 'quant-research'), in the same shape export-transcript "
        "produces."
    ),
    annotations=ToolAnnotations(read_only_hint=True),
)
def get_transcripts(selector: str = "quant-research") -> dict:
    db = CoordinatorDB()
    return {"attempts": _export(db, selector)}


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
