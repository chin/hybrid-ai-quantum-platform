from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from optengine.candidate import Candidate


@dataclass(frozen=True)
class Evaluation:
    strategy: str
    candidate: Candidate

    feasible: bool
    quality: float | None
    metrics: Mapping[str, Any]

    reference: Mapping[str, Any] = field(default_factory=dict)
    policy_evidence: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)
