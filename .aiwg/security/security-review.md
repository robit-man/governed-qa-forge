# Final Security Review — Governed QA Forge 0.1.0

**Reviewed:** 2026-09-25T13:01:38-07:00
**Scope:** `/srv/question_stack` application source, tests, security policy, threat model,
requirements, dependency lock, distributions, and GitHub Actions
**Method:** source-assisted STRIDE and trust-boundary review, dependency/secret/static analysis,
package inspection, and safe adversarial regression probes
**Decision:** **PASS WITH DOCUMENTED RESIDUAL RISKS**

## Executive decision

The current release candidate closes every High and Medium finding from the first review. The exact
post-review contamination exploit, post-release checksum rewrite, unsafe teacher endpoint cases,
review forgery cases, path traversal cases, semantic-rewrite case, response-size attack, and regex
resource-exhaustion case were re-executed against the current code. Each was blocked.

No open Critical, High, or Medium security finding remains in the reviewed local candidate. The
security gate passes for public-source publication and the 0.1.0 release process, provided the
separately supplied release anchor remains mandatory for official artifacts and the remote GitHub
checks pass on the commit that is actually published.

The remaining limitations are explicit properties of the local-tool trust model, not hidden
controls: local reviewer registries do not cryptographically authenticate humans; regex-based
content scans do not prove that generated data contains no secret or personal information; and DNS
resolution checks should be backed by production egress controls. These are documented in
`SECURITY.md` and the threat model.

## Finding disposition

| ID | Prior severity | Final status | Retest evidence |
|---|---|---|---|
| QAF-SEC-001 | High | Closed | Reviewed-row mutation is rejected; sealed selection equality, run hashes, validators, verifiers, and decontamination are rechecked at release |
| QAF-SEC-002 | High | Closed | Verification fails without an external anchor and rejects a rewritten bundle against the retained anchor |
| QAF-SEC-003 | High | Closed | HTTP credential endpoints, private/link-local IPs, URL userinfo, arbitrary env names, private endpoints with credentials, and private DNS resolutions are blocked |
| QAF-SEC-004 | Medium | Closed for declared local trust model | Decision digest and reviewer registry/category authorization are enforced; cryptographic identity remains a documented residual risk |
| QAF-SEC-005 | Medium | Closed | Run/release identifiers are constrained to safe basenames; checksum and manifest filenames are confined and symlinks rejected |
| QAF-SEC-006 | Medium | Closed for base provider | Teacher returns answers only; compiler-owned allowlisted transforms bind every question to the seed; prompt-injection patterns are gated |
| QAF-SEC-007 | Medium | Closed | Response byte cap, schema string/list caps, bounded YAML/JSONL readers, and timeout-bounded regex matching are present and exercised |
| QAF-SEC-008 | Medium | Closed with documented defense-in-depth limitation | Expanded runtime patterns plus pinned gitleaks CI; public distribution scan is clean; policy no longer makes an absolute prevention claim |
| QAF-SEC-009 | High | Closed | All actions use reviewed 40-character SHAs; trusted token job is same-repo guarded; fork scan is credential-free and checksum-pinned |
| QAF-SEC-010 | Medium | Closed | pytest is 9.1.1; both `uv audit` and `pip-audit` report no known dependency vulnerability |
| QAF-SEC-011 | Low | Closed | Explicit Hatch package boundary excludes AIWG/provider/runtime/private artifacts; rebuilt sdist and wheel are clean |

Final totals: 0 Critical, 0 High, 0 Medium, 0 Low open.

## Control verification

### 1. Review sealing, decontamination, and authorization

The generation manifest records the hashes of raw, evaluated, selected, and rejection artifacts as
well as every registry/config input (`src/qaforge/pipeline.py`). Review export/import verifies that
seal. Decisions carry `candidate_sha256`, and the named reviewer must resolve to an approved,
category-authorized `registry/reviewers.yaml` entry.

At release, the implementation:

- checks the sealed run and unchanged workspace inputs;
- requires reviewed IDs and non-review fields to equal the selected records;
- recomputes canonical content hashes, validation, answer verification, and decontamination;
- validates split allocation, review binding, reviewer authorization, coverage floors, and target
  size.

The original exploit was repeated by replacing an approved question with the protected benchmark
and updating its content hash. Current result:

```text
BLOCKED: reviewed record differs from sealed selection
```

A mismatched review digest was blocked with `review digest mismatch`; an unregistered identity was
blocked because the reviewer ID did not resolve.

### 2. Release integrity and external anchor

`qaforge release` emits the SHA-256 of `SHA256SUMS`. Normal verification requires that value through
`--expected-sha256`; missing it produces `missing-external-anchor`. `--allow-unanchored` is an
explicit demo-only mode.

The original rewrite probe changed a released answer, recomputed the row content hash, manifest,
and colocated checksums, then verified using the retained pre-mutation anchor. Current result
included:

```text
external-anchor
review-binding:<record-id>
```

Checksum entries must be unique safe basenames and exactly cover all regular, non-symlink evidence
files. Manifest data filenames receive the same confinement checks.

### 3. Remote teacher and credential boundary

Credential variable names must match `QAFORGE_TEACHER_[A-Z0-9_]+`. Credentialed endpoints require
public HTTPS and reject userinfo/fragments. Literal non-global addresses are rejected at schema
validation, and hostname resolution is checked immediately before request dispatch. Explicit
private-endpoint mode cannot use ambient credentials.

Adversarial model and resolver probes produced:

| Case | Result |
|---|---|
| Credentialed HTTP URL | Blocked |
| HTTPS loopback | Blocked |
| HTTPS link-local/metadata address | Blocked |
| URL userinfo | Blocked |
| `AWS_SECRET_ACCESS_KEY` selector | Blocked |
| Private endpoint with ambient credential | Blocked |
| Public hostname resolving to `127.0.0.1` | Blocked |
| Explicit private endpoint without ambient credential | Accepted as designed |

The request streams the response and stops above `max_response_bytes`; output schema validation
forbids extra fields and bounds answers and citations.

### 4. Prompt and output trust

The base remote schema accepts answers only. Questions are generated locally from a small,
versioned allowlist of meaning-preserving transforms, and both release construction and release
verification reconstruct the expected question. The prior "unrelated question with still-correct
answer" path therefore cannot be created by the teacher.

Runtime gates cover canonical hash consistency, secret/PII patterns, common prompt-injection
phrases, risk scope, generation depth, grounding, and semantic transform binding. Exact, numeric,
JSON, citation, and regex answer contracts remain deterministic. Regex matching uses the `regex`
package with a 50 ms timeout and a 512-character pattern cap; a catastrophic-style `(a+)+$` probe
against a maximum-length non-match failed closed with `regex was invalid or exceeded the
verification time limit`.

### 5. Paths and input bounds

Run/release IDs accept only a conservative 1–128 character identifier and reject separators, dot
segments, absolute paths, and control characters. Retests of `../outside`, `nested/path`, and an
absolute path were blocked; a normal ID resolved under `runs/`.

Registry/config YAML reads are capped at 10 MiB. JSONL reads are capped at 256 MiB, one million
records, and one MiB per line. Candidate and benchmark question/answer fields have independent
schema limits.

### 6. Secrets and privacy

Runtime patterns now cover private-key headers, AWS access-key IDs, labeled AWS secret keys,
GitHub/OpenAI/Anthropic tokens, JWTs, bearer tokens, email addresses, US SSNs, phone numbers, and
IPv4 addresses. The re-test detected each representative labeled/structured sample plus common
prompt-injection wording.

A bare high-entropy AWS-secret-shaped string without a label is not distinguishable reliably by the
in-process patterns. This is accepted as the documented defense-in-depth limitation rather than an
absolute guarantee. Human review and organization-specific DLP remain required for private data.

The pinned gitleaks 8.30.1 binary was independently downloaded and matched the committed
`551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb` checksum. Scanning the exact
rebuilt public sdist tree found no leak. A worktree-wide scan found only ignored compiled test
bytecode containing the deliberately concatenated fake AWS test fixture; neither the source tree
nor distribution contains that assembled token.

### 7. Dependency and CI supply chain

- `uv.lock` resolves 57 registry packages, all with SHA-256 artifact hashes; the only non-registry
  entry is the project itself in editable form.
- `uv audit --locked`: no known vulnerabilities or adverse project statuses in 57 packages.
- `pip-audit` 2.10.1: no known vulnerabilities; the unpublished local project is the only skipped
  package.
- pytest resolved to 9.1.1, closing the prior temporary-directory advisory.
- `actions/checkout`, `astral-sh/setup-uv`, and `gitleaks/gitleaks-action` are pinned to 40-character
  commits recorded in `ci/digests.txt`.
- Direct `git ls-remote` checks confirmed that those commits are the current recorded `v4`, `v6`,
  and `v3` tag targets respectively.
- The only `secrets.*` reference is in a job guarded to pushes or same-repository pull requests.
  Fork pull requests run a credential-free gitleaks binary downloaded by version and checked
  against the separately committed SHA-256 before execution.
- CI uses `uv sync --locked`, runs static/type/test/dependency gates, inspects package contents, and
  verifies its demo with a separately supplied anchor.

The detailed workflow result is in `working/ci-workflow-audit.md`.

### 8. Distribution hygiene and reproducibility

The Hatch sdist target has an explicit allowlist and exclusions for `.aiwg`, provider state,
environment files, and private/runtime artifacts. The rebuilt archives contain no AIWG tree,
provider tree, `.env`, generated run/release, PDF, extracted research source, or absolute `/srv` or
`/home` path.

The sdist was extracted and compared against the current `src`, `tests`, `docs`, README, security
policy, project metadata, and lockfile; differences were limited to local ignored `__pycache__`
directories. Two consecutive builds were byte-identical:

```text
1b0f72d00721f4775a6461a6ba483f7785bd2bfeeab8f8af9f7500a6d1e70a04  governed_qa_forge-0.1.0-py3-none-any.whl
943d22523bc405e84998b4435366f79a536918faff5a8d976add012d19684ab9  governed_qa_forge-0.1.0.tar.gz
```

## Final verification evidence

| Check | Final result |
|---|---|
| `uv lock --check` | Pass |
| `uv audit --locked` | Pass; 57 packages, no known vulnerability |
| `uv run pip-audit` | Pass; no known vulnerability |
| `uv run ruff format --check src tests` | Pass; 23 files formatted |
| `uv run ruff check src tests` | Pass |
| `uv run mypy src` | Pass; 16 source files |
| `uv run pytest --cov=qaforge` | Pass; 39 tests, 84.86% coverage |
| `git diff --check` | Pass |
| Adversarial security probe suite | Pass; prior exploit paths blocked |
| AIWG CI workflow audit | Pass |
| Public sdist gitleaks scan | Pass; no leaks |
| Archive private-material scan | Pass |
| Two consecutive builds | Pass; byte-identical hashes |
| Offline CLI demo plus anchored verification | Pass; 8 records, 9 evidence files |

## Residual risks and operating requirements

1. Publish and retain each official release anchor separately from the release bundle. Do not use
   `--allow-unanchored` for production or fine-tuning inputs.
2. The local reviewer registry is an authorization control, not proof of human identity. Programs
   exposed to insider or multi-user threats should add signed decisions or a protected review
   service and require multiple reviewers for sensitive categories.
3. Apply outbound network policy in production. Application-level public-address resolution reduces
   SSRF risk but cannot replace egress enforcement against DNS/routing-layer attacks.
4. Treat generated-content scanning as defense in depth. Apply domain-specific DLP, privacy review,
   and independent source-grounding checks appropriate to the corpus.
5. The base provider deliberately trades open-ended question evolution for deterministic semantic
   binding. Any future semantic-evolution plugin needs its own threat model and independent verifier.
6. Require the remote GitHub CI run to pass on the exact commit selected for public `main`; local
   evidence cannot attest repository settings, branch protection, or hosted-runner state.

## Final gate

**PASS WITH DOCUMENTED RESIDUAL RISKS.** No release-blocking security defect remains in the reviewed
candidate. Reopen the gate if the published commit differs from this candidate, an official release
is distributed without its separately trusted anchor, or the remote CI/security checks do not pass.
