# Threat Model — Governed QA Forge

## Protected assets

Provider credentials, private source material, protected evaluation sets, review identities, lineage integrity, release fixity, and downstream model behavior.

## Trust boundaries

- human-authored workspace inputs;
- remote teacher endpoint and its outputs;
- local filesystem containing run and release artifacts;
- reviewer decisions;
- downstream fine-tuning loader.
- opaque worker API and untrusted agent workers;
- private control API and SQLite task broker.

## Principal threats and controls

| Threat | Control |
|---|---|
| unauthorized source or teacher | deny-by-default registry and release-time doctor |
| credential disclosure | dedicated environment prefix; public HTTPS default; no credential serialization |
| SSRF | public-address resolution check; credential-free explicit private-endpoint mode |
| prompt/output poisoning | structured derivation/final-answer schema, compiler-owned semantic transforms and response formatting, content gates, protected benchmarks |
| evaluation contamination | lineage split before generation; benchmark overlap checks |
| forged approval | approved reviewer registry, exact trainer-message-bound decision, derivation-verification attestation, rationale, timestamp, complete-decision import |
| artifact tampering | sealed run hashes, release-time revalidation, per-file SHA-256, externally supplied root digest |
| path traversal | workspace-bound run and release resolution |
| arbitrary code execution | no executable-code verifier in the base package |
| partial official release | temporary build directory followed by atomic promotion |
| reference/provenance leakage to a worker | split worker/control apps; minimal worker schema; disabled worker discovery; private mapping retained server-side |
| private identifier embedded in task text | collection preflight rejects exact registered source, teacher, benchmark, seed, lineage, behavior-anchor, AIWG, and anchor-source identifiers; operator content review covers informal names and contextual clues |
| reward hacking from evaluation feedback | submission returns receipt only; verification, selection, contamination, and review remain control-plane-only |
| task theft or replay | independent bearer auth, random task IDs, expiring one-time lease secret stored as a digest, transactional state transition |
| cross-plane privilege escalation | distinct credentials, ports, processes, and route tables; loopback-default control bind |
| concurrent double claim/submission | SQLite `BEGIN IMMEDIATE`, conditional updates, and exactly-one accepted submission |
| service secret disclosure | environment file outside the repository, restrictive umask and service account, authorization headers excluded from application data |
| worker resource exhaustion | 64 KiB pre-parse request limit, bounded derivation/final-answer schema, bounded server concurrency, operator ingress rate limits |
| calibration relabeled as production | corpus class sealed in run inputs; release builder rejects calibration unconditionally; verifier rejects released calibration manifests |
| framework mechanics leak into training | messages-only trainer files, metadata sidecars, latent-rendering content gate, behavior/source identifiers retained only in provenance |

## Residual risks

Pattern scans do not prove privacy, feature-hashed similarity is not a universal semantic oracle, local reviewer registries do not authenticate a human cryptographically, reviewers can collude or err, and authorization metadata can be incorrect. The base provider deliberately does not perform arbitrary semantic question evolution. Production programs should add signed review attestations, independent governance review, domain-specific solver or entailment adapters, neural embedding checks where appropriate, protected evaluator custody, and external security controls.

An opaque API cannot stop a worker from reasoning about information contained in the question
itself, infer every informal source name or category clue, colluding outside the service, or
fingerprinting public material. Exact registered source, teacher, benchmark, seed, lineage,
behavior-anchor, and anchor-source identifiers are rejected before collection. The API prevents
the service from supplying privileged context or adaptive reward signals. Operators exposing the
worker plane beyond a trusted network must add TLS, per-identity rate limits, and preferably
workload identity or mTLS at the ingress.

The deployed worker and control processes share a SQLite queue. External agent frameworks are outside its filesystem trust boundary, but code execution as the worker service account can inspect or alter queue rows, including private seed/task mappings. Programs that include worker-service compromise in scope must substitute an isolated broker or narrow RPC boundary before production use.
