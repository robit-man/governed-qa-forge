# Run Plan — Opaque Calibration 1000

1. Scaffold a new, non-demo workspace with 1,000 project-authored lineages and deny release before review.
2. Create a service collection through the authenticated control API.
3. Randomly lease each task through the worker API. The calibration solver receives only the returned user message; it has no workspace, seed, source, reference-answer, verifier, lineage, category, or score input.
4. Submit one bounded answer with the one-time lease credential and require the non-diagnostic `recorded` receipt.
5. Finalize only after all 3,000 tasks are durable, then execute normal validation, independent verification, decontamination, coverage-aware selection, and run sealing.
6. Preserve counts, hashes, split/category distributions, failures, and limitations.
7. Stop before review and release.

## AIWG routing note

The installed AIWG 2026.9.4 CLI returned `Unknown command: dataset` for the dataset-intelligence skill's canonical `aiwg dataset` route. The equivalent governed intake, plan, run evidence, and limitations are therefore materialized in this directory. No conversational-only decision is treated as the record of truth.

## Calibration adjustment

Attempt 1 completed all 3,000 submissions but was interrupted during finalization after the initial 4,096-dimension/eight-band fingerprint configuration produced about 992,000 summed band-bucket hits (714,743 unique candidate comparisons) for the controlled templates. The attempt is preserved locally at `pilot-workspace-attempt-1/` and was never reviewed or released.

Attempt 2 retained exact hashes, normalized lexical checks, semantic fingerprints, protected-benchmark checks, and thresholds of 1.0, while right-sizing the calibration index to 384 dimensions and two LSH bands. It produced roughly 2,765 summed band-bucket hits (2,760 unique candidate comparisons). Content audit then rejected that attempt because 100 questions carried an avoidable “calibration” cue and several templates had weak article grammar. It is preserved locally at `pilot-workspace-attempt-2-context-cue/` and was never reviewed or released. The definitive run performed 2,642 unique candidate comparisons.

Attempt 3 removed the contextual cue and repaired the templates. It passed the technical gates, but is preserved as `pilot-workspace-attempt-3-pre-security-hardening/` because it preceded the final input-sealing, citation-integrity, service-account, and restart-recovery changes. The definitive run repeats the complete 1,000-record calibration against the hardened implementation. These adjustments change only the calibration workspace; library defaults remain unchanged.

Attempt 4 was intentionally interrupted after 1,940 submissions when the independent audit identified projected-question bounds, private-identifier preflight, broker-path confinement, and request-resource limits that needed to be in the definitive implementation. It is preserved locally at `pilot-workspace-attempt-4-interrupted-hardening/`; it produced no Forge run, review, or release.
