---
name: openwiki
description: >-
  Manage, consult, and update OpenWiki (openwiki/ directory, openwiki/INSTRUCTIONS.md, and
  openwiki CLI) as the General Project Encyclopedia and Institutional Memory Single Source of
  Truth (SSOT) — covering EVERYTHING in the project with durable knowledge impact across all
  domains (domain knowledge, research, concepts, entities, events, ideas/theses, workflows,
  system architecture, decisions, caveats, and runbooks). Use whenever reading, querying, or
  running an update/sync on openwiki/ documentation (including /openwiki, /openwiki:update,
  /openwiki-update, or lifecycle handoffs from opsx-archive and opsx-bulk-archive).
license: Apache-2.0
compatibility: Works with openwiki CLI, .agents/skills/openwiki/scripts/wiki_scout.py, ripgrep (rg), OKF v0.2 markdown files, and OpenWiki Claims sidecars in openwiki/.
author: akatzmann (https://github.com/akatzmann)
attribution: >-
  Adapted and extended by akatzmann (github.com/akatzmann) for multi-archetype project encyclopedias and institutional memory. Inspired by OpenWiki (MIT).
version: "1.0.0"
---
# OpenWiki — General Project Encyclopedia & Institutional Memory SSOT (`openwiki`)

> **Six-Pillar Agentic Engineering Suite**  
> Extended by [@akatzmann](https://github.com/akatzmann) | Licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)  
> *Conceptual inspiration from OpenWiki (MIT).*


**OpenWiki** is the **general, encyclopedic wiki for the entire project**, covering **everything that has relevant, durable knowledge impact** without arbitrary restriction:

1. **Comprehensive Project Encyclopedia (Domain & Subject Knowledge):**
   - Synthesizes all domain concepts, research findings, events/conferences, sessions, people/speakers, organizations, datasets, experiments, critical analyses, and sparked product/venture theses in the repository.
   - Never treat `openwiki/` as "code-only" or restrict it to software plumbing; if a project contains notes, research, domain models, or strategic ideas, those are first-class encyclopedia subjects.
2. **Codebase Wiki & Institutional Engineering Memory (SSOT):**
   - Captures software & system architecture, module/component guides, data flows, **Architecture Decision Records (ADRs)**, **implementation caveats / gotchas**, and **operational runbooks** — everything durable outside transient OpenSpec changes (`openspec/`) and Beads task queues (`.beads/`).

---

## 1. Mandatory Quality Standard: The Multi-Archetype Quality Contract

Whenever authoring or updating `openwiki/` pages, enforce **lossless structural depth and primary-source fidelity**. Rather than forcing all pages into a narrow software template or collapsing into shallow bullet lists, apply the rigorous quality contract specific to the topic's **Domain Archetype**:

### Archetype A: System & Code Architecture (`caveats/` [A1], `architecture/` & `runbooks/` [A2], `adr/` [A3])
1. **Responsibility & Component Ownership:** Identify clear service, daemon, and module boundaries; state what the system owns, delegates, or rejects.
2. **Runtime & Build Entrypoints:** Document CLI commands, API routes, main loops, worker spawns, and configuration entrypoints.
3. **Mechanisms & Control/Data Flow:** Detail end-to-end data paths, asynchronous threading, event queues, and message reconciliation.
4. **State, Persistence & Lifecycle:** Document storage schemas (e.g. SQLite tables), state machines, retry policies, and cleanup triggers.
5. **Invariants, Gotchas & Failure Semantics:** Highlight non-obvious platform quirks, rate limits, error unmasking, and workarounds for external API quirks.
6. **Concrete Evidence & Tests:** Cite representative focused tests, test files, and verification scripts that validate system behaviors.
7. **Extension Seams & Operations:** Document operational commands, environment variables, configuration flags, and extension hooks.

### Archetype B: Domain Research & Conceptual Syntheses (`conference/`, `concepts/`, `research/`, `speakers-and-entities/`)
1. **Core Thesis & Conceptual Scope:** Define the fundamental assertion, scientific hypothesis, or session premise with philosophical precision.
2. **Primary-Source Grounding:** Ground every claim in primary repository materials (markdown notes, transcript files, datasets, literature). Never synthesize from memory.
3. **Strict Attribution Hygiene:** Unambiguously distinguish between:
   - **Speaker / Source Claims:** What a speaker, researcher, or primary document explicitly argues.
   - **Moderator / Counterpart Rebuttals:** Questions, critiques, or counter-positions raised during debates.
   - **Author Commentary & Critique:** Personal observations, field notes, or syntheses recorded by the repository author (`Personal opinion:`, `Commentary:`), attributed explicitly as author thoughts.
4. **Causal Mechanisms & Conceptual Evolution:** Explain the structural or theoretical dynamics of the argument rather than listing passive facts.
5. **Boundary Conditions, Gotchas & Caveats:** Call out counter-evidence, unaddressed assumptions, theoretical friction, and edge cases where claims break down.
6. **Zero Lossy Compression:** Preserve quantitative statistics, category breakdowns, verbatim exchanges, and concrete historical/empirical case studies.
7. **Unresolved Questions & Follow-Up Vectors:** Capture sparked theoretical seams, unanswered open questions, and research vectors.

### Archetype C: Strategic Analysis & Venture Theses (`analysis-and-ideas/`, `theses/`)
1. **Core Problem & Market Reality:** Articulate the underlying friction, structural inefficiency, or failure of existing alternatives that creates the opportunity.
2. **Value Hypothesis & Mechanism:** Explain the core insight, technical leverage, or innovative dynamic that resolves the problem.
3. **Operational Loops & Systems Model:** Outline the operational workflow, feedback loops, flywheels, or architectural mechanisms that power the thesis.
4. **Fatal Failure Modes & Boundary Risks:** Explicitly document potential points of failure (regulatory barriers, unit economics, data access, user adoption cliffs).
5. **Actionable Validation Milestones:** Detail concrete validation experiments, MVP specifications, and empirical test steps.

---

## 2. OpenWiki Charter (`openwiki/INSTRUCTIONS.md`), OKF v0.2 §5 Provenance & Claims Lifecycle

### Repository Charter (`openwiki/INSTRUCTIONS.md`)
- `openwiki/INSTRUCTIONS.md` is the persistent, project-owned charter (`wikiGoal`) that defines the wiki's encyclopedic scope.
- The `openwiki` CLI preserves `openwiki/INSTRUCTIONS.md` across `openwiki --init` runs and injects it on every `openwiki --init` and `openwiki --update` run.
- Always read and respect `openwiki/INSTRUCTIONS.md` before organizing or updating `openwiki/`.

### OKF v0.2 Frontmatter, Multi-Archetype §5 Provenance & Reserved Files
- **Reserved Files (`index.md`, `log.md`, `INSTRUCTIONS.md`):**
  - Root `openwiki/index.md` (`okf_version: "0.2"`) and subdirectory `index.md` files are **deterministically generated** by OpenWiki's `synchronizeWikiIndexes` pass (`# Files` and `# Directories`).
  - **Never place unique narrative prose inside `index.md`** — it will be overwritten by OpenWiki's index finalizer. Place all rich entry-point narrative, executive summaries, and topic routing in **`openwiki/quickstart.md`**.
- **Concept Page Frontmatter & Mandatory YAML Quoting:**
  - Every factual Markdown page under `openwiki/` (including `quickstart.md`) must begin with OKF v0.2 YAML frontmatter, with **double quotes (`"..."`) around `type`, `title`, and `description`** (an unquoted colon `:` inside a YAML scalar causes OpenWiki's strict parser to reject the frontmatter and replace it with `openwiki_generated: true` and `type: "Reference"`):
    ```yaml
    ---
    type: "<Concept | Conference Synthesis | Venture Thesis | Architecture | ADR | Caveat | Runbook>"
    title: "<Human-Readable Title — Always Double-Quoted>"
    description: "<One or two sentence summary optimized for search and retrieval — Always Double-Quoted>"
    tags:
      - "<tag-1>"
      - "<tag-2>"
    status: "stable"
    verified:
      by: "<actor>"
      at: "2026-11-14T15:00:00Z"
    ---
    ```
  - **Strict OKF v0.2 §5 Validator Warnings (`status` & UTC Timestamps):**
    - `status:` **MUST** be `"draft"`, `"stable"`, or `"deprecated"`. Upstream OpenWiki's `validateOkfFrontmatter` **rejects `"Accepted"`** in `status` (stripping invalid values during repair)!
    - `verified.at` and `stale_after` **MUST** be full ISO-8601 datetimes with an explicit UTC offset (`Z` or `±HH:MM`, e.g. `"2026-11-14T15:00:00Z"`). Bare `"YYYY-MM-DD"` dates are **rejected** by OKF v0.2 §5!
- **Archetype-Specific OKF v0.2 §5 Provenance Schema:**
  - **Archetype A1 (`openwiki/caveats/`):** Deterministic & temporal provenance — OKF v0.2 `status`, `verified: {by, at}`, `stale_after` (UTC ISO-8601 `Z`), `sources: [{resource: "<repo-path>"}]`, and `applies_to: "<component/version>"` (**NO** probabilistic `epistemic:` block; rely on automated tests and git-mtime / `stale_after` checks).
  - **Archetype A2 (`openwiki/architecture/`, `openwiki/runbooks/`, `openwiki/quickstart.md`):** Deterministic dated provenance **ONLY** — OKF v0.2 `status: "stable"`, `verified: {by, at}`, and `sources: [{resource: "<repo-path>"}]` (**NO** artificial probabilistic `p` or `epistemic:` block).
  - **Archetype A3 (`openwiki/adr/`):** Normative lifecycle **ONLY** — OKF v0.2 `status: "draft" | "stable" | "deprecated"`, `verified: {by, at}`, and optional `superseded_by: "ADR-NNNN"` when `status: "deprecated"` (**NO** artificial probabilistic `p` or `epistemic:` block).
  - **Archetype B (Domain Research & Concepts):** OKF v0.2 `status`, `verified: {by, at}`, `sources: [{resource: "<path-or-uri>"}]`, claim-level attribution/corroboration in body, plus **optional** `epistemic: {p, obs, exceptions}` when tracking uncertain/empirical hypotheses.
  - **Archetype C (Strategic Ideas & Venture Theses):** OKF v0.2 `status`, `verified: {by, at}`, `stale_after` (UTC ISO-8601 `Z` review horizon), plus **optional** `epistemic: {p, obs, exceptions}` prior $\rightarrow$ posterior tracking on falsifiable strategic bets.
  - **Zero `openwiki_generated: true` Fallback Policy:** Always verify `rg -n "openwiki_generated" openwiki/` returns zero matches.
  - **POSIX EOF Newline Invariant:** Every Markdown file in `openwiki/` (including ADRs, architecture docs, caveats, quickstart, and indexes) MUST end with a single trailing newline (`\n`). Creating files without a trailing newline causes IDE auto-formatters (e.g. `files.insertFinalNewline`) to modify files post-commit, resulting in dirty working trees.
- **Graph Cross-Linking (`openwiki visualize` & `wiki_scout.py`):**
  - Link extensively between wiki pages using relative `.md` paths (e.g., `[Related Topic](../domain/topic.md)`) so `openwiki visualize` and `python3 .agents/skills/openwiki/scripts/wiki_scout.py neighbors` construct a richly connected knowledge graph with zero broken internal links.

### Claims Engine & Deterministic Lifecycle (`openwiki/.claims/`, `.page-manifest.json`, `.last-update.json`)
- OpenWiki (`v0.7.x`) tracks grounded propositions in `openwiki/.claims/*.json` and stamps `verified:`, `sources:`, and `generated:` into concept page frontmatter during its repository lifecycle (`beginRepositoryRun` -> `submitRepositoryPlan` -> `nextRepositoryPage` -> `submitRepositoryPage` -> `finishRepositoryRun`, exposed as `openwiki_*` lifecycle tools or `openwiki --init` / `openwiki --update`).
- When updating pages in `openwiki/`, ensure `openwiki/.claims/`, `openwiki/.page-manifest.json`, and `openwiki/.last-update.json` remain synchronized and `"status": "complete"` when present.
- **`AGENTS.md` Code-Mode Snippet Guard:** `openwiki --init` / `openwiki --update` (`ensureCodeModeRepoSetup`) automatically appends a generic `<!-- OPENWIKI:START --> ... <!-- OPENWIKI:END -->` block to `AGENTS.md` (and creates `.github/workflows/openwiki-update.yml` on `init`). Because `AGENTS.md` already defines the authoritative Six-Pillar **OpenWiki First & Last** constitution, strip or `git checkout -- AGENTS.md` the generic `<!-- OPENWIKI:START -->` block after CLI runs so `AGENTS.md` remains clean and unambiguous.
- **Standard CLI Commands:**
  ```bash
  openwiki --init
  openwiki --update "<summary of new/updated project knowledge, domain pages, architecture, ADRs, or caveats>"
  openwiki visualize openwiki --no-open
  openwiki visualize openwiki --export docs/openwiki-visualizer
  ```

---

## 3. Adaptive Encyclopedia Taxonomy (`openwiki/` Structure)

Do **not** force every repository into a fixed software-only folder checklist. Organize `openwiki/` dynamically around the **actual knowledge domains of the project**, giving domain/subject knowledge first-class directories alongside institutional engineering memory:

```text
openwiki/
├── INSTRUCTIONS.md             # Persistent project encyclopedia brief (preserved across --init)
├── index.md                    # Deterministic OKF v0.2 root index (# Files & # Directories)
├── quickstart.md               # Rich narrative entry point, executive summary & topic router (Archetype A2)
├── <domain-section-1>/         # e.g., concepts/, conference/, research/, domain-models/ (Archetype B)
├── <domain-section-2>/         # e.g., speakers-and-entities/, datasets/, experiments/ (Archetype B)
├── <domain-section-3>/         # e.g., analysis-and-ideas/, theses/, workflows/ (Archetype C)
├── architecture/               # System & codebase architecture, components, data flows (Archetype A2)
├── adr/                        # Architecture Decision Records — ADR-NNNN-<slug>.md (Archetype A3)
├── caveats/                    # Non-obvious implementation caveats, gotchas, & invariants (Archetype A1)
└── runbooks/                   # Operational procedures, verification commands, & setup guides (Archetype A2)
```

---

## 4. Operational Protocols: Read Mode vs. Update Mode

OpenWiki provides two standardized operational protocols to serve both ad-hoc queries and structured lifecycle updates.

### Mode A: Read / Consult Protocol (`/openwiki <query>` — System-1 Radar $\rightarrow$ System-2 Full-Page Reading)
Use a two-phase **non-destructive radar orientation followed by lossless full-page reading** whenever exploring questions, grounding proposed changes, or retrieving architectural and domain knowledge without modifying documentation:
1. **System-1 Radar Orientation (Fast Discovery, Staleness & Graph Triage):**
   - Run `python3 .agents/skills/openwiki/scripts/wiki_scout.py` (with `openwiki/quickstart.md` and `<section>/index.md`) before falling back to `rg` (`ripgrep`, reserved inside `openwiki/` strictly for regex, punctuation, or exact-literal patterns) to locate high-signal pages, check temporal/source freshness, and inspect 1-hop links without dumping the entire wiki:
     ```bash
     python3 .agents/skills/openwiki/scripts/wiki_scout.py overview --root openwiki [--section caveats] [--stale-only]
     python3 .agents/skills/openwiki/scripts/wiki_scout.py search "<natural-language or keyword query>" [--section architecture]
     python3 .agents/skills/openwiki/scripts/wiki_scout.py neighbors openwiki/caveats/<slug>.md
     # Fallback only (regex, punctuation, or exact-literal patterns inside openwiki/):
     rg -n "<regex_or_exact_literal>" openwiki/
     ```
2. **System-2 Lossless Full-Page Reading:**
   - Once the System-1 radar identifies relevant pages, **read the target Markdown pages in full** (never rely solely on BM25 snippets or frontmatter summaries for design, debugging, or research synthesis).
   - Follow 1-hop relative links (`[Link](../path/page.md)`) and `wiki_scout.py neighbors` backlinks across section boundaries; if `wiki_scout.py` flags a page as `[STALE]` (e.g. a cited `sources:` file changed after `verified.at` or `stale_after` expired), verify the underlying repository source files directly.
3. **Context Grounding:** Cite the retrieved knowledge, ADRs, or caveats in design discussions or execution packets. Never modify files during Mode A.

### Mode B: Write / Update Protocol (`/openwiki:update`, `/openwiki-update`, or Lifecycle Handoff)
Use whenever syncing new project knowledge, updating system architecture, or responding to lifecycle handoffs from `opsx-archive` / `opsx-bulk-archive`:
1. **Step 1: Source Discovery & Scope Audit**
   - For ad-hoc `/openwiki:update`: Inspect modified repository files, notes, datasets, git logs (`git status`, `git log -n 5 --stat`), and `python3 .agents/skills/openwiki/scripts/wiki_scout.py overview --root openwiki --stale-only` to catch pages whose `sources:` drifted.
   - For lifecycle handoff (`opsx-archive` / `opsx-bulk-archive`): Receive the completed change context, delta specs, design rationale, and any discovered ADRs/caveats from the archiving skill.
2. **Step 2: Multi-Archetype Content & Provenance Synthesis**
   - Apply the rigorous **Multi-Archetype Quality Contract** (Section 1) and **Archetype-Specific OKF v0.2 §5 Provenance Schema** (Section 2):
     - *Caveats (`caveats/`, Archetype A1):* Include `status`, `verified: {by, at}`, `stale_after`, `sources`, and `applies_to` (no `epistemic:`).
     - *Architecture, Runbooks & Quickstart (Archetype A2):* Include deterministic `status: "stable"`, `verified: {by, at}`, and `sources` (no `epistemic:`).
     - *ADRs (`adr/`, Archetype A3):* Include normative `status: "draft" | "stable" | "deprecated"`, `verified: {by, at}`, and optional `superseded_by` when `deprecated` (no `epistemic:`).
     - *Research/Domain Notes (Archetype B):* Include `status`, `verified: {by, at}`, `sources`, plus optional `epistemic: {p, obs, exceptions}` when tracking empirical/uncertain claims.
     - *Venture/Product Theses (Archetype C):* Include `status`, `verified: {by, at}`, `stale_after`, plus optional `epistemic: {p, obs, exceptions}` for falsifiable strategic bets.
   - Ensure all concept pages use double-quoted scalars (`type`, `title`, `description`) and explicit UTC ISO-8601 `Z` timestamps.
3. **Step 3: Capture Institutional Engineering Memory**
   - Record significant architectural or dependency decisions under `openwiki/adr/ADR-NNNN-<slug>.md`.
   - Record non-obvious gotchas, platform quirks, or invariants under `openwiki/caveats/<slug>.md`.
   - Update existing system architecture overviews under `openwiki/architecture/<system>.md` and operational guides under `openwiki/runbooks/<slug>.md`, refreshing `verified.at` after verifying against `sources`.
4. **Step 4: Index & Quickstart Router Synchronization**
   - Update `openwiki/quickstart.md` narrative router and section links to integrate new pages.
   - Update directory `index.md` files in affected subdirectories to list new files.
   - If `.last-update.json` exists, update timestamp and status to `"complete"`.
5. **Step 5: Integrity Verification**
   - Run verification checks:
     ```bash
     rg -n "openwiki_generated" openwiki/                                                          # Must return 0 matches
     python3 .agents/skills/openwiki/scripts/wiki_scout.py overview --root openwiki --stale-only   # Verify 0 unexpected stale pages
     ```
   - Verify zero broken relative `.md` links and POSIX trailing newlines (`\n`) across all updated pages.

---

## 5. When & How Other Workflow Skills Interact with OpenWiki

### During `opsx-explore` & `opsx-propose` (Read Mode A)
1. Orient with `python3 .agents/skills/openwiki/scripts/wiki_scout.py search "<topic>"`, `openwiki/quickstart.md`, and `openwiki/index.md`, then read relevant domain, concept, research, architecture, `adr/`, and `caveats/` pages in full **before** scanning raw files from scratch.
2. Check whether any existing domain knowledge, ADR, or documented caveat informs or constrains the proposed change.
3. Reference applicable OpenWiki pages directly inside `openspec/changes/<name>/design.md` so downstream subagents receive them.

### During `superpowers-writing-plans` & `superpowers-test-driven-development` (Read + Note Mode)
1. Read the OpenWiki domain context, architecture notes, and caveats passed in the **Execution Packet** (using `python3 .agents/skills/openwiki/scripts/wiki_scout.py neighbors <page>` when tracing adjacent components).
2. If work inside the worktree uncovers new domain insights, tricky edge cases, platform quirks, or architectural invariants, include them in the subagent's completion report under **`Discovered OpenWiki Knowledge / Caveats / ADRs`**.

### During `opsx-verify` (Integrity Audit)
1. Audit `openwiki/` against primary repository sources (assisted by `rg -n "openwiki_generated" openwiki/` and `python3 .agents/skills/openwiki/scripts/wiki_scout.py overview --root openwiki`) to verify zero speaker/author attribution inversions, zero omitted domain topics, zero broken internal links, and zero `openwiki_generated: true` fallback frontmatter flags.

### During `opsx-archive` & `opsx-bulk-archive` (Lifecycle Handoff to Update Mode B)
1. The archiving skill invokes the `openwiki` skill in **Mode B (Update Protocol)**, handing over the completed change context, design decisions, and newly discovered ADRs/caveats.
2. `openwiki` performs the synchronized update across project knowledge, system models, `quickstart.md`, and directory indices.
