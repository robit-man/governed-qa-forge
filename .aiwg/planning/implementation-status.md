# Implementation Status — Governed QA Forge

**Updated:** 2026-09-25

## Complete

- AIWG research induction and best-practices audit
- project intake, requirements, architecture decision, and threat model
- typed schema and deny-by-default registries
- deterministic lineage splitting before generation
- offline and bounded OpenAI-compatible answer providers with compiler-owned semantic transforms
- deterministic validation and independent, seed-bound answer verifiers
- indexed exact, lexical, semantic-fingerprint, and benchmark decontamination
- eight-dimension coverage selection and digest-bound authorized review workflow
- atomic immutable release builder with Datasheet, Croissant, PROV, rejection ledger, fixity, and
  external root-anchor verification
- CLI, documentation, tests, coverage gate, CI, package build, and offline E2E demo
- split worker/control service with opaque task leases, feedback-free receipts, and SQLite concurrency
- hardened systemd templates and framework-neutral HTTP integration documentation
- sanitized direct-provider prompts that exclude private seed, source, lineage, and verifier metadata
- 1,000-lineage calibration: 3,000/3,000 valid submissions, 1,000 selected, exact category balance,
  and no validation/verifier/contamination failures
- fixed production corpus policy: 20,000 train, 2,000 validation, 2,000 test, ten categories, three
  difficulty tiers, structured review-verified derivations, and ten AIWG-informed behavior domains
- messages-only conversational JSONL with bound provenance sidecars
- machine-enforced calibration and test-fixture non-production boundaries
- AIWG behavior-anchor registry with latent rendering that excludes framework identifiers from
  worker questions and trainer-visible messages

## Next operational milestone

Treat the existing calibration only as technical evidence. Authorize a domain-specific model
teacher, build the production-scale anchored seed bank, run open-ended quality pilots, and generate
a separate corpus that satisfies the fixed release policy. Run a split-process/systemd deployment
smoke before claiming OS-level isolation.
