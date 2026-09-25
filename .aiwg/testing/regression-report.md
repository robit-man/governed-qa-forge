# Regression and Publication Readiness — Opaque Service Extension

**Project:** Governed QA Forge 0.1.0

**Evaluated:** 2026-09-25

**Branch:** `feat/opaque-agent-service-pilot`

**Baseline:** `50b0cf8` (`origin/main`)

**Scope:** opaque worker/control APIs, service deployment assets, direct-provider context minimization,
calibration generator, and the existing compiler/review/release flow.

## Decision

- **Local regression gate: PASS.** The extension and pre-existing compiler tests pass.
- **Pull-request gate: GO.** The candidate still requires an immutable commit and hosted CI.
- **Production corpus gate: HOLD.** The 1,000-record technical calibration is awaiting independent
  record review and did not exercise a live model teacher or split-process/systemd deployment.

## Executed evidence

| Gate | Result |
|---|---|
| Lockfile | `uv lock --check` passed; 62 packages resolved |
| Formatting and lint | 26 files formatted; Ruff passed |
| Strict typing | mypy passed across 18 source modules |
| Tests | 49/49 passed on local Python 3.13.12 |
| Coverage | 83.08% combined branch/statement coverage; configured 80% floor passed |
| Dependencies | `pip-audit` found no known third-party vulnerabilities |
| Package | wheel and sdist built; systemd units and split env templates are present in both |
| Wheel SHA-256 | `5bfd6c98eabcd3f70c383b1478ad16c2b790713682fd3fef1500cad44e1162f1` |
| sdist SHA-256 | `9cfdee35f11ec92250dbddf76c0c7e2f24c5b52373db08f83abe06c46fc6b341` |
| Diff hygiene | `git diff --check` passed; runtime pilot workspaces are ignored |
| Systemd static parse | Units parsed; the development host reported only its expected missing `/opt/qaforge` executable and unrelated unreadable host units |

The archive hashes identify an uncommitted local candidate and must be regenerated from the final
reviewed commit if release provenance is required.

## Calibration evidence

The definitive in-process HTTP/broker calibration completed through the opaque worker contract:

- 3,000 submitted and raw candidates;
- 0 validation failures, verifier failures, or contamination rejections;
- 1,000 selected records and 1,000 unique lineages;
- 100 selected records in each of 10 categories;
- splits of 910 train, 48 validation, and 42 test;
- immutable Forge stage `awaiting_review`;
- no `reviewed.jsonl` and no release directory.

Exact artifact hashes are recorded in
`.aiwg/datasets/opaque-calibration-1000/evidence.md`. The pilot used two FastAPI test clients in one
Python process. It validates route separation, outbound payload minimization, queue behavior, input
sealing, normal compiler gates, and scale at 3,000 tasks; it does not validate TCP, TLS, separate
Unix identities, or systemd lifecycle behavior.

## Requirement traceability

| Requirement | Status | Evidence |
|---|---|---|
| FR-001..FR-014 | PASS | Existing compiler, provider, governance, review, release, and CLI regression tests remain green |
| FR-015 opaque worker API | PASS | worker schema absent; minimal lease body; non-diagnostic receipt; private identifier and prompt leakage regressions |
| FR-016 control API | PASS | independently authenticated create/status/finalize routes and protected OpenAPI schema |
| FR-017 atomic queue | PASS | concurrent unique leases, one-time submission, expiring digest-only lease credentials |
| FR-018 deployment contract | PASS-I | separate CLI apps, accounts, env files, ports, hardening directives, and framework-neutral HTTP documentation; installed-service smoke pending |
| FR-019 1,000-record calibration | PASS | exact completed counts and fixity above; review/release intentionally withheld |
| NFR-001..NFR-008 | PASS | Existing deterministic, confinement, package, credential, and release-integrity regression remains green |
| NFR-009 feedback-free responses | PASS | no score, correctness, provenance, verifier, selection, benchmark, or review fields/errors |
| NFR-010 split planes | PASS-I | separate app factories, entry points, tokens, env files, users, and route tables; OS deployment not executed |
| NFR-011 secret handling | PASS | environment-only bearer secrets, placeholder rejection, constant-time digest comparison, lease digests only |
| NFR-012 consistency/restart | PASS | transactional claims/submits, sealed input/task binding, and unstarted-finalization recovery test |
| NFR-013 bounded/confined service | PASS | broker path confinement, projected-question preflight, 64 KiB pre-parse body cap, and Uvicorn concurrency cap |

`PASS-I` means implementation plus static/contract evidence; `PASS` includes executed behavior.

## Residual risks and re-entry criteria

1. The external agent framework must remain outside the broker filesystem group. A compromise of
   the worker service account can inspect or alter shared SQLite rows; use an isolated broker/RPC
   boundary when that threat is in scope.
2. Exact registered source, teacher, benchmark, seed, and lineage IDs are blocked in outbound
   questions, but contextual source clues and category inference require content review.
3. Ingress must provide TLS, workload identity or mTLS, and per-identity rate limiting when exposed
   beyond a trusted host.
4. Independent review is mandatory before release or fine-tuning use.
5. Commit the candidate, run hosted Python 3.11/3.12/3.13 and security CI, review the diff, and merge
   through the configured PR policy before publication.
