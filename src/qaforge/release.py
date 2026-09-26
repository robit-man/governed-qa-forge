from __future__ import annotations

import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from qaforge.anchors import aiwg_behavior_anchors, behavior_anchor_private_identifiers
from qaforge.dedup import decontaminate
from qaforge.errors import ConfigurationError, GateError, ImmutableArtifactError
from qaforge.formatting import (
    ASSISTANT_FORMAT_ID,
    is_standard_training_row,
    legacy_content_sha256,
    training_messages,
)
from qaforge.io import (
    canonical_json,
    read_jsonl,
    sha256_file,
    sha256_text,
    utc_now,
    write_json,
    write_jsonl,
    write_text,
)
from qaforge.models import (
    BehaviorAnchorEntry,
    CandidateRecord,
    CorpusClass,
    GateStatus,
    ReviewState,
    RunStage,
    Split,
)
from qaforge.opacity import assert_training_content_is_opaque, exposed_private_identifiers
from qaforge.pipeline import _write_state, assert_run_artifacts, load_state
from qaforge.selection import coverage_features
from qaforge.splitter import assign_split
from qaforge.standards import (
    EVALUATION_POLICY_ID,
    PRODUCTION_POLICY_ID,
    REQUIRED_TRAINING_SEEDS,
    ProductionCorpusMetrics,
    production_policy_failures,
)
from qaforge.transforms import transform_question
from qaforge.validation import validate_candidate, verify_answer
from qaforge.workspace import Workspace


def _training_row(item: CandidateRecord) -> dict[str, Any]:
    return {"messages": training_messages(item.question, item.derivation, item.answer)}


def _metadata_row(
    item: CandidateRecord, anchor_map: dict[str, BehaviorAnchorEntry]
) -> dict[str, Any]:
    return {
        "record_id": item.record_id,
        "category": item.dimensions.category,
        "domain": item.dimensions.domain,
        "task": item.dimensions.task,
        "reasoning": item.dimensions.reasoning,
        "answer_form": item.dimensions.answer_form,
        "difficulty": item.dimensions.difficulty,
        "evidence_mode": item.dimensions.evidence_mode,
        "risk": item.dimensions.risk.value,
        "is_synthetic": True,
        "generation_depth": item.generation_depth,
        "seed_id": item.seed_id,
        "seed_question": item.seed_question,
        "question_transform_id": item.question_transform_id,
        "lineage_id": item.lineage_id,
        "source_ids": item.source_ids,
        "behavior_anchors": [
            {
                "anchor_id": anchor_id,
                "domain": anchor_map[anchor_id].domain,
            }
            for anchor_id in item.behavior_anchor_ids
        ],
        "teacher_id": item.teacher_id,
        "teacher_model": item.teacher_model,
        "teacher_terms_snapshot_id": item.teacher_terms_snapshot_id,
        "prompt_template_id": item.prompt_template_id,
        "prompt_template_sha256": item.prompt_template_sha256,
        "generation_run_id": item.generation_run_id,
        "content_sha256": item.content_sha256,
        "verifier": item.verification.model_dump(mode="json") if item.verification else None,
        "review": item.review.model_dump(mode="json") if item.review else None,
    }


def _datasheet(workspace: Workspace, counts: Counter[str], created_at: str) -> str:
    config = workspace.config()
    intended = "\n".join(f"- {item}" for item in config.release.intended_uses)
    prohibited = "\n".join(f"- {item}" for item in config.release.prohibited_uses)
    production_policy = (
        PRODUCTION_POLICY_ID
        if config.release.corpus_class is CorpusClass.PRODUCTION
        else "not applicable"
    )
    return f"""# Dataset card: {config.release.dataset_id} {config.release.version}

Generated: {created_at}

## Summary

Governed synthetic question/answer records for supervised fine-tuning. Every row passed
authorization, deterministic validation, independent answer verification, decontamination,
coverage-aware selection, and explicit review of its structured derivation. AIWG-informed
behavior anchors are expressed through the examples rather than named in trainer-visible messages.

## Composition

- Train: {counts["train"]}
- Validation: {counts["validation"]}
- Test: {counts["test"]}
- Synthetic fraction: 1.0
- Language: {config.language_bcp47}
- Corpus class: {config.release.corpus_class.value}
- Production policy: {production_policy}

## Intended uses

{intended}

## Prohibited uses

{prohibited}

## Limitations

Synthetic records inherit seed, teacher, verifier, taxonomy, and reviewer limitations. Passing
these gates is not proof of factual completeness, representativeness, legal fitness, or
suitability for high-stakes deployment.

## Evidence

See `manifest.json`, `croissant.json`, `provenance.jsonld`, `rejection-ledger.jsonl`, and
`generation-run-manifest.json`, `EVALUATION-PROTOCOL.md`, and `SHA256SUMS` in this release.
"""


def _evaluation_protocol() -> str:
    seeds = ", ".join(str(seed) for seed in REQUIRED_TRAINING_SEEDS)
    return f"""# Required fine-tuning evaluation protocol

Policy: `{EVALUATION_POLICY_ID}`

This dataset release is eligible for a training experiment; it is not evidence of convergence or
improved intelligence. Any improvement claim must:

1. train otherwise identical configurations with seeds {seeds};
2. compare every tuned checkpoint against the unchanged base model;
3. keep `test.jsonl` sealed until training, checkpoint selection, and hyperparameter choices end;
4. report aggregate and per-category capability, calibration, safety, and repetition metrics;
5. report all runs, variance, regressions, failures, and the exact dataset release anchor;
6. reject the claim if gains are not repeatable or material regressions appear.
"""


def build_release(workspace: Workspace, run_id: str, *, allow_test_fixture: bool = False) -> Path:
    config = workspace.config()
    if config.schema_version != "1.1":
        raise GateError("schema 1.0 workspaces are read-only and cannot build new releases")
    if config.release.corpus_class is CorpusClass.CALIBRATION:
        raise GateError("calibration corpora are permanently non-releasable")
    if config.release.corpus_class is CorpusClass.TEST_FIXTURE and not allow_test_fixture:
        raise GateError("test fixtures can be released only by the internal demo workflow")
    final_release_dir = workspace.release_dir(config.release.version)
    if final_release_dir.exists():
        raise ImmutableArtifactError(f"release already exists: {config.release.version}")
    report = workspace.doctor()
    if not report.passed:
        raise GateError("workspace doctor failed at release time")
    state = load_state(workspace, run_id)
    if state.stage is not RunStage.APPROVED:
        raise GateError(f"run is not review-complete: {state.stage.value}")
    assert_run_artifacts(workspace, run_id)
    selected = read_jsonl(workspace.run_dir(run_id) / "selected.jsonl", CandidateRecord)
    reviewed = read_jsonl(workspace.run_dir(run_id) / "reviewed.jsonl", CandidateRecord)
    selected_by_id = {item.record_id: item for item in selected}
    if {item.record_id for item in reviewed} != set(selected_by_id):
        raise GateError("reviewed records do not match the sealed selection")
    for item in reviewed:
        selected_item = selected_by_id[item.record_id]
        if item.model_dump(mode="json", exclude={"review"}) != selected_item.model_dump(
            mode="json", exclude={"review"}
        ):
            raise GateError(f"reviewed record differs from sealed selection: {item.record_id}")
    approved = [
        item for item in reviewed if item.review and item.review.decision is ReviewState.APPROVED
    ]
    if not approved:
        raise GateError("release has no approved records")
    if len(approved) < config.quality.target_size:
        raise GateError(
            "approved record count is below target_size: "
            f"approved={len(approved)}; target={config.quality.target_size}"
        )

    anchors = workspace.behavior_anchors()
    anchor_map = {item.anchor_id: item for item in anchors}
    private_identifiers = {
        *[source.source_id for source in workspace.sources()],
        *behavior_anchor_private_identifiers(anchors),
    }

    release_checked = decontaminate(approved, workspace.benchmarks(), config.quality)
    release_checks = {item.record_id: item for item in release_checked}
    for item in approved:
        if item.split is not assign_split(item.lineage_id, config.split):
            raise GateError(f"split drift detected: {item.record_id}")
        validation = validate_candidate(item, config)
        verification = verify_answer(item)
        if (
            any(result.status is GateStatus.FAIL for result in validation)
            or not verification.passed
        ):
            raise GateError(f"release-time validation failed: {item.record_id}")
        if not release_checks[item.record_id].contamination.passed:
            raise GateError(f"contaminated record cannot release: {item.record_id}")
        if not item.review or not item.review.reviewer or not item.review.reviewed_at:
            raise GateError(f"incomplete review evidence: {item.record_id}")
        if item.review.candidate_sha256 != item.content_sha256:
            raise GateError(f"review digest mismatch: {item.record_id}")
        if not item.review.derivation_verified:
            raise GateError(f"derivation was not explicitly verified: {item.record_id}")
        if not item.review.behavior_alignment_verified:
            raise GateError(f"behavior alignment was not explicitly verified: {item.record_id}")
        if not item.behavior_anchor_ids:
            raise GateError(f"record has no behavior anchor: {item.record_id}")
        if any(anchor_id not in anchor_map for anchor_id in item.behavior_anchor_ids):
            raise GateError(f"record has an unknown behavior anchor: {item.record_id}")
        visible_content = "\n".join([item.question, *item.derivation, item.answer]).casefold()
        assert_training_content_is_opaque(visible_content, private_identifiers, item.record_id)
        workspace.reviewer(item.review.reviewer, item.dimensions.category)
        if (
            item.review.reviewer == "demo-fixture"
            and config.release.corpus_class is CorpusClass.PRODUCTION
        ):
            raise GateError("demo review evidence cannot authorize a production release")

    duplicates = [
        item for item, count in Counter(x.content_sha256 for x in approved).items() if count > 1
    ]
    if duplicates:
        raise GateError(f"duplicate content hashes at release: {duplicates}")
    lineage_splits: dict[str, set[Split]] = defaultdict(set)
    for item in approved:
        lineage_splits[item.lineage_id].add(item.split)
    leaked = sorted(lineage for lineage, splits in lineage_splits.items() if len(splits) > 1)
    if leaked:
        raise GateError(f"lineages cross release splits: {leaked}")
    coverage_counts = Counter(feature for item in approved for feature in coverage_features(item))
    unmet = {
        f"{dimension}.{value}": floor - coverage_counts[(dimension, value)]
        for dimension, values in config.quality.coverage_floors.items()
        for value, floor in values.items()
        if coverage_counts[(dimension, value)] < floor
    }
    if unmet:
        raise GateError(f"coverage floors unmet after review: {unmet}")

    split_counts = Counter(item.split.value for item in approved)
    if config.release.corpus_class is CorpusClass.PRODUCTION:
        policy_failures = production_policy_failures(
            ProductionCorpusMetrics(
                train=split_counts[Split.TRAIN.value],
                validation=split_counts[Split.VALIDATION.value],
                test=split_counts[Split.TEST.value],
                categories=frozenset(item.dimensions.category for item in approved),
                difficulties=frozenset(item.dimensions.difficulty for item in approved),
                aiwg_behavior_domains=frozenset(
                    anchor_map[anchor_id].domain
                    for item in approved
                    for anchor_id in item.behavior_anchor_ids
                ),
            )
        )
        if policy_failures:
            raise GateError("fixed production corpus policy failed: " + "; ".join(policy_failures))

    releases_root = workspace.root / "releases"
    releases_root.mkdir(parents=True, exist_ok=True)
    release_dir = Path(
        tempfile.mkdtemp(prefix=f".{config.release.version}.building-", dir=releases_root)
    )
    created_at = utc_now()
    split_rows: dict[str, list[dict[str, Any]]] = {item.value: [] for item in Split}
    metadata_rows: dict[str, list[dict[str, Any]]] = {item.value: [] for item in Split}
    for item in sorted(approved, key=lambda row: row.record_id):
        split_rows[item.split.value].append(_training_row(item))
        metadata_rows[item.split.value].append(_metadata_row(item, anchor_map))
    for split_name, rows in split_rows.items():
        write_jsonl(release_dir / f"{split_name}.jsonl", rows)
        write_jsonl(release_dir / f"{split_name}.metadata.jsonl", metadata_rows[split_name])

    rejection_source = workspace.run_dir(run_id) / "rejection-ledger.jsonl"
    rejection_lines = (
        rejection_source.read_text(encoding="utf-8") if rejection_source.exists() else ""
    )
    review_rejections = [
        {
            "record_id": item.record_id,
            "seed_id": item.seed_id,
            "lineage_id": item.lineage_id,
            "reasons": [f"human_review:{item.review.rationale if item.review else 'rejected'}"],
        }
        for item in reviewed
        if item.review and item.review.decision is ReviewState.REJECTED
    ]
    write_text(
        release_dir / "rejection-ledger.jsonl",
        rejection_lines + "".join(canonical_json(item) + "\n" for item in review_rejections),
    )

    counts = Counter({name: len(rows) for name, rows in split_rows.items()})
    data_files = [release_dir / f"{item.value}.jsonl" for item in Split]
    metadata_files = [release_dir / f"{item.value}.metadata.jsonl" for item in Split]
    distribution_files = data_files + metadata_files
    file_hashes = {path.name: sha256_file(path) for path in distribution_files}
    run_manifest_path = workspace.run_dir(run_id) / "run-manifest.json"
    run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    write_json(release_dir / "generation-run-manifest.json", run_manifest)
    manifest = {
        "schema_version": "1.1",
        "dataset_id": config.release.dataset_id,
        "version": config.release.version,
        "created_at": created_at,
        "generation_run_id": run_id,
        "language_bcp47": config.language_bcp47,
        "corpus_class": config.release.corpus_class.value,
        "production_policy_id": (
            PRODUCTION_POLICY_ID if config.release.corpus_class is CorpusClass.PRODUCTION else None
        ),
        "trainer_row_schema": "conversational-messages-v1",
        "assistant_format_id": ASSISTANT_FORMAT_ID,
        "required_evaluation": {
            "policy_id": EVALUATION_POLICY_ID,
            "training_seeds": list(REQUIRED_TRAINING_SEEDS),
            "compare_unchanged_base": True,
            "test_is_held_out": True,
        },
        "license": config.release.license,
        "counts": dict(counts),
        "total": len(approved),
        "human_fraction": 0.0,
        "synthetic_fraction": 1.0,
        "generation_depth_max": max(item.generation_depth for item in approved),
        "coverage_counts": {
            dimension: {
                value: count
                for (item_dimension, value), count in sorted(coverage_counts.items())
                if item_dimension == dimension
            }
            for dimension in sorted({dimension for dimension, _value in coverage_counts})
        },
        "teacher_ids": sorted({item.teacher_id for item in approved}),
        "source_ids": sorted(
            {
                source_id
                for item in approved
                for source_id in (
                    item.source_ids
                    + [
                        source_id
                        for anchor_id in item.behavior_anchor_ids
                        for source_id in anchor_map[anchor_id].source_ids
                    ]
                )
            }
        ),
        "behavior_anchor_ids": sorted(
            {anchor_id for item in approved for anchor_id in item.behavior_anchor_ids}
        ),
        "split_policy": config.split.model_dump(mode="json"),
        "quality_policy": config.quality.model_dump(mode="json"),
        "files": file_hashes,
        "input_sha256": run_manifest["input_sha256"],
        "run_artifact_sha256": run_manifest["artifact_sha256"],
        "run_manifest_sha256": sha256_file(run_manifest_path),
    }
    write_json(release_dir / "manifest.json", manifest)
    write_text(release_dir / "DATASHEET.md", _datasheet(workspace, counts, created_at))
    write_text(release_dir / "EVALUATION-PROTOCOL.md", _evaluation_protocol())
    write_json(
        release_dir / "croissant.json",
        {
            "@context": "https://mlcommons.org/croissant/1.1",
            "@type": "sc:Dataset",
            "name": config.release.dataset_id,
            "version": config.release.version,
            "license": config.release.license,
            "datePublished": created_at,
            "distribution": [
                {
                    "@type": "cr:FileObject",
                    "name": path.name,
                    "contentUrl": path.name,
                    "sha256": file_hashes[path.name],
                    "encodingFormat": "application/x-ndjson",
                }
                for path in distribution_files
            ],
        },
    )
    write_json(
        release_dir / "provenance.jsonld",
        {
            "@context": {"prov": "http://www.w3.org/ns/prov#"},
            "@id": f"urn:qaforge:{config.release.dataset_id}:{config.release.version}",
            "@type": "prov:Entity",
            "prov:wasGeneratedBy": {
                "@type": "prov:Activity",
                "@id": f"urn:qaforge:run:{run_id}",
                "prov:endedAtTime": created_at,
                "prov:used": sorted({item.seed_id for item in approved}),
                "prov:wasAssociatedWith": sorted({item.teacher_id for item in approved}),
            },
            "records": [
                {
                    "record_id": item.record_id,
                    "prov:wasDerivedFrom": item.parent_record_ids,
                    "prov:wasAttributedTo": item.review.reviewer if item.review else None,
                    "content_sha256": item.content_sha256,
                }
                for item in approved
            ],
        },
    )
    evidence_files = sorted(path for path in release_dir.iterdir() if path.name != "SHA256SUMS")
    write_text(
        release_dir / "SHA256SUMS",
        "".join(f"{sha256_file(path)}  {path.name}\n" for path in evidence_files),
    )
    os.replace(release_dir, final_release_dir)
    _write_state(
        workspace,
        state.model_copy(
            update={
                "stage": RunStage.RELEASED,
                "updated_at": utc_now(),
                "release_version": config.release.version,
            }
        ),
    )
    return final_release_dir


def release_anchor(release_dir: Path) -> str:
    return sha256_file(release_dir / "SHA256SUMS")


def verify_release(
    workspace: Workspace,
    version: str,
    expected_sha256: str | None = None,
    allow_unanchored: bool = False,
) -> dict[str, Any]:
    release_dir = workspace.release_dir(version)
    sums_path = release_dir / "SHA256SUMS"
    failures: list[str] = []
    checked = 0
    anchor_sha256 = sha256_file(sums_path)
    if expected_sha256:
        if anchor_sha256 != expected_sha256:
            failures.append("external-anchor")
    elif not allow_unanchored:
        failures.append("missing-external-anchor")
    seen_files: set[str] = set()
    for line_number, line in enumerate(sums_path.read_text(encoding="utf-8").splitlines(), 1):
        parts = line.split("  ", 1)
        if len(parts) != 2:
            failures.append(f"invalid-checksum-line:{line_number}")
            continue
        expected, filename = parts
        if (
            Path(filename).name != filename
            or filename in seen_files
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", filename)
        ):
            failures.append(f"invalid-checksum-name:{line_number}")
            continue
        seen_files.add(filename)
        path = release_dir / filename
        checked += 1
        if path.is_symlink() or not path.is_file() or sha256_file(path) != expected:
            failures.append(filename)

    actual_files = {
        path.name
        for path in release_dir.iterdir()
        if path.name != "SHA256SUMS" and path.is_file() and not path.is_symlink()
    }
    if seen_files != actual_files:
        failures.append("checksum-file-set")

    manifest = json.loads((release_dir / "manifest.json").read_text(encoding="utf-8"))
    run_manifest_path = release_dir / "generation-run-manifest.json"
    if sha256_file(run_manifest_path) != manifest.get("run_manifest_sha256"):
        failures.append("run-manifest-hash")
    for filename, expected in manifest.get("files", {}).items():
        if (
            not isinstance(filename, str)
            or Path(filename).name != filename
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", filename)
        ):
            failures.append("invalid-manifest-filename")
            continue
        data_path = release_dir / filename
        if data_path.is_symlink() or not data_path.is_file() or sha256_file(data_path) != expected:
            failures.append(f"manifest-file-hash:{filename}")
    if manifest.get("schema_version", "1.0") == "1.0":
        result = _verify_legacy_release(release_dir, manifest, failures)
        return {
            "passed": not result["failures"],
            "checked_files": checked,
            "records": result["records"],
            "failures": result["failures"],
            "anchor_sha256": anchor_sha256,
            "legacy_schema": True,
            "production_standard": False,
        }
    if manifest.get("schema_version") != "1.1":
        failures.append("unsupported-schema-version")

    canonical_anchors = aiwg_behavior_anchors()
    canonical_anchor_json = canonical_json(
        [item.model_dump(mode="json") for item in canonical_anchors]
    )
    source_ids = {
        source_id for source_id in manifest.get("source_ids", []) if isinstance(source_id, str)
    }
    try:
        workspace_anchors = workspace.behavior_anchors()
        workspace_anchor_json = canonical_json(
            [item.model_dump(mode="json") for item in workspace_anchors]
        )
    except (ConfigurationError, OSError, ValueError):
        workspace_anchors = []
        workspace_anchor_json = ""
        failures.append("workspace-anchor-registry")
    if workspace_anchor_json != canonical_anchor_json:
        failures.append("behavior-anchor-registry")
    anchor_map = {item.anchor_id: item for item in canonical_anchors}
    private_identifiers = {
        *source_ids,
        *behavior_anchor_private_identifiers(canonical_anchors),
    }

    record_ids: set[str] = set()
    content_hashes: set[str] = set()
    lineage_splits: dict[str, set[str]] = defaultdict(set)
    observed_counts: Counter[str] = Counter()
    observed_categories: set[str] = set()
    observed_difficulties: set[str] = set()
    observed_anchor_domains: set[str] = set()
    observed_anchor_ids: set[str] = set()
    observed_coverage: Counter[tuple[str, str]] = Counter()
    for split in Split:
        path = release_dir / f"{split.value}.jsonl"
        metadata_path = release_dir / f"{split.value}.metadata.jsonl"
        try:
            data_lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
        except OSError:
            failures.append(f"missing-data:{split.value}")
            continue
        try:
            metadata_lines = [
                line for line in metadata_path.read_text(encoding="utf-8").splitlines() if line
            ]
        except OSError:
            failures.append(f"missing-sidecar:{split.value}")
            continue
        if len(data_lines) != len(metadata_lines):
            failures.append(f"sidecar-count:{split.value}")
        for line_number, (line, metadata_line) in enumerate(
            zip(data_lines, metadata_lines, strict=False), 1
        ):
            try:
                row = json.loads(line)
                metadata = json.loads(metadata_line)
                messages = row["messages"]
                record_id = metadata["record_id"]
                lineage_id = metadata["lineage_id"]
                recorded_content_hash = metadata["content_sha256"]
                seed_question = metadata["seed_question"]
                transform_id = metadata["question_transform_id"]
                review = metadata["review"]
                question = messages[0]["content"]
                category = metadata["category"]
                domain = metadata["domain"]
                task = metadata["task"]
                reasoning = metadata["reasoning"]
                answer_form = metadata["answer_form"]
                difficulty = metadata["difficulty"]
                evidence_mode = metadata["evidence_mode"]
                risk = metadata["risk"]
                behavior_anchors = metadata["behavior_anchors"]
            except (json.JSONDecodeError, KeyError, TypeError):
                failures.append(f"invalid-row:{split.value}:{line_number}")
                continue
            if not is_standard_training_row(row):
                failures.append(f"trainer-schema:{split.value}:{line_number}")
            if exposed_private_identifiers(canonical_json(row), private_identifiers):
                failures.append(f"latent-anchor-opacity:{record_id}")
            if record_id in record_ids:
                failures.append(f"duplicate-record-id:{record_id}")
            record_ids.add(record_id)
            lineage_splits[lineage_id].add(split.value)
            observed_counts[split.value] += 1
            observed_categories.add(category)
            observed_difficulties.add(difficulty)
            observed_coverage.update(
                {
                    ("category", category): 1,
                    ("domain", domain): 1,
                    ("task", task): 1,
                    ("reasoning", reasoning): 1,
                    ("answer_form", answer_form): 1,
                    ("difficulty", difficulty): 1,
                    ("evidence_mode", evidence_mode): 1,
                    ("risk", risk): 1,
                }
            )
            if not isinstance(behavior_anchors, list) or not behavior_anchors:
                failures.append(f"behavior-anchor:{record_id}")
            else:
                for anchor in behavior_anchors:
                    try:
                        anchor_id = anchor["anchor_id"]
                        declared_domain = anchor["domain"]
                        canonical_anchor = anchor_map[anchor_id]
                    except (KeyError, TypeError):
                        failures.append(f"behavior-anchor:{record_id}")
                        continue
                    if declared_domain != canonical_anchor.domain:
                        failures.append(f"behavior-anchor-domain:{record_id}")
                    observed_anchor_ids.add(anchor_id)
                    observed_anchor_domains.add(canonical_anchor.domain)
            content_hash = sha256_text(canonical_json(row))
            if content_hash != recorded_content_hash:
                failures.append(f"content-hash:{record_id}")
            if content_hash in content_hashes:
                failures.append(f"duplicate-content:{record_id}")
            content_hashes.add(content_hash)
            try:
                if question != transform_question(seed_question, transform_id):
                    failures.append(f"semantic-binding:{record_id}")
            except ConfigurationError:
                failures.append(f"semantic-binding:{record_id}")
            if (
                not isinstance(review, dict)
                or review.get("candidate_sha256") != content_hash
                or review.get("derivation_verified") is not True
                or review.get("behavior_alignment_verified") is not True
            ):
                failures.append(f"review-binding:{record_id}")
    for lineage, splits in lineage_splits.items():
        if len(splits) > 1:
            failures.append(f"lineage-split:{lineage}")
    if dict(observed_counts) != {key: value for key, value in manifest["counts"].items() if value}:
        zero_filled = {item.value: observed_counts[item.value] for item in Split}
        if zero_filled != manifest["counts"]:
            failures.append("manifest-counts")
    if len(record_ids) != manifest["total"]:
        failures.append("manifest-total")
    if observed_anchor_ids != set(manifest.get("behavior_anchor_ids", [])):
        failures.append("manifest-behavior-anchors")
    observed_coverage_json = {
        dimension: {
            value: count
            for (item_dimension, value), count in sorted(observed_coverage.items())
            if item_dimension == dimension
        }
        for dimension in sorted({dimension for dimension, _value in observed_coverage})
    }
    if observed_coverage_json != manifest.get("coverage_counts"):
        failures.append("manifest-coverage-counts")
    if manifest.get("corpus_class") == CorpusClass.PRODUCTION.value:
        if manifest.get("production_policy_id") != PRODUCTION_POLICY_ID:
            failures.append("production-policy-id")
        failures.extend(
            f"production-policy:{detail}"
            for detail in production_policy_failures(
                ProductionCorpusMetrics(
                    train=observed_counts[Split.TRAIN.value],
                    validation=observed_counts[Split.VALIDATION.value],
                    test=observed_counts[Split.TEST.value],
                    categories=frozenset(observed_categories),
                    difficulties=frozenset(observed_difficulties),
                    aiwg_behavior_domains=frozenset(observed_anchor_domains),
                )
            )
        )
        if manifest.get("required_evaluation") != {
            "policy_id": EVALUATION_POLICY_ID,
            "training_seeds": list(REQUIRED_TRAINING_SEEDS),
            "compare_unchanged_base": True,
            "test_is_held_out": True,
        }:
            failures.append("required-evaluation-policy")
    elif manifest.get("corpus_class") != CorpusClass.TEST_FIXTURE.value:
        failures.append("non-releasable-corpus-class")
    return {
        "passed": not failures,
        "checked_files": checked,
        "records": len(record_ids),
        "failures": failures,
        "anchor_sha256": anchor_sha256,
        "legacy_schema": False,
        "production_standard": manifest.get("corpus_class") == CorpusClass.PRODUCTION.value,
    }


def _verify_legacy_release(
    release_dir: Path, manifest: dict[str, Any], failures: list[str]
) -> dict[str, Any]:
    """Verify historical schema-1.0 inline-metadata releases without promoting them."""
    record_ids: set[str] = set()
    content_hashes: set[str] = set()
    lineage_splits: dict[str, set[str]] = defaultdict(set)
    observed_counts: Counter[str] = Counter()
    for split in Split:
        path = release_dir / f"{split.value}.jsonl"
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            failures.append(f"missing-data:{split.value}")
            continue
        for line_number, line in enumerate(lines, 1):
            if not line:
                continue
            try:
                row = json.loads(line)
                metadata = row["metadata"]
                messages = row["messages"]
                if (
                    not isinstance(messages, list)
                    or len(messages) != 2
                    or not all(isinstance(message, dict) for message in messages)
                ):
                    raise TypeError
                record_id = metadata["record_id"]
                lineage_id = metadata["lineage_id"]
                recorded_content_hash = metadata["content_sha256"]
                seed_question = metadata["seed_question"]
                transform_id = metadata["question_transform_id"]
                review = metadata["review"]
                question = messages[0]["content"]
                answer = messages[1]["content"]
            except (json.JSONDecodeError, KeyError, TypeError):
                failures.append(f"invalid-row:{split.value}:{line_number}")
                continue
            if record_id in record_ids:
                failures.append(f"duplicate-record-id:{record_id}")
            record_ids.add(record_id)
            lineage_splits[lineage_id].add(split.value)
            observed_counts[split.value] += 1
            content_hash = legacy_content_sha256(question, answer)
            if content_hash != recorded_content_hash:
                failures.append(f"content-hash:{record_id}")
            if content_hash in content_hashes:
                failures.append(f"duplicate-content:{record_id}")
            content_hashes.add(content_hash)
            try:
                if question != transform_question(seed_question, transform_id):
                    failures.append(f"semantic-binding:{record_id}")
            except ConfigurationError:
                failures.append(f"semantic-binding:{record_id}")
            if not isinstance(review, dict) or review.get("candidate_sha256") != content_hash:
                failures.append(f"review-binding:{record_id}")
    if any(len(splits) > 1 for splits in lineage_splits.values()):
        failures.append("lineage-split")
    zero_filled = {item.value: observed_counts[item.value] for item in Split}
    if zero_filled != manifest.get("counts"):
        failures.append("manifest-counts")
    if len(record_ids) != manifest.get("total"):
        failures.append("manifest-total")
    return {"records": len(record_ids), "failures": failures}
