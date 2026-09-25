from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from itertools import pairwise

from qaforge.models import BenchmarkRecord, CandidateRecord, ContaminationResult, QualityConfig


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", value)).strip()


def _features(value: str) -> list[str]:
    tokens = normalize_text(value).split()
    features = list(tokens)
    features.extend(f"{left}::{right}" for left, right in pairwise(tokens))
    return features


def _stable_int(value: str, size: int = 8) -> int:
    return int.from_bytes(hashlib.blake2b(value.encode(), digest_size=size).digest(), "big")


@dataclass(slots=True)
class Fingerprint:
    exact: str
    shingles: frozenset[str]
    vector: tuple[float, ...]
    signature: int


def fingerprint(value: str, dimensions: int) -> Fingerprint:
    normalized = normalize_text(value)
    features = _features(value)
    vector = [0.0] * dimensions
    bit_scores = [0] * 64
    for feature in features:
        digest = _stable_int(feature)
        index = digest % dimensions
        sign = 1.0 if (digest >> 8) & 1 else -1.0
        vector[index] += sign
        for bit in range(64):
            bit_scores[bit] += 1 if (digest >> bit) & 1 else -1
    norm = math.sqrt(sum(value * value for value in vector))
    if norm:
        vector = [value / norm for value in vector]
    signature = sum(1 << bit for bit, score in enumerate(bit_scores) if score >= 0)
    shingles = frozenset(
        " ".join(normalized.split()[index : index + 3])
        for index in range(max(1, len(normalized.split()) - 2))
    )
    return Fingerprint(
        exact=hashlib.sha256(normalized.encode()).hexdigest(),
        shingles=shingles,
        vector=tuple(vector),
        signature=signature,
    )


def jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return max(0.0, min(1.0, sum(a * b for a, b in zip(left, right, strict=True))))


class FingerprintIndex:
    def __init__(self, bands: int) -> None:
        self.bands = bands
        self.band_bits = 64 // bands
        self.mask = (1 << self.band_bits) - 1
        self.buckets: dict[tuple[int, int], set[str]] = defaultdict(set)
        self.exact: dict[str, set[str]] = defaultdict(set)
        self.items: dict[str, Fingerprint] = {}

    def _keys(self, item: Fingerprint) -> list[tuple[int, int]]:
        return [
            (band, (item.signature >> (band * self.band_bits)) & self.mask)
            for band in range(self.bands)
        ]

    def query(self, item: Fingerprint) -> set[str]:
        result = set(self.exact.get(item.exact, set()))
        for key in self._keys(item):
            result.update(self.buckets.get(key, set()))
        return result

    def add(self, item_id: str, item: Fingerprint) -> None:
        self.items[item_id] = item
        self.exact[item.exact].add(item_id)
        for key in self._keys(item):
            self.buckets[key].add(item_id)


def _similarity(left: Fingerprint, right: Fingerprint) -> tuple[float, float]:
    return jaccard(left.shingles, right.shingles), cosine(left.vector, right.vector)


def decontaminate(
    candidates: list[CandidateRecord],
    benchmarks: list[BenchmarkRecord],
    config: QualityConfig,
) -> list[CandidateRecord]:
    """FR-008: indexed exact, lexical, semantic-fingerprint, and benchmark checks."""
    benchmark_index = FingerprintIndex(config.semantic_lsh_bands)
    for benchmark in benchmarks:
        benchmark_index.add(
            benchmark.benchmark_id, fingerprint(benchmark.question, config.semantic_dimensions)
        )

    candidate_index = FingerprintIndex(config.semantic_lsh_bands)
    candidate_map: dict[str, CandidateRecord] = {}
    seen_content: dict[str, str] = {}
    result: list[CandidateRecord] = []

    for candidate in sorted(candidates, key=lambda item: item.record_id):
        item = fingerprint(candidate.question, config.semantic_dimensions)
        contamination = ContaminationResult()
        reasons = list(candidate.rejection_reasons)

        if candidate.content_sha256 in seen_content:
            match_id = seen_content[candidate.content_sha256]
            contamination = ContaminationResult(
                passed=False,
                match_type="exact_record",
                match_id=match_id,
                similarity=1.0,
                detail="canonical question/answer duplicate",
            )

        if contamination.passed:
            for match_id in sorted(benchmark_index.query(item)):
                lexical, semantic = _similarity(item, benchmark_index.items[match_id])
                if (
                    lexical >= config.near_duplicate_threshold
                    or semantic >= config.semantic_threshold
                ):
                    contamination = ContaminationResult(
                        passed=False,
                        match_type="protected_benchmark",
                        match_id=match_id,
                        similarity=max(lexical, semantic),
                        detail=f"lexical={lexical:.3f}; semantic={semantic:.3f}",
                    )
                    break

        nearest = 0.0
        if contamination.passed:
            for match_id in sorted(candidate_index.query(item)):
                prior = candidate_map[match_id]
                lexical, semantic = _similarity(item, candidate_index.items[match_id])
                nearest = max(nearest, lexical, semantic)
                if prior.lineage_id == candidate.lineage_id:
                    continue
                if (
                    lexical >= config.near_duplicate_threshold
                    or semantic >= config.semantic_threshold
                ):
                    contamination = ContaminationResult(
                        passed=False,
                        match_type="cross_lineage_near_duplicate",
                        match_id=match_id,
                        similarity=max(lexical, semantic),
                        detail=f"lexical={lexical:.3f}; semantic={semantic:.3f}",
                    )
                    break

        if not contamination.passed:
            reasons.append(f"contamination:{contamination.match_type}:{contamination.match_id}")
        elif nearest:
            contamination = contamination.model_copy(
                update={
                    "similarity": nearest,
                    "detail": f"nearest candidate similarity={nearest:.3f}",
                }
            )

        updated = candidate.model_copy(
            update={"contamination": contamination, "rejection_reasons": reasons}
        )
        result.append(updated)
        seen_content.setdefault(candidate.content_sha256, candidate.record_id)
        candidate_index.add(candidate.record_id, item)
        candidate_map[candidate.record_id] = candidate

    return result
