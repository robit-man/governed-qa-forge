from __future__ import annotations

import json
import re
import secrets
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from qaforge.errors import ConfigurationError, ImmutableArtifactError
from qaforge.io import (
    canonical_json,
    read_jsonl,
    sha256_text,
    write_json,
    write_jsonl,
    write_text,
    write_yaml,
)
from qaforge.models import (
    AuthorizationStatus,
    CandidateRecord,
    Dimensions,
    ForgeConfig,
    GenerationConfig,
    QualityConfig,
    ReleaseConfig,
    ReviewerEntry,
    RiskLevel,
    SeedRecord,
    SourceEntry,
    SplitConfig,
    TeacherEntry,
    VerifierKind,
    VerifierSpec,
)
from qaforge.service import ServiceSettings, create_agent_app, create_control_app
from qaforge.workspace import Workspace

PILOT_CATEGORIES = (
    "inventory-reconciliation",
    "financial-arithmetic",
    "linear-equations",
    "proportional-allocation",
    "robust-statistics",
    "dependency-planning",
    "set-accounting",
    "structured-aggregation",
    "deductive-logic",
    "program-tracing",
)
LABEL_LEFT = (
    "amber",
    "birch",
    "cobalt",
    "delta",
    "ember",
    "fjord",
    "granite",
    "harbor",
    "indigo",
    "juniper",
)
LABEL_RIGHT = (
    "atlas",
    "beacon",
    "cedar",
    "drift",
    "elm",
    "falcon",
    "grove",
    "hearth",
    "islet",
    "keystone",
)


def _label(index: int) -> str:
    return f"{LABEL_LEFT[index % 10]} {LABEL_RIGHT[(index // 10) % 10]}".title()


def _article(noun: str) -> str:
    return "an" if noun[0].casefold() in "aeiou" else "a"


def _difficulty(index: int) -> str:
    position = index % 10
    if position < 3:
        return "introductory"
    if position < 8:
        return "intermediate"
    return "advanced"


def _dimensions(
    category: str,
    domain: str,
    task: str,
    reasoning: str,
    answer_form: str,
    index: int,
) -> Dimensions:
    return Dimensions(
        category=category,
        domain=domain,
        task=task,
        reasoning=reasoning,
        answer_form=answer_form,
        difficulty=_difficulty(index),  # type: ignore[arg-type]
        evidence_mode="deterministic",
        risk=RiskLevel.ORDINARY,
    )


def _seed(
    category: str,
    index: int,
    question: str,
    answer: str,
    verifier: VerifierSpec,
    dimensions: Dimensions,
) -> SeedRecord:
    slug = category.replace("-", "_")
    return SeedRecord(
        seed_id=f"pilot-{slug}-{index:04d}",
        lineage_id=f"pilot-family-{slug}-{index:04d}",
        question=question,
        reference_answer=answer,
        dimensions=dimensions,
        verifier=verifier,
        source_ids=["SRC-PILOT-AUTHORED"],
    )


def calibration_seeds(size: int = 1000) -> list[SeedRecord]:
    if size < 10 or size % len(PILOT_CATEGORIES) != 0:
        raise ConfigurationError("calibration size must be a positive multiple of 10")
    per_category = size // len(PILOT_CATEGORIES)
    seeds: list[SeedRecord] = []
    for index in range(per_category):
        label = _label(index)

        start = 140 + index * 7
        received = 31 + (index * 11) % 83
        shipped = 44 + (index * 13) % 71
        damaged = 2 + index % 9
        inventory = start + received - shipped - damaged
        seeds.append(
            _seed(
                "inventory-reconciliation",
                index,
                f"At the {label} depot, inventory starts at {start} units, then {received} "
                f"units arrive, {shipped} units ship, and {damaged} damaged units are removed. "
                "How many usable units remain? Answer with the integer only.",
                str(inventory),
                VerifierSpec(kind=VerifierKind.NUMERIC, expected=inventory),
                _dimensions(
                    "inventory-reconciliation",
                    "operations",
                    "derive",
                    "quantitative",
                    "concise",
                    index,
                ),
            )
        )

        price = Decimal(25 + (index * 13) % 170) + Decimal((index * 7) % 100) / 100
        discount = (5, 10, 15, 20, 25)[index % 5]
        tax = (5, 6, 7, 8, 9)[(index // 5) % 5]
        final_price = (price * Decimal(100 - discount) / 100 * Decimal(100 + tax) / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        seeds.append(
            _seed(
                "financial-arithmetic",
                index,
                f"The {label} procurement item costs {price:.2f} dollars. Apply a {discount}% "
                f"discount, then apply {tax}% sales tax to the discounted price. What is the "
                "final price rounded to the nearest cent? Answer with the number only.",
                f"{final_price:.2f}",
                VerifierSpec(kind=VerifierKind.NUMERIC, expected=str(final_price), tolerance=0.001),
                _dimensions(
                    "financial-arithmetic",
                    "mathematics",
                    "derive",
                    "quantitative",
                    "concise",
                    index,
                ),
            )
        )

        solution = 4 + index
        coefficient = 2 + index % 7
        offset = 9 + (index * 5) % 31
        total = coefficient * solution + offset
        seeds.append(
            _seed(
                "linear-equations",
                index,
                f"At the {label} station, solve {coefficient}x + {offset} = {total}. "
                "Return only the integer value of x.",
                str(solution),
                VerifierSpec(kind=VerifierKind.NUMERIC, expected=solution),
                _dimensions(
                    "linear-equations", "mathematics", "derive", "quantitative", "concise", index
                ),
            )
        )

        first_ratio = 2 + index % 3
        second_ratio = 3 + (index // 3) % 3
        third_ratio = 4 + (index // 7) % 3
        unit = 40 + index
        total_budget = unit * (first_ratio + second_ratio + third_ratio)
        second_share = unit * second_ratio
        seeds.append(
            _seed(
                "proportional-allocation",
                index,
                f"The {label} budget of {total_budget} credits is divided among teams A, B, and C "
                f"in the ratio {first_ratio}:{second_ratio}:{third_ratio}. How many credits does "
                "team B receive? Answer with the integer only.",
                str(second_share),
                VerifierSpec(kind=VerifierKind.NUMERIC, expected=second_share),
                _dimensions(
                    "proportional-allocation",
                    "mathematics",
                    "derive",
                    "quantitative",
                    "concise",
                    index,
                ),
            )
        )

        center = 20 + index
        readings = [center + 7, center - 2, center + 3, center - 9, center + 1, center + 12, center]
        median = sorted(readings)[len(readings) // 2]
        seeds.append(
            _seed(
                "robust-statistics",
                index,
                f"The seven {label} sensor readings are {readings}. What is their median? "
                "Answer with the integer only.",
                str(median),
                VerifierSpec(kind=VerifierKind.NUMERIC, expected=median),
                _dimensions(
                    "robust-statistics", "mathematics", "derive", "quantitative", "concise", index
                ),
            )
        )

        duration_a = 2 + index % 6
        duration_b = 3 + (index * 2) % 7
        duration_c = 4 + (index * 3) % 8
        duration_d = 2 + index % 5
        finish = max(duration_a, duration_b) + duration_c + duration_d
        seeds.append(
            _seed(
                "dependency-planning",
                index,
                f"In the {label} plan, independent tasks A and B take {duration_a} and "
                f"{duration_b} hours. Task C takes {duration_c} hours and starts only after both "
                f"A and B finish. Task D then takes {duration_d} hours after C. If A and B start "
                "together, what is the earliest completion time in hours? Answer with the "
                "integer only.",
                str(finish),
                VerifierSpec(kind=VerifierKind.NUMERIC, expected=finish),
                _dimensions(
                    "dependency-planning", "operations", "derive", "constraint", "concise", index
                ),
            )
        )

        population = 180 + index * 3
        uses_alpha = 70 + index % 31
        uses_beta = 65 + (index * 2) % 29
        uses_both = 20 + index % 17
        neither = population - (uses_alpha + uses_beta - uses_both)
        seeds.append(
            _seed(
                "set-accounting",
                index,
                f"Among {population} members of the {label} group, {uses_alpha} use service "
                f"Alpha, {uses_beta} use service Beta, and {uses_both} use both. How many use "
                "neither service? Answer with the integer only.",
                str(neither),
                VerifierSpec(kind=VerifierKind.NUMERIC, expected=neither),
                _dimensions(
                    "set-accounting", "mathematics", "derive", "quantitative", "concise", index
                ),
            )
        )

        values = [11 + index, 7 + (index * 3) % 41, 19 + (index * 5) % 37]
        aggregation = {
            "maximum": max(values),
            "minimum": min(values),
            "range": max(values) - min(values),
            "total": sum(values),
        }
        aggregation_answer = canonical_json(aggregation)
        seeds.append(
            _seed(
                "structured-aggregation",
                index,
                f"For the {label} readings {values}, return one JSON object with exactly the "
                'integer keys "maximum", "minimum", "range", and "total". Range means maximum '
                "minus minimum. Do not include prose.",
                aggregation_answer,
                VerifierSpec(kind=VerifierKind.JSON, expected=aggregation),
                _dimensions(
                    "structured-aggregation", "computing", "transform", "constraint", "json", index
                ),
            )
        )

        noun_a = f"{LABEL_LEFT[index % 10]}ling"
        noun_b = f"{LABEL_RIGHT[(index // 10) % 10]}er"
        noun_c = f"{LABEL_LEFT[(index + 3) % 10]}form"
        if index % 2 == 0:
            logic_question = (
                f"Every {noun_a} is {_article(noun_b)} {noun_b}, and no {noun_b} is "
                f"{_article(noun_c)} {noun_c}. Can any {noun_a} be {_article(noun_c)} "
                f"{noun_c}? Answer yes or no."
            )
            logic_answer = "no"
        else:
            logic_question = (
                f"Some {noun_a}s are {noun_b}s, and every {noun_b} is {_article(noun_c)} "
                f"{noun_c}. Must at least one {noun_a} be {_article(noun_c)} {noun_c}? "
                "Answer yes or no."
            )
            logic_answer = "yes"
        seeds.append(
            _seed(
                "deductive-logic",
                index,
                logic_question,
                logic_answer,
                VerifierSpec(kind=VerifierKind.EXACT, expected=logic_answer),
                _dimensions("deductive-logic", "logic", "classify", "deductive", "concise", index),
            )
        )

        sequence = [3 + index % 11, 4 + index % 13, 7 + index % 17, 8 + index % 19, 10 + index % 23]
        factor = 2 + index % 4
        traced = sum(value * factor for value in sequence if value % 2 == 0)
        seeds.append(
            _seed(
                "program-tracing",
                index,
                f"The {label} routine starts with {sequence}, keeps only even integers, multiplies "
                f"each retained integer by {factor}, and sums the results. What integer does the "
                "routine return? Answer with the integer only.",
                str(traced),
                VerifierSpec(kind=VerifierKind.NUMERIC, expected=traced),
                _dimensions(
                    "program-tracing", "computing", "derive", "constraint", "concise", index
                ),
            )
        )
    return seeds


def scaffold_calibration_workspace(root: Path, size: int = 1000) -> Path:
    root = root.resolve()
    if root.exists() and any(root.iterdir()):
        raise ImmutableArtifactError(f"workspace is not empty: {root}")
    root.mkdir(parents=True, exist_ok=True)
    (root / "registry").mkdir()
    (root / "seeds").mkdir()
    seeds = calibration_seeds(size)
    category_floor = size // len(PILOT_CATEGORIES)
    config = ForgeConfig(
        demo_mode=False,
        split=SplitConfig(train=0.9, validation=0.05, test=0.05, salt="opaque-pilot-2026-v1"),
        generation=GenerationConfig(
            provider_id="teacher-opaque-calibration",
            candidates_per_seed=3,
            max_generation_depth=1,
            temperature=0,
            max_tokens=256,
        ),
        quality=QualityConfig(
            target_size=size,
            near_duplicate_threshold=1.0,
            semantic_threshold=1.0,
            semantic_dimensions=384,
            semantic_lsh_bands=2,
            max_per_lineage=1,
            coverage_floors={
                "category": {category: category_floor for category in PILOT_CATEGORIES},
                "difficulty": {
                    value: 1 for value in sorted({seed.dimensions.difficulty for seed in seeds})
                },
                "answer_form": {
                    value: 1 for value in sorted({seed.dimensions.answer_form for seed in seeds})
                },
            },
        ),
        release=ReleaseConfig(
            dataset_id="opaque-agent-calibration",
            version="0.2.0-calibration.1",
            license="MIT",
            intended_uses=["dataset pipeline evaluation"],
            prohibited_uses=[
                "production fine-tuning before independent review",
                "high-stakes automated decisions",
                "misrepresentation as human-authored production data",
            ],
        ),
    )
    source = SourceEntry(
        source_id="SRC-PILOT-AUTHORED",
        uri="urn:qaforge:project-authored:opaque-calibration-v1",
        retrieved_at="2026-09-25T00:00:00Z",
        snapshot_sha256=sha256_text("qaforge-opaque-calibration-generator-v1"),
        authorization_status=AuthorizationStatus.APPROVED,
        license_basis="project-authored deterministic calibration material",
        redistribution_allowed=True,
        allowed_target_uses=["dataset pipeline evaluation"],
        compatible_release_licenses=["MIT"],
        attribution="Governed QA Forge calibration corpus",
        reviewer="project-team",
    )
    teacher = TeacherEntry(
        teacher_id="teacher-opaque-calibration",
        provider="opaque-agent-service",
        model="codex-authored-deterministic-calibration-v1",
        authorization_status=AuthorizationStatus.APPROVED,
        terms_snapshot_id="operator-authorization-2026-09-25",
        authorization_basis=(
            "operator explicitly authorized Codex to act as teacher for the documented "
            "1,000-record calibration pilot"
        ),
        allowed_target_uses=["dataset pipeline evaluation"],
        reviewed_at="2026-09-25T00:00:00Z",
        reviewer="project-operator",
    )
    reviewer = ReviewerEntry(
        reviewer_id="independent-calibration-reviewer",
        authorization_status=AuthorizationStatus.APPROVED,
        allowed_categories=["*"],
        authorization_basis="registered for a later independent review; pilot records no decisions",
        reviewed_at="2026-09-25T00:00:00Z",
        authorized_by="project-team",
    )
    write_yaml(root / "qaforge.yaml", config)
    write_yaml(root / "registry" / "sources.yaml", {"sources": [source]})
    write_yaml(root / "registry" / "teachers.yaml", {"teachers": [teacher]})
    write_yaml(root / "registry" / "reviewers.yaml", {"reviewers": [reviewer]})
    write_yaml(
        root / "registry" / "taxonomy.yaml",
        {
            "categories": list(PILOT_CATEGORIES),
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
                "benchmark_id": "protected-calibration-example-001",
                "question": "Reserved evaluation item withheld from calibration generation.",
                "answer": "reserved",
            }
        ],
    )
    write_text(
        root / "README.md",
        "# Opaque service calibration workspace\n\n"
        "This workspace is a deterministic technical calibration. Its selected records remain "
        "pending independent review and are not a production release.\n",
    )
    return root


def solve_blind_calibration_task(question: str) -> str:
    """Solve only from the worker-visible question; no workspace or broker access is accepted."""
    match = re.search(
        r"inventory starts at (\d+) units, then (\d+) units arrive, (\d+) units ship, "
        r"and (\d+) damaged units",
        question,
    )
    if match:
        start, received, shipped, damaged = map(int, match.groups())
        return str(start + received - shipped - damaged)

    match = re.search(
        r"costs (\d+\.\d{2}) dollars\. Apply a (\d+)% discount, then apply (\d+)% sales tax",
        question,
    )
    if match:
        price = Decimal(match.group(1))
        discount = Decimal(match.group(2))
        tax = Decimal(match.group(3))
        result = (price * (100 - discount) / 100 * (100 + tax) / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return f"{result:.2f}"

    match = re.search(r"solve (\d+)x \+ (\d+) = (\d+)", question)
    if match:
        coefficient, offset, total = map(int, match.groups())
        return str((total - offset) // coefficient)

    match = re.search(r"budget of (\d+) credits .* ratio (\d+):(\d+):(\d+)", question)
    if match:
        total, first, second, third = map(int, match.groups())
        return str(total * second // (first + second + third))

    match = re.search(r"sensor readings are (\[[0-9, ]+\])", question)
    if match:
        values = json.loads(match.group(1))
        return str(sorted(values)[len(values) // 2])

    match = re.search(
        r"tasks A and B take (\d+) and (\d+) hours\. Task C takes (\d+) hours.*"
        r"Task D then takes (\d+) hours",
        question,
    )
    if match:
        duration_a, duration_b, duration_c, duration_d = map(int, match.groups())
        return str(max(duration_a, duration_b) + duration_c + duration_d)

    match = re.search(
        r"Among (\d+) members .* (\d+) use service Alpha, (\d+) use service Beta, "
        r"and (\d+) use both",
        question,
    )
    if match:
        population, alpha, beta, both = map(int, match.groups())
        return str(population - (alpha + beta - both))

    match = re.search(r"readings (\[[0-9, ]+\]), return one JSON object", question)
    if match:
        values = json.loads(match.group(1))
        return canonical_json(
            {
                "maximum": max(values),
                "minimum": min(values),
                "range": max(values) - min(values),
                "total": sum(values),
            }
        )

    if "Can any" in question and "Answer yes or no" in question:
        return "no"
    if "Must at least one" in question and "Answer yes or no" in question:
        return "yes"

    match = re.search(
        r"starts with (\[[0-9, ]+\]), keeps only even integers, multiplies each retained "
        r"integer by (\d+)",
        question,
    )
    if match:
        values = json.loads(match.group(1))
        factor = int(match.group(2))
        return str(sum(value * factor for value in values if value % 2 == 0))
    raise ConfigurationError("blind calibration worker could not solve the supplied task")


def run_calibration_pilot(
    root: Path,
    size: int = 1000,
    run_id: str = "opaque-calibration-1000",
) -> dict[str, object]:
    from fastapi.testclient import TestClient

    scaffold_calibration_workspace(root, size)
    settings = ServiceSettings(
        workspace=root,
        database=root / ".service" / "service.sqlite3",
        agent_token=secrets.token_urlsafe(48),
        control_token=secrets.token_urlsafe(48),
        lease_seconds=900,
    )
    control_headers = {"Authorization": f"Bearer {settings.control_token}"}
    agent_headers = {"Authorization": f"Bearer {settings.agent_token}"}
    submitted = 0
    with (
        TestClient(create_control_app(settings)) as control,
        TestClient(create_agent_app(settings)) as agent,
    ):
        created = control.post("/v1/runs", json={"run_id": run_id}, headers=control_headers)
        created.raise_for_status()
        while True:
            lease_response = agent.post("/v1/tasks/lease", headers=agent_headers)
            if lease_response.status_code == 204:
                break
            lease_response.raise_for_status()
            task = lease_response.json()
            answer = solve_blind_calibration_task(task["messages"][0]["content"])
            response = agent.post(
                f"/v1/tasks/{task['task_id']}/responses",
                json={"lease_token": task["lease_token"], "answer": answer},
                headers=agent_headers,
            )
            response.raise_for_status()
            if response.json() != {"status": "recorded"}:
                raise ConfigurationError("worker receipt exposed an unexpected response")
            submitted += 1
        finalized = control.post(f"/v1/runs/{run_id}/finalize", headers=control_headers)
        finalized.raise_for_status()
        service_status = finalized.json()

    workspace = Workspace(root)
    raw = read_jsonl(workspace.run_dir(run_id) / "raw.jsonl", CandidateRecord)
    evaluated = read_jsonl(workspace.run_dir(run_id) / "evaluated.jsonl", CandidateRecord)
    selected = read_jsonl(workspace.run_dir(run_id) / "selected.jsonl", CandidateRecord)
    category_counts = Counter(item.dimensions.category for item in selected)
    failed_verification = sum(
        item.verification is None or not item.verification.passed for item in evaluated
    )
    failed_validation = sum(
        any(gate.status.value == "fail" for gate in item.validation) for item in evaluated
    )
    contamination_rejections = sum(not item.contamination.passed for item in evaluated)
    result: dict[str, object] = {
        "calibration_only": True,
        "production_release_created": False,
        "review_status": "awaiting_independent_review",
        "workspace": str(root.resolve()),
        "run_id": run_id,
        "service_state": service_status["state"],
        "submitted_tasks": submitted,
        "raw_candidates": len(raw),
        "selected_records": len(selected),
        "unique_lineages": len({item.lineage_id for item in selected}),
        "failed_validation_candidates": failed_validation,
        "failed_verification_candidates": failed_verification,
        "contamination_rejections": contamination_rejections,
        "category_counts": dict(sorted(category_counts.items())),
        "forge_stage": service_status["forge_state"]["stage"],
    }
    write_json(root / "calibration-report.json", result)
    return result
