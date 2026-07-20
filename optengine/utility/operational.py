from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from optengine.analysis import Analysis
from optengine.evaluation import Evaluation
from optengine.utility.base import (
    StrategyUtility,
    UtilityAssessment,
    UtilityModel,
)


def _optional_float(value: Any) -> float | None:
    return None if value is None else float(value)


def _is_reference(evaluation: Evaluation) -> bool:
    return bool(
        evaluation.reference.get("is_reference")
        or evaluation.candidate.metadata.get("is_reference")
        or evaluation.candidate.native_metrics.get("is_reference")
    )


class OperationalUtilityModel(UtilityModel):
    """Deterministic public fallback until OptChin is connected."""

    def assess(
        self,
        evaluations: Sequence[Evaluation],
        analysis: Analysis | None,
    ) -> UtilityAssessment:
        reference_quality = self._reference_quality(evaluations)
        strategies = tuple(
            self._assess_strategy(evaluation, reference_quality)
            for evaluation in evaluations
        )
        feasible = [
            item for item in strategies if item.feasible and item.utility is not None
        ]

        if not feasible:
            return UtilityAssessment(
                selected_strategy=None,
                feasible=False,
                utility=None,
                marginal_utility=None,
                expected_improvement=None,
                execution_cost=None,
                confidence=None,
                reference_gap=None,
                strategies=strategies,
                evidence={
                    "evaluation_count": len(evaluations),
                    "feasible_count": 0,
                },
            )

        selected = max(
            feasible,
            key=lambda item: float(item.utility),
        )

        return UtilityAssessment(
            selected_strategy=selected.strategy,
            feasible=True,
            utility=selected.utility,
            marginal_utility=selected.marginal_utility,
            expected_improvement=selected.expected_improvement,
            execution_cost=selected.execution_cost,
            confidence=selected.confidence,
            reference_gap=selected.reference_gap,
            strategies=strategies,
            evidence={
                "evaluation_count": len(evaluations),
                "feasible_count": len(feasible),
                "reference_quality": reference_quality,
                "strategy_utilities": [
                    self._strategy_payload(item) for item in strategies
                ],
            },
        )

    @staticmethod
    def _reference_quality(
        evaluations: Sequence[Evaluation],
    ) -> float | None:
        values = [
            float(evaluation.quality)
            for evaluation in evaluations
            if (
                evaluation.feasible
                and evaluation.quality is not None
                and _is_reference(evaluation)
            )
        ]
        return max(values) if values else None

    def _assess_strategy(
        self,
        evaluation: Evaluation,
        reference_quality: float | None,
    ) -> StrategyUtility:
        supplied = evaluation.evidence_for_utility()
        quality = _optional_float(evaluation.quality)

        execution_cost = _optional_float(
            supplied.get(
                "execution_cost",
                supplied.get(
                    "estimated_cost",
                    evaluation.candidate.resource_cost,
                ),
            )
        )
        if execution_cost is None:
            execution_cost = 0.0

        confidence = (
            1.0
            if _is_reference(evaluation)
            else _optional_float(supplied.get("confidence"))
        )
        if confidence is None:
            confidence = 0.0

        expected_improvement = _optional_float(
            supplied.get(
                "expected_improvement",
                evaluation.candidate.native_metrics.get(
                    "expected_improvement",
                    0.0,
                ),
            )
        )
        if expected_improvement is None:
            expected_improvement = 0.0

        reference_gap = _optional_float(supplied.get("reference_gap"))
        if (
            reference_gap is None
            and reference_quality is not None
            and quality is not None
        ):
            reference_gap = max(0.0, reference_quality - quality)

        utility = _optional_float(supplied.get("utility"))
        if utility is None and evaluation.feasible:
            utility = quality

        marginal_utility = _optional_float(supplied.get("marginal_utility"))
        if marginal_utility is None:
            marginal_utility = expected_improvement - execution_cost

        evidence: dict[str, Any] = {
            "quality": quality,
            "execution_cost": execution_cost,
            "confidence": confidence,
            "expected_improvement": expected_improvement,
            "reference_gap": reference_gap,
            "is_reference": _is_reference(evaluation),
        }
        evidence.update(supplied)

        return StrategyUtility(
            strategy=evaluation.strategy,
            feasible=evaluation.feasible,
            quality=quality,
            utility=utility,
            marginal_utility=marginal_utility,
            expected_improvement=expected_improvement,
            execution_cost=execution_cost,
            confidence=confidence,
            reference_gap=reference_gap,
            evidence=evidence,
        )

    @staticmethod
    def _strategy_payload(
        item: StrategyUtility,
    ) -> Mapping[str, Any]:
        return {
            "strategy": item.strategy,
            "feasible": item.feasible,
            "quality": item.quality,
            "utility": item.utility,
            "marginal_utility": item.marginal_utility,
            "expected_improvement": item.expected_improvement,
            "execution_cost": item.execution_cost,
            "confidence": item.confidence,
            "reference_gap": item.reference_gap,
            "evidence": dict(item.evidence),
        }
