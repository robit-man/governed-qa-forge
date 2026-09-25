---
title: "Synthetic Q/A corpus generation: AIWG best-practices audit"
date: 2026-09-25
status: complete
decision: pass_with_required_controls
scope: /srv/question_stack and adjacent /srv/fine_tuning_suite
evidence_refs: [REF-001, REF-002, REF-003, REF-004, REF-005, REF-006, REF-007, REF-008, REF-009, REF-010, REF-011, REF-012, REF-013, REF-014, REF-015, REF-016, REF-017, REF-018]
---

# Synthetic Q/A corpus generation: AIWG best-practices audit

## Executive decision

**PASS WITH REQUIRED CONTROLS.** The evidence supports building a several-thousand-record categorical synthetic Q/A stack, but not a direct prompt → JSONL generator. The scaffold must be a governed candidate factory with independent verification, family-aware splitting, multi-layer decontamination, calibrated review, and immutable lineage.

The adjacent fine-tuning suite already has valuable controls: deterministic split artifacts and hashes, fixed evaluation seeds, base-vs-tuned evaluation, completion-only loss, early stopping, category counts, and explicit anti-repetition work. Its data curation is nevertheless row-oriented. Before this new corpus is consumed downstream, the surrounding system needs semantic/family grouping, protected benchmark decontamination, per-record provenance, provider authorization records, and evaluation isolation across historical rounds.

## Research question

What practices most reliably produce synthetic instruction/Q&A data that adds robust learning signal to a larger model, while remaining correct, diverse, non-contaminating, legally usable, reproducible, and evaluable?

## Method

The pass combined:

- AIWG discovery and the `research-workflow`, `induct-research`, `best-practices-audit`, `research-document`, `grade-on-ingest`, `citation-guard`, `provenance-create`, and `quality-assess` procedures;
- 18 locally acquired primary research papers, fixed by SHA-256 and extracted for review;
- authoritative governance standards from NIST, W3C, MLCommons, the EU, and dataset-documentation literature;
- three independent evidence lanes: generation methods, quality/evaluation, and governance/provenance;
- read-only inspection of the adjacent fine-tuning suite;
- GRADE-style assessment of directness, design strength, limitations, and applicability.

No CUDA, container, service, model inference, or training workload was started.

## Findings

### 1. Curated signal beats nominal scale

Self-Instruct establishes a practical seed-and-filter loop; LIMA shows that small, curated sets can be disproportionately effective; DEITA and QDIT show why joint quality/diversity selection beats undifferentiated volume. The target should be several thousand *accepted* records, not several thousand first-pass generations. [REF-001, REF-004, REF-006, REF-017]

### 2. Difficulty and diversity must be designed

Evol-Instruct supplies bounded mutation operators, #InsTag supplies fine-grained taxonomy analysis, and Persona Hub supplies a conditional diversity mechanism. Together they argue for a versioned coverage cube and auditable evolution edges, not generic prompts asking for “diverse hard questions.” Persona use must be bounded to avoid stereotypes and spurious demographic inference. [REF-002, REF-014, REF-015]

### 3. Over-generation is useful only with selection

Magpie’s large candidate pools and multi-axis selection, plus DPP-style diversity research, support generating multiple candidates per desired record and retaining only those that add quality and coverage. Temperature and sampling settings expose tradeoffs; they are not correctness controls. [REF-005, REF-007]

### 4. Answers require independent verification

Orca and textbook-style synthesis show the value of explanation-rich material, while the imitation study warns that plausible teacher style is not underlying capability. Prefer deterministic solvers, tests, compilers, grounded citations, and explicit rubrics. Use selective reflection on detected failures, then rerun the original validators. [REF-003, REF-012, REF-016, REF-018]

### 5. Deduplication and split isolation are graph problems

Exact hashes alone miss paraphrases, template siblings, shared source passages, and evolved descendants. Build a lineage/similarity graph, assign connected families to one split, and check against protected evaluations before release. Deduplication cutoffs must be calibrated on this corpus because useful controlled variants can resemble duplicates. [REF-002, REF-008]

### 6. Synthetic ancestry must remain visible

Recursive replacement can erase rare modes; retaining authoritative/original data changes the risk regime. Record generation depth and synthetic fractions by category and family. Default to first-generation synthesis, retain immutable authoritative anchors, and quarantine deeper recursive ancestry. [REF-009, REF-010]

### 7. Automated judges need controls

LLM judges show position and other biases. Use deterministic validation before judging, record judge version and prompt, reverse pair order, calibrate against independently reviewed human samples, and adjudicate disagreements. A generator must not be its own sole release authority. [REF-011]

### 8. Governance belongs in the row and release

Datasheets, Data Cards, PROV-O, Croissant, and NIST guidance converge on documented origin, processing, intended use, quality, privacy, and maintenance. Synthetic text is not automatically anonymous or rights-cleared. Provider terms can constrain competitive model development even when output is assigned to the customer, so source and teacher authorization must be deny-by-default when unclear. [REF-013]

## Audit of the adjacent fine-tuning suite

### Controls worth preserving

| Existing control | Evidence | Assessment |
|---|---|---|
| fixed mixture intentions and categories | `curate_r5.py:503-531` | useful baseline composition record |
| deterministic shuffle and file hashes | `curate_r5.py:533-569`; `app.py:261-307` | strong reproducibility foundation |
| fixed base/tuned evaluation samples | `app.py:29-30`, `app.py:310-336` | appropriate paired comparison |
| assistant/completion-only loss | `app.py:680-698` | aligns loss with response learning |
| early stopping and saved best model | `app.py:649-699` | limits blind overtraining |
| repetition filters and anti-loop data | `curate_r6.py:54-65`; `curate_r7.py:36-37` | addresses a real observed failure mode |
| additive treatment of a proven base | `curate_r7.py:4-8`, `curate_r7.py:190-200` | directionally consistent with retaining prior data |

### Gaps to close before integration

| Gap | Current evidence | Required change |
|---|---|---|
| row-level split only | R5/R6/R7 shuffle rows then slice at 90/5/5 | assign connected seed/template/source/semantic families to a split before generation |
| historical evaluation leakage | R7 loads the full R5 training set, adds layers, then creates new validation/test slices | mark historical exposure; never treat descendants or previously trained rows as independent evaluation |
| shallow provenance | manifests list source names, counts, seeds, and file hashes | pin source revision/config, original row ID, license/terms snapshot, teacher, prompt, verifier, and ancestry per record |
| no semantic or benchmark decontamination | repetition checks target loops, not meaning or benchmark overlap | exact + n-gram + embeddings + lineage graph + protected-suite adjudication |
| source sampling without family caps | fixed source counts, followed by row shuffle | measure source/template/category concentration and enforce caps |
| no rejection ledger | accepted outputs are written, failed decisions are not release artifacts | preserve candidate IDs, failed gates, revisions, and terminal disposition |
| evaluation author independence unclear | generation/curation and evaluation live in the same suite | freeze an authoritative, separately authored evaluation registry with access controls |
| rights and provider terms not represented | source names are descriptive strings | add source/provider registry and authorization gate |

The historical-leakage observation is conditional: if a downstream model or adapter has previously trained on the R5 training rows, an R7 validation/test sample drawn from that pool is not historically unseen even though it is held out within the R7 run.

## Required scaffold architecture

The next implementation should have explicit stages and immutable transitions:

`source registry → seed bank → coverage planner → split-family assignment → candidate generation → deterministic validation → grounding/verification → selective critique/revision → dedup/decontamination → multi-objective selection → calibrated review → release builder`

Each stage reads versioned artifacts and writes append-only decisions. A record promoted to `released` must retain pointers to every prior state. Re-running from the same source snapshots, code/config hash, model version, prompts, parameters, and random seeds must reproduce deterministic stages and explain nondeterministic differences.

## Minimum release gate

The release gate is the conjunction of:

1. source and teacher authorization;
2. 100% schema and lineage completeness;
3. zero exact duplicates and zero confirmed benchmark contamination;
4. calibrated semantic/family deduplication;
5. independent answer verification appropriate to category;
6. privacy, secrets, safety, and suspicious-verbatim checks;
7. category/difficulty/answer-form coverage targets;
8. judge-human calibration and stratified human audit;
9. frozen lineage-disjoint splits and authoritative evaluation;
10. reproducible data card, manifests, rejection ledger, provenance bundle, and SHA-256 inventory.

Numerical starting thresholds are defined in the companion design-principles document. They are project hypotheses to validate during a 500–1,000 accepted-record pilot.

## Recommended implementation sequence

1. Scaffold schemas, registries, provenance graph, states, and release gates before any teacher integration.
2. Implement deterministic fixtures for label-first categorical generation, validators, lineage-group splitting, and exact/semantic decontamination.
3. Create a small reviewed seed bank and protected evaluation registry.
4. Run a 500–1,000 accepted-record pilot with 3–10× candidate generation.
5. Calibrate thresholds with dual-human audit and measure acceptance yield/cost.
6. Run controlled fine-tuning ablations against the adjacent suite’s best baseline.
7. Scale to the several-thousand-record release only after the pilot passes.

## Dissent and uncertainty

- Research does not settle a universal quality-versus-volume optimum. Small curated sets and large diverse pools answer different questions.
- N-gram and embedding decontamination detect different overlap; neither should be treated as complete.
- Aggressive semantic deduplication can delete pedagogically valuable contrast sets and controlled variants.
- Judge panels reduce single-model bias but can share correlated training data and failure modes.
- Accumulating real and synthetic data mitigates specific recursive-collapse regimes; it does not validate arbitrary mixtures.
- Legal and contractual applicability depends on provider, jurisdiction, source, target model, and distribution plan; the registry supports review but is not legal advice.

## Conclusion

Proceed to scaffold, but treat the stack as a dataset compiler with evidence and governance, not a text generator. Its principal product is a reproducible release decision: why each row exists, what it teaches, how it was verified, where it came from, what it may be used for, and why it cannot contaminate evaluation.

## References

See the [acquired source register](../sources/INDEX.md), [per-source findings](../findings/), [GRADE assessments](../quality-assessments/), and [fixity manifest](../fixity-manifest.json).
