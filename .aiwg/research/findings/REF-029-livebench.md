---
ref_id: REF-029
title: "LiveBench: A Challenging, Contamination-Limited LLM Benchmark"
authors: "Colin White et al."
year: 2025
source: ../sources/REF-029.pdf
source_url: https://arxiv.org/abs/2406.19314
source_type: peer-reviewed-conference-paper
full_text: ../working/fulltext/REF-029.txt
sha256: 38207db0331896e9558cc803d04188f32dddda1709139c53f985680d1b78e06c
grade: high
reviewed: 2026-09-25
status: inducted
tags: [evaluation, contamination, temporal-holdout, objective-grading]
---

# LiveBench

## Executive synthesis

LiveBench is evaluation evidence, not a training recipe. It establishes a useful pattern for proving
that a Forge corpus improved a 27B model: refreshed questions from recent sources, objective
ground truth, diverse capability categories, and a withheld slice not available to training.

## Benchmark design

The inducted version has about 1,000 questions across math, coding, reasoning, language,
instruction following, and data analysis. Tasks use recent competitions, code problems, papers,
news, movies, and datasets, or harder procedural variants of established benchmarks.

Questions are updated monthly; roughly one sixth is replaced per update, producing a six-month
refresh cycle. The newest one-sixth is withheld for one month. Scoring is automatic against
objective ground truth rather than an LLM judge.

## Findings relevant to evaluation quality

- The benchmark differentiated model strengths across its six categories.
- No evaluated model exceeded 70% on the inducted release.
- Recent-source tasks reduce but do not eliminate contamination.
- LLM judges are documented as biased toward verbosity and sometimes wrong on hard tasks.
- A static public test set inevitably becomes less informative as it enters training corpora.

The authors distinguish exact test contamination from ordinary generalization to a familiar task
distribution. Both matter for this project: the Forge must block exact/paraphrase overlap and also
hold out entire generators to test structural transfer.

## Relevance to a dense 27B target

The existing fixed test split is necessary but insufficient. If it comes from the same sixteen
templates as training, it measures interpolation. A meaningful evaluation needs external tasks,
future-generated task families, and hidden transformations that the corpus generator cannot see.

Objective grading should dominate math, code, schema, constraints, provenance reconstruction,
and operational state transitions. Expert or calibrated model judging remains necessary for some
open-ended behaviors but must be reported separately.

## Limitations

- Objective scoring excludes many valuable open-ended tasks.
- English dominates the benchmark.
- Prompt formats can favor particular model families.
- Some older questions may already be contaminated.
- Maintaining a live suite requires sustained labor and compute.
- Passing LiveBench alone does not establish safety, calibration, or agent reliability.

## Inducted controls

1. Maintain a private rolling temporal suite outside the generator's accessible context.
2. Refresh at least a fixed fraction of evaluation families for every major release.
3. Use deterministic graders whenever a ground truth can be constructed.
4. Hold out generator programs and transformations, not only random rows.
5. Report external, internal, and temporal evaluation results separately.
6. Track scoring-parser failures as test infrastructure defects, not model errors.
7. Never train on the corpus's production test split after it has served as a release gate.

## Evidence relationships

REF-022 demonstrates the value of a separate unseen suite. REF-008 supports deduplication, while
REF-029 shows why deduplication alone is insufficient. REF-011 supports skepticism toward model
judges.
