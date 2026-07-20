from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from optengine.candidate import Candidate


@dataclass(frozen=True, kw_only=True)
class Evaluation:
    """A domain interpretation of one normalized candidate."""

    strategy: str
    candidate: Candidate
    feasible: bool
    quality: float | None
    metrics: Mapping[str, Any]
    reference: Mapping[str, Any] = field(default_factory=dict)
    utility_inputs: Mapping[str, Any] = field(default_factory=dict)
    policy_evidence: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def evidence_for_utility(self) -> dict[str, Any]:
        evidence = dict(self.policy_evidence)
        evidence.update(self.utility_inputs)
        return evidence
