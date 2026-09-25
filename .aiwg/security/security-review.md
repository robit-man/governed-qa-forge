# Final Security Review — Opaque Agent Service

**Reviewed:** 2026-09-25

**Scope:** opaque worker/control applications, provider prompt boundary, SQLite queue, systemd
deployment, calibration evidence, and the pre-existing compiler/release controls

**Decision:** **PASS / SHIP WITHIN THE DOCUMENTED HTTP-CLIENT THREAT MODEL**

## Executive decision

The independent final audit found no unresolved High or Medium issue. Earlier findings involving
mutable collection inputs, fabricated citation provenance, cross-plane credentials, placeholder
tokens, finalization restart state, private identifiers, projected-question length, out-of-workspace
broker paths, transport-body limits, and fresh-workspace systemd paths were remediated and retested.

The corpus remains at `awaiting_review`; this security decision does not approve records or create a
release.

## Verified controls

| Control | Result |
|---|---|
| Minimal worker response surface and disabled schema/docs | PASS |
| Independently authenticated worker/control apps and protected control OpenAPI | PASS |
| Separate service accounts and environment files | PASS |
| Strong non-placeholder, distinct bearer secrets | PASS |
| One-time lease secrets stored only as SHA-256 digests | PASS |
| Exactly-one concurrent response acceptance | PASS |
| Collection input hashes and task/question binding | PASS |
| Post-generation manifest/input integrity | PASS |
| Exact private identifier preflight before task persistence | PASS |
| Projected question validation before lease state mutation | PASS |
| Direct and symlink-mediated broker path escape prevention | PASS |
| 64 KiB declared and chunked request-body limit | PASS |
| Uvicorn concurrency/backlog limit of 128 | PASS |
| Citation claims from untrusted workers/providers discarded | PASS |
| Control-start restart reconciliation | PASS |
| Optional systemd `runs`/`releases` paths | PASS |
| Systemd exposure score | 3.2 / OK for both units |
| Dependency audit | no known third-party vulnerabilities |
| Focused security/service tests | 18/18 passed |
| Pilot evidence and internal run seal | exact hash match; valid |

The definitive broker contains 3,000 submitted tasks and is finalized into an immutable Forge run.
There is no `reviewed.jsonl` or release artifact.

## Accepted residual boundary

The external agent framework must run as an identity with no workspace or broker filesystem access.
The worker service account itself can read or modify shared SQLite queue rows if that process is
compromised. This is explicitly disclosed in `SECURITY.md`, `.aiwg/security/threat-model.md`, and
`docs/opaque-service.md`. Deploy an isolated broker or narrow RPC boundary when worker-service
compromise is in scope.

Exact registered source, teacher, benchmark, seed, and lineage identifiers are rejected, but no
static preflight can eliminate every contextual source clue or semantic category inference.
Independent content review remains required.

Internet-facing deployments require TLS, workload identity or mTLS, and ingress per-identity rate
limits. The calibration exercised two FastAPI apps with in-process clients; it did not prove live
TCP, filesystem identity, or systemd lifecycle isolation.

## Final evidence

- Ruff and strict mypy: pass.
- Full suite: 49/49 pass; 83.08% combined coverage.
- Dependency audit: pass.
- `git diff --check`: pass.
- Package/private-material scans: pass.
- Calibration: 3,000 submissions, 1,000 selected lineages, zero deterministic gate failures,
  awaiting independent review.

## Reopen conditions

Reopen this gate if the published commit differs materially from this candidate, the external agent
is granted broker/workspace access, the worker service account is moved inside the adversary model
without an isolated broker, the worker port is exposed without transport/identity/rate controls, or
review/release requirements are bypassed.
