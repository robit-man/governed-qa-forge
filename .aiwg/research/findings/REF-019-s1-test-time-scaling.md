---
ref_id: REF-019
title: "s1: Simple test-time scaling"
authors: "Niklas Muennighoff et al."
year: 2025
source: ../sources/REF-019.pdf
source_url: https://arxiv.org/abs/2501.19393
source_type: preprint
full_text: ../working/fulltext/REF-019.txt
sha256: 598932c9f96849cd52495d8b3e12ba4d224e41d5588d2278a78f76c744d8a3bc
grade: moderate
reviewed: 2026-09-25
status: inducted
tags: [reasoning-sft, 32b, data-selection, test-time-compute]
---

# s1: Simple test-time scaling

## Executive synthesis

The paper is direct evidence that a 32B instruction model can acquire much stronger reasoning
behavior from only 1,000 selected demonstrations when the base already contains relevant knowledge.
It is evidence for targeted capability elicitation, not evidence that 1,000 examples can create a
broadly more intelligent model from an arbitrary base.

## Study design

- Base model: Qwen2.5-32B-Instruct.
- Initial pool: 59,029 question, reasoning-trace, answer triplets from 16 sources.
- Teacher: Gemini Flash Thinking Experimental.
- Final set: 1,000 examples selected for quality, difficulty, and domain diversity.
- Training: supervised fine-tuning; the paper reports 26 minutes on 16 H100 GPUs.
- Evaluation: MATH500, AIME 2024, and GPQA Diamond.
- Inference intervention: budget forcing terminates or extends the reasoning phase.

## Data-selection findings

Quality filters removed API failures and malformed examples. Difficulty was estimated by whether
Qwen2.5-7B-Instruct and Qwen2.5-32B-Instruct could solve a question and by reasoning length.
Diversity was balanced across 50 subject domains. The paper decontaminated with 8-gram matching.

The ablation is more important than the headline size. Random selection, longest-trace selection,
and diversity-only selection were all materially worse than the joint criterion—about 30 percentage
points worse on AIME 2024 on average. Training on all 59K examples brought little advantage over
the selected 1K while costing far more compute.

## Quantitative findings

- s1-32B reports 50.0% AIME 2024, 93.0% MATH500, and 57.6% GPQA Diamond without extrapolation.
- Budget forcing increased AIME 2024 from 50% to roughly 57% in the reported setting.
- Full-pool SFT used about 394 H100 GPU-hours versus about 7 for s1K.
- The authors' grader judged only 53.6% of s1K solutions correct, rising to 63.0% in s1K-1.1.

That last result is a critical limitation: the paper demonstrates that useful traces can survive noisy
final correctness labels, but it does not justify accepting incorrect traces into a governed corpus.

## Relevance to a dense 27B target

The model size and architecture class are close enough to make the sample-efficiency result highly
relevant. The useful lesson is to calibrate examples against the exact base model, select a joint
difficulty-quality-diversity frontier, and preserve inference-time room for deliberate computation.

The result does not establish broad transfer to coding, agent operation, evidence use, safety, or
multi-turn behavior. Most source domains are quantitative and the evaluation is reasoning-heavy.

## Limitations

- Preprint rather than peer-reviewed final publication at the inducted revision.
- One principal base model and a narrow evaluation suite.
- Teacher-generated traces and grader judgments may share systematic errors.
- Length was used partly as a difficulty proxy, although later work shows verbosity can hurt.
- Budget forcing eventually plateaus and is constrained by the context window.
- Exact benchmark decontamination does not eliminate latent pretraining contamination.

## Inducted controls

1. Select examples on joint quality, difficulty, and diversity—not a single scalar.
2. Measure base-model pass rate on every candidate family before selection.
3. Treat trace length as a diagnostic, never as a quality score by itself.
4. Require final-answer verification even when the teacher trace appears useful.
5. Test small curated and larger uncurated subsets under an equal-token/equal-step ablation.
6. Keep test-time scaling as an evaluation variable, separate from training-set quality.
7. Describe a 1K set as a capability primer, not a broad production corpus.

## Evidence relationships

This supports the small-curated-set results in REF-020 and the quality/diversity findings in
REF-006 and REF-017. REF-026 qualifies its preference for long traces: concise, effective traces
can outperform verbose ones. REF-021 and REF-022 show that broad assistants use much larger
mixed curricula and additional optimization stages.
