from __future__ import annotations

from dataclasses import dataclass

PRODUCTION_POLICY_ID = "qaforge-reasoning-sft-minimum-v1"
EVALUATION_POLICY_ID = "qaforge-base-vs-tuned-three-seed-v1"
REQUIRED_TRAINING_SEEDS = (17, 29, 47)
MIN_PRODUCTION_TRAIN = 20_000
MIN_PRODUCTION_VALIDATION = 2_000
MIN_PRODUCTION_TEST = 2_000
MIN_PRODUCTION_TOTAL = MIN_PRODUCTION_TRAIN + MIN_PRODUCTION_VALIDATION + MIN_PRODUCTION_TEST
MIN_PRODUCTION_CATEGORIES = 10
REQUIRED_DIFFICULTIES = frozenset({"introductory", "intermediate", "advanced"})

AIWG_BEHAVIOR_DOMAINS = frozenset(
    {
        "requirements-and-acceptance",
        "evidence-before-assertion",
        "provenance-and-traceability",
        "threat-modeling-and-least-authority",
        "independent-verification",
        "test-and-quality-gates",
        "change-impact-and-architecture",
        "operational-readiness-and-recovery",
        "context-boundaries-and-poisoning-resistance",
        "orchestration-and-accountable-integration",
    }
)


@dataclass(frozen=True, slots=True)
class ProductionCorpusMetrics:
    train: int
    validation: int
    test: int
    categories: frozenset[str]
    difficulties: frozenset[str]
    aiwg_behavior_domains: frozenset[str]


def production_policy_failures(metrics: ProductionCorpusMetrics) -> list[str]:
    failures: list[str] = []
    floors = {
        "train": MIN_PRODUCTION_TRAIN,
        "validation": MIN_PRODUCTION_VALIDATION,
        "test": MIN_PRODUCTION_TEST,
    }
    observed = {
        "train": metrics.train,
        "validation": metrics.validation,
        "test": metrics.test,
    }
    for split, floor in floors.items():
        if observed[split] < floor:
            failures.append(f"{split}={observed[split]} below fixed minimum {floor}")
    if len(metrics.categories) < MIN_PRODUCTION_CATEGORIES:
        failures.append(
            f"categories={len(metrics.categories)} below fixed minimum {MIN_PRODUCTION_CATEGORIES}"
        )
    missing_difficulties = sorted(REQUIRED_DIFFICULTIES - metrics.difficulties)
    if missing_difficulties:
        failures.append(f"missing required difficulties: {missing_difficulties}")
    missing_domains = sorted(AIWG_BEHAVIOR_DOMAINS - metrics.aiwg_behavior_domains)
    if missing_domains:
        failures.append(f"missing required AIWG behavior domains: {missing_domains}")
    return failures
