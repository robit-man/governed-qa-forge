from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from qaforge.anchors import behavior_anchor_private_identifiers
from qaforge.errors import ConfigurationError, ForgeError, GateError, ImmutableArtifactError
from qaforge.io import canonical_json, sha256_file, sha256_text, utc_now
from qaforge.models import GeneratedOutput, RunState, SeedRecord
from qaforge.pipeline import assert_run_artifacts, generate_run
from qaforge.providers import Provider
from qaforge.transforms import transform_ids, transform_question
from qaforge.workspace import Workspace

AGENT_TOKEN_ENV = "QAFORGE_AGENT_TOKEN"
CONTROL_TOKEN_ENV = "QAFORGE_CONTROL_TOKEN"
OPAQUE_PROMPT_TEMPLATE_ID = "qaforge-opaque-task-v2"
CURRENT_RESPONSE_CONTRACT = "structured-derivation-v2"
LEGACY_RESPONSE_CONTRACT = "answer-only-v1"
OPAQUE_PROMPT_CONTRACT = (
    '{"messages":[{"role":"user","content":"{transformed_question}"}],'
    '"response":{"derivation":["step"],"answer":"string"}}'
)
TOKEN_MIN_LENGTH = 32
MAX_AGENT_MESSAGE_CHARS = 16_384
MAX_REQUEST_BODY_BYTES = 65_536
TOKEN_PLACEHOLDER_MARKERS = (
    "change-me",
    "changeme",
    "example-token",
    "placeholder",
    "replace-with",
    "your-token",
)


def _validate_service_token(token: str) -> None:
    if token != token.strip():
        raise ConfigurationError("service bearer tokens cannot have surrounding whitespace")
    if len(token) < TOKEN_MIN_LENGTH:
        raise ConfigurationError(
            f"service bearer tokens must contain at least {TOKEN_MIN_LENGTH} characters"
        )
    normalized = token.casefold()
    if any(marker in normalized for marker in TOKEN_PLACEHOLDER_MARKERS):
        raise ConfigurationError("service bearer token is a known placeholder")


class RequestBodyLimitMiddleware:
    """Reject oversized request bodies before framework parsing or allocation."""

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        declared_length = headers.get(b"content-length")
        if declared_length is not None:
            try:
                if int(declared_length) > self.max_bytes:
                    await self._reject(send)
                    return
            except ValueError:
                await self._reject(send, status_code=400, detail="invalid content length")
                return

        buffered: list[Message] = []
        received = 0
        while True:
            message = await receive()
            buffered.append(message)
            if message["type"] != "http.request":
                break
            received += len(message.get("body", b""))
            if received > self.max_bytes:
                await self._reject(send)
                return
            if not message.get("more_body", False):
                break

        async def replay() -> Message:
            if buffered:
                return buffered.pop(0)
            return {"type": "http.disconnect"}

        await self.app(scope, replay, send)

    @staticmethod
    async def _reject(
        send: Send,
        status_code: int = status.HTTP_413_CONTENT_TOO_LARGE,
        detail: str = "request body too large",
    ) -> None:
        body = canonical_json({"detail": detail}).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                    (b"cache-control", b"no-store"),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})


class TaskUnavailable(ForgeError):
    """The opaque task cannot accept a response in its current state."""


@dataclass(frozen=True, slots=True)
class ServiceSettings:
    workspace: Path
    database: Path
    agent_token: str | None = None
    control_token: str | None = None
    lease_seconds: int = 900

    def __post_init__(self) -> None:
        object.__setattr__(self, "workspace", self.workspace.resolve())
        object.__setattr__(self, "database", self.database.resolve())
        try:
            self.database.relative_to(self.workspace)
        except ValueError as exc:
            raise ConfigurationError(
                "service database must be inside the selected workspace"
            ) from exc
        if self.agent_token is None and self.control_token is None:
            raise ConfigurationError("at least one service-plane bearer token is required")
        for token in (self.agent_token, self.control_token):
            if token is not None:
                _validate_service_token(token)
        if (
            self.agent_token is not None
            and self.control_token is not None
            and secrets.compare_digest(self.agent_token, self.control_token)
        ):
            raise ConfigurationError("worker and control bearer tokens must be different")
        if not 30 <= self.lease_seconds <= 86_400:
            raise ConfigurationError("lease_seconds must be between 30 and 86400")

    @classmethod
    def from_env(
        cls,
        workspace: Path,
        database: Path,
        lease_seconds: int = 900,
    ) -> ServiceSettings:
        agent_token = os.environ.get(AGENT_TOKEN_ENV, "")
        control_token = os.environ.get(CONTROL_TOKEN_ENV, "")
        if not agent_token:
            raise ConfigurationError(f"required environment variable is not set: {AGENT_TOKEN_ENV}")
        if not control_token:
            raise ConfigurationError(
                f"required environment variable is not set: {CONTROL_TOKEN_ENV}"
            )
        return cls(
            workspace=workspace,
            database=database,
            agent_token=agent_token,
            control_token=control_token,
            lease_seconds=lease_seconds,
        )

    @classmethod
    def from_agent_env(
        cls,
        workspace: Path,
        database: Path,
        lease_seconds: int = 900,
    ) -> ServiceSettings:
        agent_token = os.environ.get(AGENT_TOKEN_ENV, "")
        if not agent_token:
            raise ConfigurationError(f"required environment variable is not set: {AGENT_TOKEN_ENV}")
        return cls(
            workspace=workspace,
            database=database,
            agent_token=agent_token,
            lease_seconds=lease_seconds,
        )

    @classmethod
    def from_control_env(
        cls,
        workspace: Path,
        database: Path,
        lease_seconds: int = 900,
    ) -> ServiceSettings:
        control_token = os.environ.get(CONTROL_TOKEN_ENV, "")
        if not control_token:
            raise ConfigurationError(
                f"required environment variable is not set: {CONTROL_TOKEN_ENV}"
            )
        return cls(
            workspace=workspace,
            database=database,
            control_token=control_token,
            lease_seconds=lease_seconds,
        )


class AgentMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user"] = "user"
    content: str = Field(min_length=1, max_length=MAX_AGENT_MESSAGE_CHARS)


class TaskLease(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    lease_token: str
    expires_at_unix: int
    messages: list[AgentMessage] = Field(min_length=1, max_length=1)


class TaskSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lease_token: str = Field(min_length=32, max_length=256)
    derivation: list[str] = Field(min_length=1, max_length=16)
    answer: str = Field(min_length=1, max_length=32_768)

    @field_validator("derivation")
    @classmethod
    def normalize_derivation(cls, value: list[str]) -> list[str]:
        steps = [step.strip() for step in value]
        if any(not step or len(step) > 2048 for step in steps):
            raise ValueError("derivation steps must contain 1-2048 non-whitespace characters")
        return steps


class SubmissionReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["recorded"] = "recorded"


class CreateRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class CollectionStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    state: Literal["collecting", "ready", "finalizing", "finalized", "failed"]
    expected: int
    queued: int
    leased: int
    submitted: int
    created_at: str
    finalized_at: str | None = None
    failure: str | None = None
    response_contract: str
    forge_state: RunState | None = None


class CollectedProvider(Provider):
    """Provider bridge whose answers were collected through the blind worker plane."""

    def __init__(self, teacher: object, responses: dict[str, dict[int, GeneratedOutput]]) -> None:
        super().__init__(teacher)  # type: ignore[arg-type]
        self._responses = responses

    def generate(
        self, seed: SeedRecord, count: int, config: object
    ) -> tuple[list[GeneratedOutput], str, str]:
        del config
        self.validate_count(count)
        indexed = self._responses.get(seed.seed_id, {})
        if set(indexed) != set(range(count)):
            raise ConfigurationError(f"collection is incomplete for private seed {seed.seed_id}")
        outputs = [indexed[index] for index in range(count)]
        return outputs, OPAQUE_PROMPT_TEMPLATE_ID, sha256_text(OPAQUE_PROMPT_CONTRACT)


class TaskBroker:
    """Private mapping and transactional queue behind both API planes."""

    def __init__(self, settings: ServiceSettings) -> None:
        self.settings = settings
        self._workspace: Workspace | None = None
        self._initialize()

    @property
    def workspace(self) -> Workspace:
        if self._workspace is None:
            self._workspace = Workspace(self.settings.workspace)
        return self._workspace

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.settings.database,
            timeout=30,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 30000")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        database_existed = self.settings.database.exists()
        self.settings.database.parent.mkdir(parents=True, exist_ok=True, mode=0o770)
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS collection_runs (
                    run_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL CHECK (
                        state IN ('collecting', 'ready', 'finalizing', 'finalized', 'failed')
                    ),
                    expected_tasks INTEGER NOT NULL CHECK (expected_tasks > 0),
                    created_at TEXT NOT NULL,
                    finalized_at TEXT,
                    failure TEXT,
                    input_sha256 TEXT,
                    response_contract TEXT NOT NULL DEFAULT 'structured-derivation-v2'
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES collection_runs(run_id),
                    seed_id TEXT NOT NULL,
                    candidate_index INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    state TEXT NOT NULL CHECK (state IN ('queued', 'leased', 'submitted')),
                    lease_digest TEXT,
                    lease_expires_at REAL,
                    derivation_json TEXT,
                    answer TEXT,
                    submitted_at TEXT,
                    UNIQUE (run_id, seed_id, candidate_index)
                );

                CREATE INDEX IF NOT EXISTS idx_tasks_claim
                    ON tasks(run_id, state, lease_expires_at);
                """
            )
            connection.execute("BEGIN IMMEDIATE")
            try:
                columns = {
                    row["name"]
                    for row in connection.execute("PRAGMA table_info(collection_runs)").fetchall()
                }
                if "input_sha256" not in columns:
                    connection.execute("ALTER TABLE collection_runs ADD COLUMN input_sha256 TEXT")
                if "response_contract" not in columns:
                    connection.execute(
                        "ALTER TABLE collection_runs ADD COLUMN response_contract TEXT NOT NULL "
                        f"DEFAULT '{LEGACY_RESPONSE_CONTRACT}'"
                    )
                task_columns = {
                    row["name"] for row in connection.execute("PRAGMA table_info(tasks)").fetchall()
                }
                if "derivation_json" not in task_columns:
                    connection.execute("ALTER TABLE tasks ADD COLUMN derivation_json TEXT")
                connection.execute(
                    "UPDATE tasks SET state = 'queued', answer = NULL, submitted_at = NULL, "
                    "lease_digest = NULL, lease_expires_at = NULL "
                    "WHERE run_id IN (SELECT run_id FROM collection_runs "
                    "WHERE response_contract = ? AND state IN ('collecting', 'ready')) "
                    "AND state = 'submitted' AND derivation_json IS NULL",
                    (LEGACY_RESPONSE_CONTRACT,),
                )
                connection.execute(
                    "UPDATE collection_runs SET state = 'collecting', response_contract = ?, "
                    "failure = NULL WHERE response_contract = ? "
                    "AND state IN ('collecting', 'ready')",
                    (CURRENT_RESPONSE_CONTRACT, LEGACY_RESPONSE_CONTRACT),
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            if self.settings.control_token is not None:
                self._recover_finalizing(connection)
        if not database_existed:
            os.chmod(self.settings.database, 0o660)

    def _recover_finalizing(self, connection: sqlite3.Connection) -> None:
        rows = connection.execute(
            "SELECT run_id FROM collection_runs WHERE state = 'finalizing'"
        ).fetchall()
        for row in rows:
            run_id = row["run_id"]
            run_dir = self.workspace.run_dir(run_id)
            state_path = run_dir / "state.json"
            if state_path.is_file():
                try:
                    assert_run_artifacts(self.workspace, run_id)
                    RunState.model_validate_json(state_path.read_text(encoding="utf-8"))
                except (ForgeError, OSError, ValueError) as exc:
                    connection.execute(
                        "UPDATE collection_runs SET state = 'failed', failure = ? WHERE run_id = ?",
                        (f"interrupted finalization produced invalid artifacts: {exc}", run_id),
                    )
                else:
                    connection.execute(
                        "UPDATE collection_runs SET state = 'finalized', finalized_at = ?, "
                        "failure = NULL WHERE run_id = ?",
                        (utc_now(), run_id),
                    )
            elif run_dir.exists():
                connection.execute(
                    "UPDATE collection_runs SET state = 'failed', failure = ? WHERE run_id = ?",
                    ("interrupted finalization left partial run artifacts", run_id),
                )
            else:
                connection.execute(
                    "UPDATE collection_runs SET state = 'ready', failure = NULL WHERE run_id = ?",
                    (run_id,),
                )

    def create_collection(self, run_id: str) -> CollectionStatus:
        self.workspace.run_dir(run_id)
        report = self.workspace.doctor()
        if not report.passed:
            failures = [
                f"{item.gate}: {item.detail}"
                for item in report.checks
                if item.status.value == "fail"
            ]
            raise ConfigurationError("workspace doctor failed: " + "; ".join(failures))
        if self.workspace.run_dir(run_id).exists():
            raise ImmutableArtifactError(f"run already exists: {run_id}")

        sealed_inputs = _workspace_input_hashes(self.workspace)
        config = self.workspace.config()
        seeds = sorted(self.workspace.seeds(), key=lambda item: item.seed_id)
        behavior_anchors = self.workspace.behavior_anchors()
        private_identifiers = tuple(
            identifier.casefold()
            for identifier in {
                *[source.source_id for source in self.workspace.sources()],
                *[teacher.teacher_id for teacher in self.workspace.teachers()],
                *[benchmark.benchmark_id for benchmark in self.workspace.benchmarks()],
                *[seed.seed_id for seed in seeds],
                *[seed.lineage_id for seed in seeds],
                *behavior_anchor_private_identifiers(behavior_anchors),
            }
        )
        task_rows: list[tuple[str, str, str, int, str, str]] = []
        for seed in seeds:
            for index, transform_id in enumerate(
                transform_ids(config.generation.candidates_per_seed)
            ):
                question = transform_question(seed.question, transform_id)
                _validate_worker_question(question, seed.seed_id, private_identifiers)
                task_rows.append(
                    (
                        secrets.token_urlsafe(24),
                        run_id,
                        seed.seed_id,
                        index,
                        question,
                        "queued",
                    )
                )

        if _workspace_input_hashes(self.workspace) != sealed_inputs:
            raise GateError("workspace inputs changed while the collection was being created")

        created_at = utc_now()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "INSERT INTO collection_runs("
                "run_id, state, expected_tasks, created_at, input_sha256, response_contract"
                ") VALUES (?, 'collecting', ?, ?, ?, ?)",
                (
                    run_id,
                    len(task_rows),
                    created_at,
                    canonical_json(sealed_inputs),
                    CURRENT_RESPONSE_CONTRACT,
                ),
            )
            connection.executemany(
                "INSERT INTO tasks(task_id, run_id, seed_id, candidate_index, question, state) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                task_rows,
            )
            connection.commit()
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            raise ImmutableArtifactError(f"collection already exists: {run_id}") from exc
        finally:
            connection.close()
        return self.status(run_id)

    def lease(self, run_id: str | None = None) -> TaskLease | None:
        now = time.time()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            parameters: tuple[object, ...]
            run_filter = ""
            if run_id is None:
                parameters = (now,)
            else:
                self.workspace.run_dir(run_id)
                run_filter = " AND run_id = ?"
                parameters = (now, run_id)
            connection.execute(
                "UPDATE tasks SET state = 'queued', lease_digest = NULL, "
                "lease_expires_at = NULL WHERE state = 'leased' AND lease_expires_at < ?"
                + run_filter,
                parameters,
            )
            select_parameters: tuple[object, ...] = () if run_id is None else (run_id,)
            row = connection.execute(
                "SELECT task_id, question FROM tasks WHERE state = 'queued'"
                + (" AND run_id = ?" if run_id is not None else "")
                + " ORDER BY random() LIMIT 1",
                select_parameters,
            ).fetchone()
            if row is None:
                connection.commit()
                return None
            lease_token = secrets.token_urlsafe(32)
            expires_at = now + self.settings.lease_seconds
            lease = TaskLease(
                task_id=row["task_id"],
                lease_token=lease_token,
                expires_at_unix=int(expires_at),
                messages=[AgentMessage(content=row["question"])],
            )
            updated = connection.execute(
                "UPDATE tasks SET state = 'leased', lease_digest = ?, lease_expires_at = ? "
                "WHERE task_id = ? AND state = 'queued'",
                (_digest(lease_token), expires_at, row["task_id"]),
            )
            if updated.rowcount != 1:
                connection.rollback()
                raise TaskUnavailable("task unavailable")
            connection.commit()
            return lease
        finally:
            connection.close()

    def submit(self, task_id: str, submission: TaskSubmission) -> SubmissionReceipt:
        answer = submission.answer.strip()
        derivation = [step.strip() for step in submission.derivation]
        if not answer or not derivation or any(not step for step in derivation):
            raise TaskUnavailable("task unavailable")
        now = time.time()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT run_id FROM tasks WHERE task_id = ?",
                (task_id,),
            ).fetchone()
            if row is None:
                connection.rollback()
                raise TaskUnavailable("task unavailable")
            updated = connection.execute(
                "UPDATE tasks SET state = 'submitted', derivation_json = ?, answer = ?, "
                "submitted_at = ?, "
                "lease_digest = NULL, lease_expires_at = NULL "
                "WHERE task_id = ? AND state = 'leased' AND lease_digest = ? "
                "AND lease_expires_at >= ?",
                (
                    canonical_json(derivation),
                    answer,
                    utc_now(),
                    task_id,
                    _digest(submission.lease_token),
                    now,
                ),
            )
            if updated.rowcount != 1:
                connection.rollback()
                raise TaskUnavailable("task unavailable")
            remaining = connection.execute(
                "SELECT COUNT(*) FROM tasks WHERE run_id = ? AND state != 'submitted'",
                (row["run_id"],),
            ).fetchone()[0]
            if remaining == 0:
                connection.execute(
                    "UPDATE collection_runs SET state = 'ready' "
                    "WHERE run_id = ? AND state = 'collecting'",
                    (row["run_id"],),
                )
            connection.commit()
            return SubmissionReceipt()
        finally:
            connection.close()

    def status(self, run_id: str) -> CollectionStatus:
        self.workspace.run_dir(run_id)
        with self._connection() as connection:
            run = connection.execute(
                "SELECT * FROM collection_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if run is None:
                raise ConfigurationError(f"unknown collection: {run_id}")
            counts = {
                row["state"]: row["count"]
                for row in connection.execute(
                    "SELECT state, COUNT(*) AS count FROM tasks WHERE run_id = ? GROUP BY state",
                    (run_id,),
                )
            }
        forge_state: RunState | None = None
        state_path = self.workspace.run_dir(run_id) / "state.json"
        if state_path.exists():
            forge_state = RunState.model_validate_json(state_path.read_text(encoding="utf-8"))
        return CollectionStatus(
            run_id=run_id,
            state=run["state"],
            expected=run["expected_tasks"],
            queued=counts.get("queued", 0),
            leased=counts.get("leased", 0),
            submitted=counts.get("submitted", 0),
            created_at=run["created_at"],
            finalized_at=run["finalized_at"],
            failure=run["failure"],
            response_contract=run["response_contract"],
            forge_state=forge_state,
        )

    def finalize(self, run_id: str) -> CollectionStatus:
        self.workspace.run_dir(run_id)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            run = connection.execute(
                "SELECT state, expected_tasks, input_sha256, response_contract "
                "FROM collection_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            if run is None:
                connection.rollback()
                raise ConfigurationError(f"unknown collection: {run_id}")
            submitted = connection.execute(
                "SELECT COUNT(*) FROM tasks WHERE run_id = ? AND state = 'submitted'",
                (run_id,),
            ).fetchone()[0]
            if run["state"] != "ready" or submitted != run["expected_tasks"]:
                connection.rollback()
                raise ConfigurationError("collection is not ready for finalization")
            if run["response_contract"] != CURRENT_RESPONSE_CONTRACT:
                connection.rollback()
                raise ConfigurationError("collection uses a legacy response contract")
            try:
                sealed_inputs = self._assert_collection_binding(connection, run_id, run)
            except (ForgeError, OSError, ValueError) as exc:
                connection.execute(
                    "UPDATE collection_runs SET state = 'failed', failure = ? WHERE run_id = ?",
                    (f"{type(exc).__name__}: {exc}", run_id),
                )
                connection.commit()
                raise
            connection.execute(
                "UPDATE collection_runs SET state = 'finalizing', failure = NULL WHERE run_id = ?",
                (run_id,),
            )
            connection.commit()
        finally:
            connection.close()

        try:
            responses: dict[str, dict[int, GeneratedOutput]] = {}
            with self._connection() as read_connection:
                rows = read_connection.execute(
                    "SELECT seed_id, candidate_index, derivation_json, answer FROM tasks "
                    "WHERE run_id = ? ORDER BY seed_id, candidate_index",
                    (run_id,),
                ).fetchall()
            for row in rows:
                answer = row["answer"]
                derivation_json = row["derivation_json"]
                if not isinstance(answer, str) or not isinstance(derivation_json, str):
                    raise ConfigurationError("collection contains an empty private response")
                try:
                    output = GeneratedOutput(
                        derivation=json.loads(derivation_json),
                        answer=answer,
                        citation_ids=[],
                    )
                except (json.JSONDecodeError, ValueError, TypeError) as exc:
                    raise ConfigurationError(
                        "collection contains an invalid private derivation"
                    ) from exc
                responses.setdefault(row["seed_id"], {})[row["candidate_index"]] = output
            config = self.workspace.config()
            teacher = self.workspace.teacher(config.generation.provider_id)
            provider = CollectedProvider(teacher, responses)
            generate_run(self.workspace, run_id, provider_instance=provider)
            manifest = json.loads(
                (self.workspace.run_dir(run_id) / "run-manifest.json").read_text(encoding="utf-8")
            )
            if manifest.get("input_sha256") != sealed_inputs:
                raise GateError("generated run inputs differ from the sealed collection inputs")
            assert_run_artifacts(self.workspace, run_id)
        except Exception as exc:
            with self._connection() as failed_connection:
                failed_connection.execute(
                    "UPDATE collection_runs SET state = 'failed', failure = ? WHERE run_id = ?",
                    (f"{type(exc).__name__}: {exc}", run_id),
                )
            raise

        with self._connection() as completed_connection:
            completed_connection.execute(
                "UPDATE collection_runs SET state = 'finalized', finalized_at = ? WHERE run_id = ?",
                (utc_now(), run_id),
            )
        return self.status(run_id)

    def _assert_collection_binding(
        self,
        connection: sqlite3.Connection,
        run_id: str,
        run: sqlite3.Row,
    ) -> dict[str, str]:
        sealed_json = run["input_sha256"]
        if not isinstance(sealed_json, str):
            raise GateError("collection has no sealed input manifest")
        current_inputs = _workspace_input_hashes(self.workspace)
        if canonical_json(current_inputs) != sealed_json:
            raise GateError("workspace inputs differ from the sealed collection")

        config = self.workspace.config()
        expected_questions = {
            (seed.seed_id, index): transform_question(seed.question, transform_id)
            for seed in sorted(self.workspace.seeds(), key=lambda item: item.seed_id)
            for index, transform_id in enumerate(
                transform_ids(config.generation.candidates_per_seed)
            )
        }
        task_rows = connection.execute(
            "SELECT seed_id, candidate_index, question FROM tasks WHERE run_id = ?",
            (run_id,),
        ).fetchall()
        actual_questions = {
            (row["seed_id"], row["candidate_index"]): row["question"] for row in task_rows
        }
        if len(task_rows) != run["expected_tasks"] or actual_questions != expected_questions:
            raise GateError("collection tasks differ from the sealed seed transformation plan")
        return current_inputs


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _workspace_input_hashes(workspace: Workspace) -> dict[str, str]:
    paths = {
        "config": workspace.config_path,
        "sources": workspace.registry_dir / "sources.yaml",
        "teachers": workspace.registry_dir / "teachers.yaml",
        "reviewers": workspace.registry_dir / "reviewers.yaml",
        "taxonomy": workspace.registry_dir / "taxonomy.yaml",
        "seeds": workspace.seeds_path,
    }
    behavior_anchor_path = workspace.registry_dir / "behavior-anchors.yaml"
    if behavior_anchor_path.exists():
        paths["behavior_anchors"] = behavior_anchor_path
    if workspace.benchmarks_path.exists():
        paths["protected_benchmarks"] = workspace.benchmarks_path
    return {key: sha256_file(path) for key, path in paths.items()}


def _validate_worker_question(
    question: str,
    seed_id: str,
    private_identifiers: tuple[str, ...],
) -> None:
    if len(question) > MAX_AGENT_MESSAGE_CHARS:
        raise ConfigurationError(
            f"transformed worker question exceeds {MAX_AGENT_MESSAGE_CHARS} characters: {seed_id}"
        )
    normalized = question.casefold()
    if any(identifier in normalized for identifier in private_identifiers):
        raise ConfigurationError(
            f"worker question contains a registered private identifier: {seed_id}"
        )


def _authorize(credentials: HTTPAuthorizationCredentials | None, expected: str) -> None:
    if credentials is None or credentials.scheme.casefold() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    actual_digest = _digest(credentials.credentials)
    expected_digest = _digest(expected)
    if not secrets.compare_digest(actual_digest, expected_digest):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_agent_app(settings: ServiceSettings) -> FastAPI:
    if settings.agent_token is None:
        raise ConfigurationError("worker-plane bearer token is required")
    agent_token = settings.agent_token
    broker = TaskBroker(settings)
    app = FastAPI(
        title="Task Service",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.add_middleware(RequestBodyLimitMiddleware, max_bytes=MAX_REQUEST_BODY_BYTES)

    agent_bearer = HTTPBearer(auto_error=False, scheme_name="WorkerBearer")

    def agent_auth(
        credentials: HTTPAuthorizationCredentials | None = Depends(agent_bearer),  # noqa: B008
    ) -> None:
        _authorize(credentials, agent_token)

    @app.get("/healthz", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/v1/tasks/lease",
        response_model=TaskLease,
        dependencies=[Depends(agent_auth)],
    )
    def lease(response: Response) -> TaskLease | Response:
        response.headers["Cache-Control"] = "no-store"
        task = broker.lease()
        if task is None:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return task

    @app.post(
        "/v1/tasks/{task_id}/responses",
        response_model=SubmissionReceipt,
        status_code=status.HTTP_202_ACCEPTED,
        dependencies=[Depends(agent_auth)],
    )
    def submit(task_id: str, payload: TaskSubmission, response: Response) -> SubmissionReceipt:
        response.headers["Cache-Control"] = "no-store"
        try:
            return broker.submit(task_id, payload)
        except TaskUnavailable as exc:
            raise HTTPException(status_code=404, detail="task unavailable") from exc

    return app


def create_control_app(settings: ServiceSettings) -> FastAPI:
    if settings.control_token is None:
        raise ConfigurationError("control-plane bearer token is required")
    control_token = settings.control_token
    broker = TaskBroker(settings)
    app = FastAPI(
        title="Governed QA Forge Control API",
        version="1",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.add_middleware(RequestBodyLimitMiddleware, max_bytes=MAX_REQUEST_BODY_BYTES)

    control_bearer = HTTPBearer(auto_error=False, scheme_name="ControlBearer")

    def control_auth(
        credentials: HTTPAuthorizationCredentials | None = Depends(control_bearer),  # noqa: B008
    ) -> None:
        _authorize(credentials, control_token)

    @app.get("/healthz", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(
        "/openapi.json",
        include_in_schema=False,
        dependencies=[Depends(control_auth)],
    )
    def openapi_schema() -> dict[str, object]:
        return app.openapi()

    @app.post(
        "/v1/runs",
        response_model=CollectionStatus,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(control_auth)],
    )
    def create_run(payload: CreateRunRequest) -> CollectionStatus:
        return broker.create_collection(payload.run_id)

    @app.get(
        "/v1/runs/{run_id}",
        response_model=CollectionStatus,
        dependencies=[Depends(control_auth)],
    )
    def run_status(run_id: str) -> CollectionStatus:
        return broker.status(run_id)

    @app.post(
        "/v1/runs/{run_id}/finalize",
        response_model=CollectionStatus,
        dependencies=[Depends(control_auth)],
    )
    def finalize(run_id: str) -> CollectionStatus:
        return broker.finalize(run_id)

    return app
