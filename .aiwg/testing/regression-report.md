# Final Regression and Publication Readiness Audit

**Project:** Governed QA Forge 0.1.0
**Evaluated:** 2026-09-25T13:03:08-07:00
**Branch:** `feat/end-to-end-governed-qa-forge`
**Git baseline:** `dbd3182bc67893f5fb47fe9acc23b11d092382af` (`origin/main`)
**Scope:** requirements, source, tests, CLI/docs, offline release flow, distributions, research
boundary, and GitHub publication state

## Decision

- **Local regression gate: PASS.** No open implementation regression or Critical/High/Medium
  security finding was found in the final worktree.
- **Alpha package candidate: GO to commit and pull request.** The exact local tree is suitable for
  immutable review and hosted CI.
- **Public 0.1.0 publication: NO-GO at this checkpoint.** The candidate is uncommitted and
  unpushed, there is no pull request or hosted CI result for it, public `main` still contains only
  the research bootstrap, and `main` is not protected.
- **Production corpus operation: not yet qualified.** The deterministic eight-row demo is proven;
  a real authorized 500–1,000-record calibration pilot has not been run.

The NO-GO decision is caused by delivery state, not by a failing local code, package, security, or
documentation gate.

## Final executed evidence

| Gate | Result | Evidence |
|---|---|---|
| Locked environment | PASS | `uv sync --locked --extra dev`; 58 packages resolved, 57 checked |
| Formatting | PASS | `uv run ruff format --check src tests`; 23 files formatted |
| Lint | PASS | `uv run ruff check src tests`; no findings |
| Strict typing | PASS | `uv run mypy src`; 16 source files, no findings |
| Tests | PASS | 39/39 on Python 3.11, 3.12, and 3.13 |
| Statement coverage | PASS | 1,173/1,337 = 87.73%; exceeds the 80% requirement |
| Branch coverage | OBSERVED | 228/314 = 72.61%; measured but no separate project threshold |
| Combined coverage.py result | PASS | 84.86%; configured `fail_under = 80` passed |
| Dependency audit | PASS | `pip-audit`: no known vulnerabilities; local unpublished project was the only skip |
| Security review | PASS WITH DOCUMENTED RESIDUAL RISKS | 0 open Critical/High/Medium/Low findings; all QAF-SEC-001..011 closed |
| Build | PASS | wheel and sdist rebuilt from the final source tree |
| Python 3.11 wheel smoke | PASS | fresh venv installed the final wheel, completed demo, and verified an anchored release |
| Source offline demo | PASS | 24 raw, 8 selected, 8 released; 9 evidence files checked |
| Determinism probe | PASS | two independent demos produced identical 24-row lineage/split/question/answer/content-hash signatures |
| Docs/CLI contract | PASS | documented command names and positional arguments match CLI help and executed flows |
| Markdown links | PASS | 49 public-candidate Markdown files; 23 local links; 0 broken |
| Public candidate secret scan | PASS | checksum-verified gitleaks 8.30.1 scanned the exact candidate tree; no leaks |

Final distribution digests:

```text
1b0f72d00721f4775a6461a6ba483f7785bd2bfeeab8f8af9f7500a6d1e70a04  governed_qa_forge-0.1.0-py3-none-any.whl
943d22523bc405e84998b4435366f79a536918faff5a8d976add012d19684ab9  governed_qa_forge-0.1.0.tar.gz
```

These hashes identify uncommitted local build outputs, not publishable provenance. Rebuild and
record hashes from the committed release candidate.

## CLI and documentation regression

The actual CLI exposes `init`, `doctor`, `generate`, `review-export`, `review-import`, `review-all`,
`release`, `verify-release`, `status`, and `demo`. README and operations-guide commands use the
same command names, positional workspace arguments, run ID ordering, and anchor options.

Executed documentation journeys:

1. `qaforge demo WORKSPACE`, `qaforge status WORKSPACE`, and `qaforge doctor WORKSPACE` succeeded.
2. `qaforge verify-release WORKSPACE 0.1.0` failed with `missing-external-anchor` as required.
3. Verification with a wrong 64-hex digest failed with `external-anchor`.
4. Verification with an independently computed SHA-256 of `SHA256SUMS` succeeded.
5. The final wheel repeated the complete demo and anchored verification on Python 3.11.15.

The README accurately scopes the built-in remote provider to answer generation over compiler-owned,
meaning-preserving question transforms. It does not claim arbitrary model-generated question
evolution. It also states that a production scaffold targets a 500-row pilot and must be populated
with authorized sources, reviewers, teachers, and seeds before generation.

## Coverage-cube regression

`coverage_features()` emits all eight required dimensions:

1. category;
2. domain;
3. task;
4. reasoning;
5. answer form;
6. difficulty;
7. evidence mode;
8. risk.

The demo config declares floors in every dimension, selection applies those floors, and the release
manifest records both the observed `coverage_counts` and the full `quality_policy.coverage_floors`.
The eight-row release satisfied every configured floor. Release construction also enforces
`target_size`; a review rejection cannot silently produce an undersized release.

## Release-anchor and tamper regression

The release command produces a digest of `SHA256SUMS`, while normal verification requires that
digest from a separately retained channel. `--allow-unanchored` remains explicitly scoped to local
demos. Regression coverage proves:

- missing and wrong anchors fail;
- the correct external anchor passes;
- modified release data fails fixity;
- unsafe or extra checksum names fail;
- reviewed-row drift from the sealed selection fails before release;
- a protected benchmark cannot be inserted after review;
- run and release directories cannot be overwritten.

## Distribution and public-repository boundary

The final wheel contains only `qaforge` modules, distribution metadata, and the license. The final
sdist contains the declared package source, tests, public docs/examples, project metadata, lockfile,
and standard Hatch-generated metadata. Neither archive contains `.aiwg`, `.github`, provider
state, environment files, PDFs, extracted research text, runtime runs/releases, generated corpora,
or host-absolute paths.

The exact proposed Git tree was checked through Git's ignore engine:

- `.env` and `.env.*` are excluded; `.env.example` is retained;
- runtime `runs/`, `releases/`, and `demo-workspace/` are excluded;
- `.aiwg/research/sources/REF-*.pdf` and `.aiwg/research/working/` are excluded;
- `.aiwg/research/sources/INDEX.md` is retained;
- no PDF, extracted full text, private runtime corpus, or `.env` appeared in tracked plus
  non-ignored candidates.

All 18 locally acquired PDFs exist and match `.aiwg/research/fixity-manifest.json`. The public
source register links to the upstream papers without publishing those payloads. Research-control
digests observed in this audit were:

```text
8fb80d6fe0b029b228f0308e6ff2f65987992f8c23881c4bc92f0a0e7f754c16  sources/INDEX.md
72ac05a13ab1f5d3fc3dea40efcc9b298ef83fbe0ba5d9ecd0082c0ea9e3f72d  fixity-manifest.json
692ccc49c91cb2d3f50055d6d95875dc6c2e3254dace0b00b2dc00dd690a5657  research audit
3e8565b9ffaf39e86f1f7fd08934cc07babef420310bfbd938ca93ac0ad9b312  design synthesis
```

## Requirement-to-test traceability

Status `PASS-I` means executable evidence plus implementation inspection; `PASS-E` means direct
executed evidence. No requirement is contradicted by the final local candidate.

| Requirement | Status | Final evidence |
|---|---|---|
| FR-001 versioned input validation | PASS-I | Pydantic schemas use `schema_version = 1.0`; doctor and invalid split-schema paths execute |
| FR-002 authorization and compatibility | PASS-E | deny-by-default teacher, blocked source, incompatible release license, and incompatible teacher use tests; every non-approved status, including `expired`, fails authorization |
| FR-003 lineage split before generation | PASS-E | deterministic splitter test, E2E family isolation, repeat-demo signature comparison |
| FR-004 configurable 3–10 generation | PASS-E | boundary tests reject 2/11 and accept 3/10; demo creates 3 candidates per seed |
| FR-005 candidate provenance | PASS-I | raw rows and sealed run manifest retain teacher/model, terms snapshot, prompt hash, sampling, source IDs, parents, and depth |
| FR-006 validators | PASS-E | integrated schema/content/risk/evidence gates plus negative secret/PII test |
| FR-007 semantic binding and five verifiers | PASS-E | question-binding negative test and parametrized exact/numeric/bounded-regex/JSON/citation contracts |
| FR-008 layered decontamination | PASS-E | exact/cross-lineage and protected-benchmark tests; indexed lexical/semantic implementation; release-time recheck |
| FR-009 eight-dimensional selection | PASS-E | demo floors and release counts cover all eight dimensions; lineage cap test; target size enforced |
| FR-010 digest-bound authorized review | PASS-I | content digest binding, complete decisions, reviewer registry/category authorization, and release-time revalidation |
| FR-011 fail-closed release | PASS-E | immutability, reviewed-content tamper, fixity tamper, missing anchor, and undersized-review tests |
| FR-012 complete release evidence | PASS-E | split JSONL, manifest, datasheet, Croissant, PROV, rejection ledger, generation manifest, and SHA-256 inventory produced and verified |
| FR-013 offline and remote providers | PASS-E | deterministic source/wheel demos and mocked strict-JSON OpenAI-compatible provider test |
| FR-014 CLI journeys | PASS-E | command-help audit plus CLI demo/verify/doctor/generate/status tests and executed README flow |
| NFR-001 deterministic content | PASS-E | repeat demos produced identical lineage/split/question/answer/content hashes |
| NFR-002 infrastructure-free base | PASS-E | installed-wheel deterministic runtime completed without model, GPU, container, DB, or network call |
| NFR-003 credential and content controls | PASS-E | restricted env/endpoint/DNS tests, runtime secret/PII tests, manifest exclusion, and clean gitleaks scan |
| NFR-004 indexed near-duplicate lookup | PASS-I | exact and LSH-band indexes avoid unconditional all-pairs comparison; functional dedup tests pass |
| NFR-005 Python, typing, coverage | PASS-E | 39 tests on Python 3.11/3.12/3.13, strict mypy, 87.73% statements; hosted matrix still required for publication |
| NFR-006 workspace-confined writes | PASS-E | path, run-ID, and review-export escape tests; release/checksum confinement security probes |
| NFR-007 public exclusions | PASS-E | exact candidate-tree, archive, ignore-engine, and secret scans; public repository contains no acquired payloads |
| NFR-008 external release anchor | PASS-E | missing/wrong anchor failures and correct-anchor success in tests and manual CLI probe |

## Exact remaining defects and release blockers

### PUB-001 — No immutable release-candidate commit (Blocking)

`HEAD`, local `main`, and `origin/main` are all `dbd3182`. The implementation, tests, docs, CI, and
AIWG delivery artifacts are modified or untracked. The successful local evidence therefore cannot
yet be tied to a Git commit, reviewed diff, or reproducible checkout.

### PUB-002 — Required PR and hosted CI do not exist (Blocking)

`.aiwg/aiwg.config` sets `delivery.mode = pr-required` and `require_ci_green = true`. GitHub reports
zero pull requests and zero workflow runs. The configured Python 3.11/3.12/3.13 and gitleaks jobs
must pass on the exact pushed commit.

### PUB-003 — `main` is not protected (Blocking)

The GitHub branch-protection endpoint returns HTTP 404 `Branch not protected`. This violates step
5 of `.aiwg/deployment/release-plan.md` and leaves the required review/CI policy unenforced.

### PUB-004 — Public `main` does not contain the candidate (Blocking)

The only remote branch is `main` at `dbd3182`, containing the research bootstrap rather than the
application candidate. Public visibility is confirmed, but implementation publication and
post-merge verification have not occurred.

### OPS-001 — Production-scale pilot not demonstrated (Operational limitation)

The production scaffold defaults to `target_size: 500`, but the observed run is an eight-row
deterministic fixture. No authorized real-teacher run, 500–1,000 accepted-row calibration,
rate-limit/retry exercise, interruption recovery, or several-thousand-row resource profile exists.
This is not a blocker for an accurately labeled alpha source release; it is a blocker for claiming
production corpus readiness or demonstrated scale.

## Re-entry criteria

1. Commit the exact reviewed tree and rebuild artifacts from that immutable commit.
2. Protect `main` with required review and status checks.
3. Push the feature branch and open the required pull request.
4. Obtain green hosted Python 3.11/3.12/3.13, package, anchored-demo, dependency, and gitleaks jobs.
5. Merge without force-push, verify the public `main` contents and exclusions, then rerun the
   release/archive/secret checks against the merged commit.
6. Keep production-scale claims withheld until the separately planned calibration pilot passes.

Until items 1–5 are evidenced, publication remains **NO-GO** even though the local regression
candidate is **PASS**.
