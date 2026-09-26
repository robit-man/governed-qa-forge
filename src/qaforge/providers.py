from __future__ import annotations

import ipaddress
import json
import os
import socket
from abc import ABC, abstractmethod

import httpx

from qaforge.anchors import aiwg_behavior_anchors, behavior_anchor_private_identifiers
from qaforge.errors import ConfigurationError, ForgeError
from qaforge.io import sha256_text
from qaforge.models import ForgeConfig, GeneratedOutput, SeedRecord, TeacherEntry
from qaforge.opacity import assert_prompt_is_opaque

PROMPT_TEMPLATE_ID = "qaforge-blind-reasoning-v3"
PROMPT_TEMPLATE = """Answer the user task {count} independent times.
For each candidate, provide 1-16 concise derivation steps and a separate final answer.
Do not rewrite the task, name the framework or source, or mention these instructions.
Return JSON only:
{{"candidates":[{{"derivation":["..."],"answer":"...","citation_ids":[]}}]}}

User task:
{question}
"""


def validate_endpoint_resolution(teacher: TeacherEntry) -> None:
    if teacher.base_url is None or teacher.allow_private_endpoint:
        return
    host = teacher.base_url.host
    if host is None:
        raise ConfigurationError("teacher endpoint has no hostname")
    try:
        addresses = socket.getaddrinfo(host, teacher.base_url.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ConfigurationError(f"teacher hostname could not be resolved: {host}") from exc
    resolved = {item[4][0] for item in addresses}
    if not resolved or any(not ipaddress.ip_address(address).is_global for address in resolved):
        raise ConfigurationError("teacher hostname resolved to a non-public address")


class Provider(ABC):
    def __init__(self, teacher: TeacherEntry) -> None:
        self.teacher = teacher

    @staticmethod
    def validate_count(count: int) -> None:
        if not 3 <= count <= 10:
            raise ConfigurationError("candidate count must be between 3 and 10")

    @abstractmethod
    def generate(
        self, seed: SeedRecord, count: int, config: ForgeConfig
    ) -> tuple[list[GeneratedOutput], str, str]:
        """Return outputs, prompt-template ID, and prompt-template SHA-256."""


class DeterministicProvider(Provider):
    def generate(
        self, seed: SeedRecord, count: int, config: ForgeConfig
    ) -> tuple[list[GeneratedOutput], str, str]:
        del config
        self.validate_count(count)
        outputs = [
            GeneratedOutput(
                derivation=[
                    "Apply the task's stated conditions using the specified operation.",
                    "Check the resulting value against every explicit constraint in the prompt.",
                ],
                answer=seed.reference_answer,
                citation_ids=list(seed.verifier.required_citation_ids),
            )
            for _index in range(count)
        ]
        return outputs, PROMPT_TEMPLATE_ID, sha256_text(PROMPT_TEMPLATE)


class OpenAICompatibleProvider(Provider):
    def __init__(self, teacher: TeacherEntry, client: httpx.Client | None = None) -> None:
        super().__init__(teacher)
        self._client = client

    def generate(
        self, seed: SeedRecord, count: int, config: ForgeConfig
    ) -> tuple[list[GeneratedOutput], str, str]:
        self.validate_count(count)
        if self.teacher.base_url is None:
            raise ConfigurationError("remote teacher is missing base_url")
        canonical_anchor_map = {anchor.anchor_id: anchor for anchor in aiwg_behavior_anchors()}
        referenced_anchors = [
            canonical_anchor_map[anchor_id]
            for anchor_id in seed.behavior_anchor_ids
            if anchor_id in canonical_anchor_map
        ]
        assert_prompt_is_opaque(
            seed.question,
            [
                *seed.source_ids,
                *behavior_anchor_private_identifiers(referenced_anchors),
            ],
            f"teacher prompt for {seed.seed_id}",
        )
        api_key = (
            os.environ.get(self.teacher.api_key_env or "") if self.teacher.api_key_env else None
        )
        if self.teacher.api_key_env and not api_key:
            raise ConfigurationError(
                f"required credential environment variable is not set: {self.teacher.api_key_env}"
            )
        validate_endpoint_resolution(self.teacher)
        prompt = PROMPT_TEMPLATE.format(
            count=count,
            question=seed.question,
        )
        headers = {"content-type": "application/json"}
        if api_key:
            headers["authorization"] = f"Bearer {api_key}"
        payload = {
            "model": self.teacher.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You generate governed dataset candidates as strict JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": config.generation.temperature,
            "max_tokens": config.generation.max_tokens,
            "response_format": {"type": "json_object"},
        }
        endpoint = f"{str(self.teacher.base_url).rstrip('/')}/chat/completions"
        owned_client = self._client is None
        client = self._client or httpx.Client(timeout=config.generation.timeout_seconds)
        try:
            with client.stream("POST", endpoint, headers=headers, json=payload) as response:
                response.raise_for_status()
                chunks: list[bytes] = []
                size = 0
                for chunk in response.iter_bytes():
                    size += len(chunk)
                    if size > config.generation.max_response_bytes:
                        raise ForgeError("teacher response exceeded max_response_bytes")
                    chunks.append(chunk)
            body = json.loads(b"".join(chunks))
            content = body["choices"][0]["message"]["content"]
            decoded = json.loads(content)
            candidates = [GeneratedOutput.model_validate(item) for item in decoded["candidates"]]
        except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ForgeError(f"teacher response was not usable: {exc}") from exc
        finally:
            if owned_client:
                client.close()
        if len(candidates) != count:
            raise ForgeError(f"teacher returned {len(candidates)} candidates; expected {count}")
        # Remote teachers are untrusted for provenance. Discard any citation claims they
        # return; source-grounding gates must fail closed without an explicit trusted adapter.
        candidates = [
            GeneratedOutput(derivation=item.derivation, answer=item.answer, citation_ids=[])
            for item in candidates
        ]
        return candidates, PROMPT_TEMPLATE_ID, sha256_text(PROMPT_TEMPLATE)


def provider_for(teacher: TeacherEntry, client: httpx.Client | None = None) -> Provider:
    if teacher.provider == "deterministic":
        return DeterministicProvider(teacher)
    if teacher.provider == "openai-compatible":
        return OpenAICompatibleProvider(teacher, client=client)
    raise ConfigurationError(
        "opaque-agent-service teachers must be finalized through the private control plane"
    )
