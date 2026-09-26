# Teacher providers

## Deterministic fixture provider

The built-in deterministic provider exists for tests, demonstrations, and pipeline development. It creates controlled variants while preserving the seed answer. It is not a synthetic-data teacher and cannot establish production model quality.

## OpenAI-compatible provider

Configure an exact endpoint and model in `registry/teachers.yaml`:

```yaml
teachers:
  - teacher_id: teacher-main
    provider: openai-compatible
    model: exact-model-version
    base_url: https://provider.example/v1
    api_key_env: QAFORGE_TEACHER_API_KEY
    authorization_status: approved
    terms_snapshot_id: terms-2026-09-25-sha256-...
    authorization_basis: reviewed agreement section and permitted use
    allowed_target_uses:
      - supervised fine-tuning of the named target family
    reviewed_at: 2026-09-25T00:00:00Z
    reviewer: governance-owner
```

Every configured release intended use must appear verbatim in `allowed_target_uses`; otherwise
`doctor` fails closed. Credential variables must use the `QAFORGE_TEACHER_` prefix. Credentialed
endpoints must be public HTTPS URLs without userinfo; private endpoints require an explicit flag
and cannot receive ambient credentials. Host resolution is checked immediately before access.

The client calls `POST {base_url}/chat/completions` and requests bounded strict JSON containing
one to sixteen concise derivation steps plus a separate final answer. The request includes only the
user question: it excludes the seed ID, lineage,
source IDs, dimensions, reference answer, and verifier contract. The compiler, not the teacher,
wraps the unchanged seed question with a recorded,
allowlisted meaning-preserving transform. This makes the seed verifier relevant to the generated
candidate and prevents a teacher from silently replacing the task while reusing its expected
answer. Domain-specific question evolution belongs in a provider extension with an independent
solver, pinned-source entailment check, or calibrated rubric verifier.

Local vLLM, llama.cpp, and Ollama-compatible gateways can be used when they expose the same
chat-completions contract and `allow_private_endpoint` is explicitly enabled. Local mode rejects
ambient bearer credentials. This project does not start or reserve those services. Follow the host
GPU broker policy before starting CUDA workloads.

## Opaque agent-service provider

`opaque-agent-service` is a registry provider used only by the private service finalizer. Direct
`qaforge generate` calls reject it so an operator cannot accidentally bypass task collection. See
[the opaque service contract](opaque-service.md). Workers never receive private citation/source
IDs. Their citation claims are discarded rather than promoted into provenance, so citation-required
candidates fail closed unless a separately trusted grounding adapter verifies them.

## Adding a provider

Implement the `Provider` interface and return `GeneratedOutput` objects with `derivation`,
`answer`, and `citation_ids`, plus a stable prompt-template ID and SHA-256. Provider-specific
metadata must not weaken the common candidate schema or bypass authorization and release gates.
