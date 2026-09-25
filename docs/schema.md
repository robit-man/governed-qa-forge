# Schema guide

## Workspace inputs

```text
qaforge.yaml
registry/
  sources.yaml
  teachers.yaml
  reviewers.yaml
  taxonomy.yaml
  protected-benchmarks.jsonl
seeds/
  seeds.jsonl
```

`qaforge.yaml` controls split ratios, generation bounds, quality thresholds, review policy, and release identity. Every input is validated before provider access.

Source registry entries explicitly enumerate `allowed_target_uses` and
`compatible_release_licenses`; teacher entries enumerate `allowed_target_uses`. All configured
release uses must be a subset of each referenced source and teacher permission list, and the
release license must appear in each referenced source compatibility list.
Reviewer entries provide an operator-approved identity and category scope. Every review decision
is bound to the candidate content digest and must resolve to an approved reviewer.

Teacher `provider` values are `deterministic`, `openai-compatible`, or
`opaque-agent-service`. The last value is finalized only by the private service control plane;
direct generation fails closed. Worker tasks are intentionally not seed records and expose none of
the fields below except the transformed question.

## Seed records

Each JSONL seed requires:

- `seed_id` and `lineage_id`;
- question and authoritative reference answer;
- coverage dimensions: category, domain, task, reasoning operation, answer form, difficulty, evidence mode, and risk;
- an independent verifier specification;
- one or more approved source IDs;
- generation depth.

The lineage—not the row—is assigned to a split. Every descendant inherits that split.

## Verifier types

| Kind | Contract |
|---|---|
| `exact` | normalized, case-insensitive equality with `expected` |
| `numeric` | parsed numeric equality within `tolerance` |
| `regex` | full match against `pattern` |
| `json` | valid JSON, optionally structurally equal to `expected` |
| `citation` | all required citation IDs recorded and rendered as `[SOURCE-ID]` |

Arbitrary generated code is intentionally not executed.

## Candidate records

Candidates add immutable generation and decision metadata:

- split, parents, generation run, depth, and timestamps;
- the unchanged seed question and allowlisted question-transform identifier;
- exact teacher/model, terms snapshot, prompt template/hash, and sampling parameters;
- canonical content SHA-256;
- validator, verifier, contamination, quality, coverage, selection, and review results.

Raw, evaluated, selected, reviewed, and rejected records remain separate run artifacts. The run
manifest seals generated artifacts with SHA-256, and review may add only the review decision.

## Fine-tuning rows

Released split rows contain standard `messages` plus a `metadata` object. Training loaders that only need messages may discard metadata after separately retaining the release evidence bundle.

```json
{
  "messages": [
    {"role": "user", "content": "What is 17 multiplied by 6?"},
    {"role": "assistant", "content": "102"}
  ],
  "metadata": {
    "record_id": "qa_...",
    "lineage_id": "family-arithmetic-001",
    "content_sha256": "...",
    "is_synthetic": true
  }
}
```
