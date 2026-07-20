from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class Candidate:
    strategy: str
    formulation: str
    operation: str
    solver: str

    values: Mapping[str, Any]
    native_score: float | None
    status: str

    runtime_s: float | None = None
    resource_cost: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)
