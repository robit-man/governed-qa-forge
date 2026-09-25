# Test Quality Gate

**Gate:** Construction test quality
**Evaluated:** 2026-09-25T13:03:04-07:00
**Status:** **PASS**

## Summary

| Criterion | Result | Evidence |
|---|---|---|
| Stable test snapshot | PASS | Pre/post source, test, config, lock, requirement, and architecture hashes identical |
| Test pass rate at least 95% | PASS | 39/39 passed on Python 3.13 (100%) |
| Supported Python versions | PASS | 39/39 passed independently on Python 3.11, 3.12, and 3.13 |
| Configured coverage at least 80% | PASS | 84.86% combined; 87.73% statements |
| Branch measurement enabled | PASS | 228/314 branches covered (72.61%) |
| Formatting | PASS | 23 files checked |
| Lint | PASS | No findings |
| Strict typing | PASS | 16 source files; no findings |
| Lock and dependency audit | PASS | Lock current; no known third-party vulnerabilities |
| Package build | PASS | Wheel and sdist built from current stable snapshot |
| Archive/private-material hygiene | PASS | Distribution and Git tracked-file scans clean |
| Built artifact smoke | PASS | Isolated wheel completed demo and anchored verification |
| Offline end-to-end journey | PASS | 8 selected/released records; 9 evidence hashes verified |
| Determinism | PASS | Split/content/transform mapping identical across runs |
| Critical requirements conformance | PASS | Former FR-004 and NFR-006 blockers remediated and directly tested |

**Gate score:** 15/15 criteria passed (100%).

## Closed blocking findings

1. Candidate generation is constrained to 3–10 at schema and provider boundaries.
2. Review exports cannot escape the selected workspace.
3. License/target-use compatibility is checked before generation and release.
4. Human review is mandatory, digest-bound, and restricted to authorized reviewers.
5. Release verification requires an independently retained anchor unless local demo mode is
   explicitly requested.
6. Release and run reads are confined, reject symlinks/unsafe names, and recheck sealed evidence.

## Accepted non-blocking risk

- Branch coverage is 72.61%, below the AIWG 75% “good” guide but above its 65% “acceptable”
  guide. No project-specific branch threshold is configured.
- Production scaffolds target a 500-row governed pilot, while the fast deterministic test fixture
  remains eight records. A real 500-row pilot is a production-readiness activity, not a blocker to
  publishing the compiler.
- Remote GitHub visibility and hosted CI are verified after push and are not established by this
  local gate.

## Decision

The stable snapshot is approved to proceed to commit, public-repository publication, and hosted
CI verification. No local test-quality blocker remains.

Detailed evidence is in `.aiwg/testing/test-execution-report.md` and
`.aiwg/testing/coverage-report.md`.
