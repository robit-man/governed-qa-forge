# Test Report: Production Reasoning Minimum

**Date:** 2026-09-25  
**Issue:** #4  
**Result:** PASS

## Executed evidence

| Check | Result |
|---|---|
| Ruff formatting | PASS |
| Ruff lint | PASS |
| strict mypy | PASS |
| pytest | 70/70 PASS |
| combined statement/branch coverage | 83.35%; threshold 80% |
| package build | PASS: sdist and Python wheel 0.2.0; private-material distribution scan clean |
| context-boundary focused suite | 26/26 PASS before final boundary additions |

## Requirement coverage

- Exact 20,000/2,000/2,000 boundary accepts; each one-below case rejects.
- Nine categories, a missing difficulty, and a missing AIWG behavior domain reject.
- Production configuration cannot lower the 24,000 total floor.
- Calibration release rejects before review-state evaluation.
- Fixture release requires the internal demo path.
- Every opaque response requires structured derivation plus a final answer.
- Existing private broker schemas receive additive derivation/contract migration; unfinished
  answer-only submissions are requeued.
- Candidate hashes bind the derivation and exact trainer messages.
- Review packets bind displayed content and canonical anchor principles; production requires both
  derivation and semantic-alignment attestations.
- Trainer files contain messages only; AIWG/source governance stays in bound sidecars.
- Framework names and registered anchor/source identifiers reject at the worker boundary.
- Behavior-anchor registries must exactly match the code-owned profile bound to hashed canonical
  AIWG artifacts, even if a mutable snapshot digest is also updated.
- Schema-1.0 candidates/releases remain audit-readable but cannot be promoted.
- Production policy is exercised through both build and release-verification integration paths.

## Known warning

FastAPI's test client reports the existing Starlette `httpx` deprecation warning. It does not
affect the executed contract and remains outside this change's acceptance boundary.

## Package hashes

```text
d78ad6ab82198507ba0341f17e3d2743e9b2cb6fff04688d029c4c2e87511411  governed_qa_forge-0.2.0-py3-none-any.whl
73f67cc2cd26636bac150eb29719469adb63ef969fc4e82eddce475dc0a52a2e  governed_qa_forge-0.2.0.tar.gz
```
