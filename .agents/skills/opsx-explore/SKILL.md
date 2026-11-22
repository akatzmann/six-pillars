---
name: opsx-explore
description: >-
  Enter OpenSpec explore mode — a read-only thinking partner for investigating problems,
  consulting OpenWiki (project encyclopedia, domain knowledge, architecture, ADRs, caveats),
  mapping the codebase, and evaluating options through the Ponytail Decision Ladder before
  creating a proposal. Use when the user invokes /opsx:explore, opsx-explore, or wants to
  think through an idea or problem before proposing a change.
license: Apache-2.0
compatibility: Requires openspec and openwiki CLIs.
author: akatzmann (https://github.com/akatzmann)
attribution: >-
  Adapted and extended by akatzmann (github.com/akatzmann) for Beads issue hierarchies, Superpowers worktrees, and Ponytail gates. Inspired by OpenSpec (MIT).
version: "1.0.0"
---
# OpenSpec Explore (`opsx-explore`)

> **Six-Pillar Agentic Engineering Suite**  
> Architected by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  
> *Derived from OpenSpec (MIT) with Beads dispatch & Ponytail decision gates.*


Enter **explore mode** — a read-only thinking partner that grounds discussions in **OpenWiki**, **OpenSpec**, and the **existing codebase**, while filtering ideas through the **Ponytail Decision Ladder**.

> **CRITICAL GUARDRAIL (The Agreement-Trap Invariant):** Explore mode is strictly for thinking, reading, and visualizing — **never** for writing application code or modifying `.beads/`. Even when the user indicates agreement (*"Agreed"*, *"Sounds good"*, *"Proceed"*, *"Go ahead"*, or asks to build it), you MUST NOT write or modify application code. You MUST stop and prompt: *"Now that we agree on the approach, shall we run `/opsx-propose` to formalize the OpenSpec change and Beads hierarchy before implementing?"* You may only create or update OpenSpec artifacts if the user explicitly asks to capture an insight.

---

## Step 1: Ground Context in OpenWiki, OpenSpec, and Beads

Before theorizing, ground yourself in the repository's institutional memory and active state:

1. **Read OpenWiki (`openwiki/`) First:**
   - Check if `openwiki/` exists in the repository (or use the `openwiki` skill).
   - Read relevant encyclopedia pages: `quickstart.md` / `index.md`, domain & research knowledge, concepts, architecture overviews, **ADRs** (`openwiki/adr/`), and **known caveats/gotchas** (`openwiki/caveats/`).
2. **Check Active OpenSpec Changes:**
   ```bash
   openspec list --json
   ```
   If the user is exploring an existing change, read its `proposal.md`, `design.md`, `specs/`, and `tasks.md`.
3. **Check Active Beads State (Read-Only):**
   If `.beads/` exists and relates to the exploration topic, run:
   ```bash
   bd status
   ```

---

## Step 2: Apply the Ponytail Decision Ladder to Every Idea

When investigating a problem or comparing options, explicitly evaluate candidates against Rungs 1–5 of the **Ponytail Decision Ladder** (from `AGENTS.md`) before recommending any new code or architecture:

1. **Rung 1 (YAGNI):** Does this feature, service, or abstraction need to exist at all?
2. **Rung 2 (Existing Codebase):** Search the codebase thoroughly — does an existing module, helper, or pattern already solve 80–100% of this?
3. **Rung 3 (Standard Library):** Can the language's standard library handle it directly?
4. **Rung 4 (Native Platform):** Does the runtime, OS, database, or browser provide this natively?
5. **Rung 5 (Installed Dependencies):** Does an already-installed package in the manifest cover this without adding new dependencies?

---

## Step 3: Explore, Visualize, and Challenge Assumptions

- **Curious, not prescriptive:** Surface trade-offs and open threads rather than forcing a rigid questionnaire.
- **Visualize liberally:** Use clear ASCII architecture diagrams, state machines, data-flow sketches, and comparison tables.
- **Highlight OpenWiki Knowledge, Caveats & ADR Constraints:** Explicitly call out when an idea aligns with or contradicts existing domain knowledge, an ADR, or a documented caveat in `openwiki/`.

---

## Step 4: Transitioning Out of Explore Mode

When the problem and approach crystallize, summarize:
- **The Problem:** Crystallized understanding grounded in the repository and domain context.
- **The Minimal Approach (Ponytail-vetted):** Which rung of the Ponytail Ladder resolves the problem with minimum complexity.
- **OpenWiki Impact:** Which encyclopedia domain pages, ADRs, caveats, or architecture pages will be added or updated.
- **Next Step:** Offer to transition into **`opsx-propose`** to scaffold the OpenSpec change and decompose work into **Beads (`bd`)**. Under no circumstances begin implementing code directly in explore mode.

