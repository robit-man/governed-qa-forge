# Governed QA Forge — System Requirements

## Functional requirements

- **FR-001:** Validate all configuration and registry inputs against versioned schemas.
- **FR-002:** Block unapproved, expired, or target-use/license-incompatible sources and teachers.
- **FR-003:** Assign lineage families to deterministic splits before candidate generation.
- **FR-004:** Generate a configurable 3–10 candidates per seed through pluggable providers.
- **FR-005:** Preserve teacher model, prompt hash, sampling parameters, source IDs, parents, and generation depth per candidate.
- **FR-006:** Run schema, content, secrets/PII, risk, and evidence validators.
- **FR-007:** Bind questions to allowlisted semantic-preserving seed transforms, then independently verify exact, numeric, bounded-regex, JSON, and citation-contract answers.
- **FR-008:** Detect exact, near-duplicate, lineage, and protected-benchmark overlap; support optional embedding similarity.
- **FR-009:** Select records using quality and all eight coverage dimensions while enforcing configurable dimension floors and lineage/family caps.
- **FR-010:** Export and import digest-bound human review decisions with an authorized reviewer identity and timestamp.
- **FR-011:** Refuse release while any mandatory gate is incomplete or failed.
- **FR-012:** Produce split SFT JSONL, manifest, datasheet, Croissant JSON-LD, PROV JSON-LD, rejection ledger, and SHA-256 inventory.
- **FR-013:** Provide an offline deterministic demo and an OpenAI-compatible remote provider.
- **FR-014:** Expose doctor, generate, review, release, status, and demo CLI journeys.
- **FR-015:** Expose a worker API that leases self-contained questions under opaque identifiers and accepts bounded answers without disclosing provenance, references, verifier contracts, taxonomy, scores, or review state.
- **FR-016:** Expose an independently authenticated control API that creates collection runs, reports aggregate queue state, and finalizes complete collections through the normal governed compiler.
- **FR-017:** Atomically lease tasks with expiring one-time credentials and accept at most one durable submission per task.
- **FR-018:** Provide hardened system-service deployment assets and a framework-neutral HTTP integration contract.
- **FR-019:** Provide and execute a deterministic 1,000-selected-record calibration pass through the blind worker contract, leaving its output pending independent review.

## Non-functional requirements

- **NFR-001:** Same inputs, salt, and deterministic provider produce byte-identical split assignments and content hashes.
- **NFR-002:** Base install works without GPU, container, database, or network access.
- **NFR-003:** Provider credentials are read only from dedicated environment names, never serialized, and candidate content is blocked on maintained secret/PII controls before selection.
- **NFR-004:** Near-duplicate candidate lookup avoids unconditional O(n²) comparison.
- **NFR-005:** Python 3.11+; typed public interfaces; at least 80% line coverage.
- **NFR-006:** All artifact writes stay within the selected workspace.
- **NFR-007:** Public repository excludes acquired PDFs, extracted source text, credentials, and generated private datasets.
- **NFR-008:** Release verification requires a separately retained root digest unless the caller explicitly selects local-demo fixity-only mode.
- **NFR-009:** Worker-plane responses and errors provide no correctness, reward, selection, source, lineage, benchmark, or verifier feedback.
- **NFR-010:** Worker and control APIs use separate credentials, app instances, process entry points, and default network bindings.
- **NFR-011:** Service credentials are environment-only; bearer comparisons are constant-time and lease credentials are persisted only as digests.
- **NFR-012:** Broker claims and submissions remain consistent under concurrent clients and process restart.
- **NFR-013:** Broker writes remain inside the selected workspace; worker request bodies, transformed question sizes, and server concurrency are bounded before task delivery.

## Traceability

Tests use requirement IDs in names or docstrings, and the quality-gate report maps critical requirements to executed evidence.
