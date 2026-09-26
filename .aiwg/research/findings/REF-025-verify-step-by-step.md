---
ref_id: REF-025
title: "Let's Verify Step by Step"
authors: "Hunter Lightman et al."
year: 2023
source: ../sources/REF-025.pdf
source_url: https://arxiv.org/abs/2305.20050
source_type: research-paper
full_text: ../working/fulltext/REF-025.txt
sha256: fbd170e2042c32950c3fe97d3a558d89e8a8dffaadc942e774ccb4b751abc123
grade: moderate
reviewed: 2026-09-25
status: inducted
tags: [process-supervision, reward-model, active-learning, verification]
---

# Let's Verify Step by Step

## Executive synthesis

The paper shows that step-level process labels can train a more reliable selector than final-answer
labels alone for difficult mathematics. It directly motivates a first-error label and adversarial
hard-negative bank, but it studies reward models and best-of-N selection rather than SFT of a 27B
student.

## Study design

The large-scale generator and reward models were derived from a base GPT-4 model with additional
math pretraining. A generator was first taught newline-delimited reasoning format. Human labelers
then marked each step positive, negative, or neutral, stopping after the first incorrect step.

PRM800K contains 800,000 step labels across 75,000 solutions to 12,000 MATH problems. Because
4,500 original test problems entered reward-model training, final evaluation used the remaining 500.
Outcome reward models used final answer correctness; process reward models predicted correctness
at each step and scored a solution from its per-step probabilities.

## Findings

- At best-of-1,860, the process model solved 78.2% of the selected MATH subset.
- The outcome model solved 72.4%; majority vote solved 69.6%.
- Process supervision outperformed outcome supervision at every tested data scale.
- An active learner selected convincing wrong-answer trajectories.
- This selection was estimated to be 2.6 times as data-efficient as uniform labeling.
- On recent AP and AMC questions, PRM selection scored 72.9% versus 63.8% for the ORM.

## Relevance to a dense 27B target

The Forge should not only retain successful teacher traces. It should retain difficult rejected
trajectories privately, identify the earliest invalid step, and use them for verifier training,
preference data, or contrastive correction examples. This attacks the exact failure boundary.

For trainer-visible SFT, corrected traces should remain primary. Raw incorrect reasoning should be
used only in explicitly structured critique/correction or preference records so the wrong process is
not learned as an ordinary completion.

## Limitations

- The headline result evaluates a reward model doing search, not the student model after SFT.
- The domain is competition mathematics.
- Large-scale process and outcome datasets are not directly matched.
- Some MATH test problems were used in PRM training; evaluation therefore used a subset.
- Final-answer matching can falsely approve invalid reasoning that reaches the correct result.
- Generalization beyond math and selection/search remains open.

## Inducted controls

1. Add step-level process status and first-error location to private review metadata.
2. Prioritize plausible failures that pass superficial checks for review.
3. Maintain corrected trajectories and explicit negative pairs for preference training.
4. Keep deterministic final verification and process verification as separate gates.
5. Calibrate automated process judges against expert labels before scaling.
6. Never treat final-answer correctness as proof of a valid derivation.
7. Use temporal OOD evaluation for process verifiers.

## Evidence relationships

REF-024 shows that rationales can improve student learning; this paper shows why those rationales
need step-level quality controls. REF-021 and REF-022 support deterministic outcome rewards for an
RL phase. REF-011 documents model-judge bias and reinforces the need for calibration.
