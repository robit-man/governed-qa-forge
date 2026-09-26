import json
import socket

import httpx
import pytest
from pydantic import ValidationError

from qaforge.errors import ConfigurationError
from qaforge.fixtures import scaffold_workspace
from qaforge.models import AuthorizationStatus, TeacherEntry
from qaforge.providers import OpenAICompatibleProvider
from qaforge.workspace import Workspace


def test_fr013_openai_compatible_provider_parses_strict_json(tmp_path, monkeypatch) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "ws", demo=True))
    teacher = TeacherEntry(
        teacher_id="remote",
        provider="openai-compatible",
        model="teacher-v1",
        base_url="https://teacher.example/v1",
        api_key_env="QAFORGE_TEACHER_TEST_KEY",
        authorization_status=AuthorizationStatus.APPROVED,
        terms_snapshot_id="terms-2026-09-25",
        authorization_basis="test fixture",
        allowed_target_uses=["tests"],
        reviewed_at="2026-09-25T00:00:00Z",
        reviewer="tester",
    )
    monkeypatch.setenv("QAFORGE_TEACHER_TEST_KEY", "not-persisted-secret")
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))],
    )

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer not-persisted-secret"
        body = json.loads(request.content)
        assert body["model"] == "teacher-v1"
        worker_prompt = body["messages"][1]["content"]
        assert "reference_answer" not in worker_prompt
        assert "seed-arithmetic-001" not in worker_prompt
        assert "family-arithmetic-001" not in worker_prompt
        assert "SRC-DEMO" not in worker_prompt
        assert "verifier" not in worker_prompt
        assert "dimensions" not in worker_prompt
        assert "17 multiplied by 6" in worker_prompt
        content = {
            "candidates": [
                {
                    "derivation": ["Multiply the two stated integers to obtain the result."],
                    "answer": "102",
                    "citation_ids": ["forged-source"],
                },
                {
                    "derivation": ["Compute the requested product and check the arithmetic."],
                    "answer": "102",
                },
                {
                    "derivation": ["Use multiplication on the values given in the prompt."],
                    "answer": "102",
                },
            ]
        }
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(content)}}]},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    outputs, template_id, template_hash = OpenAICompatibleProvider(teacher, client).generate(
        workspace.seeds()[0], 3, workspace.config()
    )
    assert len(outputs) == 3
    assert all(output.answer == "102" for output in outputs)
    assert all(output.citation_ids == [] for output in outputs)
    assert template_id
    assert len(template_hash) == 64


@pytest.mark.parametrize(
    ("base_url", "api_key_env"),
    [
        ("http://teacher.example/v1", "QAFORGE_TEACHER_KEY"),
        ("https://127.0.0.1/v1", "QAFORGE_TEACHER_KEY"),
        ("https://169.254.169.254/latest", "QAFORGE_TEACHER_KEY"),
        ("https://user:password@teacher.example/v1", "QAFORGE_TEACHER_KEY"),
        ("https://teacher.example/v1", "AWS_SECRET_ACCESS_KEY"),
    ],
)
def test_nfr003_teacher_endpoint_and_credential_are_restricted(
    base_url: str, api_key_env: str
) -> None:
    with pytest.raises(ValidationError):
        TeacherEntry(
            teacher_id="unsafe",
            provider="openai-compatible",
            model="teacher-v1",
            base_url=base_url,
            api_key_env=api_key_env,
            authorization_status=AuthorizationStatus.APPROVED,
            terms_snapshot_id="terms-v1",
            authorization_basis="test",
            allowed_target_uses=["tests"],
            reviewed_at="2026-09-25T00:00:00Z",
            reviewer="tester",
        )


def test_nfr003_dns_resolution_cannot_target_private_network(tmp_path, monkeypatch) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "ws-private-dns", demo=True))
    teacher = TeacherEntry(
        teacher_id="remote",
        provider="openai-compatible",
        model="teacher-v1",
        base_url="https://teacher.example/v1",
        authorization_status=AuthorizationStatus.APPROVED,
        terms_snapshot_id="terms-v1",
        authorization_basis="test",
        allowed_target_uses=["tests"],
        reviewed_at="2026-09-25T00:00:00Z",
        reviewer="tester",
    )
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))],
    )
    with pytest.raises(ConfigurationError, match="non-public"):
        OpenAICompatibleProvider(teacher).generate(workspace.seeds()[0], 3, workspace.config())


def test_remote_provider_rejects_private_identifiers_before_network(tmp_path, monkeypatch) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "ws-private-prompt", demo=True))
    teacher = TeacherEntry(
        teacher_id="remote",
        provider="openai-compatible",
        model="teacher-v1",
        base_url="https://teacher.example/v1",
        authorization_status=AuthorizationStatus.APPROVED,
        terms_snapshot_id="terms-v1",
        authorization_basis="test",
        allowed_target_uses=["tests"],
        reviewed_at="2026-09-25T00:00:00Z",
        reviewer="tester",
    )
    called = False

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(500)

    seed = workspace.seeds()[0].model_copy(
        update={"question": workspace.seeds()[0].question + " Use SRC-DEMO."}
    )
    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(ConfigurationError, match="private identifier"):
        OpenAICompatibleProvider(teacher, client).generate(seed, 3, workspace.config())
    assert called is False


def test_nfr007_remote_response_is_byte_bounded(tmp_path, monkeypatch) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "ws-bounded", demo=True))
    teacher = TeacherEntry(
        teacher_id="remote",
        provider="openai-compatible",
        model="teacher-v1",
        base_url="https://teacher.example/v1",
        authorization_status=AuthorizationStatus.APPROVED,
        terms_snapshot_id="terms-v1",
        authorization_basis="test",
        allowed_target_uses=["tests"],
        reviewed_at="2026-09-25T00:00:00Z",
        reviewer="tester",
    )
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))],
    )
    client = httpx.Client(
        transport=httpx.MockTransport(lambda _request: httpx.Response(200, content=b"x" * 2048))
    )
    config = workspace.config().model_copy(
        update={
            "generation": workspace.config().generation.model_copy(
                update={"max_response_bytes": 1024}
            )
        }
    )
    from qaforge.errors import ForgeError

    with pytest.raises(ForgeError, match="max_response_bytes"):
        OpenAICompatibleProvider(teacher, client).generate(workspace.seeds()[0], 3, config)
