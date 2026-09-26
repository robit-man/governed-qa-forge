from __future__ import annotations

from collections.abc import Iterable

from qaforge.errors import ConfigurationError, GateError


def exposed_private_identifiers(text: str, identifiers: Iterable[str]) -> list[str]:
    """Return registered identifiers that appear in agent- or trainer-visible text."""
    normalized = text.casefold()
    return sorted(
        {
            identifier
            for identifier in identifiers
            if identifier and identifier.casefold() in normalized
        },
        key=str.casefold,
    )


def assert_prompt_is_opaque(text: str, identifiers: Iterable[str], subject: str) -> None:
    exposed = exposed_private_identifiers(text, identifiers)
    if exposed:
        raise ConfigurationError(f"{subject} contains a registered private identifier")


def assert_training_content_is_opaque(
    text: str, identifiers: Iterable[str], record_id: str
) -> None:
    exposed = exposed_private_identifiers(text, identifiers)
    if exposed:
        raise GateError(f"record exposes a registered private identifier: {record_id}")
