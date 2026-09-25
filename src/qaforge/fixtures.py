from __future__ import annotations

from pathlib import Path

from qaforge.errors import ImmutableArtifactError
from qaforge.io import sha256_text, write_jsonl, write_text, write_yaml
from qaforge.models import (
    AuthorizationStatus,
    Dimensions,
    ForgeConfig,
    GenerationConfig,
    QualityConfig,
    ReleaseConfig,
    ReviewConfig,
    ReviewerEntry,
    RiskLevel,
    SeedRecord,
    SourceEntry,
    SplitConfig,
    TeacherEntry,
    VerifierKind,
    VerifierSpec,
)


def _seeds() -> list[SeedRecord]:
    return [
        SeedRecord(
            seed_id="seed-arithmetic-001",
            lineage_id="family-arithmetic-001",
            question="What is 17 multiplied by 6?",
            reference_answer="102",
            dimensions=Dimensions(
                category="arithmetic",
                domain="mathematics",
                task="derive",
                reasoning="quantitative",
                answer_form="concise",
                difficulty="introductory",
                evidence_mode="deterministic",
                risk=RiskLevel.ORDINARY,
            ),
            verifier=VerifierSpec(kind=VerifierKind.NUMERIC, expected=102),
            source_ids=["SRC-DEMO"],
        ),
        SeedRecord(
            seed_id="seed-language-001",
            lineage_id="family-language-001",
            question="Give the past tense of the English verb 'teach'.",
            reference_answer="taught",
            dimensions=Dimensions(
                category="language",
                domain="humanities",
                task="transform",
                reasoning="retrieval",
                answer_form="concise",
                difficulty="introductory",
                evidence_mode="deterministic",
            ),
            verifier=VerifierSpec(kind=VerifierKind.EXACT, expected="taught"),
            source_ids=["SRC-DEMO"],
        ),
        SeedRecord(
            seed_id="seed-json-001",
            lineage_id="family-json-001",
            question="Return JSON with key 'status' and string value 'ready'.",
            reference_answer='{"status":"ready"}',
            dimensions=Dimensions(
                category="structured-output",
                domain="computing",
                task="transform",
                reasoning="constraint",
                answer_form="json",
                difficulty="introductory",
                evidence_mode="deterministic",
            ),
            verifier=VerifierSpec(kind=VerifierKind.JSON, expected={"status": "ready"}),
            source_ids=["SRC-DEMO"],
        ),
        SeedRecord(
            seed_id="seed-regex-001",
            lineage_id="family-regex-001",
            question="Produce the identifier made from letters ABC, a hyphen, and number 42.",
            reference_answer="ABC-42",
            dimensions=Dimensions(
                category="format-control",
                domain="computing",
                task="transform",
                reasoning="constraint",
                answer_form="concise",
                difficulty="intermediate",
                evidence_mode="deterministic",
            ),
            verifier=VerifierSpec(kind=VerifierKind.REGEX, pattern=r"ABC-42"),
            source_ids=["SRC-DEMO"],
        ),
        SeedRecord(
            seed_id="seed-citation-001",
            lineage_id="family-citation-001",
            question="According to the demo source, what color is the calibration marker?",
            reference_answer="The calibration marker is cobalt blue [SRC-DEMO].",
            dimensions=Dimensions(
                category="source-grounded",
                domain="science",
                task="explain",
                reasoning="retrieval",
                answer_form="cited",
                difficulty="intermediate",
                evidence_mode="source_grounded",
            ),
            verifier=VerifierSpec(kind=VerifierKind.CITATION, required_citation_ids=["SRC-DEMO"]),
            source_ids=["SRC-DEMO"],
        ),
        SeedRecord(
            seed_id="seed-logic-001",
            lineage_id="family-logic-001",
            question="All nims are zogs and no zogs are red. Can any nim be red? Answer yes or no.",
            reference_answer="no",
            dimensions=Dimensions(
                category="logic",
                domain="mathematics",
                task="derive",
                reasoning="deductive",
                answer_form="concise",
                difficulty="intermediate",
                evidence_mode="deterministic",
            ),
            verifier=VerifierSpec(kind=VerifierKind.EXACT, expected="no"),
            source_ids=["SRC-DEMO"],
        ),
        SeedRecord(
            seed_id="seed-science-001",
            lineage_id="family-science-001",
            question=(
                "At standard pressure, which physical state is water in at 20 degrees Celsius?"
            ),
            reference_answer="liquid",
            dimensions=Dimensions(
                category="science",
                domain="science",
                task="classify",
                reasoning="retrieval",
                answer_form="concise",
                difficulty="introductory",
                evidence_mode="deterministic",
            ),
            verifier=VerifierSpec(kind=VerifierKind.EXACT, expected="liquid"),
            source_ids=["SRC-DEMO"],
        ),
        SeedRecord(
            seed_id="seed-code-001",
            lineage_id="family-code-001",
            question="Name the Python built-in that returns the number of items in a list.",
            reference_answer="len",
            dimensions=Dimensions(
                category="programming",
                domain="computing",
                task="explain",
                reasoning="retrieval",
                answer_form="concise",
                difficulty="introductory",
                evidence_mode="deterministic",
            ),
            verifier=VerifierSpec(kind=VerifierKind.EXACT, expected="len"),
            source_ids=["SRC-DEMO"],
        ),
    ]


def scaffold_workspace(root: Path, demo: bool = False) -> Path:
    root = root.resolve()
    if root.exists() and any(root.iterdir()):
        raise ImmutableArtifactError(f"workspace is not empty: {root}")
    root.mkdir(parents=True, exist_ok=True)
    (root / "registry").mkdir()
    (root / "seeds").mkdir()

    seeds = _seeds()
    categories = sorted({seed.dimensions.category for seed in seeds})
    coverage_floors = {
        dimension: {
            str(value): 1
            for value in sorted(
                {
                    getattr(seed.dimensions, dimension).value
                    if isinstance(getattr(seed.dimensions, dimension), RiskLevel)
                    else getattr(seed.dimensions, dimension)
                    for seed in seeds
                },
                key=str,
            )
        }
        for dimension in (
            "category",
            "domain",
            "task",
            "reasoning",
            "answer_form",
            "difficulty",
            "evidence_mode",
            "risk",
        )
    }
    config = ForgeConfig(
        demo_mode=demo,
        split=SplitConfig(train=0.75, validation=0.125, test=0.125, salt="qaforge-demo-v1"),
        generation=GenerationConfig(
            provider_id="teacher-fixture" if demo else "teacher-main",
            candidates_per_seed=3,
            max_generation_depth=1,
            temperature=0.4,
            max_tokens=512,
        ),
        quality=QualityConfig(
            target_size=8 if demo else 500,
            max_per_lineage=1,
            coverage_floors=coverage_floors,
        ),
        review=ReviewConfig(required=True),
        release=ReleaseConfig(
            dataset_id="governed-qa-demo" if demo else "replace-with-dataset-id",
            version="0.1.0",
            license="MIT",
            intended_uses=["supervised fine-tuning experiments", "dataset pipeline evaluation"],
            prohibited_uses=["high-stakes automated decisions", "misrepresentation as human data"],
        ),
    )
    write_yaml(root / "qaforge.yaml", config)
    source = SourceEntry(
        source_id="SRC-DEMO",
        uri="https://example.invalid/qaforge-demo-source-v1",
        retrieved_at="2026-09-25T00:00:00Z",
        snapshot_sha256=sha256_text("qaforge-demo-authoritative-source-v1"),
        authorization_status=AuthorizationStatus.APPROVED,
        license_basis="project-authored fixture",
        redistribution_allowed=True,
        allowed_target_uses=[
            "supervised fine-tuning experiments",
            "dataset pipeline evaluation",
        ],
        compatible_release_licenses=["MIT"],
        attribution="Governed QA Forge demo fixture",
        reviewer="project-team",
    )
    write_yaml(root / "registry" / "sources.yaml", {"sources": [source]})
    if demo:
        teacher = TeacherEntry(
            teacher_id="teacher-fixture",
            provider="deterministic",
            model="deterministic-fixture-v1",
            authorization_status=AuthorizationStatus.APPROVED,
            terms_snapshot_id="internal-fixture-2026-09-25",
            authorization_basis="project-authored deterministic fixture",
            allowed_target_uses=[
                "supervised fine-tuning experiments",
                "dataset pipeline evaluation",
            ],
            reviewed_at="2026-09-25T00:00:00Z",
            reviewer="project-team",
        )
    else:
        teacher = TeacherEntry.model_validate(
            {
                "teacher_id": "teacher-main",
                "provider": "openai-compatible",
                "model": "replace-with-exact-model-version",
                "base_url": "https://example.invalid/v1",
                "api_key_env": "QAFORGE_TEACHER_API_KEY",
                "authorization_status": AuthorizationStatus.UNCLEAR,
                "terms_snapshot_id": "replace-with-dated-terms-snapshot",
                "authorization_basis": "requires review before use",
                "allowed_target_uses": ["requires review before use"],
                "reviewed_at": "2026-09-25T00:00:00Z",
                "reviewer": "project-team",
            }
        )
    write_yaml(root / "registry" / "teachers.yaml", {"teachers": [teacher]})
    reviewer = ReviewerEntry(
        reviewer_id="demo-fixture" if demo else "reviewer-main",
        authorization_status=(
            AuthorizationStatus.APPROVED if demo else AuthorizationStatus.UNCLEAR
        ),
        allowed_categories=["*"],
        authorization_basis=(
            "project-authored deterministic fixture"
            if demo
            else "requires operator approval before use"
        ),
        reviewed_at="2026-09-25T00:00:00Z",
        authorized_by="project-team",
    )
    write_yaml(root / "registry" / "reviewers.yaml", {"reviewers": [reviewer]})
    write_yaml(
        root / "registry" / "taxonomy.yaml",
        {
            "categories": categories,
            "domains": sorted({seed.dimensions.domain for seed in seeds}),
            "tasks": sorted({seed.dimensions.task for seed in seeds}),
            "reasoning": sorted({seed.dimensions.reasoning for seed in seeds}),
            "answer_forms": sorted({seed.dimensions.answer_form for seed in seeds}),
        },
    )
    write_jsonl(root / "seeds" / "seeds.jsonl", seeds)
    write_jsonl(
        root / "registry" / "protected-benchmarks.jsonl",
        [
            {
                "benchmark_id": "protected-example-001",
                "question": "A protected benchmark question that must never enter training.",
                "answer": "reserved",
            }
        ],
    )
    write_text(
        root / "README.md",
        "# Corpus workspace\n\n"
        "Run `qaforge doctor .` before generation. "
        "Generated runs and releases are immutable.\n",
    )
    return root
