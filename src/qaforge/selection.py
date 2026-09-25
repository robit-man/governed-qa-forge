from __future__ import annotations

from collections import Counter

from qaforge.errors import GateError
from qaforge.models import CandidateRecord, QualityConfig
from qaforge.validation import mandatory_gates_pass

DIFFICULTY = {"introductory": 0.25, "intermediate": 0.6, "advanced": 1.0}


def coverage_features(candidate: CandidateRecord) -> set[tuple[str, str]]:
    dimensions = candidate.dimensions
    return {
        ("category", dimensions.category),
        ("domain", dimensions.domain),
        ("task", dimensions.task),
        ("reasoning", dimensions.reasoning),
        ("answer_form", dimensions.answer_form),
        ("difficulty", dimensions.difficulty),
        ("evidence_mode", dimensions.evidence_mode),
        ("risk", dimensions.risk.value),
    }


def _quality(candidate: CandidateRecord) -> float:
    validation_fraction = (
        sum(item.status.value == "pass" for item in candidate.validation)
        / len(candidate.validation)
        if candidate.validation
        else 0
    )
    verification = 1.0 if candidate.verification and candidate.verification.passed else 0.0
    novelty = 1.0 - candidate.contamination.similarity
    difficulty = DIFFICULTY[candidate.dimensions.difficulty]
    return max(
        0.0,
        min(1.0, 0.3 * validation_fraction + 0.4 * verification + 0.2 * novelty + 0.1 * difficulty),
    )


def select_candidates(
    candidates: list[CandidateRecord], config: QualityConfig
) -> list[CandidateRecord]:
    eligible = [item for item in candidates if mandatory_gates_pass(item)]
    ranked = [item.model_copy(update={"quality_score": _quality(item)}) for item in eligible]
    ranked.sort(key=lambda item: (-item.quality_score, item.record_id))

    selected: list[CandidateRecord] = []
    lineage_counts: Counter[str] = Counter()
    covered: set[tuple[str, str]] = set()

    def add(item: CandidateRecord) -> bool:
        if len(selected) >= config.target_size:
            return False
        if lineage_counts[item.lineage_id] >= config.max_per_lineage:
            return False
        features = coverage_features(item)
        gain = len(features - covered)
        updated = item.model_copy(update={"selected": True, "coverage_score": float(gain)})
        selected.append(updated)
        lineage_counts[item.lineage_id] += 1
        covered.update(features)
        return True

    for dimension, values in sorted(config.coverage_floors.items()):
        for value, floor in sorted(values.items()):
            feature = (dimension, value)
            options = [item for item in ranked if feature in coverage_features(item)]
            count = sum(feature in coverage_features(item) for item in selected)
            for item in options:
                if count >= floor:
                    break
                if item.record_id not in {chosen.record_id for chosen in selected} and add(item):
                    count += 1
            if count < floor:
                raise GateError(
                    f"coverage floor cannot be met for {dimension}.{value}: "
                    f"required {floor}, selected {count}"
                )

    remaining = [item for item in ranked if item.record_id not in {x.record_id for x in selected}]
    while remaining and len(selected) < config.target_size:

        def utility(item: CandidateRecord) -> tuple[float, str]:
            features = coverage_features(item)
            return item.quality_score + 0.02 * len(features - covered), item.record_id

        remaining.sort(key=lambda item: (-utility(item)[0], utility(item)[1]))
        candidate = remaining.pop(0)
        add(candidate)

    return sorted(selected, key=lambda item: item.record_id)
