# Coverage Report

**Executed:** 2026-09-25

**Command:** `uv run pytest --cov=qaforge --cov-report=term-missing --cov-branch`

**Result:** 49 passed; configured global `fail_under = 80` passed

## Summary

| Metric | Covered | Total | Coverage | Assessment |
|---|---:|---:|---:|---|
| Statements | 1,725 | 2,013 | 85.69% | Passes NFR-005's 80% target |
| Branches | 338 | 470 | 71.91% | Measured; no separate project threshold |
| Combined | 2,063 | 2,483 | 83.08% | Passes configured coverage.py gate |

Coverage.py compares the combined measured opportunities to `fail_under = 80`. The service module
is covered at 82% combined, including the critical opaque payload, authentication, queue,
input-sealing, identifier-screening, size-bound, and restart-recovery paths.

## Highest-value future additions

1. Exercise the remaining CLI server startup and error-reporting branches without starting live
   listeners.
2. Add recovery probes for both completed-artifact and deliberately partial-artifact crash states.
3. Exercise malformed chunked request framing and more SQLite operational-error paths.
4. Retain the existing release-verifier and provider negative-path backlog.

## Decision

The coverage gate passes. Branch coverage remains non-blocking quality debt, with the highest-risk
service behaviors covered by direct regression tests.
