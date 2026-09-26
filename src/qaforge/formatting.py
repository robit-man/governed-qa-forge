from __future__ import annotations

from typing import Any

from qaforge.io import canonical_json, sha256_text

DERIVATION_HEADING = "Derivation:"
FINAL_ANSWER_HEADING = "Final answer:"
ASSISTANT_FORMAT_ID = "qaforge-derivation-final-v1"


def render_assistant(derivation: list[str], answer: str) -> str:
    steps = "\n".join(f"{index}. {step.strip()}" for index, step in enumerate(derivation, 1))
    return f"{DERIVATION_HEADING}\n{steps}\n\n{FINAL_ANSWER_HEADING}\n{answer.strip()}"


def training_messages(question: str, derivation: list[str], answer: str) -> list[dict[str, str]]:
    return [
        {"role": "user", "content": question},
        {"role": "assistant", "content": render_assistant(derivation, answer)},
    ]


def training_content_sha256(question: str, derivation: list[str], answer: str) -> str:
    return sha256_text(
        canonical_json({"messages": training_messages(question, derivation, answer)})
    )


def legacy_content_sha256(question: str, answer: str) -> str:
    """Return the schema-1.0 content digest used by historical releases."""
    return sha256_text(canonical_json({"question": question, "answer": answer}))


def is_standard_training_row(value: Any) -> bool:
    if not isinstance(value, dict) or set(value) != {"messages"}:
        return False
    messages = value.get("messages")
    if not isinstance(messages, list) or len(messages) != 2:
        return False
    if not all(isinstance(message, dict) for message in messages):
        return False
    if messages[0].get("role") != "user" or messages[1].get("role") != "assistant":
        return False
    if set(messages[0]) != {"role", "content"} or set(messages[1]) != {"role", "content"}:
        return False
    question = messages[0].get("content")
    assistant = messages[1].get("content")
    return (
        isinstance(question, str)
        and bool(question.strip())
        and isinstance(assistant, str)
        and assistant.startswith(f"{DERIVATION_HEADING}\n1. ")
        and assistant.count(f"\n\n{FINAL_ANSWER_HEADING}\n") == 1
        and not assistant.endswith(f"{FINAL_ANSWER_HEADING}\n")
    )
