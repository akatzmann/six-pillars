---
name: opsx-bulk-archive
description: >-
  Bulk finalize and archive multiple completed OpenSpec changes at once: batch select changes,
  detect and agentically resolve delta spec conflicts against the codebase, verify and batch-close
  Beads (bd) Epics and tasks, consolidate durable project knowledge and institutional memory in
  OpenWiki (openwiki/), move changes to archive, and commit via git-commit. Use when the user
  invokes /opsx:bulk-archive, opsx-bulk-archive, openspec-bulk-archive, or wants to archive
  multiple completed changes.
license: Apache-2.0
compatibility: Requires openspec, bd (Beads), openwiki, and git CLIs.
author: akatzmann (https://github.com/akatzmann)
attribution: >-
  Adapted and extended by akatzmann (github.com/akatzmann) for Beads issue hierarchies, Superpowers worktrees, and Ponytail gates. Inspired by OpenSpec (MIT).
version: "1.0.0"
---
# OpenSpec Bulk Archive + Beads Closure + OpenWiki Sync (`opsx-bulk-archive`)

> **Six-Pillar Agentic Engineering Suite**  
> Architected by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  
> *Derived from OpenSpec (MIT) with Beads dispatch & Ponytail decision gates.*


Finalizes multiple completed changes in a single cohesive batch across all Control-Plane pillars: **OpenSpec**, **Beads (`bd`)**, **OpenWiki (`openwiki/`)**, and **`git-commit`**.

It handles:
1. **Change Discovery & User Multi-Selection**: Interactive selection of active changes to archive.
2. **Batch Readiness Inspection**: Concurrently checking OpenSpec artifact statuses and Beads issue hierarchies (`bd children <EPIC_ID>` if an Epic exists).
3. **Cross-Change Delta Spec Conflict Detection & Agentic Resolution**: Mapping overlapping capability specs and inspecting codebase implementation evidence to establish merge order.
4. **Consolidated Pre-Archive Review & Single Confirmation Gate**: Clear summary table with conflict resolutions and warnings before executing.
5. **Batch Spec Synchronization & Directory Archival**: Syncing delta specs and moving change directories to `openspec/changes/archive/YYYY-MM-DD-<name>`.
6. **Batch Beads (`bd`) Closure**: Closing orphaned topics and parent Epics across all archived changes (gracefully skipped if a change has no Epic).
7. **Consolidated OpenWiki Synchronization (`openwiki/`)**: Single-pass update of all durable project knowledge, domain concepts, research, theses, system models, and institutional memory across all archived changes.
8. **Unified Git Commit via `git-commit`**: Staging and committing all changes under safe PII/secret verification and structured `[AI]` commit message conventions.

---

## Step 1: Discover Active Changes & Prompt Selection

1. **Query Active Changes:**
   ```bash
   openspec list --json
   ```
   If no active changes exist, inform the user and stop:
   > "No active OpenSpec changes found to archive."

2. **Prompt for Selection (Multi-Select):**
   Use the `ask_question` tool with multi-select enabled so the user can choose which changes to archive:
   - Present each active change with its schema name and summary.
   - Include a convenient option for "All active changes".
   - Allow any number of selections (1+ valid, 2+ is the standard bulk use case).
   - **Strict Invariant:** Never auto-select or auto-archive without explicit user selection.

---

## Step 2: Batch Readiness & Status Inspection

For each selected change `<name>`:

1. **Check OpenSpec Artifact Status:**
   ```bash
   openspec status --change "<name>" --json
   ```
   - Check `artifacts` array for `proposal`, `specs`, `design`, `tasks`. Note completed (`done`) vs pending artifacts.

2. **Validate OpenSpec Change:**
   ```bash
   openspec validate "<name>"
   ```
   - Record any validation warnings or errors.

3. **Check Beads (`bd`) Hierarchy Completion (if Beads Epic exists):**
   Extract `<EPIC_ID>` from `openspec/changes/<name>/tasks.md` (e.g. `<!-- bd: <EPIC_ID> -->` or task comments) or query:
   ```bash
   bd list --external-ref "openspec:<name>" --json
   ```
   - **If an Epic exists:**
     Check the full topic → subtask tree:
     ```bash
     bd children "<EPIC_ID>" --json
     ```
     Count open vs closed topics and leaf subtask beads. If any are open, flag this change with a **Warning** (and list unclosed Beads IDs).
   - **If no Epic exists:**
     Verify task completion via `tasks.md` checkboxes (`- [x]` vs `- [ ]`). Note `Beads: None (tasks verified)`.

4. **Catalog Delta Specs:**
   Check `openspec/changes/<name>/specs/` directory:
   - List each capability spec (e.g. `specs/<capability>/spec.md`).
   - Extract requirement headers (`### Requirement: <name>`) and change markers (`ADDED`, `MODIFIED`, `REMOVED`, `RENAMED`).

---

## Step 3: Cross-Change Delta Spec Conflict Detection & Agentic Resolution

1. **Map Capability Overlaps:**
   Build a collision map of `capability -> [changes touching this capability]`:
   ```text
   conference-overview-ui -> [change-a, change-b]  <- CONFLICT (2+ changes touch capability)
   speakers-directory     -> [change-c]            <- OK (single change)
   ```

2. **Agentic Conflict Resolution:**
   When 2+ selected changes modify the same capability (or overlapping requirements):
   - **Inspect Delta Specs:** Read each conflicting delta spec to determine what requirement modifications are proposed.
   - **Inspect the Codebase:** Search the codebase (`grep`, file inspection, git log) for concrete implementation evidence of the requirements.
   - **Determine Resolution:**
     - *Only one change implemented:* Sync only the implemented change's delta spec. Mark the unimplemented change's delta sync as skipped (with warning).
     - *Both changes implemented:* Determine execution/merge order:
       - Chronological order based on commit dates or change creation timestamps (older first, newer updates/refines).
       - Topological order if one depends on or refines the other.
       - If non-overlapping requirements, merge both additively into the capability spec.
     - *Neither implemented:* Skip delta spec sync for those requirements and warn the user.
   - **Record Rationale:** Clearly document which change's specs will be applied, in what order, and why.

---

## Step 4: Consolidated Pre-Archive Status Table & User Confirmation

Display a comprehensive Markdown table summarizing the state of all selected changes:

```markdown
| Change | Schema / Artifacts | Beads Status | Delta Specs | Conflicts | Readiness |
| :--- | :--- | :--- | :--- | :--- | :--- |
| change-alpha | Done (4/4) | 8/8 closed | 1 spec | None | Ready |
| change-beta  | Done (4/4) | 12/12 closed | 2 specs | ui-components (!) | Ready (Resolved) |
| change-gamma | 1 pending artifact | 4/6 closed (2 open) | None | None | Warning |
```

If conflicts were detected, display the resolution plan:
```markdown
* Spec Conflict Resolution Plan:
  - `ui-components`: Both change-beta and change-alpha implemented; applying change-beta first, then change-alpha (chronological commit order).
```

If warnings exist (unclosed Beads or incomplete artifacts), list them explicitly:
```markdown
* Warnings:
  - `change-gamma`: 1 pending artifact (`design`), 2 open Beads (`bd-abc.1`, `bd-abc.2`).
```

**Confirmation Gate:**
Prompt the user via `ask_question`:
- "Proceed with bulk archiving N changes?"
  - `(Recommended) Archive all ready changes (skip warning changes)`
  - `Archive all selected changes (including warnings)`
  - `Cancel`

**Strict Invariant:** If the user cancels, terminate immediately. Do not modify any files, move directories, or close beads.

---

## Step 5: Execute Delta Spec Synchronization & Archival

For each confirmed change (in the determined conflict resolution order):

1. **Sync Delta Specs:**
   - When changes have delta specs, apply the resolved deltas (`ADDED`, `MODIFIED`, `REMOVED`) directly into `openspec/specs/<capability>/spec.md`.
   - Ensure requirement headers, scenarios, and descriptions match the final implemented code.
   - Alternatively, for non-conflicting changes with standard structure, native OpenSpec archive may be used:
     ```bash
     openspec archive -y "<name>"
     ```
   - Verify that all main specs under `openspec/specs/` remain valid markdown and syntactically sound.

2. **Move Change to Archive:**
   - Create archive directory if missing: `mkdir -p openspec/changes/archive`
   - Determine target name:
     - If `<name>` already begins with `YYYY-MM-DD-`, keep the existing name without prepending a redundant date.
     - Otherwise, format as: `openspec/changes/archive/$(date +%Y-%m-%d)-<name>`.
     - *Collision guard:* If the destination directory already exists, append `-1`, `-2`, etc., to avoid data loss.
   - Move directory:
     ```bash
     mv "openspec/changes/<name>" "openspec/changes/archive/<target-name>"
     ```
   - Ensure `.openspec.yaml` is retained inside the archived change directory.

---

## Step 6: Batch Close Beads (`bd`) Epics & Tasks

For each successfully archived change with an associated Beads Epic:

1. **Close Dangling Topic Beads:**
   If any topic `feature` Beads are open but all their child subtasks are closed:
   ```bash
   bd close "<TOPIC_ID>" --reason "Topic subtasks complete; change bulk-archived."
   ```

2. **Close Parent Beads Epic:**
   ```bash
   bd close "<EPIC_ID>" --reason "OpenSpec change <name> verified, synced, and bulk-archived."
   ```

3. **Sync Tasks Manifest:**
   Ensure `tasks.md` in the archived change folder has all task checkboxes marked complete (`- [x]`) matching the closed Beads state.

*(If the change has no associated Beads Epic, simply ensure `tasks.md` checkboxes reflect completion.)*

---

## Step 7: Consolidated OpenWiki Project Encyclopedia & Institutional Memory Sync (`openwiki/`)

Rather than performing N separate documentation passes, consolidate all updates into **one unified OpenWiki synchronization pass** by invoking the **[`openwiki`](../openwiki/SKILL.md)** skill in **Mode B (Update Protocol)**:
1. **Pass Consolidated Changes Context:** Hand over the full batch of archived change directories, merged delta specs, and all newly introduced domain concepts, research syntheses, or venture theses.
2. **Pass Consolidated Institutional Memory:** Hand over any architectural decisions across the batch to record as ADRs (`openwiki/adr/`), non-obvious caveats/invariants (`openwiki/caveats/`), or operational playbooks (`openwiki/runbooks/`).
3. **Execute Single-Pass Update Protocol:** The `openwiki` skill applies the appropriate Multi-Archetype Quality Contract (Archetypes A, B, and C) across all touched domains, synchronizes `openwiki/quickstart.md` routing and directory `index.md` files in a single pass, and audits frontmatter and link integrity.
4. **POSIX EOF Newline Hygiene:** Ensure all created ADRs (`openwiki/adr/`), caveats (`openwiki/caveats/`), and updated architecture files terminate with a single trailing newline (`\n`) to prevent IDE auto-formatters from creating dirty working tree diffs post-commit.

---

## Step 8: Unified Git Commit via `git-commit`

Invoke the **[`git-commit`](../git-commit/SKILL.md)** skill to stage and commit all archival changes across the workspace:
- Archive directory moves under `openspec/changes/archive/`
- Synced main specifications under `openspec/specs/`
- Closed Beads state under `.beads/`
- Consolidated OpenWiki documentation under `openwiki/`

Perform the mandatory PII, secret, and absolute-path hygiene audit, and generate a clear conventional commit message:
```text
[AI] chore(opsx-bulk-archive): bulk archive N changes, sync specs, close Beads epics & update OpenWiki

* openspec:
  - Archived N changes: <change-1>, <change-2>, ...
  - Synced M delta requirements into main specs under openspec/specs/
* beads:
  - Closed parent Epics: <EPIC_1>, <EPIC_2>, ... (if applicable)
* openwiki:
  - Consolidated durable project knowledge, domain concepts, theses, and institutional memory
```

Immediately after committing, run `git status --porcelain` to verify the working tree is 100% clean with zero lingering uncommitted modifications.

---

## Step 9: Final Batch Summary

Output a clean, comprehensive summary report:

```markdown
## Bulk Archive Complete

### Archived Changes (N)
- `change-1` -> `openspec/changes/archive/YYYY-MM-DD-change-1/` (Epic: `bd-xxx` closed)
- `change-2` -> `openspec/changes/archive/YYYY-MM-DD-change-2/` (Epic: `bd-yyy` closed)

### Spec Sync & Conflict Resolution
- M delta specs synced to main specifications under `openspec/specs/`
- Resolved conflicts:
  - `capability-a`: Synced change-1 then change-2 (both implemented, chronological order)

### OpenWiki Sync
- Consolidated project knowledge and institutional memory committed to `openwiki/`

### Skipped / Warnings (if any)
- `change-3`: Skipped by user request (open Beads: `bd-zzz.1`)
```

---

## Guardrails & Non-Negotiables
- **Always Prompt for Selection:** Never guess which changes to archive; require explicit user multi-selection.
- **Never Auto-Archive on Cancellation:** If the confirmation prompt is cancelled, abort immediately without touching any files.
- **Agentic Codebase Investigation for Conflicts:** Do not blindly overwrite specs; verify whether code actually exists in the workspace.
- **Preserve Configuration:** Always retain `.openspec.yaml` inside archived change folders.
- **Single OpenWiki Pass:** Consolidate knowledge updates across all archived changes to prevent repetitive churn and broken cross-links.
- **Never Restrict OpenWiki to Code:** Treat domain concepts, empirical findings, and theses as first-class OpenWiki subjects alongside system architecture and institutional memory.
- **Strict Repository Boundary:** Never leave the repository root; keep any temporary planning files under `.tmp/`.
