from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from qaforge.errors import GateError
from qaforge.fixtures import scaffold_workspace
from qaforge.formatting import FINAL_ANSWER_HEADING, is_standard_training_row
from qaforge.io import read_jsonl, sha256_file, sha256_text, write_json, write_jsonl, write_text
from qaforge.models import CandidateRecord, CorpusClass, ForgeConfig
from qaforge.pilot import scaffold_calibration_workspace
from qaforge.pipeline import approve_all, export_review, generate_run, import_reviews
from qaforge.release import build_release, release_anchor, verify_release
from qaforge.standards import (
    AIWG_BEHAVIOR_DOMAINS,
    MIN_PRODUCTION_CATEGORIES,
    MIN_PRODUCTION_TEST,
    MIN_PRODUCTION_TRAIN,
    MIN_PRODUCTION_VALIDATION,
    REQUIRED_DIFFICULTIES,
    ProductionCorpusMetrics,
    production_policy_failures,
)
from qaforge.workspace import Workspace


def _minimum_metrics(**updates: object) -> ProductionCorpusMetrics:
    values: dict[str, object] = {
        "train": MIN_PRODUCTION_TRAIN,
        "validation": MIN_PRODUCTION_VALIDATION,
        "test": MIN_PRODUCTION_TEST,
        "categories": frozenset(f"category-{index}" for index in range(10)),
        "difficulties": REQUIRED_DIFFICULTIES,
        "aiwg_behavior_domains": AIWG_BEHAVIOR_DOMAINS,
    }
    values.update(updates)
    return ProductionCorpusMetrics(**values)  # type: ignore[arg-type]


def test_production_policy_accepts_only_the_exact_or_higher_split_floor() -> None:
    assert production_policy_failures(_minimum_metrics()) == []
    for split, floor in (
        ("train", MIN_PRODUCTION_TRAIN),
        ("validation", MIN_PRODUCTION_VALIDATION),
        ("test", MIN_PRODUCTION_TEST),
    ):
        failures = production_policy_failures(_minimum_metrics(**{split: floor - 1}))
        assert any(item.startswith(f"{split}=") for item in failures)


def test_production_policy_requires_categories_difficulties_and_aiwg_domains() -> None:
    nine_categories = frozenset(
        f"category-{index}" for index in range(MIN_PRODUCTION_CATEGORIES - 1)
    )
    assert any(
        item.startswith("categories=")
        for item in production_policy_failures(_minimum_metrics(categories=nine_categories))
    )
    assert any(
        "missing required difficulties" in item
        for item in production_policy_failures(
            _minimum_metrics(difficulties=frozenset({"introductory", "intermediate"}))
        )
    )
    assert any(
        "missing required AIWG behavior domains" in item
        for item in production_policy_failures(
            _minimum_metrics(
                aiwg_behavior_domains=frozenset(
                    set(AIWG_BEHAVIOR_DOMAINS) - {"independent-verification"}
                )
            )
        )
    )


def test_production_configuration_cannot_lower_the_total_floor(tmp_path: Path) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "config", demo=True))
    raw = workspace.config().model_dump(mode="json")
    raw["demo_mode"] = False
    raw["release"]["corpus_class"] = "production"
    raw["quality"]["target_size"] = 23_999
    from qaforge.models import ForgeConfig

    with pytest.raises(ValidationError, match="at least 24000"):
        ForgeConfig.model_validate(raw)


def test_demo_mode_and_corpus_class_cannot_be_combined_inconsistently(tmp_path: Path) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "config-mode", demo=True))
    raw = workspace.config().model_dump(mode="json")
    raw["release"]["corpus_class"] = "production"
    raw["quality"]["target_size"] = 24_000
    with pytest.raises(ValidationError, match="demo_mode"):
        ForgeConfig.model_validate(raw)


def test_calibration_is_permanently_non_releasable(tmp_path: Path) -> None:
    workspace = Workspace(scaffold_calibration_workspace(tmp_path / "calibration", size=10))
    with pytest.raises(GateError, match="permanently non-releasable"):
        build_release(workspace, "even-if-reviewed")


def test_test_fixture_requires_explicit_internal_release_flag(tmp_path: Path) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "fixture-denial", demo=True))
    generate_run(workspace, "fixture-denial-run")
    approve_all(
        workspace,
        "fixture-denial-run",
        reviewer="demo-fixture",
        rationale="fixture review",
        acknowledged_manual_review=False,
    )
    with pytest.raises(GateError, match="internal demo workflow"):
        build_release(workspace, "fixture-denial-run")


def test_release_emits_messages_only_and_bound_metadata_sidecars(tmp_path: Path) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "portable", demo=True))
    generate_run(workspace, "portable-run")
    review_path = export_review(workspace, "portable-run", workspace.root / "review-packets.jsonl")
    first_review = json.loads(review_path.read_text(encoding="utf-8").splitlines()[0])
    assert first_review["derivation"]
    assert first_review["final_answer"]
    assert first_review["derivation_verified"] is False
    assert first_review["behavior_alignment_verified"] is False
    assert first_review["behavior_anchors"][0]["principle"]
    approve_all(
        workspace,
        "portable-run",
        reviewer="demo-fixture",
        rationale="fixture review",
        acknowledged_manual_review=False,
    )
    release_dir = build_release(workspace, "portable-run", allow_test_fixture=True)
    protocol = (release_dir / "EVALUATION-PROTOCOL.md").read_text(encoding="utf-8")
    assert "unchanged base model" in protocol
    assert "seeds 17, 29, 47" in protocol

    total_rows = 0
    for split in ("train", "validation", "test"):
        rows = [
            json.loads(line)
            for line in (release_dir / f"{split}.jsonl").read_text(encoding="utf-8").splitlines()
            if line
        ]
        metadata = [
            json.loads(line)
            for line in (release_dir / f"{split}.metadata.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line
        ]
        assert len(rows) == len(metadata)
        total_rows += len(rows)
        for row, sidecar in zip(rows, metadata, strict=True):
            assert set(row) == {"messages"}
            assert FINAL_ANSWER_HEADING in row["messages"][1]["content"]
            assert "aiwg" not in json.dumps(row).casefold()
            assert "SRC-DEMO" not in json.dumps(row)
            assert sidecar["behavior_anchors"]
            assert sidecar["review"]["derivation_verified"] is True
            assert sidecar["review"]["behavior_alignment_verified"] is True
    assert total_rows == 8


def test_generated_candidate_digest_binds_derivation(demo_workspace: Workspace) -> None:
    generate_run(demo_workspace, "derivation-binding")
    path = demo_workspace.run_dir("derivation-binding") / "selected.jsonl"
    candidate = CandidateRecord.model_validate_json(path.read_text().splitlines()[0])
    changed = candidate.model_copy(
        update={"derivation": ["A different but plausible derivation step is substituted."]}
    )
    from qaforge.validation import validate_candidate

    gates = {
        gate.gate: gate.status.value
        for gate in validate_candidate(changed, demo_workspace.config())
    }
    assert gates["content_hash"] == "fail"


def test_review_packet_display_and_anchor_context_are_immutable(tmp_path: Path) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "review-binding", demo=True))
    generate_run(workspace, "review-binding-run")
    review_path = export_review(
        workspace, "review-binding-run", workspace.root / "review-binding.jsonl"
    )
    packets = [json.loads(line) for line in review_path.read_text().splitlines()]
    packets[0].update(
        {
            "question": "A substituted question that the reviewer actually saw.",
            "decision": "approved",
            "reviewer": "demo-fixture",
            "rationale": "tampered display",
        }
    )
    write_jsonl(review_path, packets)
    with pytest.raises(GateError, match="content mismatch"):
        import_reviews(workspace, "review-binding-run", review_path)

    export_review(workspace, "review-binding-run", review_path)
    packets = [json.loads(line) for line in review_path.read_text().splitlines()]
    packets[0]["behavior_anchors"][0]["principle"] += " Mutated."
    packets[0].update(
        {
            "decision": "approved",
            "reviewer": "demo-fixture",
            "rationale": "tampered anchor",
        }
    )
    write_jsonl(review_path, packets)
    with pytest.raises(GateError, match="content mismatch"):
        import_reviews(workspace, "review-binding-run", review_path)


def test_production_review_requires_derivation_and_behavior_attestations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "production-review", demo=True))
    generate_run(workspace, "production-review-run")
    fixture_config = workspace.config()
    production_config = fixture_config.model_copy(
        update={
            "demo_mode": False,
            "release": fixture_config.release.model_copy(
                update={"corpus_class": CorpusClass.PRODUCTION}
            ),
        }
    )
    monkeypatch.setattr(workspace, "config", lambda: production_config)
    review_path = export_review(
        workspace, "production-review-run", workspace.root / "production-review.jsonl"
    )
    packets = [json.loads(line) for line in review_path.read_text().splitlines()]
    for packet in packets:
        packet.update(
            {
                "decision": "approved",
                "reviewer": "demo-fixture",
                "rationale": "reviewed",
                "derivation_verified": True,
                "behavior_alignment_verified": True,
            }
        )
    packets[0]["behavior_alignment_verified"] = False
    write_jsonl(review_path, packets)
    with pytest.raises(GateError, match="derivation and behavior-alignment"):
        import_reviews(workspace, "production-review-run", review_path)


def test_malformed_standard_training_row_fails_closed() -> None:
    assert not is_standard_training_row({"messages": [1, 2]})


def _reseal_release(release_dir: Path) -> None:
    evidence = sorted(path for path in release_dir.iterdir() if path.name != "SHA256SUMS")
    write_text(
        release_dir / "SHA256SUMS",
        "".join(f"{sha256_file(path)}  {path.name}\n" for path in evidence),
    )


def test_production_policy_is_wired_into_build_and_verification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "policy-wiring", demo=True))
    generate_run(workspace, "policy-wiring-run")
    approve_all(
        workspace,
        "policy-wiring-run",
        reviewer="demo-fixture",
        rationale="fixture review",
        acknowledged_manual_review=False,
    )
    fixture_config = workspace.config()
    fixture_report = workspace.doctor()
    production_config = fixture_config.model_copy(
        update={
            "demo_mode": False,
            "quality": fixture_config.quality.model_copy(update={"target_size": 8}),
            "release": fixture_config.release.model_copy(
                update={"corpus_class": CorpusClass.PRODUCTION}
            ),
        }
    )
    reviewed_path = workspace.run_dir("policy-wiring-run") / "reviewed.jsonl"
    fixture_reviewed = read_jsonl(reviewed_path, CandidateRecord)
    production_reviewed = []
    for item in fixture_reviewed:
        assert item.review is not None
        production_reviewed.append(
            item.model_copy(
                update={"review": item.review.model_copy(update={"reviewer": "reviewer-main"})}
            )
        )
    write_jsonl(reviewed_path, production_reviewed)
    monkeypatch.setattr(workspace, "config", lambda: production_config)
    monkeypatch.setattr(workspace, "doctor", lambda *_args: fixture_report)
    monkeypatch.setattr(workspace, "reviewer", lambda *_args: None)
    with pytest.raises(GateError, match="fixed production corpus policy"):
        build_release(workspace, "policy-wiring-run")

    monkeypatch.undo()
    write_jsonl(reviewed_path, fixture_reviewed)
    release_dir = build_release(workspace, "policy-wiring-run", allow_test_fixture=True)
    manifest_path = release_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["corpus_class"] = "production"
    manifest["production_policy_id"] = "qaforge-reasoning-sft-minimum-v1"
    write_json(manifest_path, manifest)
    _reseal_release(release_dir)
    result = verify_release(workspace, "0.1.0", release_anchor(release_dir))
    assert not result["passed"]
    assert any(item.startswith("production-policy:") for item in result["failures"])


def test_verifier_rejects_fabricated_sidecar_anchor(tmp_path: Path) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "sidecar-anchor", demo=True))
    generate_run(workspace, "sidecar-anchor-run")
    approve_all(
        workspace,
        "sidecar-anchor-run",
        reviewer="demo-fixture",
        rationale="fixture review",
        acknowledged_manual_review=False,
    )
    release_dir = build_release(workspace, "sidecar-anchor-run", allow_test_fixture=True)
    metadata_path = next(
        path
        for path in release_dir.glob("*.metadata.jsonl")
        if path.read_text(encoding="utf-8").strip()
    )
    rows = [json.loads(line) for line in metadata_path.read_text().splitlines()]
    rows[0]["behavior_anchors"][0] = {
        "anchor_id": "aiwg.fabricated",
        "domain": "fabricated",
    }
    write_jsonl(metadata_path, rows)
    manifest_path = release_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files"][metadata_path.name] = sha256_file(metadata_path)
    write_json(manifest_path, manifest)
    _reseal_release(release_dir)
    result = verify_release(workspace, "0.1.0", release_anchor(release_dir))
    assert not result["passed"]
    assert any(item.startswith("behavior-anchor:") for item in result["failures"])


def test_legacy_candidate_and_release_remain_verifiable(tmp_path: Path) -> None:
    workspace = Workspace(scaffold_workspace(tmp_path / "legacy", demo=True))
    generate_run(workspace, "legacy-source")
    current = read_jsonl(workspace.run_dir("legacy-source") / "selected.jsonl", CandidateRecord)[
        0
    ].model_dump(mode="json")
    current["schema_version"] = "1.0"
    current.pop("derivation")
    current.pop("behavior_anchor_ids")
    current["content_sha256"] = sha256_text(
        json.dumps(
            {"answer": current["answer"], "question": current["question"]},
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    legacy_candidate = CandidateRecord.model_validate(current)
    assert legacy_candidate.schema_version == "1.0"

    release_dir = workspace.release_dir("0.0.1")
    release_dir.mkdir(parents=True)
    for split in ("train", "validation", "test"):
        write_jsonl(release_dir / f"{split}.jsonl", [])
    row = {
        "messages": [
            {"role": "user", "content": legacy_candidate.question},
            {"role": "assistant", "content": legacy_candidate.answer},
        ],
        "metadata": {
            "record_id": legacy_candidate.record_id,
            "lineage_id": legacy_candidate.lineage_id,
            "seed_question": legacy_candidate.seed_question,
            "question_transform_id": legacy_candidate.question_transform_id,
            "content_sha256": legacy_candidate.content_sha256,
            "review": {"candidate_sha256": legacy_candidate.content_sha256},
        },
    }
    write_jsonl(release_dir / "train.jsonl", [row])
    write_json(release_dir / "generation-run-manifest.json", {"run_id": "legacy"})
    manifest = {
        "schema_version": "1.0",
        "counts": {"train": 1, "validation": 0, "test": 0},
        "total": 1,
        "files": {
            f"{split}.jsonl": sha256_file(release_dir / f"{split}.jsonl")
            for split in ("train", "validation", "test")
        },
        "run_manifest_sha256": sha256_file(release_dir / "generation-run-manifest.json"),
    }
    write_json(release_dir / "manifest.json", manifest)
    _reseal_release(release_dir)
    result = verify_release(workspace, "0.0.1", release_anchor(release_dir))
    assert result["passed"]
    assert result["legacy_schema"] is True
    assert result["production_standard"] is False
