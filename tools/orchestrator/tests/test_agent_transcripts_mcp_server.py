from __future__ import annotations

import pytest

from orchestrator.mcp_server import agent_transcripts as mod


def test_registers_exactly_one_read_only_tool():
    tools = list(mod.server._tool_manager.list_tools())
    assert [t.name for t in tools] == ["get_transcripts"]
    assert tools[0].annotations.read_only_hint is True


def test_get_transcripts_wraps_export_transcript_result(monkeypatch: pytest.MonkeyPatch):
    calls: list[tuple[object, str]] = []

    def fake_export(db, selector):
        calls.append((db, selector))
        return [{"session_id": "sess-1", "attempt_no": 1}]

    monkeypatch.setattr(mod, "_export", fake_export)

    result = mod.get_transcripts(selector="my-change")

    assert result == {"attempts": [{"session_id": "sess-1", "attempt_no": 1}]}
    assert calls[0][1] == "my-change"


def test_get_transcripts_defaults_selector_to_quant_research(
    monkeypatch: pytest.MonkeyPatch,
):
    seen: list[str] = []
    monkeypatch.setattr(
        mod, "_export", lambda db, selector: seen.append(selector) or []
    )

    mod.get_transcripts()

    assert seen == ["quant-research"]
