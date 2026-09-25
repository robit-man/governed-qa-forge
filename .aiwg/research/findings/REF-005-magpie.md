---
ref_id: REF-005
title: "Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing"
source: ../sources/REF-005.pdf
grade: high
reviewed: 2026-09-25
---

## Executive summary

Magpie separates high-volume candidate production from selection. It generated millions of candidates and formed smaller training subsets using task, quality, difficulty, reward, and diversity signals.

## Method and findings

The aligned model’s implicit user-prompt distribution is sampled, responses are generated, and multi-axis filters select compact subsets. Temperature exposes a quality/diversity tradeoff rather than a universally best setting.

## Relevance and limitations

The key lesson is over-generate then select, while retaining the raw/rejected ledger. Prompt-free generation inherits the teacher’s hidden priors and can make coverage less controllable.

## Implementation implication

Pilot 3–10 candidates per accepted record and measure marginal yield before fixing the production ratio.
