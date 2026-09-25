# Architecture Option Matrix — Opaque Agent Service

**Generated:** 2026-09-25

## Priorities

| Criterion | Weight |
|---|---:|
| Context isolation and security | 0.40 |
| Reliability and auditability | 0.30 |
| Agent-framework interoperability | 0.20 |
| Delivery and operating cost | 0.10 |

Non-negotiable: workers cannot receive hidden answer/provenance/evaluation context or correctness feedback, and collected output cannot bypass existing review/release gates.

## Options

| Option | Isolation | Reliability | Interoperability | Cost | Weighted score |
|---|---:|---:|---:|---:|---:|
| Split worker/control ASGI apps + SQLite broker | 5.0 | 4.5 | 5.0 | 4.5 | **4.80** |
| Single role-aware API + SQLite | 3.0 | 4.5 | 5.0 | 5.0 | 4.05 |
| Message broker + multiple services | 5.0 | 5.0 | 3.5 | 2.0 | 4.10 |

## Decision

Use separate ASGI applications backed by one transactional SQLite broker and the existing immutable artifact compiler. The worker app has only health, lease, and submit routes and disables schema discovery. The control app is independently authenticated and intended for loopback binding. This gives a meaningful trust boundary without introducing distributed infrastructure before measured need.

## Rejected alternatives

- **Single API with role checks:** authorization can be correct while route discovery, error types, response models, or future middleware still reveal control-plane concepts to a worker.
- **External message broker now:** strongest horizontal scaling, but expands the trusted computing base and operations burden without evidence that the initial workload needs it.
- **File drop directory:** simple, but weak claim concurrency, replay protection, lease recovery, and framework-neutral response semantics.

## Implementation sequence

1. Add sanitized direct-provider prompts and the broker/provider bridge.
2. Add separate authenticated ASGI apps and CLI launch commands.
3. Add service deployment assets and operator documentation.
4. Add the deterministic calibration workspace/worker.
5. Run all quality gates, execute the 1,000-record pass, and preserve evidence.
