---
name: superpowers-finishing-a-development-branch
description: >-
  Complete a Superpowers git-worktree implementation for a Beads dispatch unit (topic or leaf task): verify all tests
  pass, confirm all non-trivial changes were committed via the git-commit skill, integrate
  the worktree branch back into the main branch, clean up the worktree, and return the
  completion report to opsx-apply.
license: Apache-2.0
compatibility: Requires git CLI.
author: akatzmann (https://github.com/akatzmann)
attribution: >-
  Re-architected by akatzmann (github.com/akatzmann) for Beads dispatch units, Ponytail decision gates, and isolated git worktrees. Originally created by Jesse Vincent (MIT).
version: "1.0.0"
---
# Superpowers: Finishing a Development Branch (`superpowers-finishing-a-development-branch`)

> **Six-Pillar Agentic Engineering Suite**  
> Architected by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  
> *Adapted from Jesse Vincent's Superpowers (MIT) with Ponytail gates & Beads dispatch.*


Completes the isolated git-worktree lifecycle for a **Beads (`bd`)** dispatch unit and hands control back to `opsx-apply` in the main workspace.

---

## Step 1: Verify Tests & Clean Working Tree Inside the Worktree

1. **Run the Test Suite:**
   Execute the relevant test suite inside the worktree (`cd "<WORKTREE_PATH>" && <test_command>`).
   - If any test fails, fix it before proceeding. Never merge a failing worktree branch.
2. **Verify Worktree Git Status is Clean:**
   ```bash
   git -C "<WORKTREE_PATH>" status --porcelain
   ```
   - Verify no changes exist under `openspec/` or `.beads/` inside the worktree. If any accidental edits to `openspec/` or `.beads/` occurred in the worktree, discard them (`git -C "<WORKTREE_PATH>" checkout -- openspec .beads`).
   - If uncommitted code/test changes remain, invoke the **[`git-commit`](../git-commit/SKILL.md)** skill (with `workdir: "<WORKTREE_PATH>"`) to audit for PII/secrets/absolute paths and commit them.

---

## Step 2: Integrate the Worktree Branch & Clean Up

Default behavior during an autonomous `opsx-apply` loop is **local fast-forward / merge back into the base branch** (unless the user explicitly requested a separate PR per unit):

1. **Record the Final Commit SHA from the Worktree:**
   ```bash
   COMMIT_SHA=$(git -C "<WORKTREE_PATH>" rev-parse --short HEAD)
   ```
2. **Merge into the Main Repository Checkout:**
   ```bash
   git merge --no-ff "bead/<UNIT_ID>-<slug>" -m "[AI] merge(<UNIT_ID>): integrate completed bead topic"
   ```
   *(Or fast-forward `git merge --ff-only "bead/<UNIT_ID>-<slug>"` when linear history is preferred).*
3. **Remove the Isolated Worktree & Temporary Branch:**
   *(First remove any worktree-local `.tmp/` directory if created during tests so `git worktree remove` succeeds cleanly without `--force`):*
   ```bash
   rm -rf "<WORKTREE_PATH>/.tmp"
   git worktree remove "<WORKTREE_PATH>"
   git branch -d "bead/<UNIT_ID>-<slug>"
   ```

---

## Step 3: Return the Bead Completion Report to `opsx-apply`

Provide the following structured handoff back to `opsx-apply` so it can update `.beads/`, `tasks.md`, and OpenWiki notes in the Control Plane:

```markdown
### Bead Completion Report: `<UNIT_ID>`
- **Status:** COMPLETED
- **Subtask Commits:** `<SUBTASK_ID>` → `<SHA>` (one line per subtask; mark any incomplete subtask as `NOT DONE` with reason)
- **Merge SHA:** `<MERGE_SHA>`
- **Files Changed:** `<list of files>`
- **Verification Summary:** `<test command run & pass count>`
- **Ponytail Rung Applied:** Rung `<N>` (`<brief note>`)
- **Discovered Follow-Up Tasks (for Beads):** `<None | list of new subtasks/topics to create>`
- **Discovered Knowledge / Caveats / ADRs (for OpenWiki):** `<None | domain knowledge, caveats, or ADRs to sync into openwiki/>`
```

