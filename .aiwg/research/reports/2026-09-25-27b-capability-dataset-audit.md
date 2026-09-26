# 27B Dense-Model Capability Dataset Audit

**Date:** 2026-09-25

**Decision:** current calibration set is not capability-training evidence; proceed only with a
27B-specific empirical curriculum

**Scope:** what dataset and training evidence could credibly produce meaningful capability gains in
a dense model near 27B parameters

## Bottom line

The existing 1,000-record public calibration corpus should not be used to infer improved reasoning
or intelligence. It is a successful test of the opaque service and governance path, but its content is
mostly short deterministic arithmetic and logic generated from roughly sixteen derivational forms.
Its ten private behavior-anchor labels do not make the corresponding behaviors present in the
trainer-visible examples.

Research does support meaningful improvement in this weight class, but under much stronger
conditions. Two independent studies fine-tuned Qwen2.5-32B-Instruct on only 800–1,000 highly
selected reasoning traces and reported large math gains [REF-019, REF-020]. A 2026 study trained
dense base models, including Gemma 3 27B, on 20,480 independently verified long-CoT examples
and reported late-stage transfer across math, code, science, and broad reasoning [REF-031]. These
results are conditional on a capable base, hard and diverse problems, high-quality traces, repeated
exposure, and credible external evaluation.

Broad assistant improvement has a different evidence base. DeepSeek-R1's released 32B distill used
about 805K mixed examples, while Tülu 3 used about 939K SFT examples before preference and
verifiable-reward stages [REF-021, REF-022]. Therefore:

> A compact set can be a powerful capability primer. It is not a substitute for a broad curriculum,
> safety retention, or an evaluation program.

## Research question

What changes to the Forge's data and evaluation design are most likely to cause real, transferable
capability improvement in a dense 27B-class model, rather than teach answer formatting, repeated
templates, benchmark leakage, or teacher style?

## Evidence base and method

This pass acquired full papers, extracted full text, checked fixity, prepared source-level findings,
and assigned quality assessments for REF-019 through REF-031. The new evidence covers:

- direct 27B/32B reasoning SFT and distillation [REF-019, REF-020, REF-021, REF-031];
- generalist data mixtures and multi-stage post-training [REF-022, REF-023];
- rationale and process supervision [REF-024, REF-025];
- teacher quality, question diversity, trace verbosity, and decontamination [REF-026];
- instruction hierarchy and agent behavior training [REF-027, REF-028];
- refreshed, objective evaluation [REF-029];
- SFT-versus-RL disagreement and its boundary conditions [REF-030, REF-031].

Strong recommendations below require at least two compatible evidence sources or are labeled as
project hypotheses. No source establishes a universal optimum number of rows for every 27B model.

## Current-state audit

The public baseline has 1,000 selected lineages: 910 train, 48 validation, and 42 test. It has ten
balanced labels, but the trainer-visible examples are dominated by parameterized versions of simple
inventory arithmetic, medians, ratios, linear equations, set accounting, small program traces, and
deductive syllogisms. Assistant messages nearly always contain two short derivation steps and a
single short answer.

### What the baseline proves

- an agent can answer through the opaque worker plane without seeing sources, labels, rewards, or
  selection outcomes;
- deterministic validation and final-answer verification operate end to end;
- lineage, manifests, sidecars, and public fixity artifacts can be produced;
- the service can collect multiple candidates without leaking feedback to the worker.

### What the baseline does not prove

- transfer beyond its small set of templates;
- improvement to hard reasoning, code, science, planning, tools, or evidence use;
- semantic enactment of any AIWG behavior domain;
- resistance to prompt injection or contextual poisoning;
- safety retention after reasoning SFT;
- convergence or any advantage over the unchanged 27B base model.

The present `20k/2k/2k` release floor is a governance eligibility threshold. It is not an efficacy
threshold. Multiplying the current templates until they pass that floor would satisfy row counts but
would not satisfy the research evidence.

## Finding 1 — select for the model's learning frontier

The strongest compact-set results did not sample easy questions uniformly. s1 removed problems
solved by 7B and 32B baselines and then balanced quality, difficulty, and diversity. Its single-factor
selections were about 30 AIME points worse than the joint selection [REF-019]. LIMO selected
problems solved only one to three times in 32 attempts and found that 500 advanced questions
transferred better than easier ones [REF-020].

The Forge must therefore profile the exact base checkpoint before building the corpus. A record's
difficulty label should be empirical—derived from pass rate, error mode, and response variance—not
authored as `introductory`, `intermediate`, or `advanced` without measurement.

Project implication:

- generate a large probe pool;
- sample the unchanged 27B base multiple times per prompt;
- prioritize the region where the base has relevant knowledge but fails inconsistently;
- include a smaller retention lane of easy/direct examples;
- exclude impossible or underspecified items unless the desired skill is clarification or refusal.

## Finding 2 — semantic diversity dominates surface variation

FLAN improved held-out performance as the number of tasks increased to 1,836 [REF-023].
OpenMathInstruct-2 held total pairs fixed and gained about 10.5 MATH points by raising unique
questions from 1K to 6.5K [REF-026]. Tülu 3 found real-world chat diversity beneficial across
several skills [REF-022]. These results converge on task-family diversity, not word substitution.

The Forge needs semantic-family fingerprints that describe the operation, hidden dependency graph,
required evidence, failure modes, and solution strategy. Changing names or numbers is one family.
Train/validation/test assignment must group all parameterizations, paraphrases, teacher variants,
and derived descendants before generation.

## Finding 3 — teach procedures, not a universal prose costume

Rationales can improve data efficiency relative to labels alone [REF-024], and process labels can
train better selectors than final outcomes alone [REF-025]. However, OpenMathInstruct-2 found a
40% shorter solution format outperformed a more verbose alternative [REF-026]. Agent-FLAN found
that fixed ReAct/JSON patterns were learned faster than the agent reasoning underneath [REF-028].

The current universal `Derivation:` / `Final answer:` wrapper is therefore unsuitable as the only
production materialization. A capable model should learn when to answer directly, when to explain
briefly, when to plan, when to inspect evidence, when to use a tool, and when to perform a long
search with backtracking.

The private record should preserve structured steps and verification. The trainer-visible form should
vary by response mode and use the target model's native chat/reasoning protocol where necessary.

## Finding 4 — 20K verified long traces are a credible 27B reasoning core

REF-031 is the direct anchor. Its 20,480-example Math-CoT set used multiple teacher outputs and
retained only math-verified correct traces. On Gemma 3 27B Base, the last reported checkpoint moved
MATH500 26.3→89.1, AIME24 0.7→39.3, LiveCodeBench v2 4.7→21.5, GPQA-Diamond 8.2→50.3,
and MMLU-Pro 15.5→69.0. The result is large enough to be practically important, though one model
and one principal training domain are not a universal guarantee.

The same study observed a dip-and-recovery trajectory: early training produced much longer,
lower-quality responses and worse OOD performance before later recovery. Lower-quality data did
not recover. Stronger base models internalized backtracking and verification; weaker ones copied
verbosity [REF-031]. LIMO independently found that the same 800 examples were dramatically more
effective for a newer, knowledge-richer 32B base [REF-020].

Project implication: adopt 20,480 accepted, independently verified long reasoning traces as the
first evidence-backed 27B reasoning-core target, not as the whole corpus. Monitor frequent
checkpoints through multiple effective passes rather than assuming one epoch or minimum loss is
optimal.

## Finding 5 — broad capability needs a portfolio

DeepSeek-R1's 32B distill used approximately 395K math, 211K code, 20K STEM/logic, and 178K
general examples [REF-021]. Tülu 3 used a broad 939K SFT mix and demonstrated that removing
skill-specific sources selectively harmed the corresponding skill [REF-022]. FLAN shows that
adding only ordinary instruction tasks can suppress CoT behavior unless reasoning data remains in
the mix [REF-023].

The evidence does not prescribe a cost-effective first-run optimum for this project. The following is
an explicit design hypothesis to test, not a published universal minimum:

- 20,480 verified deep-reasoning examples;
- 15K–30K broad instruction and direct-answer examples;
- 10K–20K code, tool, planning, and operational-recovery trajectories;
- 8K–15K evidence, provenance, critique, and independent-verification examples;
- 8K–15K instruction-hierarchy, refusal-boundary, and safe-completion contrasts;
- total first full training mixture: approximately 60K–100K accepted records, with token-balanced
  rather than row-balanced sampling.

This range should be tested against 2.5K, 20K, and intermediate mixture ablations. If resources
permit, scaling should continue while external evaluation improves; OpenMathInstruct-2 and Tülu 3
both show gains beyond tens of thousands [REF-022, REF-026].

## Finding 6 — AIWG anchors need diagnostic examples

Instruction-hierarchy training converted a written policy into behavior by training aligned and
conflicting cases; it generalized to attack types excluded from training [REF-027]. Agent-FLAN
reduced false tool calls with examples that explicitly taught when not to use a tool [REF-028].

Every AIWG domain needs contrastive scenario families that make the desired behavior necessary:

| Latent domain | Diagnostic training behavior |
|---|---|
| requirements and acceptance | detect ambiguity, ask only material questions, convert intent to measurable tests |
| evidence before assertion | distinguish observation, inference, uncertainty, and unsupported claim |
| provenance and traceability | reconstruct lineage, preserve hashes/actors/transforms, identify missing links |
| threat modeling and least authority | identify assets/boundaries, minimize permissions, reject excessive scope |
| independent verification | choose an independent check and withhold approval when it fails |
| test and quality gates | derive tests from risks and block delivery on mandatory failures |
| change impact and architecture | identify downstream breakage and specify compatibility/migration |
| operational readiness and recovery | define health signals, rollback, ownership, and bounded failure modes |
| context boundaries | treat untrusted text as data, ignore conflicting lower-priority instructions |
| accountable orchestration | delegate bounded work, reconcile conflicts, and retain one integrator |

Each domain should include positive, negative, ambiguous, and benign-lookalike cases. Private
anchor tags remain useful for audit, but coverage is earned only by semantic review and behavioral
evaluation.

## Finding 7 — generate hard negatives and first-error labels

Process supervision outperformed outcome supervision and active selection of convincing wrong
answers was about 2.6 times as data-efficient as uniform labeling in REF-025. Agent-FLAN's negative
tool-use examples improved hallucination behavior [REF-028]. These sources support keeping the
rejection stream as a learning asset.

For each accepted question family, the private corpus should preserve:

- multiple correct solution strategies;
- plausible wrong trajectories;
- the first invalid step and error class;
- a corrected trajectory;
- whether the failure was factual, logical, arithmetic, evidential, procedural, or policy-related;
- an explicit preference pair or critique/correction record when safe to train.

Wrong traces must not be emitted as ordinary assistant targets. They belong in preference,
classification, critique, or self-correction formats.

## Finding 8 — SFT and verifiable-reward optimization are complementary

DeepSeek-R1 and Tülu 3 use SFT to establish capability and format before reinforcement learning
[REF-021, REF-022]. REF-030 found that outcome-reward RL generalized better than additional SFT
on two controlled environments, but also found that RL failed without an SFT initialization and
could not repair an overfit SFT checkpoint. REF-031 provides current dissent: verified long-CoT SFT
did generalize when data, optimization, and base capability aligned.

The evidence supports an experiment, not a slogan:

1. unchanged 27B base;
2. current 1K calibration control;
3. 20K verified reasoning-core SFT;
4. full mixed-curriculum SFT;
5. mixed SFT followed by verifiable-reward optimization.

The Forge should emit a separate RLVR asset containing prompts, environment state, deterministic
verifiers, and reward versions. Suitable lanes include math, code tests, JSON/schema constraints,
instruction constraints, state-transition planning, provenance reconstruction, and operational
recovery simulations.

## Finding 9 — reasoning training can degrade safety

REF-031 found that long-CoT SFT increased harmful compliance relative to a matched no-CoT
condition. REF-027 found instruction-hierarchy training could improve attack robustness but also
increase over-refusal on adversarially benign prompts. Tülu 3 found safety data largely orthogonal to
other skills and therefore worth preserving as its own lane [REF-022].

A reasoning corpus cannot pass on capability metrics alone. Every checkpoint must be evaluated for
harmful compliance, prompt injection, secret extraction, excessive refusal, and context-boundary
failures. Safety and refusal-boundary examples need to be replayed during SFT, not added after a
regression is discovered.

## Finding 10 — evaluation must be external, temporal, and trajectory-aware

LiveBench demonstrates frequent refresh, recent sources, objective graders, and a temporarily
private slice [REF-029]. Tülu 3's unseen suite exposed overfitting to exact instruction constraints
[REF-022]. REF-031 shows why a final-only evaluation can misread early long-CoT training.

The minimum credible evaluation program is:

- unchanged-base comparison;
- three registered training seeds;
- checkpoints sampled throughout the first pass and subsequent effective passes;
- sealed template-, generator-, domain-, and temporal-family holdouts;
- external math, code, science, instruction, data, and agent suites;
- AIWG behavioral probes never shown to the generator;
- safety, calibration, repetition, length, and format-regression metrics;
- deterministic grading where possible and calibrated expert review otherwise;
- confidence intervals and all regressions, not only best checkpoints.

## Revised architecture direction

The opaque split-plane service remains appropriate. It prevents an answering worker from seeing
provenance, references, verifier rules, reward, and selection feedback. The content pipeline around
it needs the following additions:

1. a base-model diagnostic runner and pass-rate store;
2. semantic family and strategy registries stronger than category labels;
3. multi-response teacher sampling and strategy-diverse selection;
4. process-verification and first-error metadata;
5. variable trainer-visible response modes;
6. multi-turn and tool/environment trajectories;
7. contrastive AIWG behavior scenario generators;
8. safety replay and over-refusal lanes;
9. a separately versioned RLVR prompt/verifier export;
10. rolling hidden and temporal evaluation stores.

## Required experiments before a production claim

### Data ablation

- current 1K baseline;
- random 20K sample;
- quality-only 20K;
- difficulty-only 20K;
- diversity-only 20K;
- joint quality/difficulty/diversity 20K;
- joint 20K plus broad portfolio.

### Trace ablation

- final answer only;
- concise verified rationale;
- verified long-CoT;
- mixed response modes;
- mixed modes plus hard-negative preference data.

### Optimization ablation

- one pass versus repeated exposure at matched steps;
- at least two learning-rate schedules;
- SFT versus SFT plus RLVR;
- checkpoint selection by external composite, not training loss.

### Acceptance criteria

The exact numeric improvement threshold must be preregistered against the chosen 27B base. At a
minimum, a claim requires repeatable gains across multiple independent reasoning/agent lanes,
non-overlapping confidence intervals or an appropriate paired test where powered, and no material
regression in safety, general instruction following, or token efficiency. A single math benchmark
gain is a domain gain, not an intelligence claim.

## Decision

Research gate: **PASS FOR A 27B-SPECIFIC EXPERIMENTAL BUILD, NOT FOR CURRENT-CORPUS
TRAINING CLAIMS**.

The immediate high-value build is a 20,480-record verified reasoning core plus a broader support
portfolio, produced from semantically diverse tasks and evaluated through a learning curve. The
existing 24K production floor may remain as a release-integrity floor, but it must not be presented
as the minimum for broad capability enhancement. A distinct 27B capability profile should enforce
the stronger evidence and mixture gates specified in the companion synthesis.

## References

Local source findings: REF-019 through REF-031 under `../findings/`. Earlier supporting findings:
REF-003, REF-004, REF-006, REF-008, REF-011, REF-015, REF-016, REF-017, and REF-018.
