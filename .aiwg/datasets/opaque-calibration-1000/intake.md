# Dataset Intake — Opaque Calibration 1000

- **Dataset ID:** `opaque-agent-calibration`
- **Run ID:** `opaque-calibration-1000`
- **Date:** 2026-09-25
- **Owner:** Governed QA Forge project team
- **Purpose:** Calibrate the blind agent service, transactional queue, independent deterministic verifiers, decontamination path, coverage selection, and review boundary at a 1,000-selected-record scale.
- **Target use:** Dataset pipeline evaluation only.
- **Prohibited use:** Production fine-tuning before independent review; high-stakes decisions; representation as human-authored production data.
- **Source class:** Project-authored deterministic task families.
- **Teacher authorization:** The operator explicitly authorized Codex to act as teacher for this calibration pass.
- **Review status:** Pending independent review; the teacher did not act as reviewer.

## Composition

Ten categories contain 100 independent lineages each: inventory reconciliation, financial arithmetic, linear equations, proportional allocation, robust statistics, dependency planning, set accounting, structured aggregation, deductive logic, and program tracing. Each lineage creates three controlled question presentations for 3,000 blind worker tasks; selection is capped at one record per lineage.

## Privacy and rights

The corpus contains no personal data, private source payload, or acquired third-party text. The source registry records a project-authored snapshot and MIT-compatible redistribution basis. Runtime corpora and the SQLite broker remain Git-ignored.

## Acceptance criteria

- 3,000 worker submissions and raw candidates;
- zero validation or verifier failures;
- exactly 1,000 selected, unique lineages;
- exactly 100 selected records per category;
- state `awaiting_review`, with no release created.
