from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping


@dataclass(frozen=True, kw_only=True)
class Candidate:
    """A normalized result returned by a concrete solver."""

    strategy: str = ""
    formulation: str
    operation: str
    solver: str
    values: Mapping[str, Any]
    native_score: float | None
    status: str
    runtime_s: float | None = None
    resource_cost: float | None = None
    native_metrics: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def assigned_to(self, strategy: str) -> Candidate:
        if self.strategy and self.strategy != strategy:
            raise ValueError("Candidate is already assigned to a different strategy.")
        return replace(self, strategy=strategy)

    def with_values(
        self,
        values: Mapping[str, Any],
    ) -> Candidate:
        return replace(self, values=dict(values))
