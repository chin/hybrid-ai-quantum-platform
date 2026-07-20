from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, kw_only=True)
class Operation:
    """The method requested by a strategy."""

    name: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
