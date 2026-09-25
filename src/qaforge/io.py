from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections.abc import Iterable
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel

from qaforge.errors import ConfigurationError

ModelT = TypeVar("ModelT", bound=BaseModel)
MAX_YAML_BYTES = 10 * 1024 * 1024
MAX_JSONL_BYTES = 256 * 1024 * 1024
MAX_JSONL_LINE_CHARS = 1024 * 1024
MAX_JSONL_RECORDS = 1_000_000


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def canonical_data(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", exclude_none=True)
    if isinstance(value, dict):
        return {str(key): canonical_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [canonical_data(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        canonical_data(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_within(root: Path, path: Path) -> Path:
    resolved_root = root.resolve()
    resolved = path.resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise ConfigurationError(f"path escapes workspace: {path}")
    return resolved


def safe_identifier(value: str, label: str = "identifier") -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", value) or ".." in value:
        raise ConfigurationError(f"invalid {label}: {value!r}")
    return value


def read_text_bounded(path: Path, max_bytes: int) -> str:
    try:
        if path.stat().st_size > max_bytes:
            raise ConfigurationError(f"input exceeds byte limit: {path}")
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigurationError(f"cannot read input {path}: {exc}") from exc


def read_yaml(path: Path, model: type[ModelT]) -> ModelT:
    try:
        value = yaml.safe_load(read_text_bounded(path, MAX_YAML_BYTES))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"cannot read YAML {path}: {exc}") from exc
    return model.model_validate(value)


def read_yaml_list(path: Path, key: str, model: type[ModelT]) -> list[ModelT]:
    try:
        value = yaml.safe_load(read_text_bounded(path, MAX_YAML_BYTES))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"cannot read YAML {path}: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get(key), list):
        raise ConfigurationError(f"{path} must contain a '{key}' list")
    return [model.model_validate(item) for item in value[key]]


def read_jsonl(path: Path, model: type[ModelT]) -> list[ModelT]:
    records: list[ModelT] = []
    try:
        if path.stat().st_size > MAX_JSONL_BYTES:
            raise ConfigurationError(f"JSONL input exceeds byte limit: {path}")
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if line_number > MAX_JSONL_RECORDS:
                    raise ConfigurationError(f"JSONL input exceeds record limit: {path}")
                if len(line) > MAX_JSONL_LINE_CHARS:
                    raise ConfigurationError(
                        f"JSONL line {line_number} exceeds length limit: {path}"
                    )
                if line.strip():
                    records.append(model.model_validate_json(line))
    except ConfigurationError:
        raise
    except (OSError, ValueError) as exc:
        raise ConfigurationError(f"cannot read JSONL {path}: {exc}") from exc
    return records


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_text(path: Path, content: str) -> None:
    _atomic_write(path, content)


def write_json(path: Path, value: Any) -> None:
    _atomic_write(path, json.dumps(canonical_data(value), indent=2, sort_keys=True) + "\n")


def write_yaml(path: Path, value: Any) -> None:
    _atomic_write(path, yaml.safe_dump(canonical_data(value), sort_keys=False))


def write_jsonl(path: Path, values: Iterable[Any]) -> None:
    content = "".join(canonical_json(value) + "\n" for value in values)
    _atomic_write(path, content)
