# AIWG Behavior Anchor Induction

**Date:** 2026-09-25  
**Profile:** `qaforge-aiwg-latent-behavior-v1`  
**Installed source version:** `aiwg-cli-2026.5.11`

## Purpose

This induction turns recurring AIWG decision behaviors into governed training targets without
placing AIWG names, skills, rules, or source identifiers in worker prompts or trainer-visible
messages. The source artifacts were resolved with `aiwg show TYPE NAME --json`; the UTF-8 bytes of
each returned `content` field were fixed by SHA-256. The resulting principles are paraphrased
behavior contracts, not copied framework instructions.

## Source bindings

| Behavior domain | Canonical AIWG artifact | SHA-256 |
|---|---|---|
| requirements-and-acceptance | `agent:requirements-analyst` | `e014bbf931c340674a2018c42bc5c2a14d8052c7f823da09f50d0cfc0907f77e` |
| evidence-before-assertion | `skill:research-quickref` | `76c6931284d3051ddd065dc4c617984f82ad3bf82d0b82defb57abc8bd95ecad` |
| provenance-and-traceability | `skill:auto-provenance` | `09763b3e92c588faea90728316a299e24595ff3768f164c8db5553a681fb9298` |
| threat-modeling-and-least-authority | `skill:security-assessment` | `c7efeab34d544c4e77bdafcf5a7577ed363cd5337eba928a20e9c475e9913113` |
| independent-verification | `skill:best-practices-audit` | `8eb4e772536a58344b73abfb342d4f1684e5a51528cd489fd40f45278575376c` |
| test-and-quality-gates | `skill:flow-test-strategy-execution` | `cdd88da3123e197914e1d021053075ed19c20fe65b1f8a36e93c074b9b490066` |
| change-impact-and-architecture | `skill:architecture-evolution` | `31d0b8fe956064e97af7b8879cf424aa86c3b2fc6d2552dc21c2dc4b9bdeef13` |
| operational-readiness-and-recovery | `agent:deployment-manager` | `0bc7fa28a9c467f1f93f9360ad106a59c3e8a887e4f29517ea13a18230b86f0d` |
| context-boundaries-and-poisoning-resistance | `rule:skill-discovery` | `71854a7d3fb47de3ac86576448babd21f528293cfdf71a492095eaede069718b` |
| orchestration-and-accountable-integration | `skill:parallel-dispatch` | `eeca9f7131673f9bdaee4a5ab58e0374f1781572ebfb79553b3e27c06bf46654` |

## Training boundary

Curators express each behavior as an ordinary scenario that requires the corresponding decision
pattern. A reviewer sees the scenario, derivation, final answer, and full canonical principle, then
attests semantic alignment. The compiler emits only user and assistant messages. Anchor IDs,
domains, principles, source references, hashes, verifier details, and review outcomes remain in
private governance inputs and release sidecars.

Tag presence is not treated as evidence of behavior. Production eligibility requires exact
registry equality with the code-owned profile, per-record semantic-alignment attestation, coverage
of all ten domains, and independent release verification of those bindings.
