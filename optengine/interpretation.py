from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping

from optengine.identity import fingerprint

if TYPE_CHECKING:
    from optengine.domains.base import Domain
    from optengine.objective import Objective


@dataclass(frozen=True, kw_only=True)
class Interpretation:
    """A Domain's semantic and mathematical view of its own aggregate."""

    domain: Domain
    objective: Objective
    summary: Mapping[str, Any]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def fingerprint(self) -> str:
        return fingerprint(
            {
                "domain_type": self.domain.domain_type,
                "name": self.domain.name,
                "objective": self.objective.canonical,
                "summary": dict(self.summary),
                "metadata": dict(self.metadata),
            }
        )

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "fingerprint": self.fingerprint,
            "domain_type": self.domain.domain_type,
            "name": self.domain.name,
            "summary": dict(self.summary),
            "curve": dict(self.objective.curve.canonical),
            "metadata": dict(self.metadata),
        }
