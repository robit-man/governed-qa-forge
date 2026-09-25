# Operations runbook

## New corpus

1. Run `qaforge init PATH`.
2. Replace the example release identity and taxonomy.
3. Register sources with immutable snapshots and authorization evidence.
4. Register an exact teacher version and terms snapshot.
5. Build a reviewed seed bank with independent verifier contracts.
6. Add protected evaluations to the benchmark registry.
7. Run `qaforge doctor PATH` until every check passes.

## Generation and review

```bash
qaforge generate PATH --run-id pilot-001
qaforge review-export PATH pilot-001 PATH/review.jsonl
# Review every packet and replace pending decisions.
qaforge review-import PATH pilot-001 PATH/review.jsonl
qaforge release PATH pilot-001
qaforge verify-release PATH 0.1.0 --expected-sha256 PUBLISHED_ANCHOR
```

Run IDs and release versions are immutable. Use a new identifier after any configuration, source, seed, model, prompt, or policy change.
The release command prints the SHA-256 of `SHA256SUMS`. Retain or publish that value outside the
workspace; colocated checksums alone detect accidental damage but cannot authenticate a maliciously
rewritten bundle. `--allow-unanchored` is reserved for disposable local demonstrations.

## Failure handling

- Doctor failure: correct the registry or schema; no provider is called.
- Provider failure: retain the attempted run ID for audit and choose a new run ID after correction.
- Category-floor failure: add or repair eligible lineages; do not lower a quota merely to force release.
- Review rejection: generate replacement candidates or explicitly revise the target release plan.
- Fixity failure: quarantine the release directory and rebuild under a new version after determining the mutation source.

## Fine-tuning handoff

Copy the entire release directory into the downstream experiment’s immutable input area. Record the release manifest SHA-256 and repository commit in the training run. Never hand off split JSONL without its manifest and evidence bundle.
