# OpenWiki Repository Brief & Encyclopedia Charter (`INSTRUCTIONS.md`)

`openwiki/` is the **General Project Encyclopedia and Institutional Memory Single Source of Truth (SSOT)** for this repository.

## 1. Comprehensive Encyclopedic Scope

Unlike narrow code-only documentation, this OpenWiki must cover **EVERYTHING in the project that has relevant, durable knowledge impact** — functioning as a comprehensive encyclopedia for both humans and AI agents:

- **Domain Knowledge, Research & Subject Matter:** Core concepts, theories, scientific or domain findings, literature, events, conferences, sessions, people/speakers, organizations, datasets, experiments, and primary-source syntheses.
- **Ideas, Theses & Strategic Analysis:** Research hypotheses, critical analyses, personal observations, product/venture theses, and strategic insights developed in the project.
- **System & Codebase Knowledge:** Software architecture, data flows, components/modules, APIs, workflows, and verification/testing suites (when code exists in the repository).
- **Institutional Engineering Memory:** Architecture Decision Records (ADRs), non-obvious implementation caveats/invariants, and operational runbooks.

Never implicitly exclude non-code knowledge or force domain topics into software-only categories.

## 2. Adaptive Taxonomy & Organization

Organize `openwiki/` dynamically around the **actual knowledge domains of the project** rather than a fixed checklist of folders:
- Create domain-appropriate directories as needed (e.g., `concepts/`, `research/`, `conference/`, `speakers/`, `theses/`, `domain/`, `workflows/`, `architecture/`, `adr/`, `caveats/`, `runbooks/`).
- Include `openwiki/quickstart.md` as the high-level encyclopedia overview and topic router.
- Maintain `index.md` files (with `okf_version: "0.2"` at the root) so every directory and concept page is discoverable.

## 3. Page Format (OKF v0.2 §5), Multi-Archetype Provenance & Graph Linking

1. **OKF v0.2 Base Frontmatter & Strict Validator Invariants:** Every factual Markdown page (except reserved `index.md`, `log.md`, and `INSTRUCTIONS.md`) must begin with OKF v0.2 YAML frontmatter with **double-quoted** `type`, `title`, and `description` scalars:
   ```yaml
   ---
   type: "<Concept | Session Synthesis | Venture Thesis | Architecture | ADR | Caveat | Runbook>"
   title: "<Human-Readable Display Title — Always Double-Quoted>"
   description: "<One or two sentence summary optimized for search and retrieval — Always Double-Quoted>"
   tags:
     - "<tag1>"
     - "<tag2>"
   status: "stable"
   verified:
     by: "<actor>"
     at: "2026-11-14T15:00:00Z"
   ---
   ```
   > **Strict OKF v0.2 §5 Validator Warning:** Upstream OpenWiki's `validateOkfFrontmatter` strictly restricts `status:` to `"draft" | "stable" | "deprecated"` (it rejects `"Accepted"`, stripping invalid values during normalization!) and requires `verified.at` and `stale_after` to be full ISO-8601 timestamps with an explicit UTC offset such as trailing `Z` or `±HH:MM` (bare `"YYYY-MM-DD"` dates are rejected!).
2. **Multi-Archetype OKF v0.2 §5 Provenance Schema:** Apply provenance metadata matched to the epistemic nature of each archetype (do **not** attach artificial probabilistic `p` scores to code/system docs):
   - **Archetype A1 (`openwiki/caveats/`):** Deterministic & temporal provenance — OKF v0.2 `status`, `verified: {by, at}`, `stale_after` (UTC ISO-8601 `Z`), `sources: [{resource: "<repo-path>"}]`, and `applies_to: "<component/version>"` (no probabilistic `epistemic:` block; rely on tests and `sources`/`stale_after` checks).
   - **Archetype A2 (`openwiki/architecture/`, `openwiki/runbooks/`, `openwiki/quickstart.md`):** Deterministic dated provenance — OKF v0.2 `status: "stable"`, `verified: {by, at}`, and `sources: [{resource: "<repo-path>"}]` (no `epistemic:` block).
   - **Archetype A3 (`openwiki/adr/`):** Normative lifecycle — OKF v0.2 `status: "draft" | "stable" | "deprecated"`, `verified: {by, at}`, and optional `superseded_by: "ADR-NNNN"` when `status: "deprecated"` (no `epistemic:` block).
   - **Archetype B (Domain Research & Concepts):** OKF v0.2 `status`, `verified: {by, at}`, `sources: [{resource: "<path-or-uri>"}]`, claim-level attribution/corroboration in the body, and **optional** `epistemic: {p, obs, exceptions}` when tracking empirical/uncertain claims.
   - **Archetype C (Strategic Ideas & Venture Theses):** OKF v0.2 `status`, `verified: {by, at}`, `stale_after` (UTC ISO-8601 `Z` review horizon), and **optional** `epistemic: {p, obs, exceptions}` for falsifiable strategic hypotheses.
3. **Dense Cross-Linking for `openwiki visualize` & `wiki_scout.py`:** Use relative Markdown links pointing directly to `.md` files (e.g., `[Topic](../concepts/topic.md)`) so `openwiki visualize` and `.agents/skills/openwiki/scripts/wiki_scout.py` build a rich, connected knowledge graph with zero broken links.
4. **Grounded Evidence:** Ground all factual claims in repository files, notes, data, and tests, clearly distinguishing verified context from personal critiques or speculative ideas where applicable.

## 4. Multi-Archetype Quality Standards & Operational Protocols

Follow the standardized protocols defined in `.agents/skills/openwiki/SKILL.md`:
1. **Multi-Archetype Quality Contract:**
   - **Archetype A (System & Code Architecture — A1 Caveats, A2 Architecture/Runbooks, A3 ADRs):** Clear boundaries, entrypoints, mechanisms, state/lifecycle, failure invariants, and focused tests.
   - **Archetype B (Domain Research & Conceptual Syntheses):** Core thesis, primary sources, strict attribution hygiene (speaker vs. debate vs. author commentary), and lossless high-signal details.
   - **Archetype C (Strategic Ideas & Venture Theses):** Unmet friction, value hypothesis, operational mechanisms, failure modes, and validation milestones.
2. **Operational Protocols (System-1 Radar $\rightarrow$ System-2 Full-Page Reading):**
   - **Mode A (Read / Consult):** Non-destructive System-1 radar orientation via `python3 .agents/skills/openwiki/scripts/wiki_scout.py {overview|search|neighbors}` (checking staleness, BM25 rankings, and 1-hop neighborhoods) before falling back to `rg -n` (`ripgrep`, reserved inside `openwiki/` strictly for regex, punctuation, or exact-literal patterns), followed by lossless System-2 full-page reading of target `.md` pages without file mutations.
   - **Mode B (Write / Update):** Full update protocol responding to `/openwiki:update`, `/openwiki-update`, and lifecycle handoffs from `opsx-archive` / `opsx-bulk-archive`, verified via `rg -n "openwiki_generated" openwiki/` and `python3 .agents/skills/openwiki/scripts/wiki_scout.py overview --root openwiki --stale-only`.
