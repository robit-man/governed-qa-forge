# Design principles for a deeply meaningful synthetic Q/A corpus

Date: 2026-09-25  
Decision class: pre-scaffold architecture constraints  
Evidence base: REF-001–REF-018 plus authoritative governance standards in the source register

## Working definition of “deeply meaningful”

A record is meaningful when it adds a deliberate, verifiable learning signal that is not already supplied by a nearby record. Fluent text is insufficient. Each accepted Q/A must occupy a planned location in a coverage model, teach or test a named cognitive operation, have an answer form suited to that operation, and survive correctness, novelty, safety, and lineage checks.

The corpus therefore optimizes a vector, not a scalar:

`utility = correctness × pedagogical_value × coverage_gain × answer_fitness × authorization × reproducibility`

If any mandatory factor is zero, the row is rejected. A single “quality score” may rank surviving candidates, but may not override a failed gate.

## Coverage cube

The taxonomy should be versioned and multi-label. At minimum, plan quotas and gaps across:

| Dimension | Examples |
|---|---|
| domain | mathematics, code, science, humanities, professional, everyday reasoning |
| task | explain, classify, derive, compare, critique, transform, plan, troubleshoot |
| reasoning operation | retrieval, decomposition, causal, counterfactual, spatial, temporal, quantitative, adversarial |
| answer form | concise fact, structured explanation, worked solution, rubric, code, refusal/correction |
| difficulty | prerequisite level, step count, distractor load, constraint count, ambiguity |
| evidence mode | deterministic, source-grounded, executable, rubric-scored, expert-reviewed |
| interaction context | novice, expert, skeptical reviewer, constrained operator, multi-turn |
| risk | ordinary, sensitive, dual-use, high-stakes, prohibited/quarantined |

Personas may add interaction diversity, but must not fabricate sensitive demographic identities or substitute persona count for semantic coverage.

## Generation architecture

1. **Govern seeds.** Start with human-written or authoritative seed tasks. Approve license/terms, source snapshot, scope, and category assignment before generation.
2. **Allocate lineage groups.** Assign seed families and protected sources to train, development, or test before descendants are generated. No descendant may cross its ancestor’s split.
3. **Generate candidates, not training rows.** Produce an initial 3–10 candidates per desired acceptance, varying bounded template families, answer form, difficulty operator, and where authorized, teacher family.
4. **Validate deterministically first.** Enforce schema, language, length, format, answer constraints, citations, code/tests, calculations, and prohibited-content rules before invoking subjective judges.
5. **Verify the answer independently.** Prefer solvers, compilers, unit tests, retrieval against pinned sources, or explicit rubrics. A teacher’s confidence is not verification.
6. **Reflect selectively.** Critique and revise candidates only when a named failure signal warrants it. Preserve the original, critique, revision, and validator reruns as a provenance chain.
7. **Decontaminate in layers.** Apply normalized exact hashes, token/n-gram similarity, semantic clustering, source/template-family analysis, and protected-benchmark checks. Human-adjudicate the similarity review band.
8. **Select on a Pareto frontier.** Require quality floors, then maximize coverage gain and diversity while enforcing category floors and family caps. Preserve rare valuable examples even when embedding-space density is low.
9. **Audit independently.** Calibrate automated judges against dual-human review. Randomize pair order, evaluate both A/B and B/A, and adjudicate disagreements.
10. **Release immutably.** Emit versioned records, rejection ledger, split manifests, data card, source/provider registry, quality report, provenance bundle, and per-file checksums.

## Corpus record contract

Every candidate and accepted record should include:

- identity: `record_id`, `schema_version`, `corpus_version`, canonical-record SHA-256;
- content: system/user/assistant messages, answer form, language, category labels;
- learning signal: task, reasoning operation, prerequisite, difficulty features, misconception targeted;
- lineage: seed/source IDs, parent IDs, generation depth, generation run, template ID/hash;
- generator: provider, exact model/version, terms snapshot, authorization basis, sampling parameters, random seed, timestamp;
- grounding: citations/source IDs, verifier type/version/result, executable artifacts where applicable;
- governance: license basis, redistribution status, attribution, privacy/safety/IP scan results;
- quality: deterministic checks, factuality/rubric results, diversity/dedup scores, judge identities and order;
- disposition: review state, reviewer/adjudicator, exclusion reason, split and lineage group.

Release-level metadata adds intended and prohibited uses, language, taxonomy version, human/synthetic fractions, maximum generation depth, code commit, environment/container digest, config hash, source snapshots, counts, split definitions, data-card/provenance URIs, approvals, and all file hashes.

## Initial project gates

These thresholds are proposed starting controls and must be recalibrated with pilot data.

| Gate | Initial requirement |
|---|---|
| authorization | 100% of seed sources and teachers explicitly approved; unclear/expired/incompatible is blocked |
| schema and lineage | 100% valid; every row resolves to approved seed, generator, prompt, terms snapshot, verifier, and disposition |
| exact duplicates | zero within the release and against release history |
| semantic duplicates | calibrated threshold; all review-band pairs adjudicated; unresolved surplus below 1–2% |
| protected benchmark contamination | zero confirmed matches after exact, n-gram, semantic, and human review |
| factual support | at least 98% overall; 100% for admitted high-stakes factual rows |
| privacy/secrets | zero unresolved PII, credentials, secrets, or sensitive personal data |
| family concentration | no family above 5% corpus or 10% of a category without signed exception |
| human audit | at least 400 records and 30/category for the first material release; point validity at least 97%, one-sided Wilson lower bound at least 95%, and no category below 95% |
| judge calibration | at least 200 dual-human examples; agreement at least 80%; Cohen’s kappa at least 0.65 overall and 0.55/category |
| order robustness | at least 95% consistency under A/B ↔ B/A swap for pairwise gates |
| recursion | default generation depth ≤ 1; deeper lineage quarantined for explicit approval |
| regression | no critical slice loses >3 percentage points; aggregate retention loss limited to max(2 points, bootstrap confidence interval) |

High-risk categories should receive 100% expert review or remain out of scope for the first release.

## Experimental sequence

### Pilot A: pipeline calibration

Target 500–1,000 accepted records, not production scale. Measure acceptance yield, validator precision/recall, semantic-duplicate review bands, category gaps, judge/human agreement, cost per accepted row, and provenance completeness.

### Pilot B: causal ablations

Train controlled adapters on 25%, 50%, and 100% subsets; quality-only versus quality+diversity; concise versus mixed answer forms; with/without selective reflection; and leave-one-source/category-out variants. Use fixed seeds, token budgets, and checkpoints.

### Production release

Scale to several thousand only after the pilot gates pass. Use a frozen, independently authored evaluation suite plus capability, safety, calibration, and anti-repetition slices. Compare against the unchanged base and the strongest adjacent-suite baseline.

## Important unresolved questions

- The best accepted-record count is empirical; LIMA-like quality results and large-scale diversity results do not imply one universal optimum.
- Semantic deduplication can erase useful controlled variants, so cluster decisions need purpose-aware adjudication.
- LLM judges are useful triage, not ground truth; correlations vary by model, category, and presentation.
- Synthetic augmentation is not equivalent to recursive replacement. Preserve authoritative anchors and measure ancestry-specific effects.
- Provider output ownership is not sufficient authorization for cross-provider model development. Terms must be reviewed per provider and use.

## Scaffold acceptance criterion

The next scaffold is acceptable only if it can demonstrate, with fixtures, that a generated candidate cannot enter a release without passing authorization, lineage, split isolation, deterministic validation, independent answer verification, decontamination, review, and immutable manifest generation.
