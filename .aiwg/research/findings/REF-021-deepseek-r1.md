---
ref_id: REF-021
title: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning"
authors: "DeepSeek-AI"
year: 2025
source: ../sources/REF-021.pdf
source_url: https://arxiv.org/abs/2501.12948
source_type: technical-report
full_text: ../working/fulltext/REF-021.txt
sha256: b191b0a365a64b4ab2791d117069ed17a2933d03554a662ced58b37df52018f4
grade: moderate
reviewed: 2026-09-25
status: inducted
tags: [reasoning, distillation, 32b, rlvr, mixed-curriculum]
---

# DeepSeek-R1

## Executive synthesis

DeepSeek-R1 shows two distinct routes relevant to a dense 27B model: distill strong reasoning
trajectories through SFT, and improve verifiable reasoning with reinforcement learning. Its direct
32B comparison found 800K-example distillation substantially stronger than more than 10K steps
of RL from the same Qwen2.5-32B base. The broad recipe was multi-stage rather than Q/A-only.

## Dataset and pipeline

The pipeline used thousands of cold-start examples, a first reasoning RL stage, rejection sampling,
a second SFT stage mixing reasoning and non-reasoning data, then a second RL stage for reasoning,
helpfulness, and harmlessness.

The released SFT mixture contains about 804,745 examples:

- 395,285 math examples, averaging 6,094 tokens;
- 211,129 code examples, averaging 7,436 tokens;
- 10,124 STEM examples;
- 10,395 logic examples;
- 177,812 general examples, including writing and factual QA.

For each reasoning prompt, the system sampled multiple trajectories and retained correct ones.
It filtered mixed-language, poorly readable, and structurally chaotic traces. Human annotators
checked generated thinking processes for non-reasoning tasks. Most records are single-turn.

## Direct 32B evidence

DeepSeek-R1-Distill-Qwen-32B was trained for 2–3 epochs on the 800K mixture with a 32,768-token
context. The reported scores were 72.6% AIME 2024 pass@1, 94.3% MATH500, 62.1% GPQA
Diamond, 57.2% LiveCodeBench, and Codeforces rating 1691.

The paper trained Qwen2.5-32B-Base with more than 10K policy-gradient updates on math, code,
and STEM prompts. That RL-only model scored 47.0% AIME, 91.6% MATH, 55.0% GPQA, and
40.2% LiveCodeBench—well below the 32B distilled model under the paper's settings.

## Implications for the Forge

The strongest evidence does not support one homogeneous several-thousand-row Q/A file. It
supports a mixture with hard verifiable reasoning, code, logic/STEM, and a large general replay
component. It also supports generating more than one response and accepting only verified
trajectories.

SFT is the economical first stage for a 27B model. RL with reliable rule-based rewards remains a
useful second stage for generalization, but reward hacking becomes a documented risk when learned
reward models are optimized for too long.

## Limitations

- Technical report with incomplete disclosure of all training data and generation details.
- The frontier teacher is much larger than the proposed student and expensive to reproduce.
- Benchmark contamination cannot be fully excluded.
- The SFT mixture is predominantly single-turn and may limit conversational transfer.
- SFT and RL experiments are not strictly compute matched.
- Claims about distilled models surpassing proprietary systems depend on reported evaluation setups.

## Inducted controls

1. Split the dataset into reasoning, code, STEM/logic, agent, and general-retention lanes.
2. Use repeated sampling and deterministic verification for verifiable domains.
3. Preserve a substantial general replay mixture to protect broad behavior.
4. Prefer SFT distillation before undertaking costly RL on a 27B student.
5. Build RL prompts and executable verifiers as separate assets from SFT answer records.
6. Track reward hacking and stop on external evaluation, not reward alone.
7. Add multi-turn examples; do not reproduce the report's single-turn limitation.
8. Keep maximum trace length high enough for hard cases while filtering chaotic verbosity.

## Evidence relationships

REF-022 independently supports SFT followed by preference tuning and verifiable-reward RL.
REF-019 and REF-020 show that far smaller reasoning primers can work in narrow domains. REF-026
supports stronger teachers and question diversity. REF-031 qualifies the SFT-versus-RL story.
