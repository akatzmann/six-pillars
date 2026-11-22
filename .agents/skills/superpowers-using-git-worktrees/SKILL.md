---
name: superpowers-using-git-worktrees
description: >-
  Create and verify an isolated git worktree for implementing a single Beads (bd) dispatch
  unit (a topic with its subtask queue, or a standalone leaf task) handed over by opsx-apply. Ensures clean workspace isolation, gitignore safety, and a
  passing test baseline before micro-planning and TDD begin.
license: Apache-2.0
compatibility: Requires git CLI.
author: akatzmann (https://github.com/akatzmann)
attribution: >-
  Re-architected by akatzmann (github.com/akatzmann) for Beads dispatch units, Ponytail decision gates, and isolated git worktrees. Originally created by Jesse Vincent (MIT).
version: "1.0.0"
---
# Superpowers: Using Git Worktrees (`superpowers-using-git-worktrees`)

> **Six-Pillar Agentic Engineering Suite**  
> Architected by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  
> *Adapted from Jesse Vincent's Superpowers (MIT) with Ponytail gates & Beads dispatch.*


Creates an isolated **Execution Sandbox** (git worktree) for a single **Beads (`bd`)** dispatch unit (a topic `feature` Bead with its subtask queue, or a standalone leaf task) handed over by `opsx-apply`, keeping the main repository's Control Plane (`openspec/`, `.beads/`, `openwiki/`) untouched during code implementation.

> **Core Principle:** Systematic directory selection + safety verification + clean baseline = reliable unit isolation.
> **Strict Boundary:** Never create or modify `openspec/` or `.beads/` inside a Superpowers worktree. Never leave the repository boundary (unless particularly requested by the user); always use `.tmp/` (contained in `.gitignore`) as the parent directory whenever temporary directories or files are needed.

---

## Step 1: Select or Create the Worktree Directory

1. **Check Existing Worktree Directory:**
   ```bash
   ls -d .worktrees worktrees 2>/dev/null
   ```
   - Prefer `.worktrees/` at the repository root.
2. **Verify `.worktrees/` and `.tmp/` are Ignored by Git:**
   ```bash
   git check-ignore -q .worktrees 2>/dev/null && git check-ignore -q .tmp 2>/dev/null
   ```
   - If `.worktrees` or `.tmp` is **not** ignored, add `.worktrees/` and `.tmp/` to `.gitignore` (or `.git/info/exclude` if `.gitignore` should remain untouched) before creating the worktree.

---

## Step 2: Create the Worktree for the Assigned Unit

Given `<UNIT_ID>` and a short slug `<slug>` from the **Execution Packet** (all subtasks of the unit share this one worktree):

```bash
BRANCH_NAME="bead/${UNIT_ID}-<slug>"
WORKTREE_PATH=".worktrees/${UNIT_ID}-<slug>"

git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME"
```

> **CRITICAL TOOLING INVARIANT FOR WORKTREES:**
> 1. **Shell Commands (`run_command`):** Because each command runs in a fresh shell starting at the main workspace root, **always** prefix worktree commands with `cd "<WORKTREE_PATH>" && ...` (or `git -C "<WORKTREE_PATH>" ...`).
> 2. **File Tools (`read_file`, `edit_file`, `write_file`):** Always pass the path inside `<WORKTREE_PATH>/...` (e.g., `<REPO_ROOT>/.worktrees/<UNIT_ID>-<slug>/src/...`), **never** the main checkout's path.
> 3. **Never Leave the Repository Boundary (`.tmp/` for Temp Directories):** Never `cd`, read, or write outside the repository root (or into system `/tmp`, `/var/tmp`, or `..`) unless particularly requested by the user. Whenever temporary directories or files are needed inside the worktree, create them under `<WORKTREE_PATH>/.tmp/` (or `<REPO_ROOT>/.tmp/`).
> 4. **Subagent Option (`invoke_subagent`):** When dispatching a `self` subagent, you may either pass `<WORKTREE_PATH>` explicitly or invoke the subagent with `Workspace: "share"` (which automatically gives the subagent its own shared worktree).

---

## Step 3: Run Project Setup & Verify Clean Baseline

Inside `$WORKTREE_PATH`:
1. **Auto-detect and link/install dependencies if needed:**
   - Node.js: `npm ci` / `pnpm install` / `yarn install` (or symlink `node_modules` if appropriate and safe)
   - Python: use existing `.venv` or `uv sync` / `pip install -e .`
   - Rust / Go: `cargo check` / `go mod download`
2. **Run Baseline Tests (Target Scope):**
   Run the relevant test suite to confirm a clean green baseline before writing any new code.
   - If baseline tests fail prior to changes, report the pre-existing failure before proceeding.

---

## Step 4: Hand Off to `superpowers-writing-plans`

Report:
- Worktree path: `<WORKTREE_PATH>`
- Branch name: `<BRANCH_NAME>`
- Baseline test status: `PASS`
- Next step: Invoke **`superpowers-writing-plans`** to generate the micro-plan for the first subtask of `<UNIT_ID>`.

