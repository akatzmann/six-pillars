---
name: superpowers-writing-plans
description: >-
  Create an autonomous, Ponytail-vetted micro-implementation plan for a single Beads (bd)
  subtask (one entry of a topic's subtask queue) inside an isolated git worktree. Bypasses interactive brainstorming (already
  completed in OpenSpec) and maps out exact file paths, TDD test cases, and minimal code
  changes before execution.
license: Apache-2.0
author: akatzmann (https://github.com/akatzmann)
attribution: >-
  Re-architected by akatzmann (github.com/akatzmann) for Beads dispatch units, Ponytail decision gates, and isolated git worktrees. Originally created by Jesse Vincent (MIT).
version: "1.1.0"
---
# Superpowers: Autonomous Micro-Planning (`superpowers-writing-plans`)

> **Six-Pillar Agentic Engineering Suite**  
> Architected by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  
> *Adapted from Jesse Vincent's Superpowers (MIT) with Ponytail gates & Beads dispatch.*


Generates a concise, actionable **TDD Micro-Plan** for a **single Beads (`bd`) subtask** from the Execution Packet's subtask queue. Plan one subtask at a time, in queue order; never pre-implement later subtasks.

> **Why no interactive brainstorming here?** Macro requirements, architecture, and trade-offs were already aligned with the user during `opsx-explore` and `opsx-propose`. This skill operates autonomously on the scoped subtask, pausing to ask the user **only** if a genuine blocker or contradiction in the spec is discovered.

---

## Step 1: Analyze the Execution Packet & Trace Code

Inside the isolated worktree created by `superpowers-using-git-worktrees`:

1. **Read the Execution Packet:**
   - Goal, description, and acceptance checks for the current `<SUBTASK_ID>` (plus the unit's overall goal for context).
   - Relevant macro design sections from `openspec/changes/<name>/design.md` and `specs/`.
   - Relevant **OpenWiki (`openwiki/`)** domain knowledge, architecture docs, ADRs, and caveats.
2. **Trace the Existing Codebase:**
   - Read the exact source and test files that will be touched or called.
   - Identify existing helpers, error-handling conventions, and test fixtures.
   - **Repository Containment & `.tmp/` Rule:** Plan all paths strictly inside the repository/worktree (never leaving the repository boundary unless particularly requested by the user). If tests or verification steps require temporary directories or scratch files, plan them under `.tmp/` (contained in `.gitignore`) rather than OS `/tmp`.

---

## Step 2: Run the Ponytail 7-Step Decision Ladder (Mandatory Gate)

Before planning any new file, class, function, or dependency, evaluate the subtask against the **Ponytail Decision Ladder** (`AGENTS.md`):

1. **Rung 1 (YAGNI):** Can any part of this subtask be simplified without violating its acceptance checks?
2. **Rung 2 (Existing Codebase):** Which existing functions, types, or utilities in the repo can be reused directly?
3. **Rung 3 (Standard Library):** Can standard library primitives replace custom logic?
4. **Rung 4 (Native Platform):** Does the runtime/platform provide a built-in mechanism?
5. **Rung 5 (Installed Dependencies):** Can an already-installed package handle it? *(Never add a new package unless explicitly authorized by `design.md`).*
6. **Rung 6 (One-Liner):** Can the logic be expressed as a clear, direct expression instead of a new class/module?
7. **Rung 7 (Minimum Implementation):** Define the smallest possible code surface area that satisfies all acceptance criteria and safety requirements.

---

## Step 3: Formulate the Bite-Sized TDD Micro-Plan

Structure the micro-plan into sequential **Red -> Green -> Refactor** steps (2–5 minutes each). If the subtask clearly needs more than one TDD cycle / one coherent commit, it is mis-sized: plan only the part matching its acceptance checks and report the remainder as a follow-up subtask for `opsx-apply`.

Apply these mandatory planning rigor gates before finalizing the plan:
- **Property / Invariant & Differential Checks:** Whenever implementing or modifying **parsers, serializers, state machines, codecs, or migrations**, require at least one **property/invariant test** (e.g., round-trip `decode(encode(x)) == x`, idempotence, valid state transitions) or **differential check** against a trusted oracle.
- **No Flakiness Masking:** Explicitly forbid hiding timing or ordering flakiness behind `sleep` calls, arbitrary retry loops, or skipped/relaxed assertions. Plan deterministic synchronization, injected clocks/fixtures, and bounded explicit timeouts instead.
- **Max-3 Retry Circuit Breaker:** Plan and enforce a strict maximum of **3** auto-fix/retry attempts for any failing test or verification cycle; if unresolved after 3 attempts, halt and escalate the failure trace and diagnosis to `opsx-apply` / the user.

```markdown
## Micro-Plan for Subtask `<SUBTASK_ID>`: <Title>

### Ponytail Ladder Check
- **Selected Rung:** Rung <N> (<justification>)
- **Reused Code / Stdlib:** <existing files/functions reused>
- **Protected Safety Checks:** <trust-boundary validation, error handling, edge cases>
- **Invariant / Differential Check:** <required property/invariant or differential check if parser/serializer/state-machine/codec/migration; otherwise `N/A`>

### Files to Modify / Create
- Modify: `path/to/existing.ext`
- Test: `tests/path/to/test_existing.ext`

### TDD Steps
1. **RED:** Write failing test `<test_name>` in `tests/path/to/test_existing.ext` covering `<scenario>` (plus property/invariant or differential check when applicable; zero `sleep`/retry/skip flakiness masking).
2. **VERIFY RED:** Run `<test_command>` and confirm it fails for the expected reason.
3. **GREEN:** Implement minimal code in `path/to/existing.ext` (following Ponytail Rung <N>).
4. **VERIFY GREEN:** Run `<test_command>` and confirm all tests pass (circuit breaker: max 3 auto-fix/retry attempts before halting and escalating to the user).
5. **REFACTOR:** Clean up duplication while keeping tests green.
6. **COMMIT:** Invoke `git-commit` skill inside the worktree (one commit for this subtask, referencing `[<SUBTASK_ID>]`).
```

---

## Step 4: Hand Off to `superpowers-test-driven-development`

Immediately execute the micro-plan using **`superpowers-test-driven-development`**.

