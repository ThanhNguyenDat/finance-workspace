## 1. Rule text

- [x] 1.1 Rewrite `.agents/rules/coding-and-verification.md`'s
      "Solo-maintainer exception: commit directly to `main`" section (and
      its "Required order for a non-trivial change" block) to describe the
      per-change worktree workflow from design.md Decisions 1-6: worktree
      location (`.agents/worktrees/<change-name>`), creation via manual
      `git worktree add` + `EnterWorktree({path: ...})`, per-repository
      worktrees for a cross-repo change, `--cwd` pointed at the worktree for
      every provider turn, fast-forward/rebase-then-ff merge with no merge
      commits, and manual cleanup (`git worktree remove` + `git branch -d`)
      after merge since `ExitWorktree` cannot remove a `path`-entered
      worktree. Verify by reading the rewritten section against design.md's
      Decisions for completeness (each decision's operational consequence
      is stated).
- [x] 1.2 Update `.agents/rules/coding-and-verification.md`'s "Branch and
      merge discipline" section so it no longer contradicts the rewritten
      exception (that section currently describes feature-branch/PR
      ceremony as the general case with the exception carving direct-to-main
      out of it; after this change, the worktree-per-change flow is the one
      described everywhere, and merge is local fast-forward/rebase, not a
      PR). Verify there is no remaining sentence in the file that tells a
      reader to commit changes directly on `main` without a worktree.

## 2. Repository `.gitignore` entries

- [x] 2.1 Add a `.agents/worktrees/` line to `.gitignore` in
      `finance-workspace` (this repo), `finance-mw`, `finance-broker`,
      `finance-live-action`, and `mt5`. Verify per repo with
      `git check-ignore -v .agents/worktrees/anything` reporting a match
      against the new line.

## 3. Verification

- [ ] 3.1 In `finance-workspace`, exercise the full cycle once end-to-end
      with a throwaway change name: `git worktree add
      .agents/worktrees/worktree-workflow-smoke-test -b
      worktree-workflow-smoke-test`, `EnterWorktree({path: ...})`, make a
      trivial file change, commit it on the branch, `ExitWorktree({action:
      "keep"})`, fast-forward-merge into `main`, then `git worktree remove`
      + `git branch -d`. Verify: the commit lands on `main` with no merge
      commit (`git log --graph` shows a single linear line), the worktree
      directory is gone, the branch is gone, and `git status` in the main
      tree was never polluted with an untracked `.agents/` entry while the
      worktree existed (confirms task 2.1's `.gitignore` line works).
- [ ] 3.2 Confirm `openspec validate adopt-per-change-worktree-workflow
      --strict` passes (already skip_specs, so this is a sanity check that
      nothing else regressed).
