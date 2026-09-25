---
ref_id: REF-009
title: "The Curse of Recursion: Training on Generated Data Makes Models Forget"
source: ../sources/REF-009.pdf
grade: high
reviewed: 2026-09-25
---

## Executive summary

Recursive replacement of real data with model-generated data can shrink distribution tails and compound approximation errors across generations.

## Method and findings

The paper combines theoretical analysis with recursive-training experiments and documents progressive loss of rare modes. Later peer-reviewed publication strengthens confidence in the risk, while the exact failure rate remains regime-specific.

## Relevance and limitations

This does not imply synthetic augmentation is inherently harmful. It requires ancestry tracking, protected authoritative data, and explicit generation depth.

## Implementation implication

Default `generation_depth <= 1`; quarantine deeper descendants and never silently recycle corpus outputs as new seeds.
