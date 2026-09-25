# Security Policy

## Supported versions

Security fixes are provided for the latest released minor version.

## Reporting

Please report vulnerabilities through GitHub private vulnerability reporting for this repository. Do not place credentials, private datasets, provider outputs, or personal data in a public issue.

## Security model

- API credentials are read only from names under the `QAFORGE_TEACHER_` prefix and are never
  serialized. Explicit private-endpoint mode cannot receive ambient credentials.
- Credentialed teacher endpoints must use public HTTPS URLs without userinfo. Host addresses are
  checked immediately before access; network-layer egress controls remain recommended against DNS
  rebinding and routing-layer attacks.
- Run, release, review-export, and checksum paths are constrained to their intended workspace
  subtrees.
- Review identities resolve through an approved local registry and decisions bind candidate
  digests. This does not cryptographically authenticate a human; use signed attestations where
  that threat is material.
- Official release verification requires the root digest printed by `qaforge release` to be
  supplied from a separately trusted channel. `--allow-unanchored` provides damage detection only.
- The built-in verifiers do not execute arbitrary generated code.
- Built-in providers cannot rewrite seed semantics; independently verified question-evolution
  extensions are required for that capability.
- Generated text is scanned for common credential and personal-data patterns, but this is defense in depth rather than a privacy guarantee.
- Authorization registries and release evidence do not replace legal review.
