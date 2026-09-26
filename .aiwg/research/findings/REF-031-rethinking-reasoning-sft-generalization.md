---
ref_id: REF-031
title: "Rethinking Generalization in Reasoning SFT: A Conditional Analysis on Optimization, Data, and Model Capability"
authors: "Qihan Ren et al."
year: 2026
source: ../sources/REF-031.pdf
source_url: https://arxiv.org/abs/2604.06628
source_type: conference-paper
full_text: ../working/fulltext/REF-031.txt
sha256: 23c8527985b7e0960c011bde148e1ea3182dffbbb1bed27721710c9fa00bc37f
grade: moderate
reviewed: 2026-09-25
status: inducted
tags: [reasoning-sft, 27b, long-cot, optimization, safety]
---

# Rethinking Generalization in Reasoning SFT

## Executive synthesis

This is the most directly applicable source in the induction. It studies dense models up to Gemma 3
27B and shows that verified long-CoT SFT can transfer across math, code, science, broad reasoning,
instruction following, and truthfulness. Transfer depends jointly on trace quality, sufficient model
capability, and training long enough to pass an early imitation phase. Reasoning gains can weaken
safety.

## Study design

Primary experiments used Qwen3-14B/8B-Base and InternLM2.5-20B-Base. The default data,
Math-CoT-20K, contains 20,480 math prompts with multiple Qwen3-32B thinking responses; only
math-verified correct responses under 16,384 tokens were retained.

Default SFT used AdamW, learning rate 5e-5, batch size 256, cosine decay, and eight epochs.
Evaluation covered MATH500, AIME 2024, LiveCodeBench v2, GPQA Diamond, MMLU-Pro, IFEval,
AlpacaEval 2, HaluEval, TruthfulQA, and HEx-PHI safety.

Additional experiments varied data structure and quality, teacher, model family, size, random seed,
training schedule, and domain. Gemma3-27B-Base supplied a direct 27B replication.

## Central findings

Early checkpoints often showed a dip in OOD performance and a surge in response length. Later
checkpoints recovered beyond the base model while responses became shorter and more targeted.
The authors interpret the early stage as surface imitation of long reasoning and the later stage as
internalization of decomposition, backtracking, verification, and strategy switching.

At a fixed 640-step budget, eight passes over 2.5K examples outperformed one pass over 20K,
while eight passes over 20K was best. Thus repeated exposure and coverage both mattered.

Verified Math-CoT-20K outperformed a matched no-CoT version on reasoning-intensive tasks for
stronger models. A lower-quality NuminaMath variant broadly degraded performance. Countdown
traces from a narrow arithmetic game transferred procedures such as search and backtracking, but
only when the base model had enough relevant capability.

## Direct Gemma 3 27B result

For Gemma3-27B-Base, the reported final step moved MATH500 from 26.3% to 89.1%, AIME 2024
from 0.7% to 39.3%, LiveCodeBench v2 from 4.7% to 21.5%, GPQA-Diamond from 8.2% to 50.3%,
and MMLU-Pro from 15.5% to 69.0%. IFEval moved only from 36.2% to 38.5%.

These very large gains come from a base rather than an instruction-tuned checkpoint and should not
be treated as a guaranteed effect for every 27B model. The intermediate trajectory was noisier than
the Qwen runs, and the study did not publish a full multi-seed 27B replication.

## Safety result

Long-CoT SFT increased compliance with harmful requests more than matched no-CoT training.
The study links this to self-rationalization: extended reasoning can create room to reinterpret a
harmful request as educational and bypass a short refusal policy. The result requires an explicit
safety replay mixture and checkpoint-level safety gates.

## Relevance to the Forge

A 20K high-quality reasoning core is a credible experiment for a 27B dense base. It is not a
complete generalist corpus. The Forge should pair it with broad instruction, agent/tool, AIWG
behavior, direct-answer, safety, and retention lanes and evaluate the mixture through training.

Response length must be monitored as a learning diagnostic. An early verbose model may be less
capable than both the base and a later checkpoint. Fixed one-epoch evaluation can be misleading.

## Limitations

- Math is the main training domain, with only one code-domain replication.
- Dense models stop at 27B; larger dense and mixture-of-experts models are absent.
- The GRPO comparison is not FLOP- or token-matched and depends on reward design.
- A full factorial interaction study was not run.
- Behavioral detectors are rule-based rather than mechanistic explanations.
- Safety gains or losses may differ for an already aligned 27B instruct checkpoint.

## Inducted controls

1. Make 20,480 verified long traces the first 27B reasoning-core experimental target.
2. Generate several responses per prompt and accept only independently verified correct traces.
3. Use a strong reasoning teacher and a 16K-or-greater response allowance for hard candidates.
4. Evaluate frequent checkpoints across eight or more effective passes before diagnosing failure.
5. Monitor response length, format errors, backtracking, verification, and final correctness.
6. Co-train safety and direct-refusal examples; gate every checkpoint on attack success.
7. Preserve no-CoT and low-quality controls to identify which component drives gains.
8. Treat base-model diagnostic performance as a precondition for each capability lane.
9. Report cross-domain gains and non-reasoning regressions separately.
10. Do not claim broad intelligence improvement from math results alone.

## Evidence relationships

This qualifies REF-030's universal-sounding headline and provides direct 27B evidence missing from
REF-019 and REF-020. It agrees with REF-026 on data quality and excessive verbosity, with REF-021
on verified teacher trajectories, and with REF-027 on the need to preserve refusal boundaries.
