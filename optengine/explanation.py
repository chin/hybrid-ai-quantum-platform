from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, kw_only=True)
class Explanation:
    """Human-readable rationale produced from the completed workflow evidence."""

    summary: str
    selected_strategy: str | None
    evidence: Mapping[str, Any] = field(default_factory=dict)
    alternatives: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "summary": self.summary,
            "selected_strategy": self.selected_strategy,
            "evidence": dict(self.evidence),
            "alternatives": list(self.alternatives),
            "limitations": list(self.limitations),
        }
