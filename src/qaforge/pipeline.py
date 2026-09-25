from __future__ import annotations

import json
from pathlib import Path

import httpx

from qaforge.dedup import decontaminate
from qaforge.errors import ConfigurationError, GateError, ImmutableArtifactError
from qaforge.io import (
    canonical_json,
    ensure_within,
    read_jsonl,
    sha256_file,
    sha256_text,
    utc_now,
    write_json,
    write_jsonl,
)
from qaforge.models import (
    CandidateRecord,
    GateStatus,
    ReviewDecision,
    ReviewState,
    RunStage,
    RunState,
)
from qaforge.providers import Provider, provider_for
from qaforge.selection import select_candidates
from qaforge.splitter import assign_split
from qaforge.transforms import transform_ids, transform_question
from qaforge.validation import mandatory_gates_pass, validate_candidate, verify_answer
from qaforge.workspace import Workspace


def _state_path(workspace: Workspace, run_id: str) -> Path:
    return workspace.run_dir(run_id) / "state.json"


def load_state(workspace: Workspace, run_id: str) -> RunState:
    try:
        return RunState.model_validate_json(_state_path(workspace, run_id).read_text())
    except (OSError, ValueError) as exc:
        raise ConfigurationError(f"cannot load run state for {run_id}: {exc}") from exc


def _write_state(workspace: Workspace, state: RunState) -> None:
    write_json(_state_path(workspace, state.run_id), state)


def _input_paths(workspace: Workspace) -> dict[str, Path]:
    paths = {
        "config": workspace.config_path,
        "sources": workspace.registry_dir / "sources.yaml",
        "teachers": workspace.registry_dir / "teachers.yaml",
        "reviewers": workspace.registry_dir / "reviewers.yaml",
        "taxonomy": workspace.registry_dir / "taxonomy.yaml",
        "seeds": workspace.seeds_path,
    }
    if workspace.benchmarks_path.exists():
        paths["protected_benchmarks"] = workspace.benchmarks_path
    return paths


def assert_run_artifacts(workspace: Workspace, run_id: str) -> None:
    """Refuse mutable run inputs after the generation manifest is sealed."""
    manifest_path = workspace.run_dir(run_id) / "run-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = manifest["artifact_sha256"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise GateError(f"invalid run manifest for {run_id}: {exc}") from exc
    if manifest.get("run_id") != run_id or not isinstance(expected, dict):
        raise GateError(f"run manifest identity mismatch: {run_id}")
    for filename, digest in expected.items():
        path = ensure_within(workspace.root, workspace.run_dir(run_id) / filename)
        if not path.is_file() or sha256_file(path) != digest:
            raise GateError(f"run artifact integrity failed: {filename}")
    current_inputs = {key: sha256_file(path) for key, path in _input_paths(workspace).items()}
    if manifest.get("input_sha256") != current_inputs:
        raise GateError("workspace inputs differ from the sealed generation run")


def generate_run(
    workspace: Workspace,
    run_id: str,
    provider_id: str | None = None,
    client: httpx.Client | None = None,
    provider_instance: Provider | None = None,
) -> RunState:
    report = workspace.doctor(provider_id)
    if not report.passed:
        failed = [item for item in report.checks if item.status is GateStatus.FAIL]
        raise GateError("doctor failed: " + "; ".join(f"{x.gate}: {x.detail}" for x in failed))

    run_dir = workspace.run_dir(run_id)
    if run_dir.exists():
        raise ImmutableArtifactError(f"run already exists: {run_id}")
    run_dir.mkdir(parents=True)

    config = workspace.config()
    teacher = workspace.teacher(provider_id or config.generation.provider_id)
    if provider_instance is not None and provider_instance.teacher.teacher_id != teacher.teacher_id:
        raise ConfigurationError("injected provider teacher does not match the selected teacher")
    provider = provider_instance or provider_for(teacher, client=client)
    seeds = workspace.seeds()
    created_at = utc_now()
    raw: list[CandidateRecord] = []

    for seed in sorted(seeds, key=lambda item: item.seed_id):
        split = assign_split(seed.lineage_id, config.split)
        outputs, template_id, template_hash = provider.generate(
            seed, config.generation.candidates_per_seed, config
        )
        transformations = transform_ids(len(outputs))
        for index, output in enumerate(outputs):
            transform_id = transformations[index]
            question = transform_question(seed.question, transform_id)
            content_hash = sha256_text(
                canonical_json({"question": question, "answer": output.answer})
            )
            record_id = (
                "qa_"
                + sha256_text(
                    canonical_json(
                        {
                            "run": run_id,
                            "seed": seed.seed_id,
                            "index": index,
                            "content": content_hash,
                        }
                    )
                )[:24]
            )
            raw.append(
                CandidateRecord(
                    record_id=record_id,
                    seed_id=seed.seed_id,
                    lineage_id=seed.lineage_id,
                    split=split,
                    question=question,
                    answer=output.answer,
                    seed_question=seed.question,
                    question_transform_id=transform_id,
                    dimensions=seed.dimensions,
                    verifier=seed.verifier,
                    citation_ids=output.citation_ids,
                    source_ids=seed.source_ids,
                    parent_record_ids=[seed.seed_id],
                    generation_depth=seed.generation_depth + 1,
                    generation_run_id=run_id,
                    generated_at=created_at,
                    teacher_id=teacher.teacher_id,
                    teacher_provider=teacher.provider,
                    teacher_model=teacher.model,
                    teacher_terms_snapshot_id=teacher.terms_snapshot_id,
                    prompt_template_id=template_id,
                    prompt_template_sha256=template_hash,
                    sampling={
                        "candidate_index": index,
                        "temperature": config.generation.temperature,
                        "max_tokens": config.generation.max_tokens,
                    },
                    content_sha256=content_hash,
                )
            )

    write_jsonl(run_dir / "raw.jsonl", raw)
    evaluated: list[CandidateRecord] = []
    for candidate in raw:
        validation = validate_candidate(candidate, config)
        verification = verify_answer(candidate)
        reasons = [item.gate for item in validation if item.status is GateStatus.FAIL]
        if not verification.passed:
            reasons.append(f"verification:{verification.kind.value}")
        evaluated.append(
            candidate.model_copy(
                update={
                    "validation": validation,
                    "verification": verification,
                    "rejection_reasons": reasons,
                }
            )
        )

    evaluated = decontaminate(evaluated, workspace.benchmarks(), config.quality)
    write_jsonl(run_dir / "evaluated.jsonl", evaluated)
    selected = select_candidates(evaluated, config.quality)
    write_jsonl(run_dir / "selected.jsonl", selected)

    selected_ids = {item.record_id for item in selected}
    rejection_ledger: list[dict[str, object]] = []
    for item in evaluated:
        if item.record_id not in selected_ids:
            reasons = list(item.rejection_reasons)
            if mandatory_gates_pass(item) and not reasons:
                reasons = ["not_selected:coverage_or_capacity"]
            rejection_ledger.append(
                {
                    "record_id": item.record_id,
                    "seed_id": item.seed_id,
                    "lineage_id": item.lineage_id,
                    "reasons": reasons,
                }
            )
    write_jsonl(run_dir / "rejection-ledger.jsonl", rejection_ledger)

    input_paths = _input_paths(workspace)
    artifact_paths = {
        "raw.jsonl": run_dir / "raw.jsonl",
        "evaluated.jsonl": run_dir / "evaluated.jsonl",
        "selected.jsonl": run_dir / "selected.jsonl",
        "rejection-ledger.jsonl": run_dir / "rejection-ledger.jsonl",
    }
    write_json(
        run_dir / "run-manifest.json",
        {
            "run_id": run_id,
            "created_at": created_at,
            "provider_id": teacher.teacher_id,
            "teacher_model": teacher.model,
            "input_sha256": {key: sha256_file(path) for key, path in input_paths.items()},
            "counts": {
                "seeds": len(seeds),
                "raw": len(raw),
                "mandatory_gates_passed": sum(mandatory_gates_pass(item) for item in evaluated),
                "selected": len(selected),
                "rejected": len(rejection_ledger),
            },
            "policy_snapshot": workspace.snapshot_inputs(),
            "artifact_sha256": {name: sha256_file(path) for name, path in artifact_paths.items()},
        },
    )
    now = utc_now()
    state = RunState(
        run_id=run_id,
        stage=RunStage.AWAITING_REVIEW if config.review.required else RunStage.APPROVED,
        created_at=created_at,
        updated_at=now,
        counts={
            "seeds": len(seeds),
            "raw": len(raw),
            "selected": len(selected),
            "approved": 0,
            "review_rejected": 0,
        },
    )
    _write_state(workspace, state)
    return state


def export_review(workspace: Workspace, run_id: str, destination: Path) -> Path:
    destination = ensure_within(workspace.root, destination)
    assert_run_artifacts(workspace, run_id)
    selected = read_jsonl(workspace.run_dir(run_id) / "selected.jsonl", CandidateRecord)
    packets = [
        {
            "record_id": item.record_id,
            "candidate_sha256": item.content_sha256,
            "question": item.question,
            "answer": item.answer,
            "category": item.dimensions.category,
            "decision": ReviewState.PENDING.value,
            "reviewer": "",
            "rationale": "",
            "reviewed_at": None,
        }
        for item in selected
    ]
    write_jsonl(destination, packets)
    return destination


def import_reviews(workspace: Workspace, run_id: str, review_path: Path) -> RunState:
    assert_run_artifacts(workspace, run_id)
    selected = read_jsonl(workspace.run_dir(run_id) / "selected.jsonl", CandidateRecord)
    selected_map = {item.record_id: item for item in selected}
    decisions: dict[str, ReviewDecision] = {}
    try:
        lines = review_path.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            decision = ReviewDecision.model_validate(json.loads(line))
            if decision.record_id in decisions:
                raise GateError(f"duplicate review decision: {decision.record_id}")
            if decision.record_id not in selected_map:
                raise GateError(f"review references unknown record: {decision.record_id}")
            candidate = selected_map[decision.record_id]
            if decision.candidate_sha256 != candidate.content_sha256:
                raise GateError(f"review digest mismatch: {decision.record_id}")
            if decision.decision is ReviewState.PENDING:
                raise GateError(f"pending review at line {line_number}: {decision.record_id}")
            if not decision.reviewer.strip() or not decision.rationale.strip():
                raise GateError(f"reviewer and rationale required: {decision.record_id}")
            workspace.reviewer(decision.reviewer, candidate.dimensions.category)
            decisions[decision.record_id] = decision.model_copy(
                update={"reviewed_at": decision.reviewed_at or utc_now()}
            )
    except (OSError, ValueError) as exc:
        raise ConfigurationError(f"cannot import reviews: {exc}") from exc

    if set(decisions) != set(selected_map):
        missing = sorted(set(selected_map) - set(decisions))
        raise GateError(f"review file must decide every selected record; missing={missing}")

    reviewed = [item.model_copy(update={"review": decisions[item.record_id]}) for item in selected]
    write_jsonl(workspace.run_dir(run_id) / "reviewed.jsonl", reviewed)
    approved = sum(
        item.review is not None and item.review.decision is ReviewState.APPROVED
        for item in reviewed
    )
    rejected = len(reviewed) - approved
    prior = load_state(workspace, run_id)
    state = prior.model_copy(
        update={
            "stage": RunStage.APPROVED,
            "updated_at": utc_now(),
            "counts": {**prior.counts, "approved": approved, "review_rejected": rejected},
        }
    )
    _write_state(workspace, state)
    return state


def approve_all(
    workspace: Workspace,
    run_id: str,
    reviewer: str,
    rationale: str,
    acknowledged_manual_review: bool,
) -> RunState:
    config = workspace.config()
    if not config.demo_mode and not acknowledged_manual_review:
        raise GateError("bulk approval requires --acknowledge-manual-review")
    selected = read_jsonl(workspace.run_dir(run_id) / "selected.jsonl", CandidateRecord)
    review_path = workspace.run_dir(run_id) / "review-decisions.jsonl"
    now = utc_now()
    write_jsonl(
        review_path,
        [
            ReviewDecision(
                record_id=item.record_id,
                candidate_sha256=item.content_sha256,
                decision=ReviewState.APPROVED,
                reviewer=reviewer,
                rationale=rationale,
                reviewed_at=now,
            )
            for item in selected
        ],
    )
    return import_reviews(workspace, run_id, review_path)
