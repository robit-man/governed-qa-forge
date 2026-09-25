---
ref_id: REF-017
title: "Data Diversity Matters for Robust Instruction Tuning"
source: ../sources/REF-017.pdf
grade: high
reviewed: 2026-09-25
---

## Executive summary

This line of work reinforces a quality-diversity tradeoff: selecting only the highest-scored examples can create a brittle, redundant set, while diversity without a quality floor propagates errors.

## Method and findings

Quality and diversity objectives are jointly evaluated across instruction-tuning subsets, including worst-case or coverage-oriented behavior rather than averages alone.

## Relevance and limitations

Proxy objectives can miss rare but pedagogically valuable examples. Category quotas and adversarial slices remain necessary.

## Implementation implication

Select from a Pareto frontier, publish both average and tail-coverage metrics, and retain exclusion reasons for later threshold replays.
