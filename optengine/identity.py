from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping


def canonical_value(value: Any) -> Any:
    """Convert a controlled object graph into deterministic JSON data."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Enum):
        return canonical_value(value.value)

    if isinstance(value, Path):
        return str(value)

    canonical = getattr(value, "canonical", None)
    if canonical is not None:
        return canonical_value(canonical)

    if isinstance(value, Mapping):
        items = sorted(
            (
                (
                    json.dumps(
                        canonical_value(key),
                        sort_keys=True,
                        default=str,
                    ),
                    canonical_value(item),
                )
                for key, item in value.items()
            ),
            key=lambda item: item[0],
        )
        return {key: item for key, item in items}

    if isinstance(value, (tuple, list, set, frozenset)):
        normalized = [canonical_value(item) for item in value]
        if isinstance(value, (set, frozenset)):
            normalized.sort(
                key=lambda item: json.dumps(item, sort_keys=True, default=str)
            )
        return normalized

    if is_dataclass(value):
        return canonical_value(asdict(value))

    return {
        "type": f"{type(value).__module__}.{type(value).__qualname__}",
        "repr": repr(value),
    }


def fingerprint(value: Any) -> str:
    payload = json.dumps(
        canonical_value(value),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def identifier_value(identifier: Any) -> Mapping[str, str]:
    return {
        "type": f"{type(identifier).__module__}.{type(identifier).__qualname__}",
        "repr": repr(identifier),
    }
