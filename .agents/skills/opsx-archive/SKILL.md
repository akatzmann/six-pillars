---
name: opsx-archive
description: >-
  Finalize and archive a completed OpenSpec change: verify Beads (bd) epic completion (if used),
  sync delta specs to main OpenSpec specs, close the Beads Epic, update OpenWiki with durable
  project knowledge and institutional memory, move the change to archive, and commit via
  git-commit. Use when the user invokes /opsx:archive, opsx-archive, or wants to archive
  a finished change.
license: Apache-2.0
compatibility: Requires openspec, bd (Beads), openwiki, and git CLIs.
author: akatzmann (https://github.com/akatzmann)
attribution: >-
  Adapted and extended by akatzmann (github.com/akatzmann) for Beads issue hierarchies, Superpowers worktrees, and Ponytail gates. Inspired by OpenSpec (MIT).
version: "1.0.0"
---
# OpenSpec Archive + Beads Closure + OpenWiki Sync (`opsx-archive`)

> **Six-Pillar Agentic Engineering Suite**  
> Architected by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  
> *Derived from OpenSpec (MIT) with Beads dispatch & Ponytail decision gates.*


Finalizes a completed change across all Control-Plane pillars: **OpenSpec**, **Beads (`bd`)**, **OpenWiki (`openwiki/`)**, and **`git-commit`**.

---

## Step 1: Select Change & Verify Readiness

1. **Select Change:** Use the provided change name or prompt via `openspec list --json`.
2. **Check OpenSpec Artifact Status:**
   ```bash
   openspec status --change "<name>" --json
   ```
3. **Check Beads (`bd`) Completion (if Beads Epic exists):**
   Extract `<EPIC_ID>` from `openspec/changes/<name>/tasks.md` (or `bd list --external-ref "openspec:<name>" --json`):
   - **If an Epic exists:**
     Check the full topic → subtask tree:
     ```bash
     bd children "<EPIC_ID>" --json
     ```
     If any topic or subtask Beads are not `closed`, warn the user with the list of open Beads and ask for confirmation before proceeding. (Topics whose subtasks are all closed but which are still open can simply be closed — Beads does not auto-close parents.)
     Ensure `openspec/changes/<name>/tasks.md` checkboxes reflect the final Beads state.
   - **If no Epic exists:**
     Verify task completion via `tasks.md` checkboxes (`- [x]` vs `- [ ]`).

---

## Step 2: Sync Delta Specs & Archive the OpenSpec Change

1. **Validate Change Before Archive:**
   ```bash
   openspec validate "<name>"
   ```
2. **Sync Delta Specs & Move Change to Archive:**
   - You may run OpenSpec's native archive command:
     ```bash
     openspec archive -y "<name>"
     ```
   - Or, when intelligent partial delta merging is needed (`ADDED`, `MODIFIED`, `REMOVED`, `RENAMED` Requirements under `openspec/changes/<name>/specs/*/spec.md`), merge the deltas into `openspec/specs/<capability>/spec.md` first, then move `openspec/changes/<name>` to the archive directory:
     - Target name: if `<name>` already begins with `YYYY-MM-DD-`, keep it as-is; otherwise format as `openspec/changes/archive/$(date +%Y-%m-%d)-<name>`.

---

## Step 3: Close the Beads Epic (if applicable)

If a parent Beads Epic exists in `.beads/`:
```bash
bd close "<EPIC_ID>" --reason "OpenSpec change <name> verified, synced, and archived."
```

---

## Step 4: Synchronize OpenWiki (`openwiki/`)

Invoke the **[`openwiki`](../openwiki/SKILL.md)** skill in **Mode B (Update Protocol)**:
1. **Pass Completed Change Context:** Hand over the archived change directory (`openspec/changes/archive/...`), delta specs, design rationale, and any newly introduced or expanded domain concepts, research syntheses, or venture theses.
2. **Pass Discovered Institutional Memory:** Hand over any architectural decisions to record as ADRs (`openwiki/adr/`), non-obvious gotchas or invariants (`openwiki/caveats/`), or operational playbooks (`openwiki/runbooks/`).
3. **Execute Update Protocol:** The `openwiki` skill applies the appropriate Multi-Archetype Quality Contract (Archetype A for code/systems, Archetype B for research/domain, Archetype C for theses), synchronizes `openwiki/quickstart.md` routing and directory `index.md` files, and audits frontmatter and link integrity.
4. **POSIX EOF Newline Hygiene:** Ensure all created ADRs (`openwiki/adr/`), caveats (`openwiki/caveats/`), and updated architecture files terminate with a single trailing newline (`\n`) to prevent IDE auto-formatters from creating dirty working tree diffs post-commit.

---

## Step 5: Commit via `git-commit`

Invoke the **[`git-commit`](../git-commit/SKILL.md)** skill to stage and commit the archive move, synced specs, closed `.beads/` state, and updated `openwiki/` documentation (performing the mandatory PII/secret/absolute-path check and `[AI]` commit formatting).

Immediately after committing, run `git status --porcelain` to verify the working tree is 100% clean with zero lingering uncommitted modifications.
