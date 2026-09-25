from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation
from typing import Any

import regex

from qaforge.io import canonical_json, sha256_text
from qaforge.models import (
    CandidateRecord,
    ForgeConfig,
    GateResult,
    GateStatus,
    VerificationResult,
    VerifierKind,
)
from qaforge.transforms import transform_question

SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(r"\bgh[opusr]_[A-Za-z0-9]{20,}\b"),
    "openai_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "anthropic_key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{20,}={0,2}\b", re.IGNORECASE),
    "aws_secret": re.compile(
        r"(?i)\baws(?:_secret_access_key| secret(?: access)? key)\s*[:=]\s*[A-Za-z0-9/+=]{32,}"
    ),
}
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "us_ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"(?<!\w)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\w)"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}
PROMPT_INJECTION_PATTERNS = {
    "ignore_instructions": re.compile(
        r"\b(?:ignore|disregard|override)\b.{0,40}\b(?:instructions?|prompt|rules?)\b",
        re.IGNORECASE,
    ),
    "system_prompt_exfiltration": re.compile(
        r"\b(?:reveal|print|show|repeat)\b.{0,40}\bsystem prompt\b", re.IGNORECASE
    ),
    "jailbreak": re.compile(r"\b(?:jailbreak|developer mode|do anything now)\b", re.IGNORECASE),
}


def _gate(name: str, passed: bool, detail: str) -> GateResult:
    return GateResult(
        gate=name, status=GateStatus.PASS if passed else GateStatus.FAIL, detail=detail
    )


def validate_candidate(candidate: CandidateRecord, config: ForgeConfig) -> list[GateResult]:
    combined = f"{candidate.question}\n{candidate.answer}"
    secret_hits = sorted(
        name for name, pattern in SECRET_PATTERNS.items() if pattern.search(combined)
    )
    pii_hits = sorted(name for name, pattern in PII_PATTERNS.items() if pattern.search(combined))
    injection_hits = sorted(
        name for name, pattern in PROMPT_INJECTION_PATTERNS.items() if pattern.search(combined)
    )
    expected_content_hash = sha256_text(
        canonical_json({"question": candidate.question, "answer": candidate.answer})
    )
    return [
        _gate(
            "content_hash",
            candidate.content_sha256 == expected_content_hash,
            "canonical question/answer SHA-256",
        ),
        _gate(
            "question_length",
            len(candidate.question.strip()) >= config.quality.min_question_chars,
            f"characters={len(candidate.question.strip())}",
        ),
        _gate(
            "answer_length",
            len(candidate.answer.strip()) >= config.quality.min_answer_chars,
            f"characters={len(candidate.answer.strip())}",
        ),
        _gate("secrets", not secret_hits, f"matches={secret_hits}"),
        _gate("pii", not pii_hits, f"matches={pii_hits}"),
        _gate("prompt_injection", not injection_hits, f"matches={injection_hits}"),
        _gate(
            "question_semantic_binding",
            candidate.question
            == transform_question(candidate.seed_question, candidate.question_transform_id),
            f"transform={candidate.question_transform_id}",
        ),
        _gate(
            "risk_scope",
            candidate.dimensions.risk in config.quality.allowed_risks,
            f"risk={candidate.dimensions.risk.value}",
        ),
        _gate(
            "generation_depth",
            candidate.generation_depth <= config.generation.max_generation_depth,
            f"depth={candidate.generation_depth}",
        ),
        _gate(
            "source_grounding",
            candidate.dimensions.evidence_mode != "source_grounded" or bool(candidate.citation_ids),
            f"citations={candidate.citation_ids}",
        ),
    ]


def _decimal(value: Any) -> Decimal:
    text = str(value).strip().replace(",", "")
    match = re.search(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", text)
    if not match:
        raise InvalidOperation
    return Decimal(match.group(0))


def verify_answer(candidate: CandidateRecord) -> VerificationResult:
    spec = candidate.verifier
    passed = False
    detail = ""
    if spec.kind is VerifierKind.EXACT:
        passed = candidate.answer.strip().casefold() == str(spec.expected).strip().casefold()
        detail = "case-insensitive normalized exact comparison"
    elif spec.kind is VerifierKind.NUMERIC:
        try:
            actual = _decimal(candidate.answer)
            expected = _decimal(spec.expected)
            passed = abs(actual - expected) <= Decimal(str(spec.tolerance))
            detail = f"actual={actual}; expected={expected}; tolerance={spec.tolerance}"
        except InvalidOperation:
            detail = "numeric value could not be parsed"
    elif spec.kind is VerifierKind.REGEX:
        try:
            passed = bool(
                spec.pattern
                and regex.fullmatch(spec.pattern, candidate.answer.strip(), timeout=0.05)
            )
            detail = f"bounded full-match pattern={spec.pattern!r}"
        except (TimeoutError, regex.error):
            detail = "regex was invalid or exceeded the verification time limit"
    elif spec.kind is VerifierKind.JSON:
        try:
            actual_json = json.loads(candidate.answer)
            passed = spec.expected is None or actual_json == spec.expected
            detail = "valid JSON" if spec.expected is None else "structural JSON equality"
        except json.JSONDecodeError:
            detail = "answer is not valid JSON"
    elif spec.kind is VerifierKind.CITATION:
        required = set(spec.required_citation_ids)
        cited = set(candidate.citation_ids)
        tokens_present = all(f"[{item}]" in candidate.answer for item in required)
        passed = required.issubset(cited) and tokens_present
        detail = f"required={sorted(required)}; cited={sorted(cited)}"
    return VerificationResult(kind=spec.kind, passed=passed, detail=detail)


def mandatory_gates_pass(candidate: CandidateRecord) -> bool:
    return (
        all(item.status is GateStatus.PASS for item in candidate.validation)
        and candidate.verification is not None
        and candidate.verification.passed
        and candidate.contamination.passed
    )
