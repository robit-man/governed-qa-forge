# Synthetic Q/A Corpus Research Induction

Status: complete for the pre-scaffold research gate  
Date: 2026-09-25  
Scope: evidence-based design of a governed, categorical, several-thousand-record synthetic Q/A corpus for supervised fine-tuning

## Deliverables

- [Source register](sources/INDEX.md)
- [Fixity manifest](fixity-manifest.json)
- [Evidence synthesis](synthesis/synthetic-qa-corpus-design-principles.md)
- [Best-practices audit](reports/2026-09-25-synthetic-qa-best-practices-audit.md)
- [GRADE assessments](quality-assessments/)
- [Source findings](findings/)
- [Provenance records](provenance/records/)

## Decision

Research gate: **PASS WITH REQUIRED CONTROLS**.

The generator may be scaffolded next only if its schema and pipeline make these controls structural rather than optional:

1. coverage-cube planning and human-reviewed seeds;
2. candidate over-generation followed by staged filtering;
3. record-level source, teacher, prompt, license, and review lineage;
4. exact, semantic, benchmark, and family-level decontamination;
5. lineage-grouped train/validation/test allocation before generation;
6. deterministic verification plus calibrated independent review;
7. frozen authoritative evaluation sets kept outside the generation loop;
8. versioned releases with data cards, checksums, rejection ledgers, and reproducible manifests.

No model generation, training workload, container, service, or CUDA allocation was started during this pass.
