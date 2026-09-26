import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from qaforge.cli import app
from qaforge.errors import ConfigurationError, GateError, ImmutableArtifactError
from qaforge.formatting import training_content_sha256
from qaforge.io import read_jsonl, write_jsonl
from qaforge.models import CandidateRecord, CorpusClass, ReviewState, RunStage
from qaforge.pipeline import approve_all, export_review, generate_run
from qaforge.release import build_release, release_anchor, verify_release
from qaforge.workspace import Workspace


def test_fr004_to_fr012_end_to_end_release(demo_workspace: Workspace) -> None:
    state = generate_run(demo_workspace, "release-run")
    assert state.stage is RunStage.AWAITING_REVIEW
    raw = read_jsonl(demo_workspace.run_dir("release-run") / "raw.jsonl", CandidateRecord)
    selected = read_jsonl(demo_workspace.run_dir("release-run") / "selected.jsonl", CandidateRecord)
    assert len(raw) == 24
    assert len(selected) == 8
    assert all(item.split.value for item in raw)
    assert len({item.split for item in raw if item.lineage_id == raw[0].lineage_id}) == 1

    review_path = export_review(demo_workspace, "release-run", demo_workspace.root / "review.jsonl")
    assert review_path.exists()
    approved = approve_all(
        demo_workspace,
        "release-run",
        reviewer="demo-fixture",
        rationale="end-to-end fixture review",
        acknowledged_manual_review=False,
    )
    assert approved.stage is RunStage.APPROVED
    release_dir = build_release(demo_workspace, "release-run", allow_test_fixture=True)
    assert (release_dir / "manifest.json").exists()
    assert (release_dir / "croissant.json").exists()
    assert (release_dir / "provenance.jsonld").exists()
    assert verify_release(demo_workspace, "0.1.0", release_anchor(release_dir))["passed"]


def test_runs_and_releases_are_immutable(demo_workspace: Workspace) -> None:
    generate_run(demo_workspace, "immutable-run")
    with pytest.raises(ImmutableArtifactError):
        generate_run(demo_workspace, "immutable-run")
    approve_all(
        demo_workspace,
        "immutable-run",
        reviewer="demo-fixture",
        rationale="fixture",
        acknowledged_manual_review=False,
    )
    build_release(demo_workspace, "immutable-run", allow_test_fixture=True)
    with pytest.raises(ImmutableArtifactError):
        build_release(demo_workspace, "immutable-run", allow_test_fixture=True)


def test_release_fixity_detects_tampering(demo_workspace: Workspace) -> None:
    generate_run(demo_workspace, "tamper-run")
    approve_all(
        demo_workspace,
        "tamper-run",
        reviewer="demo-fixture",
        rationale="fixture",
        acknowledged_manual_review=False,
    )
    release_dir = build_release(demo_workspace, "tamper-run", allow_test_fixture=True)
    with (release_dir / "train.jsonl").open("a", encoding="utf-8") as handle:
        handle.write("{}\n")
    result = verify_release(demo_workspace, "0.1.0", release_anchor(release_dir))
    assert not result["passed"]
    assert "train.jsonl" in result["failures"]


def test_release_verification_requires_external_anchor(demo_workspace: Workspace) -> None:
    generate_run(demo_workspace, "anchor-run")
    approve_all(
        demo_workspace,
        "anchor-run",
        reviewer="demo-fixture",
        rationale="fixture",
        acknowledged_manual_review=False,
    )
    release_dir = build_release(demo_workspace, "anchor-run", allow_test_fixture=True)
    unanchored = verify_release(demo_workspace, "0.1.0")
    assert not unanchored["passed"]
    assert "missing-external-anchor" in unanchored["failures"]
    trusted_anchor = release_anchor(release_dir)
    with (release_dir / "SHA256SUMS").open("a", encoding="utf-8") as handle:
        handle.write("0" * 64 + "  ../outside\n")
    tampered = verify_release(demo_workspace, "0.1.0", trusted_anchor)
    assert not tampered["passed"]
    assert "external-anchor" in tampered["failures"]
    assert any(item.startswith("invalid-checksum-name") for item in tampered["failures"])


def test_production_bulk_review_requires_acknowledgements(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from qaforge.fixtures import scaffold_workspace

    workspace = Workspace(scaffold_workspace(tmp_path / "production", demo=True))
    generate_run(workspace, "review-run")
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
    with pytest.raises(GateError, match="manual-review"):
        approve_all(workspace, "review-run", "reviewer", "rationale", False)
    with pytest.raises(GateError, match="derivation-verification"):
        approve_all(workspace, "review-run", "reviewer", "rationale", True)
    with pytest.raises(GateError, match="behavior-alignment"):
        approve_all(workspace, "review-run", "reviewer", "rationale", True, True)


def test_fr014_cli_demo_and_verify(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = tmp_path / "cli-demo"
    demo_result = runner.invoke(app, ["demo", str(workspace)])
    assert demo_result.exit_code == 0, demo_result.output
    verify_result = runner.invoke(
        app, ["verify-release", str(workspace), "0.1.0", "--allow-unanchored"]
    )
    assert verify_result.exit_code == 0, verify_result.output
    assert '"passed": true' in verify_result.output


def test_fr014_cli_accepts_documented_positional_workspace(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = tmp_path / "cli-positional"
    demo_result = runner.invoke(app, ["demo", str(workspace)])
    assert demo_result.exit_code == 0, demo_result.output
    assert runner.invoke(app, ["doctor", str(workspace)]).exit_code == 0
    assert runner.invoke(app, ["status", str(workspace)]).exit_code == 0
    generation = runner.invoke(app, ["generate", str(workspace), "--run-id", "positional-run"])
    assert generation.exit_code == 0, generation.output


def test_nfr006_review_export_cannot_escape_workspace(
    demo_workspace: Workspace, tmp_path: Path
) -> None:
    generate_run(demo_workspace, "bounded-export")
    with pytest.raises(ConfigurationError, match="escapes workspace"):
        export_review(demo_workspace, "bounded-export", tmp_path / "outside.jsonl")


def test_fr008_release_rejects_reviewed_content_tampering(
    demo_workspace: Workspace,
) -> None:
    generate_run(demo_workspace, "tampered-review")
    approve_all(
        demo_workspace,
        "tampered-review",
        reviewer="demo-fixture",
        rationale="fixture",
        acknowledged_manual_review=False,
    )
    path = demo_workspace.run_dir("tampered-review") / "reviewed.jsonl"
    reviewed = read_jsonl(path, CandidateRecord)
    first = reviewed[0]
    question = "A protected benchmark question that must never enter training."
    reviewed[0] = first.model_copy(
        update={
            "question": question,
            "content_sha256": training_content_sha256(question, first.derivation, first.answer),
        }
    )
    write_jsonl(path, reviewed)
    with pytest.raises(GateError, match="sealed selection"):
        build_release(demo_workspace, "tampered-review", allow_test_fixture=True)


def test_fr011_release_requires_full_target_after_review(demo_workspace: Workspace) -> None:
    generate_run(demo_workspace, "short-review")
    review_path = demo_workspace.root / "short-review-decisions.jsonl"
    export_review(demo_workspace, "short-review", review_path)
    decisions = [json.loads(line) for line in review_path.read_text().splitlines()]
    for index, decision in enumerate(decisions):
        decision.update(
            {
                "decision": (
                    ReviewState.REJECTED.value if index == 0 else ReviewState.APPROVED.value
                ),
                "reviewer": "demo-fixture",
                "rationale": "fixture decision",
                "reviewed_at": "2026-09-25T00:00:00Z",
            }
        )
    write_jsonl(review_path, decisions)
    from qaforge.pipeline import import_reviews

    import_reviews(demo_workspace, "short-review", review_path)
    with pytest.raises(GateError, match="below target_size"):
        build_release(demo_workspace, "short-review", allow_test_fixture=True)
