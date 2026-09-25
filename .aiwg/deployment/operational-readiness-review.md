# Operational Readiness Review — Governed QA Forge 0.1.0

**Reviewed:** 2026-09-25T13:03:08-07:00
**Release candidate:** uncommitted `feat/end-to-end-governed-qa-forge` worktree
**Repository:** `https://github.com/robit-man/governed-qa-forge`
**Local technical gate:** **GO TO PR**
**Public release gate:** **NO-GO**
**Production corpus gate:** **NO-GO — pilot not executed**

## Decision statement

The final local candidate is technically ready to be committed and submitted for review. Static
quality, tests, coverage, dependency audit, security review, source and installed-wheel demos,
external-anchor verification, package hygiene, public-tree hygiene, research fixity, and CLI/docs
checks all pass.

It is not ready to be declared a public 0.1.0 release because no immutable candidate commit, pull
request, or hosted CI result exists; `main` is unprotected; and the public default branch does not
yet contain the implementation. It is also not ready to be described as operationally proven for
production corpus generation because only the bounded deterministic fixture has run.

## Readiness dashboard

| Domain | Status | Evidence |
|---|---|---|
| Requirements | PASS locally | FR-001..FR-014 and NFR-001..NFR-008 mapped to executed/inspected evidence |
| Formatting/lint/types | PASS | Ruff and strict mypy clean |
| Automated tests | PASS locally | 39/39 on Python 3.11/3.12/3.13; 87.73% statements; 72.61% branches; 84.86% combined |
| Security | PASS with documented residual risks | all QAF-SEC-001..011 closed; 0 open findings |
| Dependencies | PASS | locked sync and `pip-audit` clean |
| Offline demo | PASS | 24 generated, 8 selected/released, full evidence bundle verified |
| Release integrity | PASS | sealed run/review data, release-time rechecks, mandatory external anchor |
| Coverage governance | PASS | all eight dimensions and their configured floors appear in the release manifest |
| Packaging | PASS | final wheel/sdist clean; Python 3.11 installed-wheel journey succeeds |
| Research boundary | PASS | 18/18 local PDF hashes valid; public index retained; payloads/text excluded |
| Public-tree hygiene | PASS locally | gitleaks clean, no private payload paths, no broken Markdown links |
| Repository visibility | PASS | GitHub reports PUBLIC, active, default branch `main` |
| Immutable candidate | **FAIL** | application candidate is not committed |
| Pull request / hosted CI | **FAIL** | zero PRs and zero workflow runs for the candidate |
| Branch governance | **FAIL** | GitHub reports `main` is not protected |
| Public implementation | **FAIL** | remote `main` remains at research-bootstrap commit `dbd3182` |
| Production calibration | NOT DEMONSTRATED | no authorized 500–1,000-row pilot or target-scale profile |
| CUDA policy | Not applicable | no CUDA container, service, or workload was started |

## Operational model

Governed QA Forge is a local CLI/package rather than a hosted service. Deployment consists of
publishing reviewed source/package artifacts and handing immutable dataset release directories to
fine-tuning runs. There is no database migration, long-running daemon, network listener, or CUDA
deployment in the base product.

The operating sequence is:

```text
authorized registries + reviewed seeds
  -> deterministic lineage split
  -> bounded provider candidates
  -> validation / independent verification / decontamination
  -> coverage-aware selection
  -> digest-bound authorized review
  -> release-time revalidation
  -> immutable evidence bundle + externally retained anchor
```

The built-in remote provider returns answers only. Questions remain bound to human-reviewed seeds
through a small allowlist of compiler-owned semantic-preserving transforms. This is a deliberate
alpha safety boundary and is accurately documented. Arbitrary model-driven question evolution
requires an extension with an independent solver, pinned-source entailment checker, or calibrated
rubric; it is not silently implied by the base implementation.

## Demonstrated operating evidence

The final source and wheel flows generate a release containing:

- `train.jsonl`, `validation.jsonl`, and `test.jsonl`;
- `manifest.json` and a sanitized `generation-run-manifest.json`;
- `DATASHEET.md`, Croissant JSON-LD, and W3C PROV JSON-LD;
- a rejection ledger and `SHA256SUMS`.

The final fixture run produced 24 raw candidates from eight seeds, selected and reviewed eight,
and released seven train, zero validation, and one test row. The empty validation file is valid for
this tiny deterministic fixture; the manifest records it with the SHA-256 of an empty file. The
500-row production scaffold is intentionally deny-by-default and must be populated with sufficient
authorized seed lineages before it can meet its release target.

Normal verification failed without an external digest, failed with a wrong digest, and passed with
the independently computed digest. The verifier checked nine evidence files and all eight records.
Tamper, unsafe checksum path, sealed-review drift, protected-benchmark insertion, and undersized
approval paths fail closed.

## Package and public-data boundary

Final local build digests:

```text
1b0f72d00721f4775a6461a6ba483f7785bd2bfeeab8f8af9f7500a6d1e70a04  governed_qa_forge-0.1.0-py3-none-any.whl
943d22523bc405e84998b4435366f79a536918faff5a8d976add012d19684ab9  governed_qa_forge-0.1.0.tar.gz
```

These are validation artifacts only until rebuilt from a commit. Archive inspection found no AIWG
workspace, provider state, `.env`, acquired PDF, extracted source text, generated run/release,
private corpus, or host path. Git ignore checks preserve the public research source register while
excluding all acquired source payloads and full text. The exact proposed public tree passed the
checksum-verified gitleaks scan.

## Security and residual risk

The final security decision is **PASS WITH DOCUMENTED RESIDUAL RISKS**. All previous findings are
closed for the declared local-tool trust model. The retained limitations are:

- the local reviewer registry does not cryptographically authenticate a human;
- regex-based secret/PII screening is defense in depth, not proof of absence;
- DNS checks should be paired with production network egress controls;
- citation contracts prove identifier/token presence, not factual source entailment;
- arbitrary generated code is not executed or verified by the base product.

These limitations are stated in `SECURITY.md`, the threat model, governance/provider docs, and the
security review. They do not block public alpha publication when those claims remain scoped.

## Exact blockers

### ORR-001 — Candidate has no immutable Git identity

The audited implementation is untracked or modified while `HEAD` equals `origin/main` at
`dbd3182`. A local working tree cannot be the provenance anchor for a public release.

**Exit:** commit the exact reviewed candidate, rerun/build from that commit, and record the commit
and artifact hashes.

### ORR-002 — Required review and hosted validation are absent

The AIWG delivery policy requires a pull request and green CI. GitHub reports no PR and no Actions
run. Local results cannot substitute for the configured hosted Python-version and secret-scan gate.

**Exit:** push the feature branch, open the PR, and obtain green Python 3.11/3.12/3.13, build,
anchored-demo, dependency-audit, and gitleaks jobs.

### ORR-003 — Default branch protection is absent

The GitHub API returns `Branch not protected` for `main`, contrary to the release plan.

**Exit:** require pull-request review and the relevant CI status checks on `main`; prohibit force
push and deletion according to repository policy.

### ORR-004 — The public branch has not received the product

The public repository is correctly visible, but its only remote branch remains the research
bootstrap. No public consumer can check out the reviewed implementation yet.

**Exit:** merge the green PR without force-push, then re-audit public `main`, its release files,
and exclusions.

### ORR-005 — Target-scale production behavior is unproven

No authorized real provider, 500–1,000 accepted-row calibration, retry/rate-limit test, interrupted
run recovery, or several-thousand-row throughput/resource profile has been observed.

**Exit for production claims:** complete the documented calibration milestone with retained
quality, diversity, review, contamination, throughput, cost, failure, and release evidence. This
does not block a clearly labeled alpha source release.

## Deployment and rollback

For source/package publication, deploy only from the reviewed merge commit. Record the Git commit,
wheel/sdist hashes, workflow URL, and security/test report versions. Do not publish the local
uncommitted build hashes above as release provenance.

For dataset handoff, copy the complete release directory, publish or retain the printed root
anchor in a separate trusted system, and record the source commit in the downstream training run.
Never hand off split JSONL without its evidence bundle.

Rollback is non-destructive:

1. withdraw an affected package/tag or mark it superseded;
2. retain the failed source and dataset artifacts for audit;
3. quarantine affected dataset releases rather than overwriting them;
4. correct the defect and publish a new semantic version and dataset release directory;
5. notify downstream fine-tuning operators with the affected commit, artifact hashes, and lineage.

## Final go criteria

Public-release approval requires one immutable commit for which all of the following are true:

1. local and hosted format, lint, strict typing, tests, coverage, dependency, build, and secret
   gates pass;
2. the installed wheel completes the offline demo and anchored verification;
3. wheel, sdist, exact Git tree, and public `main` pass the private-material exclusions;
4. `main` protection enforces PR review and required status checks;
5. the green feature PR is merged without force-push and the public repository is revalidated;
6. release notes retain the documented alpha scope and do not claim an executed production pilot.

The candidate may proceed to commit and PR now. It must not be labeled or published as the final
0.1.0 release until criteria 1–5 are evidenced. The current overall decision is **NO-GO**.
