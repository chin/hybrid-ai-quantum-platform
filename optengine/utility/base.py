from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Mapping

from optengine.analysis import Analysis
from optengine.evaluation import Evaluation


@dataclass(frozen=True, kw_only=True)
class StrategyUtility:
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


@dataclass(frozen=True, kw_only=True)
class UtilityAssessment:
    selected_strategy: str | None
    feasible: bool
    utility: float | None
    marginal_utility: float | None
    expected_improvement: float | None
    execution_cost: float | None
    confidence: float | None
    reference_gap: float | None
    strategies: tuple[StrategyUtility, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)


class UtilityModel(ABC):
    @abstractmethod
    def assess(
        self,
        evaluations: Sequence[Evaluation],
        analysis: Analysis | None,
    ) -> UtilityAssessment:
        raise NotImplementedError
