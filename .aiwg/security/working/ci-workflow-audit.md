# Final CI Workflow Audit

**Generated:** 2026-09-25T13:01:38-07:00
**Repository:** `/srv/question_stack`
**Workflow files scanned:** 1 (`.github/workflows/ci.yml`)
**Decision:** **PASS**

## Findings

No open Critical, High, or Medium workflow finding remains.

## Audit results

### Action references

All external actions use full 40-character commit SHAs:

- `actions/checkout@11d5960a326750d5838078e36cf38b85af677262` (`v4`)
- `astral-sh/setup-uv@d0d8abe699bfb85fec6de9f7adb5ae17292296ff` (`v6`)
- `gitleaks/gitleaks-action@e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e` (`v3`)

The values are recorded in `ci/digests.txt`; direct upstream tag queries matched all three committed
digests.

### Container and latest-tag checks

- No container/image reference.
- No bare `:latest` reference.

### Pull-request secret isolation

The token-backed gitleaks job references `${{ secrets.GITHUB_TOKEN }}`, but the complete job is
guarded by:

```yaml
if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.full_name == github.repository
```

This is the audit's accepted same-repository exception. Untrusted fork pull requests use a separate
job with no `secrets.*` reference.

### Standalone installer check

The fork job downloads gitleaks 8.30.1 as an archive; it does not pipe network content into a shell.
The archive is checked before extraction against:

```text
551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb
```

An independent download produced the same digest. Only the named `gitleaks` file is extracted and
then run without credentials.

### Pin manifest

`ci/digests.txt` records every action and standalone binary used by the workflow.

### Permissions and release checks

- Workflow permissions are explicitly limited to `contents: read`.
- Dependencies are synchronized with `uv sync --locked --extra dev`.
- CI runs formatting, lint, strict typing, coverage, `pip-audit`, package build/content inspection,
  offline demo, and anchored release verification.
- No publishing job exists, so signed-tag verification is not currently applicable.

## Clean checks

- No mutable action refs.
- No unpinned container images.
- No `:latest` images.
- No unguarded PR job with secret access.
- No curl-to-shell or wget-to-shell installer.
- Pin manifest present and validated.
- No local reusable workflow requiring recursive inspection.

## Gate

**PASS.** Re-run this audit whenever an action, downloaded tool, event trigger, job permission, or
secret-bearing step changes.
