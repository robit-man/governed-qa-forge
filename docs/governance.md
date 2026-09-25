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
Bulk approval requires an explicit manual-review acknowledgement outside demo workspaces.
Each decision is bound to the candidate content hash and its reviewer must resolve to an approved,
category-authorized entry in `registry/reviewers.yaml`. This is an operator-controlled local trust
registry, not a replacement for organization identity or signed review attestations.

## Release

A release is assembled in a hidden temporary directory and atomically promoted to its version
path. Existing releases cannot be overwritten, and review rejection cannot silently shrink a
release below `target_size`. Its fixity file covers the split data and every evidence artifact,
including a sanitized generation-run manifest with source, teacher, policy, and input hashes.

## Suggested production policy

- Calibrate semantic thresholds against labeled duplicate and controlled-variant pairs.
- Require at least two reviewers or expert review for sensitive categories.
- Keep authoritative evaluation data in a separately controlled repository.
- Preserve rejected candidates and rationales for threshold replay.
- Re-review provider terms whenever the provider, model, target use, or effective terms change.
- Default generation depth to one; require signed approval for deeper ancestry.
