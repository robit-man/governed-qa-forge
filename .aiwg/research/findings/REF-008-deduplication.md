---
ref_id: REF-008
title: "Deduplicating Training Data Makes Language Models Better"
source: ../sources/REF-008.pdf
grade: high
reviewed: 2026-09-25
---

## Executive summary

Exact and near-duplicate training data increase memorization and distort evaluation. Deduplication improves data efficiency and reduces verbatim reproduction risk.

## Method and findings

The work studies duplicate prevalence, memorization, and downstream effects at pretraining scale using document-level similarity methods.

## Relevance and limitations

Q/A rows need normalized exact hashes, local similarity checks, and cluster-level inspection. Pretraining-scale thresholds do not transfer directly to short prompts, legitimate paraphrases, or deliberately controlled variants.

## Implementation implication

Deduplicate within records, across release history, against evaluation suites, and by seed/template lineage before split assignment.
