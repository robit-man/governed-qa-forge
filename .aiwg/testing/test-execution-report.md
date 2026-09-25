# Test Execution Report

**Project:** Governed QA Forge

**Executed:** 2026-09-25

**Scope:** compiler, CLI, opaque service, calibration generator, distributions, and dependencies

**Evaluator:** independent test-execution lane

**Overall result:** **PASS**

## Exact command evidence

| Gate | Command | Result |
|---|---|---|
| Lock | `uv lock --check` | PASS; 62 packages resolved |
| Format | `uv run ruff format --check src tests` | PASS; 26 files |
| Lint | `uv run ruff check src tests` | PASS |
| Types | `uv run mypy src` | PASS; 18 source modules |
| Tests/coverage | `uv run pytest --cov=qaforge --cov-report=term-missing --cov-branch` | PASS; 49/49; 83.08% combined |
| Dependencies | `uv run pip-audit` | PASS; no known third-party vulnerabilities; unpublished local package skipped |
| Package | `uv build` | PASS; wheel and sdist |
| Archive content | tar/zip inventory | PASS; service, pilot, tests, docs, and systemd assets included; private runtime corpora excluded |

The independent lane hashed source, tests, `pyproject.toml`, and `uv.lock` before and after its run;
the snapshots were identical.

## Distribution hashes

```text
5bfd6c98eabcd3f70c383b1478ad16c2b790713682fd3fef1500cad44e1162f1  governed_qa_forge-0.1.0-py3-none-any.whl
9cfdee35f11ec92250dbddf76c0c7e2f24c5b52373db08f83abe06c46fc6b341  governed_qa_forge-0.1.0.tar.gz
```

These hashes identify the stable local pre-commit candidate. Rebuild from the reviewed commit for
release provenance.

## Service and calibration regression

Direct tests cover worker/control authentication and route separation, disabled worker discovery,
protected control OpenAPI, minimal task payloads, exactly-once submission, concurrent leases,
workspace-confined broker paths, strong non-placeholder tokens, pre-parse body limits, projected
question limits, private-identifier preflight, sealed input hashes, finalization restart recovery,
and finalization through the normal compiler.

The final 1,000-lineage calibration submitted 3,000 tasks and selected 1,000 unique lineages with
zero validation, verification, or contamination failures. It remains `awaiting_review`; no review
or release artifact exists.

## Observation

One Starlette deprecation warning recommends migrating FastAPI's TestClient integration to
`httpx2`. It does not affect the current pass result. Hosted multi-version CI and a real installed
systemd smoke are post-commit/deployment gates.
