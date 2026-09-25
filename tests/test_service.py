from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from qaforge.errors import ConfigurationError, GateError
from qaforge.io import read_jsonl
from qaforge.models import CandidateRecord, RunStage
from qaforge.pilot import (
    calibration_seeds,
    scaffold_calibration_workspace,
    solve_blind_calibration_task,
)
from qaforge.service import (
    ServiceSettings,
    TaskBroker,
    TaskSubmission,
    TaskUnavailable,
    create_agent_app,
    create_control_app,
)
from qaforge.transforms import transform_ids, transform_question
from qaforge.workspace import Workspace

AGENT_TOKEN = "agent-token-that-is-long-enough-for-tests-00000001"
CONTROL_TOKEN = "control-token-that-is-long-enough-for-tests-00001"


def _settings(root: Path) -> ServiceSettings:
    return ServiceSettings(
        workspace=root,
        database=root / "service.sqlite3",
        agent_token=AGENT_TOKEN,
        control_token=CONTROL_TOKEN,
    )


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_fr015_worker_plane_is_opaque_and_feedback_free(tmp_path: Path) -> None:
    root = scaffold_calibration_workspace(tmp_path / "opaque", size=10)
    settings = _settings(root)
    control = TestClient(create_control_app(settings))
    agent = TestClient(create_agent_app(settings))

    created = control.post(
        "/v1/runs", json={"run_id": "opaque-test"}, headers=_headers(CONTROL_TOKEN)
    )
    assert created.status_code == 201
    assert agent.get("/openapi.json").status_code == 404
    assert agent.get("/docs").status_code == 404
    assert control.get("/openapi.json").status_code == 401
    control_schema = control.get("/openapi.json", headers=_headers(CONTROL_TOKEN))
    assert control_schema.status_code == 200
    schema = control_schema.json()
    assert "/v1/runs" in schema["paths"]
    assert schema["components"]["securitySchemes"]["ControlBearer"]["scheme"] == "bearer"
    assert {"ControlBearer": []} in schema["paths"]["/v1/runs"]["post"]["security"]
    assert agent.post("/v1/tasks/lease", headers=_headers(CONTROL_TOKEN)).status_code == 401

    response = agent.post("/v1/tasks/lease", headers=_headers(AGENT_TOKEN))
    assert response.status_code == 200
    task = response.json()
    assert set(task) == {"task_id", "lease_token", "expires_at_unix", "messages"}
    assert task["messages"][0]["role"] == "user"
    serialized = response.text.casefold()
    for private_name in (
        "seed_id",
        "lineage",
        "source_id",
        "reference_answer",
        "verifier",
        "expected",
        "category",
        "score",
        "benchmark",
        "review",
    ):
        assert private_name not in serialized

    answer = solve_blind_calibration_task(task["messages"][0]["content"])
    submitted = agent.post(
        f"/v1/tasks/{task['task_id']}/responses",
        json={"lease_token": task["lease_token"], "answer": answer},
        headers=_headers(AGENT_TOKEN),
    )
    assert submitted.status_code == 202
    assert submitted.json() == {"status": "recorded"}
    replay = agent.post(
        f"/v1/tasks/{task['task_id']}/responses",
        json={"lease_token": task["lease_token"], "answer": answer},
        headers=_headers(AGENT_TOKEN),
    )
    assert replay.status_code == 404
    assert AGENT_TOKEN.encode() not in settings.database.read_bytes()
    assert task["lease_token"].encode() not in settings.database.read_bytes()


def test_fr016_service_finalization_reuses_governed_pipeline(tmp_path: Path) -> None:
    root = scaffold_calibration_workspace(tmp_path / "finalize", size=10)
    settings = _settings(root)
    with (
        TestClient(create_control_app(settings)) as control,
        TestClient(create_agent_app(settings)) as agent,
    ):
        response = control.post(
            "/v1/runs", json={"run_id": "service-run"}, headers=_headers(CONTROL_TOKEN)
        )
        assert response.status_code == 201
        assert response.json()["expected"] == 30
        submitted = 0
        while True:
            lease = agent.post("/v1/tasks/lease", headers=_headers(AGENT_TOKEN))
            if lease.status_code == 204:
                break
            task = lease.json()
            answer = solve_blind_calibration_task(task["messages"][0]["content"])
            receipt = agent.post(
                f"/v1/tasks/{task['task_id']}/responses",
                json={"lease_token": task["lease_token"], "answer": answer},
                headers=_headers(AGENT_TOKEN),
            )
            assert receipt.status_code == 202
            submitted += 1
        assert submitted == 30
        result = control.post("/v1/runs/service-run/finalize", headers=_headers(CONTROL_TOKEN))
        assert result.status_code == 200
        body = result.json()
        assert body["state"] == "finalized"
        assert body["forge_state"]["stage"] == RunStage.AWAITING_REVIEW.value
        assert body["forge_state"]["counts"]["selected"] == 10

    selected = read_jsonl(
        Workspace(root).run_dir("service-run") / "selected.jsonl", CandidateRecord
    )
    assert len(selected) == 10
    assert len({item.lineage_id for item in selected}) == 10
    assert all(item.teacher_provider == "opaque-agent-service" for item in selected)


def test_fr017_concurrent_leases_are_unique(tmp_path: Path) -> None:
    root = scaffold_calibration_workspace(tmp_path / "concurrent", size=10)
    broker = TaskBroker(_settings(root))
    broker.create_collection("concurrent-run")
    with ThreadPoolExecutor(max_workers=8) as executor:
        leases = list(executor.map(lambda _index: broker.lease(), range(20)))
    task_ids = [lease.task_id for lease in leases if lease is not None]
    assert len(task_ids) == 20
    assert len(set(task_ids)) == 20


def test_nfr011_service_tokens_are_strong_and_separate(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="32 characters"):
        ServiceSettings(tmp_path, tmp_path / "db.sqlite3", "short", CONTROL_TOKEN)
    with pytest.raises(ConfigurationError, match="different"):
        ServiceSettings(tmp_path, tmp_path / "db.sqlite3", AGENT_TOKEN, AGENT_TOKEN)
    with pytest.raises(ConfigurationError, match="placeholder"):
        ServiceSettings(
            tmp_path,
            tmp_path / "db.sqlite3",
            "replace-with-independent-random-worker-token",
            CONTROL_TOKEN,
        )
    with pytest.raises(ConfigurationError, match="inside the selected workspace"):
        ServiceSettings(
            tmp_path / "workspace",
            tmp_path / "outside" / "db.sqlite3",
            AGENT_TOKEN,
            CONTROL_TOKEN,
        )


def test_fr019_blind_solver_uses_only_every_worker_question() -> None:
    seeds = calibration_seeds(100)
    for seed in seeds:
        for transform_id in transform_ids(3):
            question = transform_question(seed.question, transform_id)
            answer = solve_blind_calibration_task(question)
            if seed.verifier.kind.value == "json":
                assert answer == seed.reference_answer
            elif seed.verifier.kind.value == "exact":
                assert answer.casefold() == seed.reference_answer.casefold()
            else:
                assert float(answer) == float(seed.reference_answer)


def test_task_submission_rejects_blank_after_normalization(tmp_path: Path) -> None:
    root = scaffold_calibration_workspace(tmp_path / "blank", size=10)
    broker = TaskBroker(_settings(root))
    broker.create_collection("blank-run")
    lease = broker.lease()
    assert lease is not None
    with pytest.raises(TaskUnavailable, match="task unavailable"):
        broker.submit(
            lease.task_id,
            TaskSubmission(lease_token=lease.lease_token, answer="   "),
        )


def test_collection_fails_closed_if_private_inputs_change(tmp_path: Path) -> None:
    root = scaffold_calibration_workspace(tmp_path / "sealed", size=10)
    broker = TaskBroker(_settings(root))
    broker.create_collection("sealed-run")
    while (lease := broker.lease()) is not None:
        answer = solve_blind_calibration_task(lease.messages[0].content)
        broker.submit(
            lease.task_id,
            TaskSubmission(lease_token=lease.lease_token, answer=answer),
        )

    seeds_path = Workspace(root).seeds_path
    seeds_path.write_text(
        seeds_path.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    with pytest.raises(GateError, match="sealed collection"):
        broker.finalize("sealed-run")
    status_result = broker.status("sealed-run")
    assert status_result.state == "failed"
    assert not Workspace(root).run_dir("sealed-run").exists()


def test_control_restart_recovers_unstarted_finalization(tmp_path: Path) -> None:
    root = scaffold_calibration_workspace(tmp_path / "recover", size=10)
    settings = _settings(root)
    broker = TaskBroker(settings)
    broker.create_collection("recover-run")
    while (lease := broker.lease()) is not None:
        answer = solve_blind_calibration_task(lease.messages[0].content)
        broker.submit(
            lease.task_id,
            TaskSubmission(lease_token=lease.lease_token, answer=answer),
        )

    with broker._connection() as connection:
        connection.execute(
            "UPDATE collection_runs SET state = 'finalizing' WHERE run_id = 'recover-run'"
        )
    recovered = TaskBroker(
        ServiceSettings(
            workspace=root,
            database=settings.database,
            control_token=CONTROL_TOKEN,
        )
    )
    assert recovered.status("recover-run").state == "ready"
    assert recovered.finalize("recover-run").state == "finalized"


def test_fr015_collection_rejects_worker_visible_private_source_id(tmp_path: Path) -> None:
    root = scaffold_calibration_workspace(tmp_path / "private-id", size=10)
    seeds_path = Workspace(root).seeds_path
    lines = seeds_path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["question"] += " Internal source: SRC-PILOT-AUTHORED."
    lines[0] = json.dumps(first, sort_keys=True, separators=(",", ":"))
    seeds_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    broker = TaskBroker(_settings(root))
    with pytest.raises(ConfigurationError, match="private identifier"):
        broker.create_collection("private-id-run")


def test_nfr013_projected_question_and_transport_body_are_bounded(tmp_path: Path) -> None:
    root = scaffold_calibration_workspace(tmp_path / "bounded", size=10)
    seeds_path = Workspace(root).seeds_path
    lines = seeds_path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["question"] = "x" * 16_384
    lines[0] = json.dumps(first, sort_keys=True, separators=(",", ":"))
    seeds_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    settings = _settings(root)
    broker = TaskBroker(settings)
    with pytest.raises(ConfigurationError, match="transformed worker question exceeds"):
        broker.create_collection("oversized-question")

    agent = TestClient(create_agent_app(settings))
    response = agent.post(
        "/v1/tasks/not-a-task/responses",
        content=b"x" * 65_537,
        headers={**_headers(AGENT_TOKEN), "content-type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json() == {"detail": "request body too large"}
