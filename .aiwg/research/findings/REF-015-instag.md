---
ref_id: REF-015
title: "#InsTag: Instruction Tagging for Analyzing Supervised Fine-tuning of Large Language Models"
source: ../sources/REF-015.pdf
grade: high
reviewed: 2026-09-25
---

## Executive summary

#InsTag builds a fine-grained instruction taxonomy and shows that a small diverse/complex subset can outperform much larger undifferentiated collections.

## Method and findings

An automatic tagger discovers and assigns thousands of intent and semantic tags, enabling coverage analysis and diversity-aware sampling.

## Relevance and limitations

This supports categorical planning and tag-based gap detection. Automatic tags can be noisy, correlated, and unstable across domains, so the taxonomy needs versioning and human governance.

## Implementation implication

Separate stable human-owned category IDs from model-generated descriptive tags; log taxonomy migrations.
