---
ref_id: REF-022
title: "Tülu 3: Pushing Frontiers in Open Language Model Post-Training"
authors: "Nathan Lambert et al."
year: 2024
source: ../sources/REF-022.pdf
source_url: https://arxiv.org/abs/2411.15124
source_type: technical-report
full_text: ../working/fulltext/REF-022.txt
sha256: 79bed1ef4ce4bb332f43bdc87d60709e644560f8f3bb6d14913a473cc82c251f
grade: high
reviewed: 2026-09-25
status: inducted
tags: [generalist-post-training, data-mixture, dpo, rlvr, decontamination]
---

# Tülu 3

## Executive synthesis

Tülu 3 is the strongest evidence in this induction for broad assistant post-training as a portfolio
problem. It combines a 939K-example SFT mixture, preference tuning, and about 30K verifiable RL
prompts, evaluates both development and unseen suites, and publishes unsuccessful or mixed
results. It is indirect for 27B because the main sizes are 8B and 70B, but highly relevant to design.

## Prompt and SFT mixture

The project curated over 23M prompts and used 939,344 in SFT. The mix includes real-user chat,
human-written instruction data, classical NLP tasks, scientific literature, tables, math, code,
safety/non-compliance, multilingual prompts, and precise instruction-following data.

Synthetic persona generation filled targeted gaps: approximately 220K math problems, 35K code
problems, and 29,980 verifiable instruction-following pairs. Responses were kept from humans or
frontier models or regenerated with GPT-4o. The final Llama 3.1 70B SFT model was trained for two
epochs with a lower learning rate than the 8B model.

## Controlled findings

Removing diverse WildChat data caused small but broad regressions, most clearly on AlpacaEval.
Removing safety data mostly harmed safety, suggesting a partly orthogonal lane. Removing persona
data reduced the skills it targeted. Removing math data reduced GSM8K from 76.2 to 64.1 and MATH
from 31.5 to 23.5 for the 8B SFT model.

Stratified data scaling continued to improve average performance and GSM8K up to the full SFT
mixture, while TruthfulQA declined. Random seed changes produced noticeable SFT variation.
The unseen suite showed some development-set overfitting, especially for exact constraints.

## RL with verifiable rewards

The RLVR bank contained 7,473 GSM8K, 7,500 MATH, and 14,973 verifiable instruction prompts.
Binary deterministic verifiers replaced a learned reward model for these objectives. At 8B, RLVR
improved MATH, GSM8K, and IFEval modestly. At 70B, gains were smaller because some tasks were
near saturation. Learned reward scores added to verifiable rewards made training noisier.

## Decontamination and evaluation

The team compared exact, embedding, and n-gram matching and selected 8-gram prompt matching
because embeddings confused distributional similarity with paraphrase overlap. It removed training
records with over 50% matched test tokens. A separately designed unseen evaluation suite revealed
where choices had overfit development benchmarks.

## Relevance to a dense 27B target

The 27B Forge should treat data mixing as an optimization variable, not assume equal category
counts are optimal. Targeted synthetic data can close gaps, but real or independently authored
data is valuable for linguistic diversity and forgetting resistance. A dedicated unseen suite is
necessary because even a careful, open project overfit exact instruction-following constraints.

## Limitations

- Main model sizes bracket rather than match 27B.
- Nearly one million SFT examples may be infeasible for the first Forge run.
- Some evaluation uses model judges and has only moderate human agreement.
- Exact mixture choices were tuned against development evaluations.
- Public source licenses were reviewed carefully, but source quality remains heterogeneous.

## Inducted controls

1. Design separate capability lanes and tune their mixture through controlled ablations.
2. Include diverse general/replay data to limit forgetting and mode collapse.
3. Add explicit positive and negative safety/non-compliance examples.
4. Maintain a generator-hidden unseen suite with new task variants.
5. Use deterministic rewards where possible and avoid mixing weak model rewards into them.
6. Run more than one training seed and preserve every result.
7. Track per-skill regressions; an average gain may hide truthfulness or safety losses.
8. Treat persona synthesis as gap filling rather than the sole source of diversity.

## Evidence relationships

REF-023 supports breadth across many tasks. REF-021 independently supports a mixed SFT plus RL
pipeline. REF-027 and REF-028 provide concrete safety and agent lanes. REF-029 supports refreshed,
objective unseen evaluation.
