from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.evaluation import Evaluation
from optengine.policy.base import Policy
from optengine.utility.base import UtilityAssessment
from optengine.utility.operational import OperationalUtilityModel


@dataclass(frozen=True, kw_only=True)
class ChintropicStopConfig:
    confidence_threshold: float = 0.70
    improvement_threshold: float = 0.05
    minimum_marginal_utility: float = 0.0
    target_reference_gap: float = 0.0


class ChintropicStopPolicy(Policy):
    """Operational Stop/Switch/Scale policy for the public foundation."""

    def __init__(
        self,
        config: ChintropicStopConfig | None = None,
    ) -> None:
        self.config = config or ChintropicStopConfig()

    def apply(
        self,
        assessment: UtilityAssessment | Sequence[Evaluation],
        analysis: Analysis | None = None,
    ) -> Decision:
        normalized = self._normalize_assessment(
            assessment=assessment,
            analysis=analysis,
        )

        evidence = {
            "feasible": normalized.feasible,
            "utility": normalized.utility,
            "marginal_utility": normalized.marginal_utility,
            "expected_improvement": normalized.expected_improvement,
            "execution_cost": normalized.execution_cost,
            "confidence": normalized.confidence,
            "reference_gap": normalized.reference_gap,
            "confidence_threshold": self.config.confidence_threshold,
            "improvement_threshold": self.config.improvement_threshold,
            "minimum_marginal_utility": (self.config.minimum_marginal_utility),
            "target_reference_gap": self.config.target_reference_gap,
        }

        if not normalized.feasible or normalized.selected_strategy is None:
            return Decision(
                action="switch",
                selected_strategy=None,
                reason_code="NO_FEASIBLE_CANDIDATE",
                evidence=evidence,
            )

        if (
            normalized.reference_gap is not None
            and normalized.reference_gap <= self.config.target_reference_gap
        ):
            return Decision(
                action="stop",
                selected_strategy=normalized.selected_strategy,
                reason_code="REFERENCE_TARGET_REACHED",
                evidence=evidence,
            )

        confidence = float(normalized.confidence or 0.0)
        if confidence < self.config.confidence_threshold:
            return Decision(
                action="switch",
                selected_strategy=normalized.selected_strategy,
                reason_code="LOW_CONFIDENCE",
                evidence=evidence,
            )

        expected_improvement = float(normalized.expected_improvement or 0.0)
        marginal_utility = float(normalized.marginal_utility or 0.0)

        if (
            expected_improvement >= self.config.improvement_threshold
            and marginal_utility >= self.config.minimum_marginal_utility
        ):
            return Decision(
                action="scale",
                selected_strategy=normalized.selected_strategy,
                reason_code="ADDITIONAL_SEARCH_JUSTIFIED",
                evidence=evidence,
            )

        return Decision(
            action="stop",
            selected_strategy=normalized.selected_strategy,
            reason_code="MARGINAL_UTILITY_EXHAUSTED",
            evidence=evidence,
        )

    @staticmethod
    def _normalize_assessment(
        assessment: UtilityAssessment | Sequence[Evaluation],
        analysis: Analysis | None,
    ) -> UtilityAssessment:
        if isinstance(assessment, UtilityAssessment):
            return assessment

        return OperationalUtilityModel().assess(
            evaluations=tuple(assessment),
            analysis=analysis,
        )
