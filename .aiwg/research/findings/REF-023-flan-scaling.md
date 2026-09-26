---
ref_id: REF-023
title: "Scaling Instruction-Finetuned Language Models"
authors: "Hyung Won Chung et al."
year: 2022
source: ../sources/REF-023.pdf
source_url: https://arxiv.org/abs/2210.11416
source_type: research-paper
full_text: ../working/fulltext/REF-023.txt
sha256: 771f758c1b711c2a63ca2439e80ab90751351d721632897a058c0205ba9e2a22
grade: high
reviewed: 2026-09-25
status: inducted
tags: [instruction-tuning, task-diversity, chain-of-thought, scaling]
---

# Scaling Instruction-Finetuned Language Models

## Executive synthesis

FLAN shows that task diversity and model size jointly improve held-out task performance, and that
including even a modest number of chain-of-thought task families prevents reasoning degradation.
For the Forge, the unit of diversity must be the task family, not merely the number of surface rows.

## Study design

The study instruction-tuned PaLM 8B, 62B, and 540B plus several T5 sizes on aggregated mixtures.
The largest mixture contained 1,836 tasks. Evaluation used held-out MMLU, BBH, TyDiQA, and MGSM
tasks across zero-shot, few-shot, and chain-of-thought prompting settings.

The chain-of-thought component contained nine datasets and 74,730 examples. The researchers
explicitly removed MMLU-related tasks from the training mix and maintained 57 held-out tasks.

## Findings

- Flan-PaLM 540B improved the normalized held-out average by 9.4 points over PaLM 540B.
- The 8B model improved by 15.5 points from instruction tuning, though from a lower baseline.
- Performance generally increased with the number of training tasks and with model size.
- Instruction tuning without CoT data could sharply degrade CoT evaluation performance.
- Adding nine CoT datasets restored and improved reasoning while preserving non-CoT performance.
- Mixing zero-shot and few-shot formats improved usability across prompting settings.

The paper supports broad task coverage and mixed prompt/response formats. It does not show that
simply producing many paraphrases inside ten categories creates similar diversity.

## Relevance to a dense 27B target

A 27B model falls between the paper's principal 8B and 62B points. It should be capable of using a
large task portfolio, but the exact gains cannot be interpolated linearly. The core actionable result
is to maximize distinct operations and held-out generalization rather than row count.

The current calibration corpus has ten labels but roughly sixteen derivational forms. Under FLAN's
evidence model, that is shallow repetition, not a 10-category curriculum.

## Limitations

- The principal models and pretraining corpora differ from modern 27B dense models.
- Many tasks are conventional NLP benchmarks rather than open-ended agent workflows.
- The largest reported gain is at 540B and does not directly establish a 27B optimum.
- Some training and evaluation sources could exist in pretraining data.
- Aggregate scores can hide task-specific regressions.

## Inducted controls

1. Count and cap semantic task families, not only rows and category labels.
2. Hold out complete operations, generators, templates, and domains.
3. Mix direct answers, concise rationales, deep traces, few-shot interactions, and multi-turn tasks.
4. Preserve a meaningful CoT lane so general instruction tuning does not suppress reasoning.
5. Evaluate every response format the deployed model must support.
6. Increase task breadth before multiplying near-identical instances.
7. Report per-family performance and worst-family regression alongside averages.

## Evidence relationships

REF-022 is a more recent generalist implementation of the broad-mixture principle. REF-020 shows
that narrow capability primers can be far smaller when the domain is already encoded. REF-028
shows why format learning should be separated from underlying agent reasoning.
