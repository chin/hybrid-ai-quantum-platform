from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class Explanation:
    summary: str
    selected_strategy: str | None
    evidence: Mapping[str, Any] = field(default_factory=dict)
    alternatives: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
