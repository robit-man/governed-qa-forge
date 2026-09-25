# Architecture Option Matrix — Governed QA Forge

**Generated:** 2026-09-25

## Project reality

This is a public developer tool for assembling governed synthetic Q/A datasets. It must operate on thousands of records, preserve machine-auditable evidence, run locally and in CI, integrate with optional model endpoints, and remain useful without a hosted control plane.

## Priorities

| Criterion | Weight |
|---|---:|
| Quality and security | 0.40 |
| Reproducibility and reliability | 0.30 |
| Delivery speed | 0.20 |
| Cost efficiency | 0.10 |

Non-negotiable: fail-closed authorization, complete lineage, split isolation, independent verification, review before release, and reproducible manifests.

## Options

| Option | Speed | Cost | Quality/security | Reliability | Weighted score |
|---|---:|---:|---:|---:|---:|
| Python library + CLI + filesystem artifacts | 5 | 5 | 4.5 | 4.5 | **4.60** |
| Hosted API + database + web review UI | 2.5 | 2 | 4.5 | 4.5 | 3.85 |
| Workflow-engine/DAG deployment | 2 | 2.5 | 4 | 4 | 3.50 |

## Decision

Choose the Python library/CLI. It offers the smallest trusted computing base, reproducible version-controlled artifacts, straightforward integration with existing training suites, and a clean future path to a hosted reviewer without making a service mandatory.

## Trade-offs

- Filesystem review is less convenient for many simultaneous reviewers.
- Local runs rely on the operator’s storage durability.
- Optional embedding models add a heavier dependency and are not required for the base install.

These are acceptable for the initial project because correctness and inspectability matter more than centralized workflow convenience.
