# ADR-003: Latent Reasoning Release Contract

**Status:** Accepted  
**Date:** 2026-09-25

## Context

The original candidate contract stored only an answer, and released rows mixed conversational
messages with governance metadata. The technical calibration could become releasable if later
approved. The project now needs a strict production floor and wants AIWG reasoning behaviors to
become learned capabilities without exposing framework structure or evaluation context to workers
or the target model.

## Decision

1. Store derivation as one to sixteen bounded steps and keep the final answer separate.
2. Verify the final answer independently, then require digest-bound human attestations that the
   derivation is valid and the example semantically enacts its immutable canonical anchor context.
3. Let the compiler render a canonical assistant response with `Derivation:` and `Final answer:`
   markers and hash the exact two-message trainer row.
4. Emit messages-only JSONL plus same-order metadata sidecars.
5. Keep AIWG anchor IDs, source references, and governance evidence outside trainer messages.
6. Require each production record to reference an approved anchor and require all ten governed
   behavior domains in the release.
7. Make split, category, difficulty, and anchor floors immutable code policy.
8. Reject calibration release under every review state; permit test-fixture output only through the
   internal demo path.
9. Keep schema-1.0 artifacts read-only and verifiable; migrate unfinished answer-only service work
   by requeueing it under the structured v2 response contract.

## Consequences

This is a breaking generation and worker-submission contract. Old runs cannot be rehashed or
promoted. Exact trainer rows are portable, review binds the actual learning signal, and source
framework mechanics cannot accidentally become model context. The fixed floor increases seed,
review, compute, and storage requirements; it is intentionally the cost of calling an artifact a
production reasoning corpus.
