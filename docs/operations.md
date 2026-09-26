# Operations runbook

## New corpus

1. Run `qaforge init PATH`.
2. Replace the example release identity and expand the taxonomy to at least ten categories.
3. Register sources with immutable snapshots and authorization evidence.
4. Register an exact teacher version and terms snapshot.
5. Build a reviewed seed bank with independent verifier contracts and all ten governed AIWG
   behavior domains in `registry/behavior-anchors.yaml`.
6. Add protected evaluations to the benchmark registry.
7. Run `qaforge doctor PATH` until every check passes.

For resident agent workers, deploy the separate worker and control processes described in
[the opaque service guide](opaque-service.md). Keep the control bind private and back up the SQLite
broker before maintenance. Expired worker leases return to the queue automatically after restart.

## Generation and review

```bash
qaforge generate PATH --run-id pilot-001
qaforge review-export PATH pilot-001 PATH/review.jsonl
# Review every packet, validate each derivation and its stated behavior principles,
# set derivation_verified=true and behavior_alignment_verified=true,
# and replace pending decisions.
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

Copy the entire release directory into the downstream experiment’s immutable input area. Point the
trainer only at `train.jsonl` and, where appropriate, `validation.jsonl`; keep test isolated until
final evaluation. Record the release manifest SHA-256 and repository commit in the training run.
Never hand off split JSONL without its manifest, matching metadata sidecars, and evidence bundle.
Follow `EVALUATION-PROTOCOL.md`: run the same training configuration with seeds 17, 29, and 47,
compare every tuned result with the unchanged base, and report variance and regressions. A valid
dataset release is not by itself evidence of convergence or improved intelligence.

## Calibration pilot

`qaforge calibration-pilot pilot-workspace --size 1000` is a technical service and gate
calibration. It must report 3,000 submitted/raw candidates, 1,000 selected lineages, and stage
`awaiting_review`. Do not call `review-all` unless an authorized reviewer actually inspected every
packet. A successful deterministic pilot is evidence that the separate HTTP application contracts,
opaque payload projection, broker, and gates operate in-process; it does not exercise split Unix
processes, TCP listeners, or systemd identities, and it is not
evidence of production model-answer quality.
Its `calibration` corpus class is permanently rejected by the release builder even if review state
is later manipulated to approved.

When upgrading a private broker created under the answer-only worker contract, startup labels
finalized collections as legacy and leaves them audit-readable. Any unfinished submitted answer
without a structured derivation is cleared and requeued under `structured-derivation-v2`; upgrade
worker adapters before resuming. Legacy schema-1.0 corpus workspaces are likewise read-only until
regenerated and reviewed under schema 1.1.
