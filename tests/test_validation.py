from __future__ import annotations

import pytest

from qaforge.formatting import training_content_sha256
from qaforge.io import utc_now
from qaforge.models import (
    CandidateRecord,
    Dimensions,
    ForgeConfig,
    GeneratedOutput,
    Split,
    VerifierKind,
    VerifierSpec,
)
from qaforge.validation import validate_candidate, verify_answer
from qaforge.workspace import Workspace


def _candidate(
    config: ForgeConfig,
    output: GeneratedOutput,
    verifier: VerifierSpec,
    question: str = "A sufficiently long verification question?",
) -> CandidateRecord:
    content_hash = training_content_sha256(question, output.derivation, output.answer)
    return CandidateRecord(
        record_id="qa_test",
        seed_id="seed-test",
        lineage_id="family-test",
        split=Split.TRAIN,
        question=question,
        derivation=output.derivation,
        answer=output.answer,
        seed_question=question,
        question_transform_id="identity-v1",
        dimensions=Dimensions(
            category="logic",
            domain="mathematics",
            task="derive",
            reasoning="deductive",
            answer_form="concise",
            difficulty="intermediate",
            evidence_mode="deterministic",
        ),
        verifier=verifier,
        citation_ids=output.citation_ids,
        source_ids=["SRC-DEMO"],
        behavior_anchor_ids=["aiwg.independent-verification"],
        parent_record_ids=["seed-test"],
        generation_depth=1,
        generation_run_id="test-run",
        generated_at=utc_now(),
        teacher_id="teacher-fixture",
        teacher_provider="deterministic",
        teacher_model="fixture",
        teacher_terms_snapshot_id="terms-v1",
        prompt_template_id="template-v1",
        prompt_template_sha256="a" * 64,
        sampling={"temperature": 0},
        content_sha256=content_hash,
    )


@pytest.mark.parametrize(
    ("answer", "verifier", "citation_ids"),
    [
        ("YES", VerifierSpec(kind=VerifierKind.EXACT, expected="yes"), []),
        ("Result: 4.001", VerifierSpec(kind=VerifierKind.NUMERIC, expected=4, tolerance=0.01), []),
        ("ABC-42", VerifierSpec(kind=VerifierKind.REGEX, pattern=r"ABC-\d{2}"), []),
        ('{"ok":true}', VerifierSpec(kind=VerifierKind.JSON, expected={"ok": True}), []),
        (
            "Supported [1].",
            VerifierSpec(kind=VerifierKind.CITATION, required_citation_ids=["SRC-DEMO"]),
            ["SRC-DEMO"],
        ),
    ],
)
def test_fr007_independent_verifiers(
    demo_workspace: Workspace,
    answer: str,
    verifier: VerifierSpec,
    citation_ids: list[str],
) -> None:
    config = demo_workspace.config()
    candidate = _candidate(
        config,
        GeneratedOutput(
            derivation=["Apply the task constraints and independently check the result."],
            answer=answer,
            citation_ids=citation_ids,
        ),
        verifier,
    )
    assert verify_answer(candidate).passed


def test_fr006_secret_and_pii_scans_fail(demo_workspace: Workspace) -> None:
    config = demo_workspace.config()
    candidate = _candidate(
        config,
        GeneratedOutput(
            derivation=["Inspect the supplied values and check them for sensitive material."],
            answer="AKIA" + "ABCDEFGHIJKLMNOP",
        ),
        VerifierSpec(kind=VerifierKind.EXACT, expected="unused"),
        question="Contact person@example.com for this sufficiently long task.",
    )
    gates = {gate.gate: gate.status.value for gate in validate_candidate(candidate, config)}
    assert gates["secrets"] == "fail"
    assert gates["pii"] == "fail"


def test_fr007_question_must_preserve_seed_semantics(demo_workspace: Workspace) -> None:
    candidate = _candidate(
        demo_workspace.config(),
        GeneratedOutput(
            derivation=["Multiply the two stated integers and check the resulting value."],
            answer="102",
        ),
        VerifierSpec(kind=VerifierKind.NUMERIC, expected=102),
        question="What is one plus one?",
    ).model_copy(update={"seed_question": "What is 17 multiplied by 6?"})
    gates = {
        gate.gate: gate.status.value
        for gate in validate_candidate(candidate, demo_workspace.config())
    }
    assert verify_answer(candidate).passed
    assert gates["question_semantic_binding"] == "fail"
