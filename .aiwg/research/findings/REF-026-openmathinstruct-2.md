---
ref_id: REF-026
title: "OpenMathInstruct-2: Accelerating AI for Math with Massive Open-Source Instruction Data"
authors: "Shubham Toshniwal et al."
year: 2024
source: ../sources/REF-026.pdf
source_url: https://arxiv.org/abs/2410.01560
source_type: technical-report
full_text: ../working/fulltext/REF-026.txt
sha256: 348a284034d88ed17d381f2300be5cc377d323a2010403edee50d013bb003d00
grade: moderate
reviewed: 2026-09-25
status: inducted
tags: [math-sft, question-diversity, teacher-quality, decontamination, verbosity]
---

# OpenMathInstruct-2

## Executive synthesis

OpenMathInstruct-2 supplies unusually useful dataset-design ablations: question diversity mattered
strongly, a better teacher mattered, and excessively verbose solutions hurt. It also shows that large
datasets may tolerate moderate noise without endorsing deliberate contamination of a smaller,
governed corpus.

## Study design

The dataset contains about 14 million question-solution pairs over about 600,000 unique questions.
Llama-3.1-405B-Instruct generated new questions and multiple solutions. For generated questions
without labels, 32 generations and majority vote approximated the correct answer.

The team ran controlled ablations using Llama-3.1-8B-Base, typically averaged over four runs.
It examined solution format, teacher strength, quality filtering, and unique-question coverage.
Evaluation included GSM8K, MATH, AMC 2023, AIME 2024, and Omni-MATH.

## Findings

- A concise custom CoT format was about 40% shorter and improved MATH by 3.9 points over a
  more verbose format.
- At equal SFT size, a strong teacher improved performance by 7.8 points over a weak teacher.
- Models tolerated up to about 20% low-quality solutions at scales of at least 256K with little loss.
- At a fixed 256K pairs, raising unique questions from 1K to 6.5K improved MATH validation by
  about 10.5 points.
- Llama-3.1-8B-Base trained on the full set improved MATH from 51.9% to 67.8%.
- The data-scaling curve showed no saturation at 14M for the 8B experiment.

## Decontamination

Embedding retrieval produced the five closest evaluation questions; a 405B model then judged both
pair orders for paraphrase equivalence. About 50,000 of 569,000 synthetic questions were removed.
The authors acknowledge 1.4% overlap with the later Omni-MATH benchmark.

## Relevance to a dense 27B target

This paper argues against the current calibration corpus's dominant failure mode: hundreds of rows
generated from a tiny number of templates with changed names and numbers. For a 27B model,
unique semantic problems and distinct solution strategies are more valuable than surface variants.

The paper also cautions against making long derivations mandatory for all records. The Forge should
match explanation length to task complexity and retain direct-answer exemplars.

## Limitations

- Math-only study centered on an 8B student; the 70B gains were less consistent.
- Most design choices were optimized on the 8B validation result.
- Robustness to noise occurs at large scale and may not hold for a compact 20K set.
- Majority vote is not ground truth and can preserve systematic teacher errors.
- LLM decontamination has its own false positives and false negatives.

## Inducted controls

1. Measure unique semantic questions and family entropy separately from row count.
2. Prefer the strongest authorized teacher available for difficult traces.
3. Penalize unnecessary verbosity and templated filler.
4. Sample multiple solutions and preserve strategy diversity among verified answers.
5. Combine lexical and semantic/paraphrase decontamination with manual review bands.
6. Treat noise tolerance as a robustness finding, not permission to weaken verification.
7. Report scaling curves in examples, unique questions, and response tokens.

## Evidence relationships

REF-019 and REF-020 agree that quality and diversity dominate raw volume in compact reasoning
sets. REF-023 supports task-family breadth. REF-031 shows how long-CoT quality and optimization
interact with model capability.
