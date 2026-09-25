from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from qaforge.errors import AuthorizationError, ConfigurationError
from qaforge.io import (
    MAX_YAML_BYTES,
    ensure_within,
    read_jsonl,
    read_text_bounded,
    read_yaml,
    read_yaml_list,
    safe_identifier,
)
from qaforge.models import (
    AuthorizationStatus,
    BenchmarkRecord,
    DoctorReport,
    ForgeConfig,
    GateResult,
    GateStatus,
    ReviewerEntry,
    SeedRecord,
    SourceEntry,
    TeacherEntry,
)


class Workspace:
    """Validated filesystem boundary for a corpus project."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).resolve()

    @property
    def config_path(self) -> Path:
        return self.root / "qaforge.yaml"

    @property
    def registry_dir(self) -> Path:
        return self.root / "registry"

    @property
    def seeds_path(self) -> Path:
        return self.root / "seeds" / "seeds.jsonl"

    @property
    def benchmarks_path(self) -> Path:
        return self.registry_dir / "protected-benchmarks.jsonl"

    def run_dir(self, run_id: str) -> Path:
        runs_root = self.root / "runs"
        return ensure_within(runs_root, runs_root / safe_identifier(run_id, "run ID"))

    def release_dir(self, version: str) -> Path:
        releases_root = self.root / "releases"
        return ensure_within(
            releases_root, releases_root / safe_identifier(version, "release version")
        )

    def config(self) -> ForgeConfig:
        return read_yaml(self.config_path, ForgeConfig)

    def sources(self) -> list[SourceEntry]:
        return read_yaml_list(self.registry_dir / "sources.yaml", "sources", SourceEntry)

    def teachers(self) -> list[TeacherEntry]:
        return read_yaml_list(self.registry_dir / "teachers.yaml", "teachers", TeacherEntry)

    def reviewers(self) -> list[ReviewerEntry]:
        return read_yaml_list(self.registry_dir / "reviewers.yaml", "reviewers", ReviewerEntry)

    def seeds(self) -> list[SeedRecord]:
        return read_jsonl(self.seeds_path, SeedRecord)

    def benchmarks(self) -> list[BenchmarkRecord]:
        if not self.benchmarks_path.exists():
            return []
        return read_jsonl(self.benchmarks_path, BenchmarkRecord)

    def taxonomy(self) -> dict[str, list[str]]:
        path = self.registry_dir / "taxonomy.yaml"
        try:
            value = yaml.safe_load(read_text_bounded(path, MAX_YAML_BYTES))
        except (OSError, yaml.YAMLError) as exc:
            raise ConfigurationError(f"cannot read taxonomy {path}: {exc}") from exc
        if not isinstance(value, dict) or not all(
            isinstance(item, list) for item in value.values()
        ):
            raise ConfigurationError("taxonomy must map dimension names to lists")
        return {str(key): [str(item) for item in items] for key, items in value.items()}

    def teacher(self, teacher_id: str) -> TeacherEntry:
        matches = [teacher for teacher in self.teachers() if teacher.teacher_id == teacher_id]
        if len(matches) != 1:
            raise ConfigurationError(f"teacher_id must resolve exactly once: {teacher_id}")
        teacher = matches[0]
        if teacher.authorization_status is not AuthorizationStatus.APPROVED:
            raise AuthorizationError(
                f"teacher {teacher_id} authorization is {teacher.authorization_status.value}"
            )
        return teacher

    def reviewer(self, reviewer_id: str, category: str) -> ReviewerEntry:
        matches = [item for item in self.reviewers() if item.reviewer_id == reviewer_id]
        if len(matches) != 1:
            raise ConfigurationError(f"reviewer_id must resolve exactly once: {reviewer_id}")
        reviewer = matches[0]
        if reviewer.authorization_status is not AuthorizationStatus.APPROVED:
            raise AuthorizationError(
                f"reviewer {reviewer_id} authorization is {reviewer.authorization_status.value}"
            )
        if "*" not in reviewer.allowed_categories and category not in reviewer.allowed_categories:
            raise AuthorizationError(
                f"reviewer {reviewer_id} is not authorized for category {category}"
            )
        return reviewer

    def doctor(self, provider_id: str | None = None) -> DoctorReport:
        checks: list[GateResult] = []
        config = self.config()
        sources = self.sources()
        teachers = self.teachers()
        reviewers = self.reviewers()
        seeds = self.seeds()
        taxonomy = self.taxonomy()

        def check(name: str, passed: bool, detail: str) -> None:
            checks.append(
                GateResult(
                    gate=name,
                    status=GateStatus.PASS if passed else GateStatus.FAIL,
                    detail=detail,
                )
            )

        source_counts = Counter(item.source_id for item in sources)
        teacher_counts = Counter(item.teacher_id for item in teachers)
        reviewer_counts = Counter(item.reviewer_id for item in reviewers)
        seed_counts = Counter(item.seed_id for item in seeds)
        check(
            "unique_sources",
            all(count == 1 for count in source_counts.values()),
            "source IDs unique",
        )
        check(
            "unique_teachers",
            all(count == 1 for count in teacher_counts.values()),
            "teacher IDs unique",
        )
        check(
            "unique_reviewers",
            all(count == 1 for count in reviewer_counts.values()),
            "reviewer IDs unique",
        )
        approved_reviewers = [
            item for item in reviewers if item.authorization_status is AuthorizationStatus.APPROVED
        ]
        uncovered_review_categories = sorted(
            category
            for category in taxonomy.get("categories", [])
            if not any(
                "*" in reviewer.allowed_categories or category in reviewer.allowed_categories
                for reviewer in approved_reviewers
            )
        )
        check(
            "reviewer_category_coverage",
            not uncovered_review_categories,
            f"uncovered categories: {uncovered_review_categories}",
        )
        check("unique_seeds", all(count == 1 for count in seed_counts.values()), "seed IDs unique")

        source_map = {item.source_id: item for item in sources}
        unknown_sources = sorted(
            {
                source_id
                for seed in seeds
                for source_id in seed.source_ids
                if source_id not in source_map
            }
        )
        check("seed_sources_exist", not unknown_sources, f"unknown sources: {unknown_sources}")
        unauthorized = sorted(
            source_id
            for seed in seeds
            for source_id in seed.source_ids
            if source_id in source_map
            and source_map[source_id].authorization_status is not AuthorizationStatus.APPROVED
        )
        check("seed_sources_authorized", not unauthorized, f"unauthorized sources: {unauthorized}")
        nonredistributable = sorted(
            source_id
            for seed in seeds
            for source_id in seed.source_ids
            if source_id in source_map and not source_map[source_id].redistribution_allowed
        )
        check(
            "seed_sources_redistributable",
            not nonredistributable,
            f"non-redistributable sources: {nonredistributable}",
        )
        intended_uses = set(config.release.intended_uses)
        incompatible_source_uses = sorted(
            source_id
            for seed in seeds
            for source_id in seed.source_ids
            if source_id in source_map
            and not intended_uses.issubset(set(source_map[source_id].allowed_target_uses))
        )
        check(
            "source_target_use_compatible",
            not incompatible_source_uses,
            f"incompatible sources: {incompatible_source_uses}",
        )
        incompatible_source_licenses = sorted(
            source_id
            for seed in seeds
            for source_id in seed.source_ids
            if source_id in source_map
            and config.release.license not in source_map[source_id].compatible_release_licenses
        )
        check(
            "source_release_license_compatible",
            not incompatible_source_licenses,
            f"incompatible sources: {incompatible_source_licenses}",
        )

        target_teacher = provider_id or config.generation.provider_id
        teacher_matches = [item for item in teachers if item.teacher_id == target_teacher]
        check("teacher_exists", len(teacher_matches) == 1, f"teacher: {target_teacher}")
        teacher_approved = bool(
            teacher_matches
            and teacher_matches[0].authorization_status is AuthorizationStatus.APPROVED
        )
        check("teacher_authorized", teacher_approved, f"teacher: {target_teacher}")
        teacher_use_compatible = bool(
            len(teacher_matches) == 1
            and intended_uses.issubset(set(teacher_matches[0].allowed_target_uses))
        )
        check(
            "teacher_target_use_compatible",
            teacher_use_compatible,
            f"teacher: {target_teacher}",
        )

        fields = {
            "categories": "category",
            "domains": "domain",
            "tasks": "task",
            "reasoning": "reasoning",
            "answer_forms": "answer_form",
        }
        taxonomy_errors: list[str] = []
        for seed in seeds:
            dimensions = seed.dimensions.model_dump(mode="json")
            for taxonomy_key, field_name in fields.items():
                allowed = taxonomy.get(taxonomy_key, [])
                if allowed and dimensions[field_name] not in allowed:
                    taxonomy_errors.append(f"{seed.seed_id}:{field_name}={dimensions[field_name]}")
        check("taxonomy_membership", not taxonomy_errors, f"invalid: {taxonomy_errors}")

        depth_errors = [
            seed.seed_id
            for seed in seeds
            if seed.generation_depth + 1 > config.generation.max_generation_depth
        ]
        check("generation_depth", not depth_errors, f"depth blocked: {depth_errors}")
        check("seed_bank_nonempty", bool(seeds), f"seed count: {len(seeds)}")

        return DoctorReport(
            passed=all(item.status is GateStatus.PASS for item in checks),
            checks=checks,
            seed_count=len(seeds),
            source_count=len(sources),
            teacher_count=len(teachers),
            reviewer_count=len(reviewers),
        )

    def snapshot_inputs(self) -> dict[str, Any]:
        return {
            "config": self.config().model_dump(mode="json"),
            "sources": [item.model_dump(mode="json") for item in self.sources()],
            "teachers": [
                item.model_dump(mode="json", exclude={"api_key_env"}) for item in self.teachers()
            ],
            "reviewers": [item.model_dump(mode="json") for item in self.reviewers()],
            "taxonomy": self.taxonomy(),
        }
