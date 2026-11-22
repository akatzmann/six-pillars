---
name: superpowers-test-driven-development
description: >-
  Execute strict Red-Green-Refactor Test-Driven Development (TDD) inside an isolated git
  worktree for each Beads subtask of a dispatched unit, enforcing Ponytail minimalism in the Green/Refactor steps
  and committing via the git-commit skill.
license: Apache-2.0
author: akatzmann (https://github.com/akatzmann)
attribution: >-
  Re-architected by akatzmann (github.com/akatzmann) for Beads dispatch units, Ponytail decision gates, and isolated git worktrees. Originally created by Jesse Vincent (MIT).
version: "1.1.0"
---
# Superpowers: Test-Driven Development (`superpowers-test-driven-development`)

> **Six-Pillar Agentic Engineering Suite**  
> Architected by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  
> *Adapted from Jesse Vincent's Superpowers (MIT) with Ponytail gates & Beads dispatch.*


Executes the micro-plan produced by `superpowers-writing-plans` using strict **Red -> Green -> Refactor** discipline paired with the **Ponytail Decision Ladder**.

> **The Iron Law of TDD:** Write the failing test first. Watch it fail. Write the minimal code (Ponytail Rung 1–7) to make it pass. Never write production behavior before its failing test exists.

---

## The Red-Green-Refactor-Commit Loop

For each step in the current subtask's micro-plan:

### 1. RED — Write One Focused Failing Test
- Target the test file **inside `<WORKTREE_PATH>/...`**.
- Write a clear test demonstrating the required behavior or scenario from the subtask's acceptance checks / OpenSpec delta spec.
- **Parsers, Serializers, State Machines, Codecs & Migrations:** Whenever implementing or modifying any of these, require at least one **property/invariant test** (e.g., round-trip `decode(encode(x)) == x`, transition invariants, idempotence) or **differential check** against a reference oracle.
- Test real behavior and trust-boundary edge cases — avoid tautological mock-only tests.
- **No Flakiness Masking:** Never hide test flakiness behind `sleep`, arbitrary retries, or skipped/weakened assertions (`skip`, relaxed asserts). Use deterministic synchronization, injected clocks/fixtures, and explicit bounded timeouts.
- If the test requires temporary directories or files, use `.tmp/` inside the worktree (`<WORKTREE_PATH>/.tmp/`, ignored by `.gitignore`) as the parent directory — never leave the repository boundary (e.g., `/tmp` or `..`) unless particularly requested by the user.

### 2. VERIFY RED — Watch It Fail
- Run the targeted test command inside the worktree (`cd "<WORKTREE_PATH>" && <test_command>`).
- Confirm the test **fails** (not errors due to syntax/imports) because the feature/fix is not yet implemented.

### 3. GREEN — Write the Minimum Implementation (Ponytail Enforced)
- Target the source file **inside `<WORKTREE_PATH>/...`**.
- Write the **minimum amount of code** required to pass the failing test:
  - Reuse existing helpers (Rung 2), stdlib (Rung 3), native features (Rung 4), or installed packages (Rung 5).
  - Prefer a clear one-liner (Rung 6) over ceremony.
  - **Never** skip trust-boundary validation, error handling, or security checks (Ponytail Protected Non-Negotiables).
  - **Never** touch `openspec/` or `.beads/` inside the worktree.
  - **Never** leave the repository boundary (unless particularly requested by the user); use `.tmp/` as the parent directory whenever temporary directories or files are needed.

### 4. VERIFY GREEN — Watch It Pass
- Run `cd "<WORKTREE_PATH>" && <test_command>` and confirm the new test passes.
- Run the broader module test suite inside `<WORKTREE_PATH>` to confirm zero regressions.
- **Max-3 Auto-Fix / Retry Circuit Breaker:** If fixing a failing test or regression fails to turn green after **3 consecutive auto-fix/retry attempts**, **halt immediately** and escalate to `opsx-apply` / the user with the failing output and attempted fixes. Never loop indefinitely or mask failures behind `sleep`, arbitrary retries, or skipped assertions.

### 5. REFACTOR — Simplify Without Breaking
- Remove duplication, dead code, or unnecessary intermediate variables.
- Re-run tests inside `<WORKTREE_PATH>` to confirm everything remains green.

### 6. COMMIT — Persist via `git-commit` Skill (Patched Gate)
- **Do NOT run raw `git commit -m "..."`.**
- When the subtask is complete (at minimum one commit per subtask), invoke the **[`git-commit`](../git-commit/SKILL.md)** skill targeting `workdir: "<WORKTREE_PATH>"`:
  - Inspects `git -C "<WORKTREE_PATH>" status --porcelain` and `git -C "<WORKTREE_PATH>" diff --unified=0`.
  - Verifies **zero PII, secrets, or hardcoded absolute paths** exist in the diff.
  - Clusters changes and creates a structured `[AI]` commit message referencing `<SUBTASK_ID>`.

