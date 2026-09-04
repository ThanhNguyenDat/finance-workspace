# Agent Transcripts artifact

A Claude Artifact chat-style viewer for coordinator attempt transcripts
(Claude and Codex, grouped by change and round). Source lives here so it
survives a machine restart; the live page itself is hosted by claude.ai, not
by this repository.

- Live page: <https://claude.ai/code/artifact/967348bf-57c0-482f-8154-ae5ad010706a>
- Source: `agent-transcripts.html` — a static page that renders
  `db.collection("attempts").onSnapshot(...)` results (contract 0.2.41,
  `capabilities: {"db": {}}`). Only a Claude session holding the Artifact tool
  can publish this file or write to the artifact's database; no CLI in this
  repository can do either step on its own.

## Refreshing it with a new session/round

1. Export the coordinator's normalized transcript for one session or one
   change (`change_name` groups every session under it):

   ```bash
   uv run --project tools/orchestrator export-transcript <session_id_or_change>
   ```

2. Split it into one JSON file per attempt, ready for `write_db`:

   ```bash
   uv run --project tools/orchestrator prepare-transcript-docs <session_id_or_change>
   ```

   Writes to `.ops/runtime/transcript-docs/<selector>/` by default (pass
   `--out-dir` to override); each file's name is the document id the artifact
   expects (`<session_id>-<phase lowercased>-a<attempt_no>.json`) and its
   content is the single JSON object to write at that id.

3. In a Claude session with the Artifact tool, push those files into the
   `attempts` collection with one `write_db` batch call (`db_op: "batch"`,
   one `{op: "set", collection: "attempts", doc_id: <stem>, file_path: <path>}`
   entry per file), targeting the live URL above.

## Editing the page itself

Edit `agent-transcripts.html` in place, then publish it with the `Artifact`
tool using `url: <the live URL above>` so the update lands on the same page
instead of creating a new one. Pass `capabilities: {"db": {}}` again on every
publish — omitting `capabilities` also carries the existing declaration
forward, but stating it explicitly here documents that it's required, not
incidental.

## Real-time streaming: tried, blocked at publish, kept as standalone tooling

The `db` arm above is pull-only — a viewer only sees whatever a Claude
session last pushed. A local MCP server (`host:agent-transcripts`) was built
to let the page poll the coordinator DB directly instead
(`mcp.watchTool("host:agent-transcripts", "get_transcripts", ...)`, per the
`mcp` capability's `host:` local-server design), but publishing the artifact
with that capability declared from *this* environment (Claude Code) is
rejected outright:

```text
mcp manifest rejected: "host:agent-transcripts" names a locally-configured
MCP server, and host servers aren't available in this session — declare
only claude.ai connectors ..., or to publish without connector access leave
"mcp" out of capabilities
```

So the artifact itself stayed on the `db`-only design. The server is real
and independently working, though — kept in the repo in case a session that
*can* declare `host:` capabilities (a claude.ai chat session, if that turns
out to support it) ever manages this artifact instead:

- `tools/orchestrator/src/orchestrator/mcp_server/agent_transcripts.py` — the
  server (tool `get_transcripts(selector="quant-research")`, returning the
  same shape `export-transcript` produces). Entry point `agent-transcripts-mcp`,
  installed to `tools/orchestrator/.venv/bin/agent-transcripts-mcp` by
  `uv sync --project tools/orchestrator`.
- Verified directly with a real MCP client over stdio (not through an
  artifact): lists exactly one tool (`get_transcripts`, `read_only_hint:
  true`) and a real call returned 34 attempts from the live coordinator DB.
  Unit coverage in `tests/test_agent_transcripts_mcp_server.py`.
- Not verified, and not currently usable from here: registering it in a
  Claude app as a local MCP server, and whether a `claude.ai`-originated
  publish of this artifact can declare `capabilities: {"mcp": {"servers":
  [{"server": "host:agent-transcripts", "tools": ["get_transcripts"]}]}}`
  where this session cannot.

## Known open issue

Live `db` rendering was checked once via browser automation right after
populating the store: `write_db`/`read_db` confirmed the documents are
present and well-formed, but the page's `onSnapshot` callback did not fire
within roughly 40 seconds in that check (no error either — `init()` reached
the `subscribing` step and then nothing). Unconfirmed whether this is a
transient viewer/tab quirk or a real issue with this page's subscription;
re-check by opening the live URL directly before assuming it's fixed.
