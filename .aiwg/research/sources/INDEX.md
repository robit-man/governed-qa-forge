# Acquired source register

All local source PDFs were acquired on 2026-09-25, extracted to `../working/fulltext/`, and pinned by SHA-256 in `../fixity-manifest.json`.

| Ref | Year | Source | Primary relevance | GRADE |
|---|---:|---|---|---|
| REF-001 | 2023 | [Self-Instruct](https://arxiv.org/abs/2212.10560) | bootstrapping, filtering, seed design | High |
| REF-002 | 2024 | [WizardLM / Evol-Instruct](https://arxiv.org/abs/2304.12244) | controlled difficulty and breadth evolution | High |
| REF-003 | 2023 | [Orca](https://arxiv.org/abs/2306.02707) | progressive teacher traces and system diversity | Moderate |
| REF-004 | 2023 | [LIMA](https://arxiv.org/abs/2305.11206) | quality-over-volume evidence | High |
| REF-005 | 2025 | [Magpie](https://arxiv.org/abs/2406.08464) | prompt-free candidate generation and selection | High |
| REF-006 | 2024 | [DEITA](https://arxiv.org/abs/2312.15685) | complexity, quality, and diversity selection | High |
| REF-007 | 2024 | [Diversity Measurement and DPP Selection](https://arxiv.org/abs/2402.02318) | diversity metrics and subset selection | Moderate |
| REF-008 | 2022 | [Deduplicating Training Data](https://arxiv.org/abs/2107.06499) | exact/near-duplicate removal and memorization | High |
| REF-009 | 2024 | [The Curse of Recursion](https://arxiv.org/abs/2305.17493) | recursive synthetic-data collapse risk | High |
| REF-010 | 2024 | [Is Model Collapse Inevitable?](https://arxiv.org/abs/2404.01413) | accumulating real data alongside synthetic data | Moderate |
| REF-011 | 2024 | [Judging the Judges](https://arxiv.org/abs/2406.07791) | position bias in LLM evaluation | Moderate |
| REF-012 | 2023 | [Textbooks Are All You Need](https://arxiv.org/abs/2306.11644) | constrained high-quality synthetic curricula | Moderate |
| REF-013 | 2021 | [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) | dataset documentation and accountability | High |
| REF-014 | 2024 | [Persona Hub](https://arxiv.org/abs/2406.20094) | persona-conditioned diversity generation | Moderate |
| REF-015 | 2024 | [#InsTag](https://arxiv.org/abs/2308.07074) | fine-grained instruction taxonomy and sampling | High |
| REF-016 | 2024 | [Selective Reflection-Tuning](https://arxiv.org/abs/2402.10110) | targeted teacher revision | High |
| REF-017 | 2023 | [Quality-Diversity Instruction Tuning](https://arxiv.org/abs/2311.14736) | joint quality/diversity optimization | High |
| REF-018 | 2023 | [The False Promise of Imitating Proprietary LLMs](https://arxiv.org/abs/2305.15717) | limits of style imitation and shallow distillation | High |
| REF-019 | 2025 | [s1: Simple Test-Time Scaling](https://arxiv.org/abs/2501.19393) | compact 32B reasoning SFT and joint data selection | Moderate |
| REF-020 | 2025 | [LIMO: Less Is More for Reasoning](https://arxiv.org/abs/2502.03387) | 32B math reasoning from 800 selected traces | Moderate |
| REF-021 | 2025 | [DeepSeek-R1](https://arxiv.org/abs/2501.12948) | mixed reasoning distillation and reinforcement learning | Moderate |
| REF-022 | 2024 | [Tülu 3](https://arxiv.org/abs/2411.15124) | broad SFT, preference tuning, RLVR, and unseen evaluation | High |
| REF-023 | 2022 | [Scaling Instruction-Finetuned Language Models](https://arxiv.org/abs/2210.11416) | task-family diversity, model scale, and CoT mixture | High |
| REF-024 | 2023 | [Distilling Step-by-Step](https://aclanthology.org/2023.findings-acl.507/) | rationale supervision versus answer labels | High |
| REF-025 | 2023 | [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) | process supervision, first-error labels, and hard negatives | Moderate |
| REF-026 | 2024 | [OpenMathInstruct-2](https://arxiv.org/abs/2410.01560) | teacher quality, unique-question diversity, and concise traces | Moderate |
| REF-027 | 2024 | [The Instruction Hierarchy](https://arxiv.org/abs/2404.13208) | latent instruction-priority behavior through contrastive data | Moderate |
| REF-028 | 2024 | [Agent-FLAN](https://arxiv.org/abs/2403.12881) | agent reasoning, tool-use negatives, and format overfitting | Moderate |
| REF-029 | 2024 | [LiveBench](https://arxiv.org/abs/2406.19314) | rolling temporal evaluation with objective grading | High |
| REF-030 | 2025 | [SFT Memorizes, RL Generalizes](https://arxiv.org/abs/2501.17161) | controlled SFT/RL generalization comparison and dissent | Moderate |
| REF-031 | 2026 | [Rethinking Generalization in Reasoning SFT](https://arxiv.org/abs/2604.06628) | direct 27B long-CoT SFT, optimization trajectory, and safety | Moderate |

## Supplementary governance authorities

These live authoritative references informed the governance requirements in the audit; they are linked rather than copied into the local evidence cache:

- [Data Cards](https://research.google/pubs/data-cards-purposeful-and-transparent-dataset-documentation-for-responsible-ai/)
- [Data Statements for NLP](https://aclanthology.org/Q18-1041/)
- [W3C PROV-O](https://www.w3.org/TR/prov-o/)
- [MLCommons Croissant 1.1](https://docs.mlcommons.org/croissant/docs/croissant-spec-1.1.html)
- [NIST AI 600-1 Generative AI Profile](https://doi.org/10.6028/NIST.AI.600-1)
- [NIST SP 800-188](https://doi.org/10.6028/NIST.SP.800-188)
- [EU AI Act consolidated text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1689-20260727)
- [U.S. Copyright Office AI Copyrightability Report](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf)
- [Croissant dataset metadata requirements](https://docs.mlcommons.org/croissant/docs/croissant-spec-1.1.html)

Provider terms are deliberately not generalized. Every teacher provider must have a dated, hashed terms snapshot and explicit authorization review before generation.
