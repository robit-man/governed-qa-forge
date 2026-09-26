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
- **FR-019:** Provide and execute a deterministic 1,000-selected-record calibration pass through the blind worker contract, leaving its output pending independent review as permanently non-releasable technical evidence.
- **FR-020:** Require each generated candidate to contain one to sixteen structured derivation steps and a separately stored final answer; verify only the final answer against the independent seed contract.
- **FR-021:** Enforce the non-configurable production policy `qaforge-reasoning-sft-minimum-v1`: at least 20,000 train, 2,000 validation, and 2,000 test records, ten categories, and all three difficulty tiers.
- **FR-022:** Classify corpora as production, calibration, or test fixture; reject calibration release unconditionally and permit fixture release only through the internal demo path.
- **FR-023:** Emit standardized messages-only conversational JSONL and same-order provenance sidecars; bind review and content hashes to the exact trainer-visible messages.
- **FR-024:** Require every production record to reference an approved AIWG behavior anchor and require release coverage of all ten governed behavior domains while excluding framework and anchor identifiers from trainer-visible content.
- **FR-025:** Require an approved production review decision to explicitly attest that the candidate derivation was verified and that the example semantically enacts its canonical behavior-anchor principles.
- **FR-026:** Ship a manifest-bound downstream evaluation protocol requiring unchanged-base comparison, training seeds 17/29/47, and test isolation before any improvement or convergence claim.
- **FR-027:** Preserve read-only verification of schema-1.0 artifacts while preventing new generation or release, and atomically requeue unfinished answer-only broker submissions under the v2 response contract.

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
- **NFR-014:** Production size, category, difficulty, and behavior-domain floors are code-owned invariants and cannot be weakened through workspace configuration.
- **NFR-015:** Worker leases and trainer-visible messages disclose no AIWG, behavior-anchor, source, verifier, score, or reward identifiers; provenance remains in sealed private inputs and release sidecars.

## Traceability

Tests use requirement IDs in names or docstrings, and the quality-gate report maps critical requirements to executed evidence.
