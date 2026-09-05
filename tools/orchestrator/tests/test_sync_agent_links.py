from orchestrator.cli import sync_agent_links as sal


def _make_agents_dir(tmp_path):
    agents_dir = tmp_path / ".agents"
    (agents_dir / "skills" / "real-skill").mkdir(parents=True)
    (agents_dir / "rules").mkdir(parents=True)
    (agents_dir / "rules" / "a-rule.md").write_text("rule", encoding="utf-8")
    (agents_dir / "skills" / "openspec-native").mkdir(parents=True)
    return agents_dir


def _patch(monkeypatch, tmp_path, agents_dir, tools=(".claude",)):
    monkeypatch.setattr(sal, "ROOT_DIR", tmp_path)
    monkeypatch.setattr(sal, "AGENTS_DIR", agents_dir)
    monkeypatch.setattr(sal, "TOOLS", tools)


def test_check_reports_missing_links_without_creating_them(tmp_path, monkeypatch):
    agents_dir = _make_agents_dir(tmp_path)
    _patch(monkeypatch, tmp_path, agents_dir)

    status = sal.main(["--check"])

    assert status != 0
    assert not (tmp_path / ".claude" / "skills" / "real-skill").exists()


def test_run_creates_missing_links(tmp_path, monkeypatch):
    agents_dir = _make_agents_dir(tmp_path)
    _patch(monkeypatch, tmp_path, agents_dir)

    status = sal.main([])

    assert status == 0
    skill_link = tmp_path / ".claude" / "skills" / "real-skill"
    rule_link = tmp_path / ".claude" / "rules" / "a-rule.md"
    assert skill_link.is_symlink()
    assert skill_link.resolve() == (agents_dir / "skills" / "real-skill").resolve()
    assert rule_link.is_symlink()
    assert rule_link.read_text(encoding="utf-8") == "rule"


def test_run_then_check_is_clean(tmp_path, monkeypatch):
    agents_dir = _make_agents_dir(tmp_path)
    _patch(monkeypatch, tmp_path, agents_dir)

    assert sal.main([]) == 0
    assert sal.main(["--check"]) == 0


def test_openspec_prefixed_skills_are_skipped(tmp_path, monkeypatch):
    agents_dir = _make_agents_dir(tmp_path)
    _patch(monkeypatch, tmp_path, agents_dir)

    sal.main([])

    assert not (tmp_path / ".claude" / "skills" / "openspec-native").exists()


def test_real_local_entry_blocks_the_shared_link(tmp_path, monkeypatch, capsys):
    agents_dir = _make_agents_dir(tmp_path)
    _patch(monkeypatch, tmp_path, agents_dir)
    rules_dir = tmp_path / ".claude" / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "a-rule.md").write_text("a different, real copy", encoding="utf-8")

    status = sal.main([])

    assert status != 0
    assert "real local entry blocks shared link" in capsys.readouterr().err
    assert (rules_dir / "a-rule.md").read_text(encoding="utf-8") == (
        "a different, real copy"
    )


def test_stale_link_is_removed_on_run_but_only_reported_on_check(tmp_path, monkeypatch):
    agents_dir = _make_agents_dir(tmp_path)
    _patch(monkeypatch, tmp_path, agents_dir)
    skills_dir = tmp_path / ".claude" / "skills"
    skills_dir.mkdir(parents=True)
    stale_link = skills_dir / "removed-skill"
    stale_link.symlink_to("../../.agents/skills/removed-skill")

    assert sal.main(["--check"]) != 0
    assert stale_link.is_symlink()

    sal.main([])
    assert not stale_link.is_symlink()
    assert not stale_link.exists()
