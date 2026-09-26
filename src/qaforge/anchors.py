from __future__ import annotations

from qaforge.models import AuthorizationStatus, BehaviorAnchorEntry

AIWG_ANCHOR_SOURCE_ID = "SRC-AIWG-BEHAVIOR-PROFILE"


def aiwg_behavior_anchors() -> list[BehaviorAnchorEntry]:
    """Return the reviewed latent-behavior profile induced from AIWG framework surfaces."""
    definitions = (
        (
            "aiwg.requirements-and-acceptance",
            "requirements-and-acceptance",
            "Turn an ambiguous objective into explicit constraints and measurable acceptance "
            "criteria, with traceable decisions before implementation.",
            "agent:requirements-analyst",
            "e014bbf931c340674a2018c42bc5c2a14d8052c7f823da09f50d0cfc0907f77e",
        ),
        (
            "aiwg.evidence-before-assertion",
            "evidence-before-assertion",
            "Gather and grade relevant evidence, separate observation from inference, and "
            "calibrate claims to the strength and limits of the evidence.",
            "skill:research-quickref",
            "76c6931284d3051ddd065dc4c617984f82ad3bf82d0b82defb57abc8bd95ecad",
        ),
        (
            "aiwg.provenance-and-traceability",
            "provenance-and-traceability",
            "Preserve origin, transformations, responsible actors, hashes, and downstream links so "
            "an artifact and its decisions can be independently reconstructed.",
            "skill:auto-provenance",
            "09763b3e92c588faea90728316a299e24595ff3768f164c8db5553a681fb9298",
        ),
        (
            "aiwg.threat-modeling-and-least-authority",
            "threat-modeling-and-least-authority",
            "Identify assets, trust boundaries, adversary paths, and failure impact, then grant "
            "only the authority and exposure required for the task.",
            "skill:security-assessment",
            "c7efeab34d544c4e77bdafcf5a7577ed363cd5337eba928a20e9c475e9913113",
        ),
        (
            "aiwg.independent-verification",
            "independent-verification",
            "Do not treat a producer's confidence as proof; verify consequential outputs through "
            "an independent method with an explicit pass or fail condition.",
            "skill:best-practices-audit",
            "8eb4e772536a58344b73abfb342d4f1684e5a51528cd489fd40f45278575376c",
        ),
        (
            "aiwg.test-and-quality-gates",
            "test-and-quality-gates",
            "Convert requirements and known risks into tests, execute the relevant suite, preserve "
            "the results, and block delivery when a mandatory gate fails.",
            "skill:flow-test-strategy-execution",
            "cdd88da3123e197914e1d021053075ed19c20fe65b1f8a36e93c074b9b490066",
        ),
        (
            "aiwg.change-impact-and-architecture",
            "change-impact-and-architecture",
            "Assess upstream and downstream impact before changing a contract, record the "
            "decision, and provide an explicit compatibility or migration path.",
            "skill:architecture-evolution",
            "31d0b8fe956064e97af7b8879cf424aa86c3b2fc6d2552dc21c2dc4b9bdeef13",
        ),
        (
            "aiwg.operational-readiness-and-recovery",
            "operational-readiness-and-recovery",
            "Treat deployment as a reversible operational change with health evidence, bounded "
            "failure modes, recovery steps, ownership, and a clear release decision.",
            "agent:deployment-manager",
            "0bc7fa28a9c467f1f93f9360ad106a59c3e8a887e4f29517ea13a18230b86f0d",
        ),
        (
            "aiwg.context-boundaries-and-poisoning-resistance",
            "context-boundaries-and-poisoning-resistance",
            "Minimize untrusted context, distinguish instructions from evidence, prevent "
            "privileged evaluation signals from reaching producers, and fail closed on trust.",
            "rule:skill-discovery",
            "71854a7d3fb47de3ac86576448babd21f528293cfdf71a492095eaede069718b",
        ),
        (
            "aiwg.orchestration-and-accountable-integration",
            "orchestration-and-accountable-integration",
            "Delegate only bounded independent work, retain a single accountable integrator, "
            "resolve conflicts explicitly, and verify the result against the objective.",
            "skill:parallel-dispatch",
            "eeca9f7131673f9bdaee4a5ab58e0374f1781572ebfb79553b3e27c06bf46654",
        ),
    )
    return [
        BehaviorAnchorEntry(
            anchor_id=anchor_id,
            domain=domain,
            principle=principle,
            source_ref=source_ref,
            source_sha256=source_sha256,
            source_version="aiwg-cli-2026.5.11",
            source_ids=[AIWG_ANCHOR_SOURCE_ID],
            authorization_status=AuthorizationStatus.APPROVED,
            reviewed_at="2026-09-25T00:00:00Z",
            reviewer="project-team",
        )
        for anchor_id, domain, principle, source_ref, source_sha256 in definitions
    ]


def behavior_anchor_private_identifiers(
    anchors: list[BehaviorAnchorEntry],
) -> set[str]:
    identifiers = {"aiwg"}
    for anchor in anchors:
        identifiers.add(anchor.anchor_id.casefold())
        identifiers.add(anchor.domain.casefold())
        identifiers.add(anchor.source_ref.casefold())
        for reference in anchor.source_ref.split(";"):
            identifiers.add(reference.casefold())
            _kind, _separator, name = reference.partition(":")
            if name:
                identifiers.add(name.casefold())
    return identifiers
