# ADR-001: Modular Python CLI and immutable artifact store

- **Status:** Accepted
- **Date:** 2026-09-25

## Context

The system needs strong provenance and reproducibility but does not yet require a multi-user hosted control plane. Downstream fine-tuning tools already consume files.

## Decision

Build a typed Python library with a Typer CLI. Treat each run and release directory as an immutable evidence bundle. Use JSONL for row streams, YAML for human-authored registries/configuration, and JSON/JSON-LD/Markdown for release evidence. Remote teacher access uses a provider interface with an OpenAI-compatible implementation; the base package includes an offline deterministic provider. Built-in providers produce answers to an unchanged seed task, while the compiler owns a small allowlist of meaning-preserving question transforms. Arbitrary semantic evolution requires a domain-specific independent verifier extension.

## Consequences

- Auditing, CI, backup, diffing, and downstream integration remain simple.
- Release construction can revalidate all inputs without a database.
- A future service can wrap the library without replacing the core contracts.
- Concurrent human review is file-based in the first release.
- Review authority is an operator-controlled registry rather than hosted authentication; decisions are bound to candidate digests.
