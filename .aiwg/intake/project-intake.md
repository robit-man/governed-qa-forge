# Project Intake — Governed QA Forge

**Document type:** Greenfield project
**Generated:** 2026-09-25
**Source:** User objective, attached specification, AIWG research induction, and adjacent fine-tuning-suite inspection

## Metadata

- **Project:** Governed QA Forge
- **Repository:** `robit-man/governed-qa-forge` (public)
- **Owner:** Project team
- **Stakeholders:** model-training engineering, dataset curators, quality reviewers, security/governance reviewers
- **Current state:** research complete; implementation beginning

## Purpose and outcomes

Build an end-to-end governed compiler for categorical synthetic question/answer corpora. The system must create deeply useful learning signals for larger-model fine-tuning while preventing untraceable generation, evaluation leakage, unsupported answers, unsafe source use, and recursive synthetic-data contamination.

Success means:

- a local deterministic demo produces a signed, reproducible release without network or GPU access;
- an OpenAI-compatible adapter can generate real candidates after explicit teacher authorization;
- every released row resolves to its seed, source, teacher, prompt template, verification, review, split family, and release manifest;
- connected lineages cannot cross train/validation/test boundaries;
- exact, near-duplicate, semantic-optional, and protected-benchmark checks run before selection;
- releases include SFT JSONL, datasheet, Croissant metadata, PROV lineage, rejection ledger, and SHA-256 inventory;
- tests and CI cover critical gates with at least 80% line coverage.

## Users

- **Primary:** engineers and researchers constructing supervised fine-tuning corpora.
- **Secondary:** reviewers approving candidate records and auditors reconstructing release decisions.
- **Downstream:** training suites consuming chat-style JSONL and release manifests.

## Scope

### Included

- versioned configuration, coverage taxonomy, seed/source/teacher/benchmark registries;
- deterministic pre-generation lineage split assignment;
- 3–10× candidate generation through offline and OpenAI-compatible providers;
- deterministic validation and independent verifier types;
- exact, shingle/SimHash, optional embedding, and benchmark decontamination;
- diversity-aware selection with configurable floors across all eight coverage dimensions and
  lineage/family caps;
- explicit human-review import and approval states;
- immutable run directories and governed release construction;
- CLI, Python API, examples, tests, CI, public documentation, and security guidance.

### Excluded from first release

- hosted multi-user UI, authentication service, and database server;
- autonomous approval of production records;
- unsafe execution of arbitrary generated code;
- bundled proprietary prompts, source material, API credentials, or copyrighted paper PDFs;
- model training and GPU orchestration.

## Architecture

- **Style:** modular Python library with a Typer CLI and append-only filesystem artifacts.
- **Runtime:** Python 3.11+.
- **Validation:** Pydantic models and deterministic policy gates.
- **Networking:** optional HTTPX client for OpenAI-compatible chat-completion endpoints.
- **Persistence:** YAML/JSONL inputs; JSON/JSONL/Markdown/JSON-LD outputs.
- **Deployment:** local virtual environment, CI, or container supplied by downstream users; no resident service required.

## Scale and performance

- Initial pilot: 500–1,000 accepted records.
- Normal production: 5,000–20,000 accepted records and 3–10× candidate volume.
- Split and exact-dedup operations must be deterministic.
- Near-duplicate discovery uses indexed fingerprints rather than an unconditional all-pairs comparison.
- Provider concurrency is configurable and defaults conservatively.

## Security and governance

- **Posture:** strong for dataset supply-chain integrity.
- Secrets are environment-only and never serialized.
- Unapproved or expired source/teacher entries block generation or release.
- High-risk material is blocked by default.
- Provider terms require dated snapshot identifiers and an authorization basis.
- No source PDF or extracted paper text is published in the repository.
- The tool supplies controls and evidence, not legal advice.

## Team and delivery

- Small engineering team; Python and DevOps-aware.
- GitHub pull requests and green CI are required by `.aiwg/aiwg.config`.
- Initial release target: a production-quality open-source CLI/library.

## Key risks

- **Plausible but false answers:** require independent verifier results and review.
- **Lineage leakage:** allocate families before generation and reject cross-split descendants.
- **Judge correlation:** deterministic gates first; human review remains explicit.
- **Rights ambiguity:** deny by default when source or teacher authorization is unclear.
- **Recursive degradation:** default generation depth to one and preserve authoritative seeds.
- **Configuration bypass:** release builder re-evaluates mandatory gates rather than trusting prior status strings.

## Next phase

Implement the modular CLI, fixtures, tests, release builder, security checks, and CI; publish by pull request after all quality gates pass.
