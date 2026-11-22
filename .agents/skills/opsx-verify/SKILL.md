---
name: opsx-verify
description: >-
  Verify that an implemented OpenSpec change satisfies all delta specs, design decisions,
  Beads (bd) topic and subtask completion, Ponytail minimalism principles, and OpenWiki documentation
  requirements before archiving. Use when the user invokes /opsx:verify, opsx-verify, or
  wants to validate an implementation.
license: Apache-2.0
compatibility: Requires openspec and bd (Beads) CLIs.
author: akatzmann (https://github.com/akatzmann)
attribution: >-
  Adapted and extended by akatzmann (github.com/akatzmann) for Beads issue hierarchies, Superpowers worktrees, and Ponytail gates. Inspired by OpenSpec (MIT).
version: "1.1.0"
---
# OpenSpec Verify (`opsx-verify`)

> **Six-Pillar Agentic Engineering Suite**  
> Architected by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  
> *Derived from OpenSpec (MIT) with Beads dispatch & Ponytail decision gates.*


Validates an implemented OpenSpec change across **four dimensions**:
1. **Completeness** (Beads `bd` graph & OpenSpec requirements)
2. **Correctness** (Scenario & test coverage)
3. **Coherence & Ponytail Audit** (Design adherence, OpenWiki domain/ADR compliance, and zero code bloat)
4. **OpenWiki Readiness** (Identifying new domain knowledge, concepts, syntheses, caveats, ADRs, or architecture docs to sync on archive)

---

## Step 1: Load Change, Beads Graph, and OpenWiki Context

1. **Select Change:** Use the provided change name or prompt via `openspec list --json`.
2. **Load OpenSpec Status & Artifacts:**
   ```bash
   openspec status --change "<name>" --json
   openspec instructions apply --change "<name>" --json
   ```
   Read `proposal.md`, `design.md`, `specs/`, and `tasks.md`.
3. **Inspect Beads (`bd`) State:**
   Locate `<EPIC_ID>` from `tasks.md` (or `bd list --external-ref "openspec:<name>"`) and run:
   ```bash
   bd children "<EPIC_ID>" --json
   ```
4. **Check Git Worktrees:**
   Run `git worktree list` to verify no orphaned Superpowers worktrees remain unmerged.

---

## Step 2: Run the Four Verification Checks

### 1. Completeness (Beads + Specs)
- **Beads Topics & Subtasks:** Verify every descendant Bead under `<EPIC_ID>` (topics *and* their subtasks, as shown in the `bd children` tree) has status `closed`. Flag any `open`, `in_progress`, or `blocked` Bead as **CRITICAL**. A topic left open while all of its subtasks are closed is a **WARNING** (close it; Beads does not auto-close parents).
- **Manifest Sync:** Verify `openspec/changes/<name>/tasks.md` checkboxes match the leaf-Bead state and every `## N.` topic heading references its topic Bead.
- **Decomposition Audit (WARNING):** Flag subtasks that violate the `opsx-propose` sizing rules (fail the "and" test, bundle several independent items, or span multiple commits/topics) so future proposals improve.
- **Requirement Coverage:** Verify every `### Requirement:` in `openspec/changes/<name>/specs/*/spec.md` has corresponding implementation in the codebase.

### 2. Correctness (Scenarios & Tests)
- For every `#### Scenario:` in the delta specs, verify that code handles the condition and automated tests cover it.
- Run the relevant unit/module test suite to confirm all tests pass.
- **E2E Verification Gate (Repo-Local `verify` Skill/Workflow):** Check if a repo-local `verify` skill or workflow exists in the workspace (e.g., `.agents/skills/verify/SKILL.md`, `.agents/workflows/verify*`, or project-local verify target); when present, run it as an end-to-end verification gate before passing Correctness (flag failures as **CRITICAL**).
- **Invariant & Anti-Flakiness Check:** Confirm that changes to parsers, serializers, state machines, codecs, or migrations include at least one property/invariant test or differential check, and verify tests do not mask flakiness with `sleep`, arbitrary retries, or skipped assertions.

### 3. Coherence & Ponytail Audit
- **Diff-Triggered `REVIEW.md` & Caveats Audit:** Inspect the implementation diff against the base branch (`git diff <base>...HEAD`, or the change's commits) to determine all touched modules and subsystems:
  - **`REVIEW.md` Rubrics:** If `REVIEW.md` exists in the repository (preferring base-branch `HEAD`/`main` rubrics), audit the diff against every applicable rule.
  - **OpenWiki Caveats (`openwiki/caveats/`):** Consult `openwiki/caveats/index.md` and relevant caveat notes under `openwiki/caveats/` for the touched subsystems to confirm known invariants and gotchas (e.g., auth boundaries, schema invariants, subprocess timeouts, resource cleanup) are preserved.
- **Design & OpenWiki ADR Adherence:** Verify the implementation follows `design.md` and respects existing ADRs in `openwiki/`.
- **Ponytail 7-Step Ladder Audit:** Inspect the implementation diff against the Ponytail rules (`AGENTS.md`):
  - Were any unnecessary dependencies added (Rung 5 violation)?
  - Were speculative abstractions or dead helpers introduced (Rung 1/2/6 violation)?
  - Are trust-boundary validations, error handling, and security checks intact (Protected Non-Negotiables)?

### 4. OpenWiki Encyclopedic Completeness & Primary-Source Fidelity Check
- Check Epic notes (`bd show "<EPIC_ID>"`), primary repository sources (notes, data, research, code), and implementation diffs to verify what is in — or must be written to — **OpenWiki (`openwiki/`)**:
  - **Primary-Source Fidelity:** Are all domain concepts, research notes, events, entities, quantitative metrics, and ideas/theses accurately synthesized without speaker/author attribution inversions or lossy omissions?
  - **OKF v0.2 & Claims Integrity:** Do all concept pages have double-quoted YAML frontmatter (`type`, `title`, `description`, `tags`), zero `openwiki_generated: true` fallback flags (`grep -rn "openwiki_generated" openwiki/`), and zero broken relative `.md` links?
  - **System & Institutional Memory (When Applicable):** Are new or updated architecture pages, decisions (ADRs), caveats/gotchas, or runbooks identified for sync during `opsx-archive` / `opsx-bulk-archive`? (Non-code projects should verify relevant domain sections instead.)

---

## Step 3: Output the Verification Scorecard

```markdown
## Verification Report: <change-name> (Epic: <EPIC_ID>)

| Dimension | Status | Summary |
| :--- | :--- | :--- |
| **Completeness (Beads & Specs)** | PASS / FAIL | X/Y topics and A/B subtasks closed, N/N requirements implemented |
| **Correctness (Tests & Scenarios)** | PASS / FAIL | M/N scenarios tested, test suite & repo-local verify gate green |
| **Coherence & Ponytail Audit** | PASS / WARN | Design, REVIEW.md, openwiki/caveats/, and Ponytail ladder respected |
| **OpenWiki Sync Items** | READY | <List ADRs, caveats, or module docs to update on archive> |

### Issues by Priority
- **CRITICAL** (Must fix before archive): ...
- **WARNING** (Should fix): ...
- **SUGGESTION** (Nice to fix): ...
```

If CRITICAL issues exist, offer to create/reopen the necessary **Beads (`bd`)** issues and re-run `opsx-apply`. Otherwise, prompt the user to proceed with **`opsx-archive`** (or **`opsx-bulk-archive`** if archiving multiple completed changes).
