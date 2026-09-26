# Threat Assessment: CR-002 Production Reasoning Minimum

**Profile:** balanced  
**Date:** 2026-09-25  
**Issue:** #4  
**Decision:** controls implemented; final delivery verification pending

| Threat | Impact | Control | Verification |
|---|---|---|---|
| Derivation changed after review | invalid learning signal | content digest hashes exact messages; reviewed row may differ only by review object | derivation-binding and sealed-selection tests |
| Derivation influences final-answer verifier | false correctness | final answer remains a separate structured field | verifier tests use only `answer` |
| Calibration relabeled as training data | under-scale, weak corpus release | sealed `corpus_class`; unconditional calibration rejection | permanent-non-release test |
| Operator lowers production size | inadequate corpus | fixed code constants plus release and verification checks | exact/one-below policy tests |
| AIWG/source mechanics enter model context | reward hacking or scaffolding imitation | latent rendering gate; messages-only data; sidecar provenance | portable-release and worker preflight tests |
| Worker API migration loses or misclassifies responses | incomplete or corrupt runs | additive SQLite migration labels the contract and atomically requeues unfinished answer-only submissions | broker migration test |
| Inline metadata reaches trainer | context contamination | standardized messages-only split files | release schema test |
| Fabricated anchor provenance | untrusted behavioral source | registry must exactly match the code-owned profile of hashed AIWG artifacts; snapshot, authorization, redistribution, target-use, and license checks remain mandatory | canonical-registry mutation tests |
| Tag-only behavior coverage | unrelated content passes by carrying an anchor ID | immutable review packets show canonical principles and production requires explicit semantic-alignment attestation | packet-tamper and production-review tests |

## Residual risk

Human attestation can be dishonest or mistaken, scenario content can still reveal recognizable
framework ideas, and a model may learn superficial answer formatting rather than general behavior.
The production floor is an engineering gate, not proof of convergence. Base-vs-tuned evaluation,
three-seed training runs, held-out suites, ablations, and external review remain required before any
claim of improved intelligence.
