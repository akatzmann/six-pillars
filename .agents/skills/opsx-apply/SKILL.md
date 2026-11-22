---
name: opsx-apply
description: >-
  Orchestrate the implementation of an OpenSpec change by querying ready leaf subtasks from
  Beads (bd), handing each ready topic (with its subtask queue) over to Superpowers for
  isolated git-worktree TDD implementation and git-commit persistence, and updating Beads
  and tasks.md state in the Control Plane. Use when the user invokes /opsx:apply,
  opsx-apply, or asks to implement an OpenSpec change.
license: Apache-2.0
compatibility: Requires openspec, bd (Beads), and git CLIs.
author: akatzmann (https://github.com/akatzmann)
attribution: >-
  Adapted and extended by akatzmann (github.com/akatzmann) for Beads issue hierarchies, Superpowers worktrees, and Ponytail gates. Inspired by OpenSpec (MIT).
version: "1.0.0"
---
# OpenSpec Apply — Beads-to-Superpowers Dispatcher (`opsx-apply`)

> **Six-Pillar Agentic Engineering Suite**  
> Architected by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  
> *Derived from OpenSpec (MIT) with Beads dispatch & Ponytail decision gates.*


`opsx-apply` operates in the **Control Plane (Main Workspace)**. It **never** writes production code directly in the main checkout. Instead, it iterates over ready **Beads (`bd`)** topics and hands each one (with its subtask queue) to **Superpowers** for isolated git-worktree execution.

---

## Step 1: Select the Change & Load Control-Plane Context

1. **Resolve Change Name:**
   - Use the provided change name, infer from context, or list active changes via `openspec list --json`.
2. **Verify OpenSpec Readiness:**
   ```bash
   openspec status --change "<name>" --json
   openspec instructions apply --change "<name>" --json
   ```
   - Read `proposal.md`, `specs/`, `design.md`, and `tasks.md` from `openspec/changes/<name>/`.
3. **Locate the Beads Epic ID:**
   - Extract the `Beads Epic ID` (`<EPIC_ID>`) from `openspec/changes/<name>/tasks.md`, or look it up via:
     ```bash
     bd list --external-ref "openspec:<name>" --json
     ```
4. **Gather OpenWiki Context:**
   - Identify any relevant files in `openwiki/` (domain encyclopedia pages, research syntheses, ADRs, architectural boundaries, module docs, caveats) referenced in `design.md` or applicable to the change.

---

## Step 2: Dispatch Loop — Beads (`bd`) -> Superpowers (`superpowers-*`)

**Dispatch unit:** One **topic** (`feature` Bead) = one Superpowers worktree, executing its subtasks sequentially (one TDD cycle + one commit each) and merging once. A **trivial leaf task** directly under the epic is its own dispatch unit. Topics run in parallel only if they touch disjoint files.

Loop until no ready leaf Beads remain under `<EPIC_ID>`:

### 2.1 Query Ready Leaves & Resolve the Dispatch Unit
```bash
bd ready --parent "<EPIC_ID>" --exclude-type=epic,feature --json
```
- Topics must be excluded via `feature`: Beads lists parent beads as `ready` alongside their own subtasks.
- Pick the highest-priority ready leaf and read its `parent` (`bd show "<LEAF_ID>" --json`):
  - Parent is a topic (`feature`) → **`<UNIT_ID>` = that topic**; its **subtask queue** = all open children (`bd children "<UNIT_ID>" --json`) in dependency order.
  - Parent is the epic → **`<UNIT_ID>` = the leaf itself**; the queue holds just that leaf.
- If no leaves are ready, check `bd children "<EPIC_ID>" --json`:
  - If all leaf Beads are `closed`, proceed to **Step 3 (Completion)**.
  - If remaining Beads are `blocked` or `deferred`, report the blockers to the user and pause.

### 2.2 Atomically Claim the Unit in the Control Plane
```bash
bd update "<UNIT_ID>" --claim
bd update "<SUBTASK_ID>" --claim   # for each subtask in the queue
bd show "<UNIT_ID>" --json
```

### 2.3 Assemble the Execution Packet & Hand Over to Superpowers
Activate **`superpowers-subagent-driven-development`** (which coordinates `superpowers-using-git-worktrees` -> per subtask: `superpowers-writing-plans` -> `superpowers-test-driven-development` -> `git-commit` -> finally `superpowers-finishing-a-development-branch`) with the following **Execution Packet**:

```markdown
### Execution Packet
- **Unit ID:** <UNIT_ID> (topic or standalone leaf task)
- **Title:** <Unit Title>
- **Description & Goal:** <Unit Description>
- **Subtask Queue (execute in order, one TDD cycle + one commit each):**
  1. `<SUBTASK_ID>` — <title> — Acceptance: <acceptance checks>
  2. `<SUBTASK_ID>` — <title> — Acceptance: <acceptance checks> (blocked-by previous)
- **Macro Design Context (Read-Only):** Relevant excerpts/paths from `openspec/changes/<name>/design.md` and `openspec/changes/<name>/specs/`
- **OpenWiki Context (Read-Only):** Relevant domain knowledge, research pages, ADRs, architecture notes, and caveats from `openwiki/`
- **Sandbox Constraints:**
  1. Execute strictly inside a single dedicated git worktree for this unit (`superpowers-using-git-worktrees`).
  2. NEVER create or modify `openspec/` or `.beads/` inside the worktree.
  3. NEVER leave the repository boundary (unless particularly requested by the user); always use the `.tmp/` folder (contained in `.gitignore`) as the parent directory when temporary directories or files are needed.
  4. Skip interactive brainstorming; use `superpowers-writing-plans` for autonomous micro-planning of each subtask.
  5. Enforce the Ponytail 7-Step Decision Ladder (`AGENTS.md`) during planning and TDD.
  6. Commit each subtask exclusively via the `git-commit` skill, referencing its `<SUBTASK_ID>` in the commit message.
  7. Merge/finish the worktree branch once via `superpowers-finishing-a-development-branch` and return the commit SHA per subtask, test summary, and any newly discovered caveats or follow-up work.
```

### 2.4 Record Completion in the Control Plane (Main Workspace)
Once Superpowers finishes the worktree branch, merges the code back, cleans up the worktree, and returns the result:

1. **Close Each Subtask, Then the Topic, in `.beads/`:**
   ```bash
   bd close "<SUBTASK_ID>" --reason "Implemented and verified in commit <SUBTASK_COMMIT_SHA>"   # per subtask
   bd close "<UNIT_ID>" --reason "All subtasks merged in <MERGE_SHA>"                          # topic (Beads does not auto-close parents)
   ```
   If a subtask could not be completed, leave it (and the topic) open, unclaim it, and report why.
2. **Sync the Index Checkboxes in `openspec/changes/<name>/tasks.md`:**
   Update each `- [ ] N.M [<SUBTASK_ID>]` to `- [x] N.M [<SUBTASK_ID>]` (appending `*(commit: `<SUBTASK_COMMIT_SHA>`)*`).
3. **Handle Newly Discovered Work or Caveats:**
   - If Superpowers discovered new work required for the spec, create a new subtask under the relevant topic (`bd create ... --parent "<TOPIC_ID>"`) — or a new topic under `<EPIC_ID>` if it is a separate slice — wire its dependencies (`bd dep add`), and append it to `tasks.md`. Apply the `opsx-propose` sizing rules.
   - If Superpowers uncovered a non-obvious caveat, architectural decision, or durable domain insight, record a note on the Epic (`bd note "<EPIC_ID>" "OpenWiki note: ..."`) so `opsx-verify` / `opsx-archive` / `opsx-bulk-archive` syncs it into `openwiki/`.
   - **Follow-up user feedback during apply** is decomposed the same way: one new topic per feedback theme with one subtask per independent item — never one bead bundling several items.

---

## Step 3: Completion & Handoff to Verify

When all leaf and topic Beads under `<EPIC_ID>` are `closed`:
1. Commit the updated `openspec/changes/<name>/tasks.md` and `.beads/` state in the main workspace using the **`git-commit`** skill.
2. Output a summary of all completed topics and subtasks with their commit SHAs.
3. Recommend running **`opsx-verify`** to validate the complete implementation against OpenSpec, Beads, Ponytail, and OpenWiki before archiving.

