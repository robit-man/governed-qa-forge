# Opaque agent service

The service lets any HTTP-capable agent framework answer Forge tasks without receiving private corpus context. It uses two separate processes and credentials over one SQLite queue.

| Plane | Default bind | Surface | Intended caller |
|---|---|---|---|
| Worker | `127.0.0.1:8411` | health, lease, submit | untrusted or semi-trusted agent worker |
| Control | `127.0.0.1:8412` | create, aggregate status, finalize, OpenAPI | trusted operator/orchestrator |

The worker application has no OpenAPI or interactive documentation route. Network separation is still required: never proxy the control port to worker networks. Run agent frameworks under a different OS/container identity with no read access to the Forge workspace, broker, seed bank, repository checkout, or control credential; API opacity cannot compensate for shared filesystem access.

## Worker contract

Authenticate every task request with `Authorization: Bearer $QAFORGE_AGENT_TOKEN`.

Lease one task:

```http
POST /v1/tasks/lease HTTP/1.1
Authorization: Bearer ...
```

A successful response contains only (questions longer than 16,384 characters are rejected when
the control plane creates the collection):

```json
{
  "task_id": "opaque-random-id",
  "lease_token": "one-time-random-secret",
  "expires_at_unix": 1790380000,
  "messages": [{"role": "user", "content": "Self-contained question"}]
}
```

`204 No Content` means no task is currently available. Submit structured derivation steps and the
separate final answer before lease expiry:

```http
POST /v1/tasks/opaque-random-id/responses HTTP/1.1
Authorization: Bearer ...
Content-Type: application/json

{
  "lease_token":"one-time-random-secret",
  "derivation":["First bounded reasoning step.","Independent check of the result."],
  "answer":"worker final answer"
}
```

The only success body is `{"status":"recorded"}` with HTTP 202. It deliberately omits correctness, verifier, score, selection, provenance, source, category, lineage, benchmark, and review information. A worker should discard the question and lease credential after receiving the receipt.

## Control contract

The control plane uses `QAFORGE_CONTROL_TOKEN`. Its OpenAPI document is available at
`/openapi.json` only with that bearer credential; interactive documentation is disabled.

```bash
curl -fsS -X POST http://127.0.0.1:8412/v1/runs \
  -H "Authorization: Bearer $QAFORGE_CONTROL_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"run_id":"run-001"}'

curl -fsS http://127.0.0.1:8412/v1/runs/run-001 \
  -H "Authorization: Bearer $QAFORGE_CONTROL_TOKEN"

curl -fsS -X POST http://127.0.0.1:8412/v1/runs/run-001/finalize \
  -H "Authorization: Bearer $QAFORGE_CONTROL_TOKEN"
```

Creating a run privately maps every seed/candidate coordinate to a randomized worker task and seals hashes of every corpus input. Finalization is allowed only after every task is submitted and the inputs and task mapping still match that seal. It then re-enters the normal Forge validation, verification, decontamination, selection, immutable-manifest, human-review, and release workflow. It never approves or releases records.

Collections record the response contract used for every answer. On upgrade from the historical
answer-only contract, unfinished submissions without derivations are atomically requeued under
`structured-derivation-v2`; finalized historical collections remain visible as legacy evidence.

Opaque and remote workers are not trusted to assert provenance. Returned citation identifiers are discarded, and the service does not append private citation markers to an answer. A citation-required seed therefore fails closed unless a future trusted grounding adapter validates the claim independently. Put the evidence needed to answer into the question, but do not expose private source identity.

## Start locally

Use independent random secrets of at least 32 characters:

```bash
export QAFORGE_AGENT_TOKEN="$(openssl rand -base64 48)"
export QAFORGE_CONTROL_TOKEN="$(openssl rand -base64 48)"

qaforge serve-agent corpus-workspace \
  --database corpus-workspace/.service/service.sqlite3 --host 127.0.0.1 --port 8411

qaforge serve-control corpus-workspace \
  --database corpus-workspace/.service/service.sqlite3 --host 127.0.0.1 --port 8412
```

Run the processes under a supervisor for durable use. The templates in `deploy/systemd/` (source
tree) or `$(python -c 'import sys; print(sys.prefix)')/share/qaforge/systemd/` (wheel install)
intentionally use two Unix accounts and two environment files so the worker process never receives
the control credential:

```bash
groupadd --system qaforge-broker
useradd --system --gid qaforge-broker --home-dir /nonexistent --shell /usr/sbin/nologin qaforge-control
useradd --system --gid qaforge-broker --home-dir /nonexistent --shell /usr/sbin/nologin qaforge-agent
install -d -o qaforge-control -g qaforge-broker -m 0710 /var/lib/qaforge/workspace
install -d -o qaforge-control -g qaforge-broker -m 0770 /var/lib/qaforge/workspace/.service
install -d -o root -g root -m 0755 /etc/qaforge
install -o qaforge-agent -g qaforge-broker -m 0600 deploy/systemd/qaforge-agent.env.example /etc/qaforge/qaforge-agent.env
install -o qaforge-control -g qaforge-broker -m 0600 deploy/systemd/qaforge-control.env.example /etc/qaforge/qaforge-control.env
```

Populate the two blank token values independently before starting either unit. Keep corpus inputs owned by `qaforge-control` with mode 0600 and their directories mode 0700. The shared `.service` directory is the only path the worker account needs; its SQLite files are group-readable/writable but contain task mappings and answers, so agent frameworks themselves must run under a third identity with no filesystem access to it. The worker unit additionally makes the configuration, registries, seeds, runs, and releases inaccessible through systemd mount restrictions. The CLI processes cap request bodies at 64 KiB and concurrent Uvicorn work at 128 requests; configure ingress rate limits per worker identity for internet-facing use.

The HTTP API—not a compromised worker service account—is the opacity boundary. Because SQLite is shared for queue coordination, code execution as `qaforge-agent` can inspect or alter broker rows. Use a separately isolated broker/RPC deployment when worker-service compromise is in scope; never grant the external agent-framework process the `qaforge-broker` group.

On control-plane startup, an interrupted finalization is reconciled: a completed, integrity-valid run is marked finalized; a finalization interrupted before any run artifact was written becomes ready for retry; partial or invalid artifacts are marked failed and retain their evidence for operator inspection.

## Agent-framework adapter

An adapter needs no Forge-specific SDK:

1. POST the lease endpoint.
2. Pass the returned `messages` array unchanged to the agent/model.
3. Extract one to sixteen concise derivation steps and a separate final answer. Do not include the
   compiler-owned `Derivation:` or `Final answer:` headings.
4. POST both fields with the lease credential.
5. Do not retry a 202 submission; request a new task.

Keep agent conversations task-local. Do not append prior tasks, receipts, control-plane status, or corpus metadata to the model context.

## Security boundary and residual limits

Opacity means the service withholds privileged context and adaptive reward signals. Collection
creation rejects a question containing an exact registered source, teacher, benchmark, seed,
lineage, behavior-anchor, or anchor-source identifier, but it cannot infer every informal name or
contextual clue. It does not make the question text unknowable, prevent category inference,
recognize public material from memory, or stop out-of-band collusion. Put self-contained evidence
in the question when necessary, but keep source identity and verifier data private. Use TLS,
ingress rate limits, and workload identity or mTLS across an untrusted network.
