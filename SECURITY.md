# Security Policy

## Supported versions

Security fixes are provided for the latest released minor version.

## Reporting

Please report vulnerabilities through GitHub private vulnerability reporting for this repository. Do not place credentials, private datasets, provider outputs, or personal data in a public issue.

## Security model

- API credentials are read only from names under the `QAFORGE_TEACHER_` prefix and are never
  serialized. Explicit private-endpoint mode cannot receive ambient credentials.
- Opaque-service worker and control credentials use separate `QAFORGE_AGENT_TOKEN` and
  `QAFORGE_CONTROL_TOKEN` values. Task lease secrets are stored only as SHA-256 digests, the worker
  app disables schema discovery, bounds request bodies, and successful submissions return no
  evaluation signal. Collection creation seals workspace input hashes, validates transformed
  question size, and rejects exact registered source, teacher, benchmark, seed, and lineage
  identifiers in worker-visible text. Behavior-anchor IDs and source references are also private
  identifiers and remain outside worker questions and trainer-visible messages.
- Credentialed teacher endpoints must use public HTTPS URLs without userinfo. Host addresses are
  checked immediately before access; network-layer egress controls remain recommended against DNS
  rebinding and routing-layer attacks.
- Run, release, review-export, and checksum paths are constrained to their intended workspace
  subtrees. The service broker path is also constrained to the selected workspace.
- Review identities resolve through an approved local registry and decisions bind candidate
  digests, structured derivations, and immutable canonical behavior-anchor context. Production
  decisions require explicit derivation-verification and semantic-alignment attestations. This
  does not cryptographically authenticate a human; use signed attestations where that threat is
  material.
- Calibration corpora are permanently non-releasable. Test fixtures require an internal-only
  release path. Production count and coverage floors are code-owned and rechecked during release
  verification.
- Official release verification requires the root digest printed by `qaforge release` to be
  supplied from a separately trusted channel. `--allow-unanchored` provides damage detection only.
- The built-in verifiers do not execute arbitrary generated code.
- Built-in providers cannot rewrite seed semantics; independently verified question-evolution
  extensions are required for that capability.
- The service control port is a privileged interface and must remain loopback-bound or behind a
  separately authenticated trusted network. Use TLS plus workload identity or mTLS if the worker
  port crosses an untrusted network.
- Agent frameworks must run under an identity that cannot read the Forge workspace, SQLite broker,
  seed bank, repository checkout, or control token. The worker HTTP contract is not a sandbox for a
  process that already has host-filesystem access.
- The shared SQLite queue is readable/writable by the worker service account. The documented threat
  boundary protects HTTP clients, not arbitrary code execution as that account. Deploy a narrow
  external broker/RPC boundary if worker-service compromise is in scope.
- Generated text is scanned for common credential and personal-data patterns, but this is defense in depth rather than a privacy guarantee.
- Authorization registries and release evidence do not replace legal review.
