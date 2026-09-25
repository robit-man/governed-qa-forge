---
ref_id: REF-006
title: "DEITA: Data-Efficient Instruction Tuning through Automated Data Selection"
source: ../sources/REF-006.pdf
grade: high
reviewed: 2026-09-25
---

## Executive summary

DEITA shows that compact SFT and preference datasets can perform strongly when selection jointly considers complexity, quality, and diversity.

## Method and findings

Candidate instructions and responses receive learned scores, then diversity-aware selection avoids simply taking the highest-scoring near-duplicates. Reported compact subsets include 6K SFT and 10K preference examples.

## Relevance and limitations

This directly supports a several-thousand-record target, but learned scorers reproduce their training biases and may suppress rare valuable cases.

## Implementation implication

Use multi-objective Pareto selection with category floors and a human-reviewed uncertainty band, not a single opaque aggregate score.
