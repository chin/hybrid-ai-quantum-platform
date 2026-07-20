from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping


DecisionAction = Literal["stop", "switch", "scale"]


@dataclass(frozen=True, kw_only=True)
class Decision:
    action: DecisionAction
    selected_strategy: str | None
    reason_code: str
    evidence: Mapping[str, Any] = field(default_factory=dict)
    next_strategy: str | None = None
    resource_change: Mapping[str, Any] = field(default_factory=dict)
