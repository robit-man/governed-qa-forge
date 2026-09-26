# Change Request CR-002: Production Reasoning Minimum

**Status:** implemented pending delivery review  
**Issue:** #4  
**Requested:** 2026-09-25

## Change

Replace the configurable row-count release threshold with one acceptable production minimum:

- 20,000 train, 2,000 validation, and 2,000 test records;
- at least ten categories and all three difficulty tiers;
- a structured, explicitly review-verified derivation and independently verified final answer for
  every record;
- standardized messages-only trainer JSONL with governance metadata in bound sidecars;
- coverage of ten AIWG-informed behavior domains expressed latently through examples;
- permanent non-release classification for the 1,000-record technical calibration.
- a manifest-bound downstream evaluation protocol comparing the unchanged base and tuned model
  across training seeds 17, 29, and 47 before any convergence or improvement claim.

## Rationale

The earlier `target_size` gate could authorize a 500- or 1,000-record release and did not bind a
derivation. Inline metadata was convenient but could enter trainer context accidentally. The new
standard distinguishes transport calibration from training readiness and makes the minimum a
code-owned invariant rather than an operator-tunable recommendation.

AIWG artifacts remain the governed source of behavioral principles. Training questions and
answers do not name the framework or reproduce its scaffolding; instead, scenario-based examples
repeatedly enact requirements clarification, evidence discipline, provenance, threat modeling,
independent verification, testing, architecture impact, operational recovery, context boundaries,
and accountable orchestration.

## Impact

- Candidate schema moves to 1.1 and the opaque response contract moves to v2.
- Existing answer-only runs remain historical evidence and cannot become production releases.
- SQLite receives additive `derivation_json` and response-contract migrations; unfinished
  answer-only submissions are requeued under the v2 contract.
- Prompt-template and content hashes change because derivation and exact message formatting are
  now bound.
- Production seed banks need at least 24,000 eligible lineages with adequate per-split capacity;
  the scaffold targets 30,000 to provide hash-split headroom.
- Review packets include immutable canonical anchor context and add `derivation_verified` plus
  `behavior_alignment_verified`; production approval fails unless both are true.
- Schema-1.0 artifacts remain audit-readable but cannot generate or release.

## Acceptance evidence

- Unit tests exercise exact and one-below split floors, nine-category rejection, missing difficulty
  and behavior-domain rejection, config floor validation, content-hash derivation binding, and
  permanent calibration rejection.
- Integration tests require structured opaque submissions and demonstrate feedback-free receipts.
- End-to-end tests verify messages-only split files, bound sidecars, compiler-owned response
  markers, latent anchor opacity, release fixity, and fixture-only release authorization.
