# Next-Pass Directive: 27B Capability Profile

**Directive status:** approved research handoff for the next implementation pass

**Profile identifier:** `qaforge-27b-capability-v1`

**Research basis:** [27B capability audit](reports/2026-09-25-27b-capability-dataset-audit.md)
and [corpus specification](synthesis/27b-capability-corpus-specification.md)

## Mission

Implement a separate 27B capability-generation profile that can produce and evaluate genuinely
diverse, verified reasoning and agent-behavior training material without exposing private generation,
source, reward, or selection context to answering workers or trainer-visible records.

This pass is an implementation and pre-generation-validation pass. It does not authorize a claim of
model improvement. The current 1,000-record release remains a transport and opacity calibration.

## Fixed research decisions

The implementation must preserve these decisions:

1. The first evidence-aligned reasoning-core target is **20,480 accepted examples**.
2. The first full mixed build may target **60,000–100,000 accepted examples**, but that range is an
   experimental prior to be ablated, not a universal efficacy threshold.
3. The existing `20k/2k/2k` production minimum remains a release-integrity rule and must not be
   described as evidence that a corpus will improve a model.
4. Coverage is measured by semantic task families, strategies, verifier types, difficulty, and
   capability lanes—not category labels or row count alone.
5. AIWG reasoning behavior is taught through the substance of operational scenarios and
   contrastive decisions. Private anchor names are never trainer-visible targets.
6. The answering plane remains opaque to sources, teacher identity, rewards, verifier internals,
   selection results, and split membership.
7. Safety, authority boundaries, general instruction following, response length, and repetition are
   co-equal release gates with reasoning accuracy.

## Entry criteria

Before any model-backed diagnostic or generation run, record:

- exact base checkpoint and immutable revision;
- tokenizer, chat template, context limit, and target reasoning-channel convention;
- SFT implementation, packing policy, maximum sequence length, and loss-mask behavior;
- authorized teacher endpoints/models and dated terms or license snapshots;
- authorized source classes and evidence-handling rules;
- benchmark exclusion and decontamination registry;
- planned compute envelope and experiment budget.

Any CUDA workload must follow the workspace GPU broker policy beginning with `docker gpu discover`.

## Ordered work packages

### WP1 — Add the profile and semantic schema

Create `qaforge-27b-capability-v1` without weakening the existing production profile. Extend private
records with:

- `semantic_family_id`, parent family, generation program, and strategy identity;
- capability lane/subskill and reasoning-operation graph;
- difficulty evidence and target-model diagnostic statistics;
- response mode, tool/environment contract, and authority boundary;
- verifier type/version, candidate lineage, process verdicts, and first invalid step;
- source/license/teacher authorization, contamination status, and message hash.

All descendants and paraphrases of one semantic family must remain in one split.

### WP2 — Implement the 16-lane portfolio

Implement the capability lanes enumerated in the corpus specification. A lane counts only when its
behavior is semantically necessary to solve the task. Reject arithmetic templates carrying unrelated
behavior labels.

The family planner must report both row and token distributions, unique-family counts, family
entropy, verifier coverage, difficulty coverage, and cross-lane dependencies.

### WP3 — Add target-model diagnostics

Build a diagnostic runner that samples multiple responses per probe and stores pass-at-k, response
length, refusal, formatting, calibration, and error-mode distributions. Use it to identify the
solvable-but-unreliable frontier for the exact base model. Do not infer learnability from the 27B
parameter count.

Diagnostic outputs are evaluator-private and must not be returned through worker APIs.

### WP4 — Generate and select trajectories

For deep tasks, support multiple strategy-diverse teacher candidates. Selection must jointly consider
correctness, process validity, difficulty, semantic novelty, concision, and style independence.

Do not establish a universal `Derivation:`/`Final answer:` wrapper. Support direct answers, concise
verified rationales, deep reasoning, structured data, multi-turn interaction, tool calls, and bounded
refusals. Sampling quotas must be token-aware.

### WP5 — Add process verification and negative data

Implement deterministic verification where possible and calibrated independent review otherwise.
Preserve rejected candidates privately with first-error and failure-class metadata. Materialize hard
negatives only into separate preference or process-supervision artifacts; never mix them into SFT as
correct assistant answers.

Create a separately versioned RLVR bank containing prompts, deterministic verifiers, timeouts,
sandbox requirements, and reward definitions.

### WP6 — Compile AIWG behavior into latent examples

Add contrastive scenario families for:

- requirements and acceptance-criteria reconciliation;
- evidence gaps, provenance, uncertainty, and citation discipline;
- independent verification, counterexamples, testing, and critique;
- architecture/change impact and compatibility;
- operational diagnosis, rollback, recovery, and release decisions;
- instruction hierarchy, contextual poisoning, and least authority;
- bounded delegation, conflict reconciliation, and accountable integration;
- safe refusal boundaries paired with benign lookalikes.

The correct behavior must follow from scenario state and consequences rather than an instruction to
imitate AIWG terminology.

### WP7 — Materialize trainer and evaluator artifacts

Keep standardized conversational JSONL as the default SFT form. Export only trainer-visible messages
to the training artifact. Bind every message hash to a private sidecar containing governance,
research, family, and verification metadata.

Add target-specific materializers for reasoning channels and tool conversations. Preference pairs,
process labels, RLVR packages, and evaluation cases must be separate versioned artifacts.

### WP8 — Register the experiment and evaluation matrix

Preregister these comparison arms:

1. unchanged base;
2. current 1K calibration;
3. 2.5K reasoning subset;
4. 20,480-example reasoning core;
5. full mixed corpus;
6. full mixed corpus plus RLVR.

Use seeds 17, 29, and 47 for claim-bearing runs. Save intermediate checkpoints capable of revealing
early performance dips, verbosity surges, later recovery, and overfitting. Select checkpoints by a
registered external composite, never training loss alone.

Evaluation must include external math, code, science, logic, data, agent/tool, AIWG behavior,
instruction-following, temporal, injection, safety, calibration, length, repetition, and compute-cost
measures. Hold out whole semantic, generator, template, domain, and temporal families.

## Required pre-generation tests

The implementation pass is complete only when tests demonstrate:

- private fields cannot enter worker payloads or trainer-visible JSONL;
- semantic-family descendants cannot cross splits;
- all 16 lanes have substantive seed families and verifier plans;
- malformed, unverified, duplicate, contaminated, and unauthorized records fail closed;
- response-mode materializers validate against target schemas;
- hard negatives cannot be emitted as positive SFT answers;
- release manifests bind public artifacts to sidecar hashes and policy versions;
- the diagnostic, SFT, preference, RLVR, and evaluation stores remain distinct;
- existing calibration and production-integrity behavior remains backward compatible.

## Stop and review conditions

Stop generation or training when semantic-family diversity plateaus, verifier disagreement exceeds
the registered band, recurring teacher-error clusters enter accepted data, response length increases
without external recovery, safety or general instruction following regresses materially, private
scaffolding appears in model output, or hidden gains disappear under generator/temporal holdouts.

## Exit gate

The next pass exits when the profile, schema migrations, planners, materializers, verification paths,
and evaluation registry are implemented and tested, and a dry-run release can be built without
starting capability training. A subsequent explicitly authorized pass may run the target-model
diagnostic and generation pilots. Capability claims remain blocked until the preregistered training
matrix produces repeatable external gains without critical regression.
