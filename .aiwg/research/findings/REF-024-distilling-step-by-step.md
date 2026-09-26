---
ref_id: REF-024
title: "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes"
authors: "Cheng-Yu Hsieh et al."
year: 2023
source: ../sources/REF-024.pdf
source_url: https://aclanthology.org/2023.findings-acl.507/
source_type: peer-reviewed-conference-paper
full_text: ../working/fulltext/REF-024.txt
sha256: bf2651f337c936c02ea6609f7b51e5d0a8227983ebb431647bd1504aea1eef32
grade: high
reviewed: 2026-09-25
status: inducted
tags: [rationale-supervision, distillation, data-efficiency, multi-task]
---

# Distilling Step-by-Step

## Executive synthesis

This paper provides controlled evidence that teacher rationales can carry more training signal than
labels alone. Its strongest evidence concerns small task-specific T5 models on four NLP benchmarks,
so it supports rationale-rich supervision but not a direct broad-capability claim for a 27B model.

## Study design

The teacher was PaLM 540B. Few-shot chain-of-thought prompting generated a label and a rationale
for each input. Student T5 models of 220M, 770M, and 11B were trained with two objectives: label
prediction and rationale generation. Task prefixes separated the two targets.

Experiments covered e-SNLI and ANLI natural-language inference, CommonsenseQA, and SVAMP
arithmetic. Results were reported across four random runs. Baselines were standard supervised
fine-tuning, task distillation using labels, few-shot CoT prompting, and PINTO-style tuning.

## Findings

- Rationale supervision matched or exceeded label-only fine-tuning with much less labeled data.
- On e-SNLI, 12.5% of the data exceeded standard fine-tuning on the full dataset.
- Data reductions were also reported for ANLI, CommonsenseQA, and SVAMP.
- The multi-task label/rationale objective outperformed treating both as one output in ablations.
- A 770M T5 student reportedly exceeded the 540B teacher on one setting with 80% of the data.
- On three of four tasks, an 11B student distilled from unlabeled inputs exceeded teacher prompting.

## Relevance to the Forge

The current Forge requires a derivation and final answer, which is directionally supported. The
paper does not support a fixed two-step derivation template. Rationales should expose actual task
knowledge, causal links, constraints, or intermediate computations that reduce the inference burden.

For a 27B generalist, separate internal supervision fields can support an auxiliary rationale objective
or target-native reasoning channel while keeping the final answer separately verifiable. This is
preferable to asking the model to imitate decorative explanatory prose.

## Limitations

- Task-specific encoder-decoder students are unlike an autoregressive 27B assistant.
- Only four benchmark tasks were studied.
- Teacher rationales were not independently process-verified at scale.
- Better task accuracy does not prove faithful internal reasoning.
- The multi-task loss and task prefixes require trainer support beyond ordinary messages-only SFT.

## Inducted controls

1. Preserve final answer and rationale as distinct logical fields before materialization.
2. Require each rationale to contribute information not recoverable from the final label alone.
3. Support target-native multi-objective or reasoning-channel training where the trainer allows it.
4. Compare answer-only, rationale-plus-answer, and concise-rationale variants.
5. Reject stock derivation language that does not depend on the instance.
6. Use several runs because low-data rationale gains can have high variance.
7. Do not equate generated explanations with faithful causal reasoning without process checks.

## Evidence relationships

REF-003 supports rich teacher traces. REF-025 strengthens the case for step-level checking.
REF-026 warns that excessive rationale verbosity can reduce SFT quality. REF-018 warns that
teacher style alone does not transfer underlying competence.
