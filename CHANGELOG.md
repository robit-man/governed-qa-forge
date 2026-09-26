# Changelog

## Unreleased

- Fixed `qaforge-reasoning-sft-minimum-v1` production release gate: 20,000 train, 2,000
  validation, 2,000 test, ten categories, all three difficulties, and ten AIWG behavior domains.
- Structured derivation plus separately verified final-answer generation, review, and opaque API
  v2 contract.
- Messages-only conversational fine-tuning JSONL with bound provenance sidecars.
- Canonical, source-hashed latent AIWG behavior anchors with immutable review context, explicit
  semantic-alignment attestation, and trainer-context opacity checks.
- Read-only schema-1.0 verification and atomic migration of unfinished answer-only broker work to
  the structured v2 response contract.
- Permanent non-release classification for calibration corpora and internal-only fixture release.
- Split-plane opaque agent service with atomic SQLite task leases and feedback-free receipts.
- Sanitized remote teacher prompts that exclude private seed, source, lineage, and verifier data.
- Hardened systemd deployment templates and framework-neutral HTTP contract.
- Deterministic 1,000-selected-record blind-service calibration workflow.

## 0.1.0 — 2026-09-25

- Initial governed candidate generation and release compiler.
- Deterministic fixture and OpenAI-compatible providers.
- Pre-generation lineage splitting and layered decontamination.
- Independent verifier contracts and explicit review workflow.
- Datasheet, Croissant, PROV, rejection ledger, and fixity output.
