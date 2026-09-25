---
ref_id: REF-001
title: "Self-Instruct: Aligning Language Models with Self-Generated Instructions"
source: ../sources/REF-001.pdf
grade: high
reviewed: 2026-09-25
---

## Executive summary

Self-Instruct demonstrates an iterative seed → generate → filter → add loop. Starting from 175 human-written tasks, it produced 52,445 instructions and 82,439 instances, showing that a small reviewed seed bank can expand coverage when invalid and near-duplicate outputs are rejected.

## Method and findings

The method mixes output-first and instruction-first generation, classifies tasks before instance creation, and filters format failures and similarity to existing items. Its contribution is the pipeline structure, not a claim that every generated row is good.

## Relevance and limitations

Adopt label-first categorical generation, reviewed seeds, and iterative novelty checks. Do not inherit its English-centric assumptions or its relatively shallow automatic validation.

## Implementation implication

Make seed ancestry and rejection reason first-class record fields.
