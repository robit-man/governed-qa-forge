# Test Execution Report

**Project:** Governed QA Forge
**Executed:** 2026-09-25T13:03:04-07:00
**Scope:** Python package, CLI, distributions, dependency state, deterministic release journey
**Evaluator:** AIWG test-execution lane
**Overall result:** **PASS**

## Evidence snapshot

The final lane hashed all Python source, tests, configuration, lockfile, README, requirements, and
architecture before execution and compared the same set after execution. The snapshots were
identical, proving that the reported run used a stable tree.

| Input | SHA-256 |
|---|---|
| `pyproject.toml` | `adb615a972d77b06219e15842132d00cd5ea0813db64f551d37649f563630925` |
| `uv.lock` | `969f987203dbb9335e13728d41b042e9a544f5b36505a1cb1cff21b088b2d9d5` |
| `README.md` | `10acd4ef9af8a6f6151c1fd2ce4c740a4d8da18fbe46c2cbc9c85b1b4add7e3e` |
| System requirements | `5bbcadc040b079e1ed4fc8624be2f98274d492eebd6cf000f1268aeda5f0d27a` |
| Architecture decision | `61c9a684fc0271031e0a2ab40723e0bd5e6cc64d1574d9700797ec3410c6a93c` |
| Built wheel | `1b0f72d00721f4775a6461a6ba483f7785bd2bfeeab8f8af9f7500a6d1e70a04` |
| Built sdist | `943d22523bc405e84998b4435366f79a536918faff5a8d976add012d19684ab9` |

Primary environment: Linux, Python 3.13.12, pytest 9.1.1, pytest-cov 6.3.0, Ruff
0.16.9, mypy 1.20.2, build 1.6.1, pip-audit 2.10.1, uv 0.11.3. Test discovery
found 39 tests in seven test modules.

## Command results

| Gate | Exact command | Result | Evidence |
|---|---|---|---|
| Lock consistency | `uv lock --check` | PASS | 58 packages resolved; exit 0 |
| Test discovery | `uv run pytest --collect-only -q` | PASS | 39 tests collected; exit 0 |
| Format | `uv run ruff format --check src tests` | PASS | 23 files already formatted |
| Lint | `uv run ruff check src tests` | PASS | All checks passed |
| Types | `uv run mypy src` | PASS | Strict mypy found no issues in 16 source files |
| Tests + branch coverage | `uv run pytest --cov=qaforge --cov-branch --cov-report=term-missing` | PASS | 39/39 passed; configured 80% gate passed; 84.86% combined |
| Python 3.11 compatibility | isolated Python 3.11 editable install, then `pytest -q` | PASS | 39/39 passed |
| Python 3.12 compatibility | isolated Python 3.12 editable install, then `pytest -q` | PASS | 39/39 passed |
| Python 3.13 compatibility | primary full-coverage execution | PASS | 39/39 passed |
| Dependency audit | `uv run pip-audit` | PASS | No known vulnerabilities; local project skipped as unpublished |
| Package build | `uv build` | PASS | Wheel and sdist built from current tree |
| Archive hygiene | inspect `tar -tzf` and `unzip -Z1`, reject private patterns | PASS | 38 sdist and 21 wheel entries; no AIWG state, env files, runtime corpora, PDFs, or research sources |
| Tracked-file hygiene | scan `git ls-files` for private material | PASS | No PDFs, extracted research text, `.env`, runs, or releases tracked |
| Source CLI demo | `uv run qaforge demo /tmp/.../final2-source-workspace` | PASS | 8 selected; 9 evidence files checked; 8 records; no failures |
| Anchored verification | `qaforge verify-release ... --expected-sha256 8475...2ddc` | PASS | Anchor matched; no failures |
| External fixity | `sha256sum -c SHA256SUMS` inside the release | PASS | All nine evidence artifacts `OK` |
| Built-wheel demo | isolated install of the new wheel followed by `qaforge demo` | PASS | 8 selected; anchored self-check passed |
| Built-wheel verify | isolated wheel `verify-release` with anchor `266c...cdd9` | PASS | 9 files and 8 records checked; no failures |
| Determinism | repeat demo and compare sorted split/content/transform mappings | PASS | Mappings were byte-identical |

The source demo emitted `train.jsonl`, `validation.jsonl`, `test.jsonl`, `manifest.json`,
`DATASHEET.md`, `croissant.json`, `provenance.jsonld`, `generation-run-manifest.json`,
`rejection-ledger.jsonl`, and `SHA256SUMS`. Its raw corpus contained 24 rows, exactly three per
seed. Every row had a complete teacher/prompt/source/parent/depth/seed-transform provenance chain,
and every lineage occurred in one split only. Production scaffolds now target a 500-record pilot;
the deterministic demo deliberately remains eight records.

## Closed blockers from the first execution

- **FR-004:** `GenerationConfig` and provider boundaries now enforce 3–10 candidates; tests cover
  2, 3, 10, and 11.
- **NFR-006:** review export is now checked with `ensure_within`; a path-escape regression test
  passes.
- **CLI documentation:** `doctor`, `status`, and `generate` accept the documented positional
  workspace path, covered through `CliRunner`.
- **Authorization compatibility:** source license compatibility and source/teacher target-use
  compatibility are now explicit doctor gates with negative tests.
- **Release integrity:** review decisions are digest-bound, reviewers are registry-authorized,
  run artifacts are sealed, release verification requires an external root digest by default,
  and checksum names are path-confined.

## Requirements traceability

| Requirement | Status | Executed or inspected evidence |
|---|---|---|
| FR-001 versioned input validation | PASS | Pydantic version literals, doctor validation, valid fixture test, and schema boundary tests. |
| FR-002 authorization and compatibility | PASS | Deny-by-default, blocked source, incompatible license, and incompatible target-use tests. |
| FR-003 lineage split before generation | PASS | Splitter test, E2E inspection, and deterministic replay. |
| FR-004 configurable 3–10 generation | PASS | Boundary tests plus 24-row/8-seed runtime evidence. |
| FR-005 candidate provenance fields | PASS | All 24 raw rows passed the complete-provenance query. |
| FR-006 validators | PASS | E2E gates, secret/PII negative test, and inspected content/risk/evidence/prompt-injection gates. |
| FR-007 semantic binding and independent verifiers | PASS | Transform-binding negative test and five verifier parameterizations, including bounded regex. |
| FR-008 layered decontamination | PASS | Exact/cross-lineage and protected-benchmark tests plus indexed lexical/semantic implementation. |
| FR-009 quality/eight-dimension coverage and caps | PASS | Eight-dimension features, configurable floors, lineage-cap test, and E2E selection. |
| FR-010 digest-bound authorized review | PASS | Digest checks, reviewer registry checks, mandatory review schema, and E2E review/release. |
| FR-011 fail-closed release | PASS | Immutability, fixity tamper, sealed-selection tamper, anchor, and below-target tests. |
| FR-012 release artifacts and SHA-256 | PASS | All named outputs emitted; internal and external fixity checks passed. |
| FR-013 offline demo and remote provider | PASS | Offline fixture release and hardened mock OpenAI-compatible provider tests. |
| FR-014 CLI journeys | PASS | Command exposure, demo/verify, and documented positional doctor/status/generate tests. |
| NFR-001 deterministic splits/content hashes | PASS | Repeat workspaces produced identical split/content/transform mappings. |
| NFR-002 no required infrastructure/network | PASS | Deterministic source and installed-wheel demos completed without GPU, container, database, or teacher endpoint. |
| NFR-003 credential/content controls | PASS | Dedicated env-name validation, URL/DNS restrictions, reference-answer exclusion, and maintained secret/PII candidate gates. |
| NFR-004 indexed duplicate lookup | PASS | Fingerprint index uses exact and banded-LSH buckets; no unconditional candidate all-pairs loop. |
| NFR-005 Python/typing/coverage | PASS | 39 tests passed on 3.11, 3.12, and 3.13; strict mypy passed; 87.73% statement coverage. |
| NFR-006 workspace-confined writes | PASS | Path, run-ID, and review-export traversal tests pass. |
| NFR-007 public-artifact exclusions | PASS | Git tracked-file scan, ignore rules, sdist scan, and wheel scan are clean. |
| NFR-008 externally anchored verification | PASS | Missing-anchor and anchor-tampering tests plus two successful independently supplied anchors. |

## Non-blocking observations

- Branch coverage is 72.61%. This exceeds the AIWG `test-coverage` skill's 65% “acceptable”
  guide but is below its 75% “good” guide; the project does not define a separate branch gate.
- CLI error handlers, impossible selection floors, invalid transforms, and several release refusal
  branches remain the highest-value coverage additions.
- The production scaffold now enforces a 500-row pilot target, but this lane executed the 8-row
  deterministic fixture rather than a live 500-row teacher run. Run that pilot before declaring
  production corpus throughput readiness.
- `pip-audit` correctly skipped the local unpublished package itself; all resolved third-party
  packages reported no known vulnerabilities.
- Hosted-repository visibility and remote CI are delivery checks performed after commit/push,
  outside this local execution report.

## Decision

The remediated, stable snapshot passes the local test-quality gate. No test-execution blocker
remains for commit and publication.
