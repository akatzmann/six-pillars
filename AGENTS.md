# AI Agent Workflow & Core Engineering Constitution

> **Six-Pillar Agentic Engineering Architecture**  
> Formulated by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](LICENSE).  
> *Integrates Superpowers (Jesse Vincent, MIT), OpenSpec (MIT), and the Ponytail Decision Ladder (Dietrich Gebert, MIT).*

This file defines the mandatory, always-on workflow architecture, tool boundaries, and engineering principles for all repository interactions.

---

## 1. The Ponytail Decision Ladder & Core Principles (Always-On)

> **The Ponytail Decision Ladder**  
> Formalized into a 7-step multi-stage lifecycle gate by [@akatzmann](https://github.com/akatzmann).  
> Based on the Ponytail minimalism principles and ladder concept by [Dietrich Gebert](https://github.com/dietrichgebert/ponytail) (MIT License).

Before proposing an architecture, decomposing tasks, adding dependencies, or writing any code, you **must** adopt the Ponytail mindset: **rigorous about reading, lazy about writing new code**.

### Core Operational Principles
1. **Proportional Depth & Parallel Tool Batching:**
   - **Tier 1 (Conversational & Status Queries):** Answer directly or use only the minimal required lookup without scanning `openspec/` or `openwiki/architecture/`.
   - **Tier 2 (Targeted Operations, Research & Single-File Fixes):** Read only the directly relevant skill/file or run a focused search; batch independent read/status calls in parallel within a single turn rather than chaining sequential turns.
   - **Tier 3 (Architecture, Multi-File Engineering & OpenSpec Workflows):** Read first and trace deeply — thoroughly inspect `openwiki/`, `openspec/`, and existing codebase execution paths before proposing or modifying code.
2. **Walk the 7-Step Ponytail Decision Ladder (Stop at the First Rung That Works):**
   - **Rung 1 — Does this need to exist at all? (YAGNI):** If a feature, layer, abstraction, or config option is not strictly required by the user request or spec, do not build it.
   - **Rung 2 — Is the solution already in the codebase?** Search for and reuse existing helpers, components, patterns, and utilities instead of inventing parallel ones.
   - **Rung 3 — Does the standard library handle it?** Prefer built-in language and runtime primitives over third-party packages.
   - **Rung 4 — Does a native platform feature provide it?** Use native OS, runtime, database, CLI, or browser capabilities before custom code.
   - **Rung 5 — Does an already-installed dependency solve it?** Inspect package manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.) before introducing any new dependency.
   - **Rung 6 — Can it be written in one clear line?** Favor direct, idiomatic expressions over multi-file ceremony or premature abstraction.
   - **Rung 7 — Only then: Write the minimum implementation.** Write the smallest, cleanest, most maintainable code that satisfies the requirement.
3. **Protected Non-Negotiables:** Minimalism **never** compromises safety. Trust-boundary validation, error handling, security checks, PII/secret hygiene, accessibility, and automated tests are strictly protected and must never be skipped.

---

## 2. Six-Pillar Workflow Architecture & Plane Boundaries

All development separates the **Control Plane** (Main Workspace) from the **Execution Sandbox** (Isolated Git Worktrees):

| Pillar | Role | Plane | Scope & Ownership |
| :--- | :--- | :--- | :--- |
| **A) OpenSpec (`opsx-*`)** | Macro Lifecycle & Spec Control | Control Plane (Main Repo) | Owns `openspec/`. Lifecycle: `opsx-explore` -> `opsx-propose` -> `opsx-apply` -> `opsx-verify` -> `opsx-archive` (or `opsx-bulk-archive`). |
| **B) Beads (`bd`)** | Issue & Dependency Graph Tracker | Control Plane (Main Repo) | Owns `.beads/`. Replaces markdown checkbox tracking. Hierarchy: one `epic` per OpenSpec change → topic `feature` Beads → leaf subtask `task` Beads. `openspec/changes/<name>/tasks.md` acts as a manifest index (`## N.` = topic, `- [ ] N.M` = subtask) referencing the Beads IDs (`bd-xxxx`). |
| **C) Superpowers (`superpowers-*`)** | Micro-Task Implementation Engine | Execution Sandbox (Worktree) | Receives a **single dispatch unit** (one topic with its subtask queue, or one standalone leaf task) from `opsx-apply`. Runs in one isolated git worktree per unit (`superpowers-using-git-worktrees`), then per subtask writes a micro-plan (`superpowers-writing-plans`), executes TDD (`superpowers-test-driven-development` / `superpowers-subagent-driven-development`) and commits, and finally merges back once (`superpowers-finishing-a-development-branch`). |
| **D) Ponytail** | Anti-Bloat Decision Ladder | Cross-Cutting (Both Planes) | Applied during macro design (`opsx-explore`, `opsx-propose`) and micro implementation (`superpowers-*`, `opsx-verify`). |
| **E) Git-Commit (`git-commit`)** | Safe Commit & PII Gate | Cross-Cutting (Both Planes) | Mandatory for **every non-trivial commit**. Audits diffs for PII, secrets, and absolute paths, and writes structured `[AI]` commit messages. |
| **F) OpenWiki (`openwiki`)** | Project Encyclopedia & Institutional Memory SSOT | Control Plane (Main Repo) | Owns `openwiki/` (guided by `openwiki/INSTRUCTIONS.md`). Serves as the general, comprehensive encyclopedia for the entire project — covering **everything** with relevant knowledge impact across any project domain (domain knowledge, concepts, research, entities, events, ideas/theses, codebase architecture, modules, ADRs, implementation caveats, and operational runbooks). |

---

## 3. Mandatory Handoff & Invariant Rules

1. **OpenWiki First & Last (Comprehensive Project Encyclopedia):**
   - **Read (System-1 Radar → System-2 Full-Page Read):** Consult `openwiki/` during `opsx-explore`, `opsx-propose`, and `superpowers-writing-plans` (and whenever domain or project context is needed) to ground work in the project's domain knowledge, concepts, research syntheses, existing architecture, and institutional memory. When locating unfamiliar or multi-concept topics, auditing staleness, or tracing 1-hop links across `openwiki/`, orient first with `python3 .agents/skills/openwiki/scripts/wiki_scout.py` (`search`, `overview --section`, `neighbors`) before falling back to `rg` (reserving `rg` inside `openwiki/` strictly for regex, punctuation, or exact-literal patterns such as `#15` or path globs that FTS5 tokenization strips, while keeping `rg` unrestricted for non-`openwiki/` files), then **always** read complete matched `.md` pages (using `lines=[...]` hints on long files) before answering rather than synthesizing from search snippets alone.
   - **Write:** Update `openwiki/` (via the `openwiki` skill / CLI, respecting `openwiki/INSTRUCTIONS.md`) whenever durable project knowledge is added or modified, and during `opsx-archive` / `opsx-bulk-archive` so the encyclopedia and institutional memory stay synchronized with the repository. Never restrict OpenWiki to code-only documentation.
2. **Beads (`bd`) Over Plaintext Checkboxes:**
   - Never manage task state exclusively in plaintext markdown.
   - `opsx-propose` must create exactly one parent Beads Epic per change (`bd create ... --type epic`), one `feature` Bead per topic (`--parent <epic-id>`), and atomic, dependency-linked subtask Beads under each topic (`--parent <topic-id>`; trivial topics may be a single leaf `task` directly under the epic), recording their IDs in `tasks.md`.
   - **Sizing (split triggers, not quotas):** a subtask passes the "and" test (one sentence, no enumerations), fits one TDD cycle / one commit, has ~1–5 testable acceptance checks, and stays a reviewable diff (~≤300 changed lines). A change exceeding ~3 topics or ~7 subtasks, or bundling independently shippable features, is split into separate OpenSpec changes (or justified in `design.md`).
   - `opsx-apply` must query leaves via `bd ready --parent <epic-id> --exclude-type=epic,feature`, dispatch each ready topic as one unit, and `bd close` each subtask and then its topic upon completion (Beads does not auto-close parents).
3. **Strict Explore/Propose Boundary (The Agreement-Trap Invariant):**
   - `opsx-explore` is strictly read-only for thinking, mapping, and evaluating — never write application code or modify `.beads/`.
   - `opsx-propose` creates specification and tracking artifacts (`openspec/changes/`, `.beads/`), but is strictly read-only with respect to the application codebase.
   - Even if the user says *"Agreed"*, *"Sounds good"*, *"Proceed"*, *"Go ahead"*, or asks to build it during explore or propose, you MUST NOT begin modifying application code. You MUST stop and prompt for the next lifecycle phase (e.g. asking to run `/opsx-propose` after explore, or `/opsx-apply` after propose).
   - Application/production code may ONLY be written during `opsx-apply` via Superpowers inside isolated git worktrees.
4. **Strict Worktree Isolation & Repository Containment for Superpowers:**
   - `opsx-apply` never implements production code directly in the main workspace; it dispatches each ready topic (or standalone leaf task) to **Superpowers**.
   - Superpowers operates strictly inside an isolated git worktree and **must never** create or modify `openspec/` or `.beads/` files inside that worktree.
   - **Never Leave the Repository Boundary:** Agents and skills (particularly `superpowers-*`) should never leave the repository boundary (never `cd`, read, or write outside the repository root or in system `/tmp`, `/var/tmp`, or `..`) unless particularly requested by the user. Whenever temporary directories or files are needed, always use the gitignored `.tmp/` folder (`<REPO_ROOT>/.tmp/` or `<WORKTREE_PATH>/.tmp/`) as the parent directory.
   - Superpowers skips interactive `brainstorming` (already handled by `opsx-explore` / `opsx-propose`) and uses `superpowers-writing-plans` strictly for autonomous micro-planning of each assigned subtask.
5. **No Raw `git commit` on Non-Trivial Changes:**
   - Never run ad-hoc `git commit -m "..."` for non-trivial changes. Always follow the [`git-commit`](.agents/skills/git-commit/SKILL.md) skill to enforce diff clustering, `[AI]` conventional messages, and the mandatory PII/secret/absolute-path check.
6. **Idempotent Day-Zero Workspace Bootstrap (First-Run Gate):**
   - If the workspace was freshly initialized from this template (i.e., `.git/` or `.beads/` does not exist yet), run this **non-destructive, idempotent bootstrap** before executing any workflow step (and never overwrite existing files):
     ```bash
     [ -d .git ] || git init
     [ -f openspec/config.yaml ] || openspec init --tools none --no-animation
     bd init --init-if-missing --prefix bd --non-interactive --skip-agents --skip-hooks
     grep -qxF '.worktrees/' .gitignore 2>/dev/null || printf '\n# Superpowers isolated git worktrees\n.worktrees/\n' >> .gitignore
     grep -qxF '.tmp/' .gitignore 2>/dev/null || printf '\n# Repository-contained temporary files and directories\n.tmp/\n' >> .gitignore
     mkdir -p openwiki
     ```
   - Immediately after bootstrapping, if `AGENTS.md`, `.agents/`, `.gitignore`, `.beads/`, `openspec/`, or `openwiki/` have uncommitted scaffold changes, commit **only** those control-plane scaffold paths via the [`git-commit`](.agents/skills/git-commit/SKILL.md) skill so `HEAD` exists for git worktrees.
