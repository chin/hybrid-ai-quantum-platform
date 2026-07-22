from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from optengine.analysis import Analysis
    from optengine.execution import Execution


@dataclass(frozen=True, kw_only=True)
class StrategyAssessment:
    strategy: str
    feasible: bool
    quality: float | None
    utility: float | None
    marginal_utility: float | None
    expected_improvement: float | None
    execution_cost: float | None
    confidence: float | None
    reference_gap: float | None
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "strategy": self.strategy,
            "feasible": self.feasible,
            "quality": self.quality,
            "utility": self.utility,
            "marginal_utility": self.marginal_utility,
            "expected_improvement": self.expected_improvement,
            "execution_cost": self.execution_cost,
            "confidence": self.confidence,
            "reference_gap": self.reference_gap,
            "evidence": dict(self.evidence),
        }


@dataclass(frozen=True, kw_only=True)
class Assessment:
    """Persistent result produced by a Utility object."""

    selected_strategy: str | None
    feasible: bool
    utility: float | None
    marginal_utility: float | None
    expected_improvement: float | None
    execution_cost: float | None
    confidence: float | None
    reference_gap: float | None
    strategies: tuple[StrategyAssessment, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)

    @property
    def ranked(self) -> tuple[StrategyAssessment, ...]:
        return tuple(
            sorted(
                self.strategies,
                key=lambda item: (
                    item.utility is None,
                    -(float("-inf") if item.utility is None else float(item.utility)),
                    item.strategy,
                ),
            )
        )

    @property
    def best(self) -> StrategyAssessment | None:
        return self.ranked[0] if self.ranked else None

    def for_strategy(self, name: str) -> StrategyAssessment:
        try:
            return next(item for item in self.strategies if item.strategy == name)
        except StopIteration as error:
            raise KeyError(f"Unknown assessed Strategy: {name}") from error

    def dominates(self, first: str, second: str) -> bool:
        first_value = self.for_strategy(first).utility
        second_value = self.for_strategy(second).utility
        if first_value is None:
            return False
        if second_value is None:
            return True
        return float(first_value) > float(second_value)

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "selected_strategy": self.selected_strategy,
            "feasible": self.feasible,
            "utility": self.utility,
            "marginal_utility": self.marginal_utility,
            "expected_improvement": self.expected_improvement,
            "execution_cost": self.execution_cost,
            "confidence": self.confidence,
            "reference_gap": self.reference_gap,
            "strategies": [item.to_dict() for item in self.strategies],
            "evidence": dict(self.evidence),
        }


class Utility(ABC):
    """Behavior object that determines comparative execution utility."""

    @abstractmethod
    def assess(
        self,
        executions: Sequence[Execution],
        analysis: Analysis | None,
    ) -> Assessment:
        raise NotImplementedError  # pragma: no cover


# Backward-compatible public names. Canonical code uses Utility, Assessment,
# and StrategyAssessment; the aliases remain exact type identities.
UtilityModel = Utility
UtilityAssessment = Assessment
StrategyUtility = StrategyAssessment
