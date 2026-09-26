# Synthetic Q/A Corpus Research Induction

Status: complete for the pre-scaffold and 27B capability research gates
Date: 2026-09-25  
Scope: evidence-based design of a governed synthetic corpus, including a capability-enhancement profile for dense 27B-class models

## Deliverables

- [Next-pass implementation directive](NEXT-PASS.md)
- [Source register](sources/INDEX.md)
- [Fixity manifest](fixity-manifest.json)
- [Evidence synthesis](synthesis/synthetic-qa-corpus-design-principles.md)
- [Best-practices audit](reports/2026-09-25-synthetic-qa-best-practices-audit.md)
- [27B capability corpus specification](synthesis/27b-capability-corpus-specification.md)
- [27B capability dataset audit](reports/2026-09-25-27b-capability-dataset-audit.md)
- [GRADE assessments](quality-assessments/)
- [Source findings](findings/)
- [Provenance records](provenance/records/)

## Decision

Research gate: **PASS WITH REQUIRED CONTROLS**.

27B capability gate: **PASS FOR AN EMPIRICAL 27B-SPECIFIC BUILD, NOT FOR A
CAPABILITY CLAIM FROM THE CURRENT CORPUS**.

The generator may be scaffolded next only if its schema and pipeline make these controls structural rather than optional:

1. coverage-cube planning and human-reviewed seeds;
2. candidate over-generation followed by staged filtering;
3. record-level source, teacher, prompt, license, and review lineage;
4. exact, semantic, benchmark, and family-level decontamination;
5. lineage-grouped train/validation/test allocation before generation;
6. deterministic verification plus calibrated independent review;
7. frozen authoritative evaluation sets kept outside the generation loop;
8. versioned releases with data cards, checksums, rejection ledgers, and reproducible manifests.

For the 27B profile, the first evidence-aligned target is a 20,480-record verified reasoning core
inside a broader experimental curriculum. The current 1,000-record corpus remains a service and
format calibration; the fixed 24,000-record production floor remains an integrity threshold rather
than evidence of efficacy.

No model generation, training workload, container, service, or CUDA allocation was started during this pass.

## Next pass

Implement the separate `qaforge-27b-capability-v1` profile according to
[NEXT-PASS.md](NEXT-PASS.md). The pass ends at a validated dry-run release; model-backed diagnostics,
generation pilots, and training require their own recorded authorization and entry criteria.
