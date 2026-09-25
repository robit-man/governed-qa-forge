from __future__ import annotations

from qaforge.dedup import decontaminate
from qaforge.io import read_jsonl
from qaforge.models import BenchmarkRecord, CandidateRecord
from qaforge.pipeline import generate_run
from qaforge.selection import select_candidates
from qaforge.workspace import Workspace


def test_fr008_exact_and_cross_lineage_duplicates_are_rejected(
    demo_workspace: Workspace,
) -> None:
    generate_run(demo_workspace, "dedup-source")
    raw = read_jsonl(demo_workspace.run_dir("dedup-source") / "raw.jsonl", CandidateRecord)
    first = raw[0]
    duplicate = first.model_copy(
        update={"record_id": "qa_duplicate", "lineage_id": "different-family"}
    )
    checked = decontaminate([first, duplicate], [], demo_workspace.config().quality)
    assert checked[0].contamination.passed
    assert not checked[1].contamination.passed
    assert checked[1].contamination.match_type == "exact_record"


def test_fr008_protected_benchmark_overlap_is_rejected(demo_workspace: Workspace) -> None:
    generate_run(demo_workspace, "benchmark-source")
    raw = read_jsonl(demo_workspace.run_dir("benchmark-source") / "raw.jsonl", CandidateRecord)
    candidate = raw[0].model_copy(
        update={"question": "A protected benchmark question that must never enter training."}
    )
    checked = decontaminate(
        [candidate],
        [
            BenchmarkRecord(
                benchmark_id="protected-example-001",
                question="A protected benchmark question that must never enter training.",
            )
        ],
        demo_workspace.config().quality,
    )
    assert checked[0].contamination.match_type == "protected_benchmark"


def test_fr009_selection_enforces_one_record_per_lineage(demo_workspace: Workspace) -> None:
    generate_run(demo_workspace, "selection-source")
    evaluated = read_jsonl(
        demo_workspace.run_dir("selection-source") / "evaluated.jsonl", CandidateRecord
    )
    selected = select_candidates(evaluated, demo_workspace.config().quality)
    assert len(selected) == 8
    assert len({item.lineage_id for item in selected}) == 8
