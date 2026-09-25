from __future__ import annotations

import ipaddress
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class AuthorizationStatus(StrEnum):
    APPROVED = "approved"
    BLOCKED = "blocked"
    UNCLEAR = "unclear"
    EXPIRED = "expired"


class Split(StrEnum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


class RiskLevel(StrEnum):
    ORDINARY = "ordinary"
    SENSITIVE = "sensitive"
    DUAL_USE = "dual_use"
    HIGH_STAKES = "high_stakes"
    PROHIBITED = "prohibited"


class VerifierKind(StrEnum):
    EXACT = "exact"
    NUMERIC = "numeric"
    REGEX = "regex"
    JSON = "json"
    CITATION = "citation"


class GateStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    REVIEW = "review"


class ReviewState(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RunStage(StrEnum):
    GENERATED = "generated"
    AWAITING_REVIEW = "awaiting_review"
    APPROVED = "approved"
    RELEASED = "released"


class SplitConfig(BaseModel):
    train: float = Field(default=0.9, gt=0, lt=1)
    validation: float = Field(default=0.05, ge=0, lt=1)
    test: float = Field(default=0.05, ge=0, lt=1)
    salt: str = Field(min_length=8)

    @model_validator(mode="after")
    def ratios_sum_to_one(self) -> SplitConfig:
        if abs(self.train + self.validation + self.test - 1.0) > 1e-9:
            raise ValueError("split ratios must sum to 1.0")
        return self


class GenerationConfig(BaseModel):
    provider_id: str
    candidates_per_seed: int = Field(default=3, ge=3, le=10)
    max_generation_depth: int = Field(default=1, ge=0, le=8)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, ge=32, le=32768)
    timeout_seconds: float = Field(default=60, gt=0, le=600)
    max_response_bytes: int = Field(default=1_000_000, ge=1024, le=10_000_000)


class QualityConfig(BaseModel):
    target_size: int = Field(default=1000, ge=1)
    min_question_chars: int = Field(default=12, ge=1)
    min_answer_chars: int = Field(default=1, ge=1)
    near_duplicate_threshold: float = Field(default=0.86, ge=0, le=1)
    semantic_threshold: float = Field(default=0.94, ge=0, le=1)
    semantic_dimensions: int = Field(default=384, ge=64, le=4096)
    semantic_lsh_bands: Literal[1, 2, 4, 8, 16] = 8
    max_per_lineage: int = Field(default=1, ge=1)
    coverage_floors: dict[str, dict[str, int]] = Field(default_factory=dict)
    allowed_risks: list[RiskLevel] = Field(
        default_factory=lambda: [RiskLevel.ORDINARY, RiskLevel.SENSITIVE]
    )

    @model_validator(mode="after")
    def validate_coverage_floors(self) -> QualityConfig:
        allowed = {
            "category",
            "domain",
            "task",
            "reasoning",
            "answer_form",
            "difficulty",
            "evidence_mode",
            "risk",
        }
        unknown = set(self.coverage_floors) - allowed
        if unknown:
            raise ValueError(f"unknown coverage dimensions: {sorted(unknown)}")
        invalid = [
            f"{dimension}.{value}"
            for dimension, values in self.coverage_floors.items()
            for value, floor in values.items()
            if floor < 1
        ]
        if invalid:
            raise ValueError(f"coverage floors must be positive: {invalid}")
        return self


class ReviewConfig(BaseModel):
    required: Literal[True] = True


class ReleaseConfig(BaseModel):
    dataset_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
    license: str
    intended_uses: list[str] = Field(min_length=1)
    prohibited_uses: list[str] = Field(min_length=1)


class ForgeConfig(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    language_bcp47: str = "en"
    demo_mode: bool = False
    split: SplitConfig
    generation: GenerationConfig
    quality: QualityConfig
    review: ReviewConfig = Field(default_factory=ReviewConfig)
    release: ReleaseConfig


class SourceEntry(BaseModel):
    source_id: str
    uri: HttpUrl | str
    retrieved_at: str
    snapshot_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    authorization_status: AuthorizationStatus
    license_basis: str
    redistribution_allowed: bool
    allowed_target_uses: list[str] = Field(min_length=1)
    compatible_release_licenses: list[str] = Field(min_length=1)
    attribution: str | None = None
    reviewer: str


class TeacherEntry(BaseModel):
    teacher_id: str
    provider: Literal["deterministic", "openai-compatible"]
    model: str
    base_url: HttpUrl | None = None
    api_key_env: str | None = Field(default=None, pattern=r"^QAFORGE_TEACHER_[A-Z0-9_]+$")
    allow_private_endpoint: bool = False
    authorization_status: AuthorizationStatus
    terms_snapshot_id: str
    authorization_basis: str
    allowed_target_uses: list[str] = Field(min_length=1)
    reviewed_at: str
    reviewer: str

    @model_validator(mode="after")
    def endpoint_required_for_remote(self) -> TeacherEntry:
        if self.provider == "openai-compatible" and self.base_url is None:
            raise ValueError("openai-compatible teachers require base_url")
        if self.base_url is None:
            return self
        if self.base_url.username or self.base_url.password or self.base_url.fragment:
            raise ValueError("teacher base_url cannot contain userinfo or a fragment")
        if self.base_url.scheme != "https" and not self.allow_private_endpoint:
            raise ValueError("teacher base_url must use HTTPS")
        host = self.base_url.host
        if host is None:
            raise ValueError("teacher base_url must have a hostname")
        private_host = host.casefold() == "localhost" or host.casefold().endswith(
            (".localhost", ".local")
        )
        try:
            private_host = private_host or not ipaddress.ip_address(host).is_global
        except ValueError:
            pass
        if private_host and not self.allow_private_endpoint:
            raise ValueError("teacher base_url cannot use a non-public host")
        if self.allow_private_endpoint and self.api_key_env:
            raise ValueError("private teacher endpoints cannot receive ambient credentials")
        return self


class ReviewerEntry(BaseModel):
    reviewer_id: str
    authorization_status: AuthorizationStatus
    allowed_categories: list[str] = Field(min_length=1)
    authorization_basis: str
    reviewed_at: str
    authorized_by: str


class VerifierSpec(BaseModel):
    kind: VerifierKind
    expected: Any = None
    tolerance: float = Field(default=1e-6, ge=0)
    pattern: str | None = Field(default=None, max_length=512)
    required_citation_ids: list[str] = Field(default_factory=list)


class Dimensions(BaseModel):
    category: str
    domain: str
    task: str
    reasoning: str
    answer_form: str
    difficulty: Literal["introductory", "intermediate", "advanced"]
    evidence_mode: Literal["deterministic", "source_grounded", "rubric"]
    risk: RiskLevel = RiskLevel.ORDINARY


class SeedRecord(BaseModel):
    seed_id: str
    lineage_id: str
    question: str = Field(min_length=1, max_length=16_384)
    reference_answer: str = Field(min_length=1, max_length=32_768)
    dimensions: Dimensions
    verifier: VerifierSpec
    source_ids: list[str] = Field(min_length=1)
    generation_depth: int = Field(default=0, ge=0)


class BenchmarkRecord(BaseModel):
    benchmark_id: str
    question: str = Field(min_length=1, max_length=16_384)
    answer: str | None = Field(default=None, max_length=32_768)


class GeneratedOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str = Field(min_length=1, max_length=32_768)
    citation_ids: list[str] = Field(default_factory=list, max_length=64)


class GateResult(BaseModel):
    gate: str
    status: GateStatus
    detail: str


class VerificationResult(BaseModel):
    kind: VerifierKind
    passed: bool
    detail: str


class ContaminationResult(BaseModel):
    passed: bool = True
    match_type: str | None = None
    match_id: str | None = None
    similarity: float = 0.0
    detail: str = "no material overlap detected"


class ReviewDecision(BaseModel):
    record_id: str
    candidate_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    decision: ReviewState = ReviewState.PENDING
    reviewer: str = ""
    rationale: str = ""
    reviewed_at: str | None = None


class CandidateRecord(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    record_id: str
    seed_id: str
    lineage_id: str
    split: Split
    question: str = Field(min_length=1, max_length=16_384)
    answer: str = Field(min_length=1, max_length=32_768)
    seed_question: str = Field(min_length=1, max_length=16_384)
    question_transform_id: str
    dimensions: Dimensions
    verifier: VerifierSpec
    citation_ids: list[str] = Field(default_factory=list)
    source_ids: list[str]
    parent_record_ids: list[str]
    generation_depth: int
    generation_run_id: str
    generated_at: str
    teacher_id: str
    teacher_provider: str
    teacher_model: str
    teacher_terms_snapshot_id: str
    prompt_template_id: str
    prompt_template_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    sampling: dict[str, str | int | float]
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    validation: list[GateResult] = Field(default_factory=list)
    verification: VerificationResult | None = None
    contamination: ContaminationResult = Field(default_factory=ContaminationResult)
    quality_score: float = Field(default=0, ge=0, le=1)
    coverage_score: float = Field(default=0, ge=0)
    selected: bool = False
    rejection_reasons: list[str] = Field(default_factory=list)
    review: ReviewDecision | None = None


class RunState(BaseModel):
    run_id: str
    stage: RunStage
    created_at: str
    updated_at: str
    counts: dict[str, int]
    release_version: str | None = None


class DoctorReport(BaseModel):
    passed: bool
    checks: list[GateResult]
    seed_count: int
    source_count: int
    teacher_count: int
    reviewer_count: int
