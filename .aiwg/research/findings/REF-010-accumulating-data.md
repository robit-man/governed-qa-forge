---
ref_id: REF-010
title: "Is Model Collapse Inevitable? Breaking the Curse of Recursion by Accumulating Real and Synthetic Data"
source: ../sources/REF-010.pdf
grade: moderate
reviewed: 2026-09-25
---

## Executive summary

This work distinguishes replacing original data from accumulating synthetic data alongside retained real data, finding that the latter can avoid the same collapse behavior under studied assumptions.

## Method and findings

Theoretical and empirical analyses compare recursive regimes and show why preservation of original observations matters.

## Relevance and limitations

The result supports additive corpus growth and protected anchors but is not proof that any synthetic mixture is safe. Domain, teacher, and selection errors can still accumulate.

## Implementation implication

Track synthetic fractions by category and ancestry, keep authoritative anchors immutable, and run mixture ablations before release.
