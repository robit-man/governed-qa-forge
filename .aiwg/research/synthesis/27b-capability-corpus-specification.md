# 27B Capability Corpus Specification

**Status:** inducted research specification; implementation changes not yet applied

**Target:** dense language model in the 27B–32B class

**Primary objective:** transferable gains in reasoning and agent decision behavior without material
regression in general capability, safety, calibration, or token efficiency

## Normative interpretation

The words **must**, **should**, and **may** express research-derived requirements, strong
recommendations, and optional methods for the next implementation pass. Numeric mixture ranges
not directly established by a cited study are labeled **experimental priors** and must be ablated.

## Corpus classes

### Calibration

The existing 1,000-record corpus remains a transport and opacity calibration only. It must never be
promoted to a production capability corpus or used as evidence of model improvement.

### Capability primer

A compact set of 400–2,500 examples may be used to test whether the exact base can express a
narrow capability already supported by pretraining. It must be model-calibrated, independently
verified, semantically diverse, and evaluated on external OOD families. It is not a broad corpus.

### 27B reasoning core

The first research-backed target is 20,480 accepted verified long-reasoning examples. This is based
on the direct dense-model study in REF-031 and is a target for the experimental profile, not a claim
that 20,480 is universally optimal.

### 27B full capability mixture

The full mixture combines the reasoning core with broad instruction, code/tool, evidence,
AIWG-behavior, safety, and retention data. The first build should target 60K–100K accepted training
records as an experimental prior, then scale or reweight based on external learning curves.

## Gate A — target-model diagnostic

Before generation, the operator must pin the exact base checkpoint, tokenizer, chat template,
context length, and intended SFT method. The diagnostic runner must:

1. sample at least several independent responses for each probe;
2. calculate pass@k or an equivalent objective success rate;
3. store response-length, format, refusal, and error-mode distributions;
4. identify skills already saturated, inconsistently expressed, and absent;
5. reject the assumption that parameter count alone predicts learnability.

Candidate selection should emphasize the solvable-but-unreliable frontier. The exact pass-rate bands
are experimental and must be recorded, not embedded as research fact.

## Gate B — semantic coverage model

Every seed must have a semantic-family identity derived from stable task structure, not its surface
wording. At minimum the family representation must bind:

- capability lane and subskill;
- reasoning operations and dependency graph;
- evidence sources or environment state;
- valid solution strategies;
- expected failure classes;
- verifier type;
- tool availability and authority boundary;
- output/interaction mode;
- generation program and parent family.

All paraphrases, parameter changes, teacher variants, and descendant tasks remain in one split.
Release reports must expose the number and entropy of semantic families in aggregate without
leaking private generation context into trainer messages.

## Gate C — capability portfolio

The production taxonomy must extend beyond the current ten simple categories. It must cover at
least the following capability lanes with genuinely different task families:

1. mathematical and quantitative reasoning;
2. algorithmic reasoning and executable code;
3. scientific reasoning and data analysis;
4. logic, constraint satisfaction, and counterexample construction;
5. planning, state tracking, and replanning;
6. requirements analysis and acceptance criteria;
7. evidence synthesis, uncertainty, and source grounding;
8. provenance and traceability reconstruction;
9. testing, critique, debugging, and independent verification;
10. tool/API selection, argument construction, and result interpretation;
11. architecture/change-impact and compatibility reasoning;
12. operational diagnosis, release decisions, rollback, and recovery;
13. instruction hierarchy, context poisoning, and least authority;
14. bounded delegation, conflict reconciliation, and accountable integration;
15. general instruction following, concise answers, and conversational retention;
16. safety, refusal boundaries, and benign lookalikes.

The AIWG-derived lanes must be enacted by the task. A tag on unrelated arithmetic cannot satisfy
coverage.

## Gate D — candidate generation

For every deep-reasoning prompt, the system must generate multiple candidate trajectories from one
or more strong, authorized teachers. Generation must intentionally vary solution strategy rather than
temperature alone.

Candidate generation should include:

- direct derivation;
- decomposition into subproblems;
- constructive and contradiction strategies where applicable;
- tool-assisted or executable solution;
- verification and alternative check;
- recovery after an injected mistake or failed tool;
- concise expert solution after exploration.

The system must preserve teacher, prompt, sampling, trace, and parent hashes privately. The opaque
worker must continue to receive only the self-contained task and interaction state.

## Gate E — answer and process verification

Final-answer verification remains mandatory. Long or plausible reasoning cannot compensate for an
incorrect final result.

For multi-step records, process review must additionally record:

- whether every consequential step is valid;
- the first invalid or unsupported step, if any;
- whether the reasoning relies on the supplied evidence only;
- whether a stated check is independent of the original method;
- whether uncertainty is calibrated;
- whether the conclusion follows without hidden assumptions.

Deterministic, executable, symbolic, or schema verifiers should be preferred. Model judges may
triage but must be calibrated against expert labels and cannot be the sole authority for high-risk or
open-ended records.

## Gate F — response-mode diversity

The compiler must no longer require every trainer-visible completion to use one universal reasoning
wrapper. Private structured reasoning remains mandatory for review, but the emitted target should be
one of several registered modes:

- direct answer;
- answer with concise justification;
- structured proof or derivation;
- deep exploratory reasoning with recovery;
- tool call and observation trajectory;
- critique followed by correction;
- clarification request;
- refusal with a safe alternative;
- plan, execution report, or decision memo;
- machine-readable output where the task genuinely requires it.

Mode choice must depend on task needs. Length should be normalized by task complexity, and
unnecessary verbosity should reduce candidate quality.

## Gate G — hard negatives and contrastive behavior

Rejected candidates are evidence. The private system must retain plausible failures and label their
first error. A governed transformation may turn them into:

- chosen/rejected preference pairs;
- error-localization tasks;
- critique-and-repair examples;
- verifier training examples;
- safe/unsafe and call/no-call contrasts.

Incorrect trajectories must never appear as ordinary assistant targets. Negative examples must be
balanced with positive and benign-lookalike cases to avoid over-refusal or tool avoidance.

## Gate H — AIWG latent-behavior construction

Each of the ten canonical AIWG behavior domains must have scenario families that include:

- a clear positive case;
- a tempting but wrong shortcut;
- an ambiguous boundary case;
- an adversarial or poisoned-context case where relevant;
- a benign lookalike that should still be handled normally;
- an independently verifiable final decision.

Reviewers must attest semantic alignment against the canonical private principle. The behavioral
test suite must use novel scenarios and withhold at least one transformation/attack family per
domain.

## Gate I — safety and capability retention

Reasoning SFT must be mixed with safety and general-retention examples from the beginning. Every
checkpoint must be evaluated for:

- harmful request compliance;
- prompt injection and system-secret extraction;
- context-data/instruction separation;
- excessive refusal on benign requests;
- false tool calls and unauthorized actions;
- truthfulness and unsupported assertions;
- ordinary chat and direct-answer quality;
- token efficiency and repetitive reasoning.

Any critical safety regression blocks the checkpoint regardless of reasoning gain.

## Gate J — split and decontamination

Split assignment must precede all generation and operate at the semantic-family level. The system
must check:

- exact canonical equality;
- token-shingle overlap;
- paraphrase/semantic overlap in a manually reviewed similarity band;
- generator/program identity;
- shared source passage or environment seed;
- protected benchmark and benchmark-derived content;
- cross-round ancestry.

The external temporal evaluation suite must be physically and logically outside the generation
service. Its content, verifier details, and scores must never enter teacher or worker context.

## Gate K — trainer outputs

The primary SFT release remains standardized conversational JSONL, with exactly trainer-visible
messages and no private labels. The sidecar must bind the message hash to all governance and
research fields.

The release builder should support target-specific materializations:

- ordinary chat messages;
- target-native reasoning-channel messages if the trainer and model support them;
- tool-call/tool-result conversations;
- preference pairs in a separate artifact;
- RLVR prompts and verifier packages in a separate artifact.

The same record must not be materialized twice into one training run unless the sampling plan
explicitly treats the forms as one family.

## Gate L — 27B training experiment

The first credible experiment must compare:

| Arm | Purpose |
|---|---|
| unchanged base | establishes all capability and safety baselines |
| current 1K calibration | detects pure format/template effects |
| 2.5K reasoning subset | small-primer learning point |
| 20,480 reasoning core | direct evidence-aligned SFT arm |
| full mixed corpus | broad capability and retention arm |
| full mixed corpus + RLVR | tests generalization from verifiable rewards |

All trainable arms must use seeds 17, 29, and 47 unless a preregistered compute-limited pilot is
explicitly labeled exploratory. Report all runs.

Training must save enough checkpoints to observe an early length surge, performance dip, recovery,
and possible late overfitting. One final checkpoint and training loss are insufficient.

## Gate M — evaluation and claims

Evaluation must include:

- external math, code, science, logic, and data analysis;
- held-out agent tools and environments;
- novel AIWG behavioral cases;
- general instruction following and open-ended utility;
- temporal and generator-held-out sets;
- safety, injection, refusal, and authority boundaries;
- calibration, uncertainty, answer length, repetition, and compute cost.

The project may claim a narrow capability gain when that lane improves repeatably without critical
regression. It may claim broad capability improvement only when gains repeat across several
independent lanes and survive family/temporal holdouts. It must not claim increased intelligence from
training loss, acceptance rate, in-family test rows, or one benchmark.

## Initial experimental mixture prior

This is a starting hypothesis to ablate, not an evidence-defined optimum:

| Lane | Approximate share by training tokens |
|---|---:|
| hard verified reasoning across math/code/science/logic/data | 35–45% |
| planning, tools, debugging, architecture, and operations | 15–20% |
| evidence, provenance, requirements, verification, and orchestration | 15–20% |
| general/direct/replay instruction data | 15–25% |
| safety, instruction hierarchy, refusal boundaries, and negative contrasts | 10–15% |

Sampling must be token-aware because one long-CoT record can carry orders of magnitude more loss
tokens than a direct answer. Shares should be tuned by external evaluation, not fixed permanently.

## Stop conditions

Generation or training must stop for review if:

- semantic-family diversity plateaus while row count grows;
- verifier disagreement exceeds the calibrated review band;
- teacher-error clusters repeat across accepted records;
- response length rises without external capability recovery;
- safety or instruction-following drops materially;
- the tuned model begins emitting the private scaffolding or universal response format;
- hidden-set gains disappear under generator or temporal holdout;
- a source, teacher, or provider authorization becomes invalid.

## Implementation impact

The current service boundary, authorization registries, provenance sidecars, and immutable release
builder remain useful. Implementation must add model diagnostics, semantic-family identities,
process labels, response modes, negative/preference artifacts, RLVR exports, safety replay, and
rolling evaluation. The fixed `qaforge-reasoning-sft-minimum-v1` remains an integrity floor until a
separate code change is approved; it must not be represented as this 27B profile.

## Evidence map

- compact 32B primers: REF-019, REF-020;
- 32B mixed distillation and RL: REF-021;
- broad portfolio and RLVR: REF-022, REF-023;
- rationale/process supervision: REF-024, REF-025;
- diversity, teacher quality, and verbosity: REF-026;
- latent instruction hierarchy and negative agent examples: REF-027, REF-028;
- external temporal evaluation: REF-029;
- SFT/RL boundary: REF-030, REF-031;
- direct 27B conditional-generalization evidence and safety cost: REF-031.
