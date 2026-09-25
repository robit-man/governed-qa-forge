---
ref_id: REF-011
title: "Judging the Judges: A Systematic Investigation of Position Bias in LLM-as-a-Judge"
source: ../sources/REF-011.pdf
grade: moderate
reviewed: 2026-09-25
---

## Executive summary

LLM evaluators can prefer answers because of presentation order, making one-pass pairwise judging unsuitable as a release gate.

## Method and findings

The study swaps candidate order across multiple evaluation settings and measures inconsistent preferences.

## Relevance and limitations

Judge versions and prompts change, and position bias is only one evaluator failure mode. Self-preference, verbosity bias, shared training data, and correlated errors also matter.

## Implementation implication

Run A/B and B/A, randomize labels, calibrate judges against dual-human samples, record judge/version/prompt, and send disagreements to adjudication.
