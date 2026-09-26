# Operational Readiness Review — Opaque Agent Service

**Reviewed:** 2026-09-25

**Candidate:** uncommitted `feat/opaque-agent-service-pilot` worktree over `50b0cf8`

**Local technical gate:** **GO TO PR**

**Installed-service gate:** **CONDITIONAL — deployment smoke pending**

**Corpus-use gate:** **HOLD — independent review pending**

## Decision statement

The service extension is locally ready for immutable pull-request review. It exposes a minimal,
feedback-free worker API and a separately authenticated control API; seals source inputs before
collection; sends only transformed question text to workers; rejects exact private identifiers;
and routes completed answers back through the existing validation, verification, decontamination,
selection, review, and release controls.

The technical 1,000-record calibration passed, but it is not a production dataset or an OS-level
deployment proof. Its selected records remain at `awaiting_review`, and no release exists.

## Readiness dashboard

| Domain | Status | Evidence |
|---|---|---|
| Requirements | PASS locally | FR-001..019 and NFR-001..013 mapped in the current regression report |
| Format/lint/types | PASS | Ruff and strict mypy clean |
| Automated tests | PASS | 49/49; 83.08% combined coverage |
| Dependencies/package | PASS | clean dependency audit; wheel/sdist include deployment assets |
| HTTP opacity | PASS | minimal lease, structured derivation/final-answer submission, no reward feedback, no worker OpenAPI |
| Input integrity | PASS | collection-time hashes, task-binding recheck, post-generation manifest match |
| Citation integrity | PASS | untrusted provider citation claims are discarded and citation-required work fails closed |
| Queue consistency | PASS | atomic random lease, digest-only one-time credential, exactly-once response, restart reconciliation |
| Resource boundaries | PASS locally | 64 KiB request cap, 16,384-character projected-question cap, 128-request server concurrency cap |
| Systemd design | PASS-I | separate accounts/env files, control-only corpus access, workspace-local shared broker, hardening directives |
| Installed systemd smoke | PENDING | no daemon was installed or started on this development host |
| 1,000-record calibration | PASS TECHNICAL | 3,000 tasks, 1,000 unique selected lineages, all deterministic gates pass |
| Independent record review | HOLD | no review decisions exist |
| Production model quality | NOT DEMONSTRATED | deterministic teacher/solver only; no live open-ended model teacher |

## Operating boundary

The worker and control apps are separate processes with independent bearer tokens. The worker sees
only an opaque task ID, one-time lease token, expiry, and a single user message. It receives no
source, seed, lineage, taxonomy, reference answer, verifier, score, benchmark, selection, or review
fields. Submission success is only `{"status":"recorded"}`.

The documented deployment uses `qaforge-agent` and `qaforge-control` accounts. Corpus inputs are
control-only; `.service/service.sqlite3` is shared for queue coordination. Therefore the opacity
boundary is the HTTP caller, not arbitrary code execution as `qaforge-agent`. Deploy a minimal
external broker or RPC boundary if worker-service compromise must be contained.

## Calibration result

The definitive runtime workspace at `/srv/question_stack/pilot-workspace` is ignored by Git. It
contains 3,000 raw/evaluated records and 1,000 selected records across 10 balanced categories. All
selected lineages are unique; splits are 910/48/42; all mandatory deterministic gates pass. The
run has neither review decisions nor release artifacts. Hashes are retained in the governed
calibration evidence file.

The command exercised two application instances through in-process HTTP clients. A deployment
operator must still smoke-test the wheel-installed unit locations, filesystem ownership, both TCP
listeners, restart behavior, TLS/ingress, and external-agent identity before production service.

## Deployment and rollback

1. Install only a reviewed wheel built by green hosted CI.
2. Generate independent tokens in the two mode-0600 env files; placeholder values fail startup.
3. Keep the control plane loopback-only and expose the worker through authenticated, rate-limited
   TLS ingress when remote access is required.
4. Run the documented unit/permission smoke and a disposable collection before admitting real
   work.
5. On failure, stop both units, retain the workspace and broker for audit, quarantine any affected
   run, and deploy a new version. Do not overwrite run or release artifacts.

## Exit criteria

- Commit and push the exact candidate through the PR-required workflow.
- Obtain green hosted matrix, package, dependency, and secret-scanning checks.
- Perform an installed split-process/systemd smoke in the target environment.
- Complete authorized independent review of the calibration before any fine-tuning use.
- Run a separately governed open-ended pilot before claiming production teacher quality.
