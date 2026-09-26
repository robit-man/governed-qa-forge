---
ref_id: REF-030
title: "SFT Memorizes, RL Generalizes: A Comparative Study of Foundation Model Post-training"
authors: "Tianzhe Chu et al."
year: 2025
source: ../sources/REF-030.pdf
source_url: https://arxiv.org/abs/2501.17161
source_type: peer-reviewed-conference-paper
full_text: ../working/fulltext/REF-030.txt
sha256: ebe6aaf90a9e309732a45c1f809a40808b61ec46f737b0306dba80f21a149c54
grade: moderate
reviewed: 2026-09-25
status: inducted
tags: [sft, reinforcement-learning, generalization, dissent]
---

# SFT Memorizes, RL Generalizes

## Executive synthesis

In two controlled rule-variation environments, outcome-reward RL improved out-of-distribution
performance while additional SFT degraded it. SFT was still required to stabilize output format
before RL. This is meaningful evidence for adding a verifiable-reward stage, but its headline should
not be generalized to all reasoning SFT; REF-031 directly challenges that interpretation.

## Study design

The base was Llama-3.2-Vision-11B. Tasks were GeneralPoints, a synthetic arithmetic card game,
and V-IRL, a visual navigation simulator. Training and evaluation varied textual rules and visual
distributions. SFT and PPO-based sequential-revision RL were compared at matched reported
training compute from a shared SFT initialization.

## Findings

Across rule variants, RL improved OOD success or accuracy by 3.0–11.0 points while additional
SFT reduced it by 5.6–79.5 points in the reported settings. Across visual variants, RL improved
GeneralPoints by 17.6 points and V-IRL by 61.1 points; SFT degraded both.

Increasing verifier/revision steps improved OOD generalization: one step produced only a 0.48-point
gain, while ten steps produced a 5.99-point gain at the reported budget.

RL directly from the unaligned base failed because outputs were long, unstructured, and difficult to
score. An initial SFT stage established the response protocol. RL also failed to recover an
over-trained SFT checkpoint that had collapsed to the training rule.

## Relevance to a dense 27B target

The paper supports a division of labor: use SFT to establish task semantics, interaction format, and
good priors; use verifiable-reward optimization to improve policy search and OOD adaptation. It
also supports conservative SFT checkpointing because later RL cannot necessarily reverse collapse.

The result does not imply that the Forge corpus is useless. It implies that corpus generation should
also emit prompt-plus-verifier assets suitable for RLVR, especially for code, math, schemas,
constraints, planning states, tests, and operational recovery.

## Limitations

- One 11B multimodal model and two controlled environments.
- The SFT demonstrations lack the verified long-CoT structure studied in REF-031.
- GeneralPoints is synthetic and V-IRL is a simulator.
- Results depend on PPO, verifier design, and sequential revision.
- Broad language, code, knowledge, safety, and agent benchmarks were not the main focus.

## Inducted controls

1. Export a separate RLVR prompt bank with deterministic verifier functions.
2. Begin RL only after the model reliably produces parseable actions and answers.
3. Preserve pre-collapse checkpoints and never assume RL can repair overfit SFT.
4. Compare unchanged base, SFT, and SFT-plus-RLVR.
5. Hold out rule and environment variants for OOD evaluation.
6. Scale verifier/revision opportunities only while external metrics improve.
7. Treat the paper's headline as task-conditional, not a universal law.

## Evidence relationships

REF-021 and REF-022 support multi-stage SFT plus verifiable-reward optimization. REF-031 provides
current dissent: high-quality long-CoT SFT can generalize when optimization, data, and base-model
capability align.
