from __future__ import annotations

from collections.abc import Sequence

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.evaluation import Evaluation
from optengine.policy.base import Policy


class ChintropicStopPolicy(Policy):
    """Initial operational Stop/Switch/Scale policy."""

    confidence_threshold = 0.70
    improvement_threshold = 0.05

    def apply(
        self,
        evaluations: Sequence[Evaluation],
        analysis: Analysis | None,
    ) -> Decision:
        if not evaluations:
            return Decision(
                action="switch",
                selected_strategy=None,
                reason_code="NO_EVALUATION",
                evidence={
                    "evaluation_count": 0,
                },
            )

        feasible = [evaluation for evaluation in evaluations if evaluation.feasible]

        if not feasible:
            return Decision(
                action="switch",
                selected_strategy=None,
                reason_code="NO_FEASIBLE_CANDIDATE",
                evidence={
                    "evaluation_count": len(evaluations),
                    "feasible_count": 0,
                },
            )

        # Python's max() preserves the first item when keys are equal,
        # giving deterministic tie behavior.
        selected = max(
            feasible,
            key=lambda evaluation: (
                float("-inf") if evaluation.quality is None else evaluation.quality
            ),
        )

        evidence = dict(selected.policy_evidence)

        confidence = float(evidence.get("confidence", 0.0))
        expected_improvement = float(
            evidence.get(
                "expected_improvement",
                0.0,
            )
        )

        evidence.update(
            {
                "quality": selected.quality,
                "confidence": confidence,
                "expected_improvement": (expected_improvement),
                "confidence_threshold": (self.confidence_threshold),
                "improvement_threshold": (self.improvement_threshold),
            }
        )

        if confidence < self.confidence_threshold:
            return Decision(
                action="switch",
                selected_strategy=selected.strategy,
                reason_code="LOW_CONFIDENCE",
                evidence=evidence,
            )

        if expected_improvement >= self.improvement_threshold:
            return Decision(
                action="scale",
                selected_strategy=selected.strategy,
                reason_code="ADDITIONAL_SEARCH_JUSTIFIED",
                evidence=evidence,
            )

        return Decision(
            action="stop",
            selected_strategy=selected.strategy,
            reason_code="MARGINAL_UTILITY_EXHAUSTED",
            evidence=evidence,
        )
