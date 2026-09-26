---
ref_id: REF-027
title: "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions"
authors: "Eric Wallace et al."
year: 2024
source: ../sources/REF-027.pdf
source_url: https://arxiv.org/abs/2404.13208
source_type: preprint
full_text: ../working/fulltext/REF-027.txt
sha256: fbc2d65e913e75b8f0ae74e83e3443c36a727636d1038a071a2f10d8be63dac4
grade: moderate
reviewed: 2026-09-25
status: inducted
tags: [instruction-hierarchy, prompt-injection, synthetic-data, latent-behavior]
---

# The Instruction Hierarchy

## Executive synthesis

This paper is direct evidence that a governance behavior can become latent model behavior through
synthetic examples rather than runtime prose. It trained models to distinguish higher- and
lower-privilege instructions and generalized to attack types withheld from training.

## Data construction

For aligned instructions, context synthesis decomposed a compositional request and placed pieces at
different privilege levels while retaining the original correct response. For misaligned instructions,
context ignorance trained the model to answer as if the lower-priority attack were absent or to
refuse when the legitimate task could not proceed.

Training examples covered direct prompt injection in open- and closed-domain tasks, indirect
browsing injection, and system-prompt extraction. Jailbreak examples, tool-output attacks, and
password extraction were deliberately withheld to test transfer.

## Findings

- Robustness increased on every main attack evaluation, by as much as 63 percentage points.
- Held-out attack types also improved, by as much as 34 points.
- Generic capability benchmarks were broadly comparable to the baseline.
- Some benign, attack-like requests suffered over-refusal regressions.
- A system message merely describing the hierarchy was much weaker than training on examples.

The essential mechanism is conditional compliance: follow a lower-priority instruction when it is
compatible, ignore it when it conflicts, and refuse only when the valid task cannot otherwise proceed.

## Relevance to the Forge

This strongly supports the project's goal of making AIWG behaviors latent. The behavior must be
demonstrated through paired situations and decisions, not attached as a private tag to unrelated
arithmetic questions. Context-boundary examples should include both attacks and benign lookalikes.

It also supports the opaque worker design: source and reward context should remain outside the
answering agent's context. Model behavior still needs explicit examples of instruction/data
separation because deployment opacity alone does not teach the student that distinction.

## Limitations

- The evaluated model was a proprietary GPT-3.5 Turbo variant, not a 27B open model.
- Training included both SFT and RLHF, so the marginal contribution of each is unclear.
- Exact data size and full pipeline are not disclosed.
- Many evaluations use GPT-4 as judge.
- Over-refusal regressions remain and high-stakes robustness is not established.
- The current approach assumes all instructions in tool/browser outputs are untrusted.

## Inducted controls

1. Encode every AIWG anchor through behaviorally diagnostic examples.
2. Create aligned, conflicting, ambiguous, and benign-lookalike cases for each behavior.
3. Pair attack-resistance examples with compliance examples to calibrate refusal boundaries.
4. Hold out entire attack and transformation families for generalization tests.
5. Treat instruction provenance as a semantic input dimension.
6. Measure both attack success and over-refusal.
7. Never count a tag as behavior coverage without reviewer attestation and behavioral testing.

## Evidence relationships

REF-028 independently supports negative samples for agent reliability. REF-022 shows exact
instruction constraints can overfit, reinforcing family holdouts. REF-031 warns that reasoning SFT
can weaken refusal behavior unless safety is co-trained and evaluated.
