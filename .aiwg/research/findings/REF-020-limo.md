---
ref_id: REF-020
title: "LIMO: Less is More for Reasoning"
authors: "Yixin Ye et al."
year: 2025
source: ../sources/REF-020.pdf
source_url: https://arxiv.org/abs/2502.03387
source_type: conference-paper
full_text: ../working/fulltext/REF-020.txt
sha256: a4f2ac531f22d57ae0cc1c5374655a4424588e4883e2e251b0df1cdc291fb943
grade: moderate
reviewed: 2026-09-25
status: inducted
tags: [reasoning-sft, 32b, cognitive-templates, data-efficiency]
---

# LIMO: Less is More for Reasoning

## Executive synthesis

LIMO is unusually direct evidence for the proposed 27B-class project. Full-parameter SFT of
Qwen2.5-32B-Instruct on 800 selected math traces produced large in-domain and reported OOD gains.
The authors' hypothesis is conditional: a few demonstrations can elicit complex reasoning only when
the required domain knowledge is already encoded in the base model.

## Study design

- Candidate questions came from tens of millions of math problems.
- Qwen2.5-Math-7B-Instruct removed questions it solved within four attempts.
- DeepSeek-R1-Distill-Qwen-32B sampled 32 solutions for the remainder.
- Questions solved in only 1–3 of 32 attempts formed a 2,125-question pool.
- Three reasoning models generated multiple solution candidates.
- A rule-based score favored elaboration, verification, exploration, and adaptive granularity.
- The top 800 question/trace pairs trained Qwen2.5-32B-Instruct for 15 epochs.

## Quantitative findings

The reported LIMO-800 result is 63.3% on AIME 2024, 95.6% on MATH500, and 96.3% on AMC23.
Across the paper's ten-benchmark table, the mean is 78.1% versus 49.9% for the base model,
58.3% for OpenThoughts-114K SFT, and 32.3% for NuminaMath-100K SFT.

The size ablation is central. LIMO-400 increased AIME 2024 from 16.5% to 57.5% and MATH500
from 79.4% to 94.8%. Gains diminished after 800 examples, though 2,000 examples yielded the
best reported AIME score of 69.6%.

The backbone ablation is equally important. On the same data, Qwen1.5-32B-Chat reached only
9.2% AIME versus 63.3% for Qwen2.5-32B-Instruct. Across 3B, 7B, 14B, 32B, and 72B, larger
models made much better use of the curated traces.

## What the traces contained

The selected traces were intended to demonstrate explicit decomposition, intermediate checking,
exploration of alternatives, and detail proportional to task complexity. These are close to the
latent AIWG behaviors the Forge intends to teach, but the paper addresses mathematical problem
solving rather than software/process governance.

## Relevance to a dense 27B target

The 32B results support a compact reasoning-primer lane. They do not support using 800 examples
as the complete training mixture. The same evidence says that model choice and pretrained
knowledge dominate whether a small set elicits transfer.

For the Forge, each capability primer should contain model-calibrated hard questions, multiple
verified solution paths, explicit recovery or checking where useful, and domain coverage. A broad
27B curriculum should combine several such primers with general instruction, agent, safety, and
behavioral data.

## Limitations

- The study is math-centric, even when its evaluations include adjacent STEM tasks.
- A rule-based quality score uses length and keyword frequency as proxies for reasoning quality.
- The test suite is small relative to the magnitude of the claimed generalization.
- It uses one main 32B instruction-tuned base and one training recipe.
- Long training over 800 examples creates a memorization risk not fully resolved by the paper.
- The paper's decontamination is based on n-grams and cannot rule out pretraining exposure.

## Inducted controls

1. Add an explicit base-capability diagnostic before dataset generation.
2. Target examples just beyond the base model's reliable solve frontier.
3. Generate several solution paths and select by verified substance, not prose markers.
4. Treat 400/800/2,000-example subsets as a learning-curve experiment.
5. Require OOD family and temporal holdouts before calling the effect transferable.
6. Do not equate long text with deep reasoning; include concise expert trajectories.
7. Report which gains are elicitation of latent knowledge versus acquisition of new facts.

## Evidence relationships

REF-019 independently supports the 32B small-curated-set result. REF-026 supports question
diversity and strong teachers but contradicts a naive preference for verbosity. REF-031 strengthens
the conditional-generalization account and includes a direct 27B replication.
