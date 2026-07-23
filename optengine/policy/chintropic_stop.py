from __future__ import annotations

from dataclasses import dataclass

from optengine.analysis import Analysis
from optengine.decision import Decision, Scale, Stop, Switch
from optengine.policy.base import Policy
from optengine.utility.base import Assessment


@dataclass(frozen=True, kw_only=True)
class ChintropicStopConfig:
    confidence_threshold: float = 0.70
    improvement_threshold: float = 0.05
    minimum_marginal_utility: float = 0.0
    target_reference_gap: float = 0.0


class ChintropicStopPolicy(Policy):
    """Operational Stop/Switch/Scale policy."""

    def __init__(
        self,
        config: ChintropicStopConfig | None = None,
    ) -> None:
        self.config = config or ChintropicStopConfig()

    def apply(
        self,
        assessment: Assessment,
        analysis: Analysis | None = None,
    ) -> Decision:
        evidence = {
            "feasible": assessment.feasible,
            "utility": assessment.utility,
            "marginal_utility": assessment.marginal_utility,
            "expected_improvement": assessment.expected_improvement,
            "execution_cost": assessment.execution_cost,
            "confidence": assessment.confidence,
            "reference_gap": assessment.reference_gap,
            "confidence_threshold": self.config.confidence_threshold,
            "improvement_threshold": self.config.improvement_threshold,
            "minimum_marginal_utility": (self.config.minimum_marginal_utility),
            "target_reference_gap": (self.config.target_reference_gap),
        }

        if not assessment.feasible or assessment.selected_strategy is None:
            return Switch(
                selected_strategy=None,
                reason_code="NO_FEASIBLE_CANDIDATE",
                evidence=evidence,
            )

        if (
            assessment.reference_gap is not None
            and assessment.reference_gap <= self.config.target_reference_gap
        ):
            return Stop(
                selected_strategy=assessment.selected_strategy,
                reason_code="REFERENCE_TARGET_REACHED",
                evidence=evidence,
            )

        confidence = float(assessment.confidence or 0.0)
        if confidence < self.config.confidence_threshold:
            return Switch(
                selected_strategy=assessment.selected_strategy,
                reason_code="LOW_CONFIDENCE",
                evidence=evidence,
            )

        expected_improvement = float(assessment.expected_improvement or 0.0)
        marginal_utility = float(assessment.marginal_utility or 0.0)
        if (
            expected_improvement >= self.config.improvement_threshold
            and marginal_utility >= self.config.minimum_marginal_utility
        ):
            return Scale(
                selected_strategy=assessment.selected_strategy,
                reason_code="ADDITIONAL_SEARCH_JUSTIFIED",
                evidence=evidence,
            )

        return Stop(
            selected_strategy=assessment.selected_strategy,
            reason_code="MARGINAL_UTILITY_EXHAUSTED",
            evidence=evidence,
        )
