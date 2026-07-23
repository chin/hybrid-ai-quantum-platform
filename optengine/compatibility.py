from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, kw_only=True)
class Compatibility:
    """The result of one local compatibility evaluation."""

    supported: bool
    reasons: tuple[str, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.supported

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "supported": self.supported,
            "reasons": list(self.reasons),
            "evidence": dict(self.evidence),
        }

    @classmethod
    def accepted(
        cls,
        *,
        evidence: Mapping[str, Any] | None = None,
    ) -> Compatibility:
        return cls(
            supported=True,
            evidence={} if evidence is None else dict(evidence),
        )

    @classmethod
    def rejected(
        cls,
        *reasons: str,
        evidence: Mapping[str, Any] | None = None,
    ) -> Compatibility:
        normalized = tuple(reason for reason in reasons if reason)
        if not normalized:
            normalized = ("unsupported",)
        return cls(
            supported=False,
            reasons=normalized,
            evidence={} if evidence is None else dict(evidence),
        )
