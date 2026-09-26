# Governance and release gates

Governed QA Forge treats every synthetic answer as a derivative artifact with a reviewable ancestry.

## Authorization

Sources and teachers are deny-by-default unless their registry entry is `approved`. Each source
records its snapshot hash, license basis, redistribution decision, compatible output licenses, and
allowed target uses. Each teacher records its exact model, terms snapshot, authorization basis,
allowed target uses, reviewer, and review date. Every release use and license must be explicitly
compatible; free-form similarity is not treated as permission. Output ownership alone is not
treated as sufficient authorization.

## Split isolation

The deterministic split function consumes the lineage ID, project salt, and configured ratios before generation. Descendants cannot be moved independently. Release verification reconstructs the lineage-to-split map and fails on cross-split families.

## Verification

Deterministic content and answer gates run before selection. A provider’s own confidence or
stylistic quality is not a verifier. The release builder checks sealed run hashes and reviewed-row
identity, then runs validators, verifiers, and decontamination again rather than trusting cached
statuses.

## Decontamination

The base implementation combines:

- canonical question/answer SHA-256;
- normalized word-trigram Jaccard similarity;
- deterministic feature-hashed semantic vectors;
- locality-sensitive semantic signatures to avoid unconditional all-pairs comparison;
- explicit lineage handling;
- the protected benchmark registry.

Same-lineage variants may remain candidates so selection can choose the best controlled variant, but exact duplicates are rejected and the default lineage cap is one released record.

## Review

All selected records require complete decisions. `review-export` produces one packet per row inside
the workspace boundary; `review-import` refuses missing, duplicate, unknown, or pending decisions.
Bulk approval requires an explicit manual-review acknowledgement for every non-fixture corpus.
Each decision is bound to the candidate content hash and its reviewer must resolve to an approved,
category-authorized entry in `registry/reviewers.yaml`. This is an operator-controlled local trust
registry, not a replacement for organization identity or signed review attestations.
For an approved production decision, both `derivation_verified` and
`behavior_alignment_verified` must be true. The review packet repeats the exact question,
derivation, final answer, category, and canonical anchor principles; import rejects any displayed
content or anchor-context change. The digest covers the question, derivation, final answer, roles,
and compiler-owned response format.

## Latent AIWG behavior anchors

The governed anchor registry captures ten AIWG-informed reasoning domains. Anchors are private
provenance, not prompt decoration: examples must enact the behavior through concrete scenarios,
tradeoffs, derivations, and actions without naming AIWG, skill IDs, source IDs, or framework
mechanics in trainer-visible messages. The registry must exactly match the code-owned profile
induced from hashed AIWG artifacts, and reviewers explicitly attest that each example semantically
enacts its assigned principles. The opaque worker plane also rejects exact registered anchor
identifiers in questions. This repetition turns the decision patterns into learned behavior while
keeping source and evaluation context outside the model conversation.

## Release

A release is assembled in a hidden temporary directory and atomically promoted to its version
path. Existing releases cannot be overwritten. Production can never release below 20,000 train,
2,000 validation, and 2,000 test rows, ten categories, three difficulty tiers, or the ten required
AIWG behavior domains. These floors are code constants, not operator configuration. Review
rejection also cannot shrink the release below `target_size`. Fixity covers messages-only split
data, bound metadata sidecars, and every evidence artifact.

## Suggested production policy

- Calibrate semantic thresholds against labeled duplicate and controlled-variant pairs.
- Require at least two reviewers or expert review for sensitive categories.
- Keep authoritative evaluation data in a separately controlled repository.
- Preserve rejected candidates and rationales for threshold replay.
- Re-review provider terms whenever the provider, model, target use, or effective terms change.
- Default generation depth to one; require signed approval for deeper ancestry.
