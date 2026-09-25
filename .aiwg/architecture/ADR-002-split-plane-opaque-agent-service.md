# ADR-002: Split-plane opaque agent service

- **Status:** Accepted
- **Date:** 2026-09-25

## Context

The compiler must accept answers from arbitrary agent frameworks while withholding private generation context. A role-aware monolithic API would still advertise administrative concepts through OpenAPI, route shape, validation errors, and future shared middleware. A distributed broker is premature for the measured single-host workload.

## Decision

Provide two independently authenticated ASGI applications over one SQLite task broker:

- the worker plane exposes only health, lease, and submit operations; disables OpenAPI and interactive docs; returns a self-contained user message with opaque task and lease credentials; and acknowledges durable receipt without evaluation feedback;
- the control plane creates collection runs, exposes aggregate status, and finalizes complete collections through an injected provider into the existing compiler;
- private seed IDs, lineage, sources, reference answers, verifier specifications, transforms, scores, benchmark matches, and review state never cross the worker API;
- bearer tokens are environment-only and task lease secrets are stored only as SHA-256 digests;
- systemd runs the planes as separate processes and binds control to loopback by default.

## Consequences

- Agent frameworks integrate using two small JSON calls without learning the corpus control model.
- The service adds SQLite and ASGI dependencies but does not replace immutable run/release artifacts.
- Workers receive no adaptive correctness signal, reducing direct reward hacking; this does not prevent inference from the task text itself.
- SQLite constrains horizontal scale; a future broker adapter can replace it behind the same contract.
- Control-plane compromise still exposes private metadata, so host isolation and secret management remain operator responsibilities.
