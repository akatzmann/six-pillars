---
name: superpowers-subagent-driven-development
description: >-
  Execute a handed-over Beads (bd) dispatch unit (a topic with its subtask queue, or a
  standalone leaf task) end-to-end inside one isolated git worktree by coordinating worktree
  creation, per-subtask micro-planning, TDD implementation, two-stage review (Spec/Ponytail
  compliance + Code Quality), per-subtask git-commit persistence, and branch finishing.
  Use when opsx-apply dispatches a Bead topic or task for implementation.
license: Apache-2.0
author: akatzmann (https://github.com/akatzmann)
attribution: >-
  Re-architected by akatzmann (github.com/akatzmann) for Beads dispatch units, Ponytail decision gates, and isolated git worktrees. Originally created by Jesse Vincent (MIT).
version: "1.1.0"
---
# Superpowers: Subagent-Driven Bead Execution (`superpowers-subagent-driven-development`)

> **Six-Pillar Agentic Engineering Suite**  
> Architected by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  
> *Adapted from Jesse Vincent's Superpowers (MIT) with Ponytail gates & Beads dispatch.*


This is the primary **Execution Plane entrypoint** called by `opsx-apply` for each ready **Beads (`bd`)** dispatch unit (`<UNIT_ID>`: a topic `feature` Bead with its subtask queue, or a standalone leaf task).

You may execute this pipeline either by launching an isolated `self` subagent (`invoke_subagent` with `TypeName: "self"`, passing the **Execution Packet**) or in the current agent session strictly scoped to the dedicated git worktree.

---

## Execution Pipeline for a Dispatch Unit (`<UNIT_ID>`)

```
1. superpowers-using-git-worktrees (one worktree for the whole unit)
        │
        ▼
   ┌─ For each <SUBTASK_ID> in the queue (in order) ──────────────────┐
   │ 2. superpowers-writing-plans (Micro-Plan + Ponytail Gate)        │
   │ 3. superpowers-test-driven-development (Red → Green → Refactor)  │
   │ 4. Two-Stage Review Gate (Spec/Subtask + Ponytail/Quality)       │
   │ 5. git-commit Skill (PII/Secret/Path Check + [AI] [<SUBTASK_ID>]) │
   └──────────────────────────────────────────────────────────────────┘
        │
        ▼
6. superpowers-finishing-a-development-branch (Merge once & cleanup worktree)
```

---

## Step 1: Isolate Worktree
Follow **`superpowers-using-git-worktrees`** to create `.worktrees/<UNIT_ID>-<slug>` on branch `bead/<UNIT_ID>-<slug>` and verify baseline tests pass.

## Step 2: Autonomous Micro-Plan (per Subtask)
Follow **`superpowers-writing-plans`** to translate the current subtask (its acceptance checks, OpenSpec `design.md`, and OpenWiki domain/architecture/caveat context) into a Ponytail-vetted TDD micro-plan. Stay within the subtask's scope; do not pre-implement later subtasks.

## Step 3: TDD Implementation (per Subtask)
Follow **`superpowers-test-driven-development`** to implement the micro-plan via strict Red -> Green -> Refactor loops.
- **Strict Sandbox Rule:** Never create or modify `openspec/` or `.beads/` inside the worktree.
- **Repository Containment Rule:** Never leave the repository boundary (unless particularly requested by the user); always use `.tmp/` (contained in `.gitignore`) as the parent directory when creating temporary directories or files.

## Step 4: Two-Stage Self/Subagent Review Gate (per Subtask)

Before committing each subtask, read any base-branch `REVIEW.md` rubrics (from `HEAD` or `main` if present in the repo, e.g., `git show HEAD:REVIEW.md` or `git show main:REVIEW.md`) so review standards cannot be weakened by the diff itself, then audit `git diff` against two gates:

### Stage A — Spec, Rubric & Acceptance Criteria Compliance
- Does the implementation satisfy every acceptance check of `<SUBTASK_ID>` and the relevant OpenSpec delta scenarios?
- Are all base-branch `REVIEW.md` rubrics (if present), OpenWiki caveats, and ADR constraints respected?
- Do changes to parsers, serializers, state machines, codecs, or migrations include at least one property/invariant test or differential check?

### Stage B — Ponytail & Safety Audit
- Walk the **Ponytail 7-Step Ladder**: Is there any unnecessary abstraction, unrequested feature, or avoidable dependency in the diff? If so, simplify it now.
- Are trust-boundary validations, error handling, and security checks present and tested without hiding flakiness behind `sleep`, arbitrary retries, or skipped assertions?
- Does all code and test execution stay strictly within the repository boundary (using `.tmp/` for any temporary directories rather than system `/tmp` or external paths)?

### Review Finding Triage & Repair Pass (Max 3 Rounds)
- Categorize every review finding with an explicit tag:
  - `[Important]` — correctness, safety, spec, `REVIEW.md`, or Ponytail defect introduced by the diff (blocks commit).
  - `[Nit]` — minor clarity, naming, or polish suggestion in touched code.
  - `[Pre-existing]` — issue predating this diff (do not expand subtask scope; record for follow-up unless it breaks safety).
- Carry all unresolved `[Important]` findings (and trivial `[Nit]` fixes) forward into **one focused repair/fix pass**, re-run the affected tests, and re-verify the diff.
- **Max-3 Rounds Circuit Breaker:** Repeat review + focused repair at most **3 rounds** total. If `[Important]` findings remain unresolved after 3 rounds, halt and escalate to `opsx-apply` / the user instead of looping or committing unverified code.

## Step 5: Safe Commit via `git-commit` Skill (per Subtask)
Activate the **[`git-commit`](../git-commit/SKILL.md)** skill inside the worktree:
- Run `git status --porcelain` and `git diff --unified=0`.
- Verify **no PII, secrets, or absolute paths** are present.
- Commit with an `[AI]` conventional commit message referencing `[<SUBTASK_ID>]`, and record the SHA for that subtask.
- Then return to **Step 2** for the next subtask in the queue. If a subtask turns out to be blocked or mis-scoped, stop, commit what is complete, and report it instead of silently expanding scope.

## Step 6: Finish Branch & Report to `opsx-apply`
Once all subtasks are committed, follow **`superpowers-finishing-a-development-branch`** to merge the verified worktree branch back into the target branch once, remove the worktree, and return the structured completion packet (with one commit SHA per subtask) to `opsx-apply`.

