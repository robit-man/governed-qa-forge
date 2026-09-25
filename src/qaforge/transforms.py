from __future__ import annotations

from qaforge.errors import ConfigurationError

QUESTION_TRANSFORMS = {
    "identity-v1": "{question}",
    "work-carefully-v1": "Work carefully and answer this task: {question}",
    "requested-form-v1": "{question}\nGive the answer in the requested form.",
    "check-constraints-v1": "Check the relevant constraints, then answer: {question}",
    "precise-response-v1": "Provide a precise response to: {question}",
    "solve-unchanged-v1": "Without changing the task, solve: {question}",
    "reason-requirements-v1": "Reason about the requirements and answer: {question}",
    "complete-task-v1": "Complete this self-contained task: {question}",
    "verified-answer-v1": "Return a verified answer for: {question}",
    "concise-analysis-v1": "Analyze and respond concisely: {question}",
}


def transform_ids(count: int) -> list[str]:
    identifiers = list(QUESTION_TRANSFORMS)
    if count > len(identifiers):
        raise ConfigurationError(f"only {len(identifiers)} controlled transforms are available")
    return identifiers[:count]


def transform_question(seed_question: str, transform_id: str) -> str:
    try:
        return QUESTION_TRANSFORMS[transform_id].format(question=seed_question)
    except KeyError as exc:
        raise ConfigurationError(f"unknown question transform: {transform_id}") from exc
