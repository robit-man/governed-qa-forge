# Coverage Report

**Executed:** 2026-09-25
**Command:** `uv run pytest --cov=qaforge --cov-branch --cov-report=term-missing`
**Result:** 39 passed; configured global `fail_under = 80` passed

## Summary

| Metric | Covered | Total | Coverage | Assessment |
|---|---:|---:|---:|---|
| Statements | 1,173 | 1,337 | 87.73% | Passes NFR-005's 80% line target |
| Branches | 228 | 314 | 72.61% | Acceptable; below the AIWG 75% “good” guide |
| Combined | 1,401 | 1,651 | 84.86% | Passes the configured coverage.py gate |
| Missing statements | 164 | 1,337 | 12.27% | Concentrated in CLI and failure handling |
| Missing branches | 86 | 314 | 27.39% | Most remaining gaps are negative paths |

Coverage.py uses statement/line coverage for NFR-005. With branch measurement enabled, its
combined figure is the value compared to the configured `fail_under` threshold.

## File-level results

| File | Statements | Statement % | Branches | Branch % | Combined % | Risk note |
|---|---:|---:|---:|---:|---:|---|
| `__init__.py` | 5 | 100.00 | 0 | 100.00 | 100.00 | None |
| `__main__.py` | 2 | 0.00 | 0 | 100.00 | 0.00 | Module entry shim not invoked directly |
| `cli.py` | 112 | 58.93 | 10 | 60.00 | 59.02 | Success journeys improved; error handlers remain |
| `dedup.py` | 112 | 98.21 | 34 | 94.12 | Strong |
| `errors.py` | 5 | 100.00 | 0 | 100.00 | None |
| `fixtures.py` | 32 | 96.88 | 4 | 75.00 | Strong |
| `io.py` | 110 | 85.45 | 28 | 75.00 | 83.33 | Malformed and symlink edge paths remain |
| `models.py` | 251 | 98.01 | 20 | 75.00 | 96.31 | Strong schema coverage |
| `pipeline.py` | 151 | 86.75 | 46 | 69.57 | 82.74 | Review-import rejection matrix incomplete |
| `providers.py` | 85 | 87.06 | 24 | 66.67 | 82.57 | HTTP/stream/size/count errors remain |
| `release.py` | 205 | 84.39 | 92 | 69.57 | 79.80 | Several defensive verifier branches remain |
| `selection.py` | 55 | 83.64 | 18 | 66.67 | 79.45 | Impossible floors and utility paths remain |
| `splitter.py` | 10 | 100.00 | 4 | 100.00 | 100.00 | Strong |
| `transforms.py` | 13 | 76.92 | 2 | 50.00 | 73.33 | Overflow and unknown-transform paths remain |
| `validation.py` | 64 | 89.06 | 12 | 83.33 | 88.16 | Numeric/JSON/regex failure paths remain |
| `workspace.py` | 125 | 92.00 | 20 | 60.00 | 87.59 | Malformed registries and reviewer errors remain |

## Highest-value additions

1. Exercise every CLI `_fail` path and the module entry shim.
2. Add malformed/oversized provider response, timeout, HTTP error, and wrong-count tests.
3. Add duplicate/unknown/pending/incomplete review-import cases.
4. Exercise impossible coverage floors, lineage-cap skips, and utility ranking.
5. Add the remaining release verifier cases: invalid row, duplicate record/content, content hash,
   semantic binding, review binding, split leakage, and manifest count/total drift.
6. Add invalid transform and transform-count overflow tests.

## Coverage gate decision

The project coverage gate passes with 87.73% statements and 84.86% combined coverage. Branch
coverage is adequate for this alpha release but remains the principal non-blocking quality debt.
