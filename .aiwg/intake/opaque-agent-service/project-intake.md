# Project Intake — Opaque Agent Service and 1,000-Record Calibration

**Document type:** Existing-system architectural extension
**Generated:** 2026-09-25
**Source:** Operator request, existing Governed QA Forge baseline, and AIWG architecture-evolution intake

## Metadata

- **Project:** Governed QA Forge opaque agent service
- **Owner:** Project team
- **Stakeholders:** dataset engineering, agent-framework integrators, security, operations, reviewers, and fine-tuning consumers
- **Current state:** Governed filesystem compiler at version 0.1.0; resident service and calibration corpus are new work
- **Delivery:** Pull request required, CI green, protected `main`

## Problem and outcomes

Agent workers need a small, framework-neutral API for answering corpus tasks without receiving the seed record, source identity, reference answer, verifier contract, category, lineage, quality score, benchmark match, or acceptance result. Exposing those fields lets a worker infer the evaluation target, imitate the reference, or optimize against reward feedback instead of solving the task.

Success requires:

- a worker receives only an opaque task identifier, a self-contained user message, a one-time lease credential, and the response shape;
- submission acknowledges durable receipt but never discloses correctness, selection, reward, provenance, or review state;
- a separately authenticated, loopback-oriented control API creates runs, reports aggregate queue state, and finalizes collected answers through the existing governed compiler;
- queue claims are atomic, leases expire safely, submissions are exactly-once, and bearer secrets are never persisted in plaintext;
- the service can run under hardened systemd units and remains usable by any HTTP-capable agent framework;
- a 1,000-selected-record calibration run exercises 3,000 blind candidate tasks without GPU or network dependencies;
- calibration results remain non-production until an independent reviewer decides every selected row.

## Scope

### Included

- SQLite-backed task broker with atomic leasing and bounded submissions;
- separate worker and control ASGI applications;
- disabled worker OpenAPI/docs endpoints and non-diagnostic receipt responses;
- dedicated environment credentials for each plane;
- service-side mapping from opaque tasks to private seed/candidate coordinates;
- finalization through normal validation, verification, decontamination, coverage selection, and immutable run sealing;
- systemd units, environment template, API contract, runbook, and threat-model updates;
- deterministic, project-authored 1,000-record calibration seed bank and a blind calibration worker that only consumes the worker contract.

### Excluded

- automatic approval of production records;
- sending private source bodies, expected answers, verifier specifications, or gate feedback to workers;
- public exposure of the control API;
- arbitrary code execution, browser tools, or worker-supplied callbacks;
- installing or starting host services as part of the repository change;
- GPU inference for this calibration pass.

## Constraints and security classification

- **Data:** corpus questions and candidate answers are internal until release; provenance and protected benchmarks are confidential control-plane data.
- **Authentication:** independent high-entropy bearer tokens, compared in constant time; task leases use separately generated one-time secrets.
- **Networking:** worker bind is operator-selected; control bind defaults to loopback. TLS termination is an operator responsibility when traffic leaves a trusted host.
- **Persistence:** SQLite WAL for the queue; existing immutable filesystem artifacts remain the release source of truth.
- **Scale:** initial 3,000 task submissions; normal use tens of thousands of tasks on one host before a distributed queue is justified.

## Risks and mitigations

- **Metadata inference:** minimal worker response, random opaque IDs, randomized leasing, no schema discovery, and no correctness response.
- **Cross-plane privilege:** separate processes, tokens, ports, and app factories; worker routes cannot import control responses through HTTP discovery.
- **Task replay:** hash-bound lease secret, expiration, atomic state transition, and one accepted submission.
- **Poisoned answers:** existing content gates and independent verifiers; no direct release from the service queue.
- **Correlated calibration:** deterministic verifier evidence is useful for pipeline calibration but does not replace independent human review.
- **Queue loss or corruption:** SQLite transactions, restricted file permissions, backup guidance, and immutable finalized run artifacts.

## Acceptance criteria

1. Tests prove the worker response contains none of the private seed/provenance/verifier fields.
2. Tests prove submissions receive no pass/fail or score signal.
3. Concurrency tests prove a task cannot be leased or submitted twice.
4. A finalized service run passes the same gates as a CLI/provider run.
5. The calibration pass yields exactly 1,000 selected records from 1,000 lineages and 3,000 submitted candidates.
6. The pilot stops at `awaiting_review`; no release is represented as human-approved.
