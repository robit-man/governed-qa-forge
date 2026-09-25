---
ref_id: REF-004
title: "LIMA: Less Is More for Alignment"
source: ../sources/REF-004.pdf
grade: high
reviewed: 2026-09-25
---

## Executive summary

LIMA provides a strong counterexample to volume-first alignment: a carefully curated set of roughly one thousand examples produced competitive instruction-following behavior for its studied model.

## Method and findings

The work emphasizes prompt diversity, response quality, and coherent conversational style, evaluated with human preferences and model comparisons.

## Relevance and limitations

Several thousand deeply checked records can be more valuable than a much larger unfiltered dump. The result is model- and setting-specific, so it cannot determine this project’s optimal size.

## Implementation implication

Treat accepted-record count as an output of quality gates, not a generation target that overrides them.
