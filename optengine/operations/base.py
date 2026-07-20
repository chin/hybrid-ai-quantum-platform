from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class Operation:
    """Algorithm or method requested by a Strategy."""

    name: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
