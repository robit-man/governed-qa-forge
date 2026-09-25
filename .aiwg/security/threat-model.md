# Threat Model — Governed QA Forge

## Protected assets

Provider credentials, private source material, protected evaluation sets, review identities, lineage integrity, release fixity, and downstream model behavior.

## Trust boundaries

- human-authored workspace inputs;
- remote teacher endpoint and its outputs;
- local filesystem containing run and release artifacts;
- reviewer decisions;
- downstream fine-tuning loader.

## Principal threats and controls

| Threat | Control |
|---|---|
| unauthorized source or teacher | deny-by-default registry and release-time doctor |
| credential disclosure | dedicated environment prefix; public HTTPS default; no credential serialization |
| SSRF | public-address resolution check; credential-free explicit private-endpoint mode |
| prompt/output poisoning | answer-only teacher schema, compiler-owned semantic transforms, content gates, protected benchmarks |
| evaluation contamination | lineage split before generation; benchmark overlap checks |
| forged approval | approved reviewer registry, candidate-bound decision, rationale, timestamp, complete-decision import |
| artifact tampering | sealed run hashes, release-time revalidation, per-file SHA-256, externally supplied root digest |
| path traversal | workspace-bound run and release resolution |
| arbitrary code execution | no executable-code verifier in the base package |
| partial official release | temporary build directory followed by atomic promotion |

## Residual risks

Pattern scans do not prove privacy, feature-hashed similarity is not a universal semantic oracle, local reviewer registries do not authenticate a human cryptographically, reviewers can collude or err, and authorization metadata can be incorrect. The base provider deliberately does not perform arbitrary semantic question evolution. Production programs should add signed review attestations, independent governance review, domain-specific solver or entailment adapters, neural embedding checks where appropriate, protected evaluator custody, and external security controls.
