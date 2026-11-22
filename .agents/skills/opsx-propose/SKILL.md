---
name: opsx-propose
description: >-
  Propose a new OpenSpec change, generate spec/design artifacts grounded in OpenWiki and
  the Ponytail Decision Ladder, decompose the change into one Beads (bd) Epic, topic-level
  feature Beads, and sized, dependency-linked subtask Beads (splitting oversized changes),
  and write tasks.md as a manifest referencing the Beads issue IDs. Use when the
  user invokes /opsx:propose, opsx-propose, or wants to turn an idea into a formal proposal
  and task graph ready for implementation.
license: Apache-2.0
compatibility: Requires openspec and bd (Beads) CLIs.
author: akatzmann (https://github.com/akatzmann)
attribution: >-
  Adapted and extended by akatzmann (github.com/akatzmann) for Beads issue hierarchies, Superpowers worktrees, and Ponytail gates. Inspired by OpenSpec (MIT).
version: "1.0.0"
---
# OpenSpec Propose + Beads Decomposition (`opsx-propose`)

> **Six-Pillar Agentic Engineering Suite**  
> Architected by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  
> *Derived from OpenSpec (MIT) with Beads dispatch & Ponytail decision gates.*


Creates a complete OpenSpec change (`proposal.md`, `specs/`, `design.md`, `tasks.md`) **and** hands over task tracking to **Beads (`bd`)** by decomposing the change into one Epic, topic-level `feature` Beads, and atomic, dependency-linked subtask Beads.

---

## Step 1: Clarify Intent & Consult OpenWiki

1. **Derive Change Name:** If the user has not provided a clear scope, ask a concise clarifying question. Derive a `kebab-case` change name (e.g., `add-token-cache`).
2. **Consult OpenWiki (`openwiki/`):**
   - Inspect `openwiki/` (including `INSTRUCTIONS.md`, `quickstart.md`, domain/research pages, architecture docs, **ADRs**, and **known caveats**).
   - Ensure the proposed design grounds itself in existing project knowledge and respects documented architectural constraints (or explicitly notes which ADR will be superseded).
3. **Ponytail Design Gate:**
   - Run the proposed solution through the **Ponytail 7-Step Decision Ladder** (`AGENTS.md`).
   - Eliminate speculative abstractions (Rung 1), reuse existing codebase utilities (Rung 2), and prefer stdlib/native/existing dependencies (Rungs 3–5) before designing custom components.

---

## Step 2: Scaffold the OpenSpec Change & Build Spec/Design Artifacts

1. **Ensure Git, OpenSpec & Beads are Initialized in the Repo:**
   - If `.git/` does not exist, run `git init`.
   - If `openspec/config.yaml` does not exist, initialize it without overwriting custom skills (`openspec init --tools none --no-animation`).
   - If `.beads/` does not exist, initialize Beads idempotently without overwriting `AGENTS.md` (`bd init --init-if-missing --prefix bd --non-interactive --skip-agents --skip-hooks`).
2. **Create the Change Directory:**
   ```bash
   openspec new change "<name>"
   ```
3. **Inspect Artifact Build Order:**
   ```bash
   openspec status --change "<name>" --json
   ```
4. **Generate `proposal.md`, `specs/`, and `design.md`:**
   - First check existing capability specs via `openspec list --specs` so `proposal.md` reuses existing capability paths where appropriate (or sets `skip_specs: true` in `.openspec.yaml` if a pure refactor/doc/tooling change has no spec-level behavior delta).
   - For each artifact leading up to `tasks`:
     ```bash
     openspec instructions <artifact-id> --change "<name>" --json
     ```
   - Follow the schema template and rules (e.g., `#### Scenario:` must use 4 hashtags, new capabilities start with `## Purpose`).
   - In `design.md`, explicitly reference relevant **OpenWiki** pages/ADRs/caveats and document why the chosen approach is the minimal viable solution under the **Ponytail Ladder**.

---

## Step 3: Decompose Tasks into Beads (`bd`)

Instead of managing standalone markdown task lists, decompose the implementation into a **three-level Beads (`bd`) hierarchy**:

| Level | Beads type | `tasks.md` | Execution unit |
| :--- | :--- | :--- | :--- |
| **Change** | `epic` (exactly one per OpenSpec change) | Header (`Beads Epic ID`) | — |
| **Topic** (cohesive task group) | `feature`, child of the epic | `## N. [<TOPIC_ID>] <Topic>` (no checkbox) | **One Superpowers worktree** |
| **Subtask** (leaf) | `task`, child of a topic | `- [ ] N.M [<SUBTASK_ID>] ...` | **One TDD cycle + one commit** |

**Trivial topics** (a single subtask's worth of work) skip the `feature` level: create one leaf `task` directly under the epic and list it as `## N.` heading plus a single `- [ ] N.1 [<TASK_ID>] ...` line. Do not split trivial work into multiple tickets.

> [!IMPORTANT]
> Topics must use `--type feature` (not `task`). Beads lists parent tasks as `ready` alongside their own subtasks and does not auto-close parents; `opsx-apply` therefore queries leaves via `--exclude-type=epic,feature`.

### Sizing Rules (Split Triggers, Not Quotas)

Grounded in INVEST / vertical-slicing practice and adapted to agent execution (context drift and unreviewable diffs are the main failure modes; per-worktree overhead is the cost of over-splitting):

- **Subtask — split it if any check fails:**
  1. **"And" test:** Its title is a single sentence without "and" / enumerations (e.g., "feedback items A–F" fails).
  2. **One TDD cycle:** One Red→Green→Refactor loop, landing as one coherent commit.
  3. **Testable:** ~1–5 concrete acceptance checks, at least one automated or observable.
  4. **Reviewable diff:** Roughly ≤ ~300 changed lines / a handful of files.
- **Topic:** A vertical slice of the change that delivers independently verifiable value and owns its own tests and docs (never a trailing "tests" or "docs" topic).
- **Change — split into separate OpenSpec changes** if it exceeds **~3 topics or ~7 subtasks**, or bundles features that could ship independently. Each change gets its own proposal and epic; order dependent changes via `bd dep add <later-epic-id> <earlier-epic-id>`. If a larger change is genuinely indivisible, justify it explicitly in `design.md`.

### Commands

1. **Create the Parent Beads Epic:**
   ```bash
   EPIC_ID=$(bd create "OpenSpec: <name>" \
     --type epic \
     --spec-id "openspec:<name>" \
     --external-ref "openspec:<name>" \
     --description "Tracking epic for OpenSpec change <name> (openspec/changes/<name>/)" \
     --silent)
   ```
2. **Create Topic Beads (`feature`) Under the Epic:**
   For each topic derived from `design.md` and `specs/`:
   ```bash
   TOPIC_ID=$(bd create "<topic title>" \
     --type feature \
     --parent "$EPIC_ID" \
     --spec-id "openspec:<name>" \
     --description "<what this vertical slice delivers and why>" \
     --design "See openspec/changes/<name>/design.md. Relevant OpenWiki caveats: <paths/notes>" \
     --acceptance "<topic-level outcome matching delta specs>" \
     --silent)
   ```
3. **Create Subtask Beads (`task`) Under Each Topic:**
   ```bash
   SUBTASK_ID=$(bd create "<one-sentence subtask title>" \
     --parent "$TOPIC_ID" \
     --spec-id "openspec:<name>" \
     --description "<what needs to be built and why>" \
     --acceptance "<1–5 clear, testable acceptance checks>" \
     --silent)
   ```
   *(For a trivial topic, create a single leaf `task` with `--parent "$EPIC_ID"` instead, including `--design`.)*
4. **Wire Dependencies (Ordering & Blockers):**
   - **Across topics:** Link at topic level (`bd dep add <topic-b-id> <topic-a-id>`). A blocked topic blocks all of its subtasks.
   - **Within a topic:** Link subtasks in execution order (`--deps "blocked-by:<subtask-id>"` or `bd dep add <later> <earlier>`).
   - Avoid subtask→subtask dependencies across topics; lift them to the topic level instead.
5. **Verify the Dependency Graph:**
   ```bash
   bd children "$EPIC_ID"
   bd ready --parent "$EPIC_ID" --exclude-type=epic,feature
   ```

---

## Step 4: Write `openspec/changes/<name>/tasks.md` as a Beads Manifest & Validate

To satisfy OpenSpec's `tasks` parser (`- [ ] X.Y ...` under `## N.` headings) while keeping **Beads (`bd`)** as the authoritative issue tracker, write `openspec/changes/<name>/tasks.md` using the following structure:

```markdown
# Tasks

> **Source of Truth:** Task state, dependencies, and blockers are tracked in **Beads (`bd`)**.
> - **Beads Epic ID:** `<EPIC_ID>`
> - **Query Ready Work:** `bd ready --parent <EPIC_ID> --exclude-type=epic,feature`
> - **View Full Graph:** `bd children <EPIC_ID>`

## 1. [`<TOPIC_1_ID>`] <Topic 1 title> *(deps: none)*

- [ ] 1.1 [`<TOPIC_1_ID>.1`] <Subtask title and verification check> *(deps: none)*
- [ ] 1.2 [`<TOPIC_1_ID>.2`] <Subtask title and verification check> *(deps: blocked-by `<TOPIC_1_ID>.1`)*

## 2. [`<TOPIC_2_ID>`] <Topic 2 title> *(deps: blocked-by `<TOPIC_1_ID>`)*

- [ ] 2.1 [`<TOPIC_2_ID>.1`] <Subtask title and verification check> *(deps: none)*

## 3. [`<TASK_3_ID>`] <Trivial topic title> *(deps: none)*

- [ ] 3.1 [`<TASK_3_ID>`] <Single leaf task and verification check> *(deps: none)*
```

Topic headings carry no checkbox; only leaf Beads are tracked as checkboxes, so OpenSpec progress equals leaf-Bead progress. Workflow follow-up (verify/archive) goes into an optional trailing `## Workflow follow-up` section as plain bullets.

Verify OpenSpec recognizes all required artifacts as `done` and passes validation:
```bash
openspec status --change "<name>"
openspec validate "<name>"
```

---

## Step 5: Output Summary

Report to the user:
- OpenSpec change location (`openspec/changes/<name>/`) and created artifacts (`proposal.md`, `specs/`, `design.md`, `tasks.md`).
- **Beads Epic ID** (`<EPIC_ID>`) and the topic → subtask tree with dependencies (`bd children <EPIC_ID>`).
- Which leaf Beads are immediately `ready` (`bd ready --parent <EPIC_ID> --exclude-type=epic,feature`).
- If any sizing split trigger was exceeded, the justification recorded in `design.md` (or the follow-up changes proposed instead).
- Prompt: *"Ready for implementation. Run `opsx-apply` to dispatch ready topics into Superpowers worktrees."*

