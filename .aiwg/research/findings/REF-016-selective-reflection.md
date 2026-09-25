---
ref_id: REF-016
title: "Selective Reflection-Tuning"
source: ../sources/REF-016.pdf
grade: high
reviewed: 2026-09-25
---

## Executive summary

Selective reflection improves weak examples by asking a stronger model to critique and revise them instead of rewriting the entire corpus.

## Method and findings

The workflow identifies examples that merit reflection, obtains revised instructions/responses, and evaluates the resulting student model.

## Relevance and limitations

Targeted revision controls cost and reduces needless homogenization, but critic and teacher errors remain correlated and revision can hide rather than fix unsupported claims.

## Implementation implication

Trigger critique on explicit failure signals, preserve every revision edge, and require the revised row to pass the original deterministic validators again.
