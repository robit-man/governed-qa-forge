# Solution Profile — Opaque Agent Service

**Generated:** 2026-09-25

## Selection

- **Profile:** Production service extension with calibration-only first run
- **Security posture:** Strong
- **Reliability target:** atomic at-least-once leasing with exactly-once accepted submission and fail-closed finalization
- **Process rigor:** Full architecture, threat model, tests, deployment hardening, runbook, and pilot evidence

The service is production-shaped because it crosses an adversarial agent trust boundary and protects evaluation inputs. The generated calibration corpus is not production-approved until independent review is complete.

## Quality targets

- Python 3.11–3.13 and strict typing;
- no worker-plane OpenAPI or documentation route;
- no private metadata in worker task or receipt schemas;
- SQLite transactional tests plus worker/control API integration tests;
- existing repository coverage remains at or above 80%;
- 1,000 selected records and zero failed deterministic verification gates in the calibration run;
- explicit evidence for selected counts, category balance, rejection reasons, and pending review.

## Operations targets

- loopback defaults and separate worker/control ports;
- graceful restart with leases recoverable after expiration;
- health endpoints that disclose only readiness state;
- JSON access logs may be supplied by the supervisor, with authorization headers excluded;
- backup the broker before maintenance and retain finalized immutable run directories;
- systemd sandboxing, private umask, fixed service identity, and writable paths limited to service state.

## Evolution triggers

- Move from SQLite to a network queue only after measured single-host contention or multi-host requirements.
- Add mTLS or workload identity before exposing the worker plane across an untrusted network.
- Add signed review attestations before treating service-originated corpora as production releases.
- Add GPU-backed workers only through the host GPU broker and after a separate capacity/security review.
