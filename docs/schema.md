# Schema guide

## Workspace inputs

```text
qaforge.yaml
registry/
  sources.yaml
  teachers.yaml
  reviewers.yaml
  behavior-anchors.yaml
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
Reviewer entries provide an operator-approved identity and category scope. Behavior anchors bind
AIWG-informed reasoning principles to approved source snapshots. Every review decision is bound
to the candidate content digest and must resolve to an approved reviewer.

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
- one or more approved AIWG behavior-anchor IDs;
- generation depth.

The lineage—not the row—is assigned to a split. Every descendant inherits that split.

## Verifier types

| Kind | Contract |
|---|---|
| `exact` | normalized, case-insensitive equality with `expected` |
| `numeric` | parsed numeric equality within `tolerance` |
| `regex` | full match against `pattern` |
| `json` | valid JSON, optionally structurally equal to `expected` |
| `citation` | all required private citation IDs recorded in provenance and rendered opaquely as `[1]`, `[2]`, ... |

Arbitrary generated code is intentionally not executed.

## Candidate records

Candidates add immutable generation and decision metadata:

- split, parents, generation run, depth, and timestamps;
- the unchanged seed question and allowlisted question-transform identifier;
- exact teacher/model, terms snapshot, prompt template/hash, and sampling parameters;
- structured derivation steps and a separately verifiable final answer;
- canonical SHA-256 of the exact trainer-visible messages;
- validator, verifier, contamination, quality, coverage, selection, and review results.

Raw, evaluated, selected, reviewed, and rejected records remain separate run artifacts. The run
manifest seals generated artifacts with SHA-256, and review may add only the review decision.
Production approval requires both `derivation_verified: true` and
`behavior_alignment_verified: true`, so the digest-bound decision attests to the derivation and
the example's enactment of its canonical behavior principles while the deterministic verifier
independently checks the final answer.

## Fine-tuning rows

Released split files contain only standard conversational `messages`. Matching
`SPLIT.metadata.jsonl` files preserve record IDs, dimensions, lineage, provenance, verifier
evidence, behavior anchors, and review evidence in the same row order. Training loaders consume
only the messages files; governance systems retain the complete release bundle.

```json
{
  "messages": [
    {"role": "user", "content": "What is 17 multiplied by 6?"},
    {
      "role": "assistant",
      "content": "Derivation:\n1. Multiply 17 by 6.\n2. Check that 102 divided by 6 returns 17.\n\nFinal answer:\n102"
    }
  ]
}
```

The compiler owns the `Derivation:` and `Final answer:` headings. Generated fields may not inject
them. The final answer remains structurally separate inside governed candidates so derivation
content cannot influence exact, numeric, JSON, regex, or citation verification.

## Corpus classes and production policy

`release.corpus_class` is one of `production`, `calibration`, or `test_fixture`. Omission defaults
to production. Calibration is permanently non-releasable; fixtures can be emitted only by the
internal demo path and are marked non-production.

The non-configurable production policy is `qaforge-reasoning-sft-minimum-v1`: at least 20,000
train rows, 2,000 validation rows, 2,000 test rows, ten categories, all of `introductory`,
`intermediate`, and `advanced`, plus coverage of all ten governed AIWG behavior domains. Every
production record must carry an approved behavior anchor and a review-verified derivation.

Schema 1.0 workspaces and inline-metadata releases remain readable for audit and fixity
verification. They are reported as legacy/non-production-standard and cannot generate or build a
new release. Migrate inputs to schema 1.1, regenerate candidates under the structured-derivation
contract, and repeat review before promotion.

Every release also carries `EVALUATION-PROTOCOL.md` and a manifest-bound requirement for three
training seeds (17, 29, and 47), comparison against the unchanged base model, and isolation of the
test split until all training and selection decisions are complete. These are downstream claim
requirements; release eligibility does not assert convergence.
