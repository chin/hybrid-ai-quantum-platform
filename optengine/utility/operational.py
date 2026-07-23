from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from optengine.utility.base import (
    Assessment,
    StrategyAssessment,
    Utility,
)

if TYPE_CHECKING:
    from optengine.analysis import Analysis
    from optengine.execution import Execution


def _optional_float(value: Any) -> float | None:
    return None if value is None else float(value)


class OperationalUtility(Utility):
    """Deterministic public Utility implementation."""

    def assess(
        self,
        executions: Sequence[Execution],
        analysis: Analysis | None,
    ) -> Assessment:
        reference_quality = self._reference_quality(executions)
        strategies = tuple(
            self._assess_execution(
                execution,
                reference_quality,
            )
            for execution in executions
        )
        feasible = [
            item for item in strategies if item.feasible and item.utility is not None
        ]

        if not feasible:
            return Assessment(
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
                    "execution_count": len(executions),
                    "successful_count": sum(
                        execution.succeeded for execution in executions
                    ),
                    "feasible_count": 0,
                },
            )

        selected = max(
            feasible,
            key=lambda item: float(item.utility),
        )
        return Assessment(
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
                "execution_count": len(executions),
                "successful_count": sum(
                    execution.succeeded for execution in executions
                ),
                "feasible_count": len(feasible),
                "reference_quality": reference_quality,
                "strategy_assessments": [item.to_dict() for item in strategies],
            },
        )

    @staticmethod
    def _reference_quality(
        executions: Sequence[Execution],
    ) -> float | None:
        values = [
            float(execution.evaluation.quality)
            for execution in executions
            if (
                execution.succeeded
                and execution.evaluation is not None
                and execution.evaluation.feasible
                and execution.evaluation.quality is not None
                and OperationalUtility._is_reference(execution)
            )
        ]
        return max(values) if values else None

    @staticmethod
    def _is_reference(execution: Execution) -> bool:
        return bool(
            execution.strategy.reference
            or (
                execution.result is not None
                and execution.result.metrics.get("is_reference")
            )
        )

    def _assess_execution(
        self,
        execution: Execution,
        reference_quality: float | None,
    ) -> StrategyAssessment:
        if not execution.succeeded or execution.evaluation is None:
            failure = {} if execution.failure is None else execution.failure.to_dict()
            return StrategyAssessment(
                strategy=execution.strategy.name,
                feasible=False,
                quality=None,
                utility=None,
                marginal_utility=None,
                expected_improvement=None,
                execution_cost=None,
                confidence=None,
                reference_gap=None,
                evidence={
                    "execution_status": execution.state.code,
                    "failure": failure,
                },
            )

        evaluation = execution.evaluation
        result = execution.result
        supplied = evaluation.evidence_for_utility()
        quality = _optional_float(evaluation.quality)

        execution_cost = _optional_float(
            supplied.get(
                "execution_cost",
                supplied.get(
                    "estimated_cost",
                    (None if result is None else result.resource_cost),
                ),
            )
        )
        if execution_cost is None:
            execution_cost = (
                0.0 if execution.runtime_s is None else float(execution.runtime_s)
            )

        confidence = (
            1.0
            if self._is_reference(execution)
            else _optional_float(
                supplied.get(
                    "confidence",
                    (None if result is None else result.metrics.get("confidence")),
                )
            )
        )
        if confidence is None:
            confidence = 0.0

        expected_improvement = _optional_float(
            supplied.get(
                "expected_improvement",
                (
                    0.0
                    if result is None
                    else result.metrics.get(
                        "expected_improvement",
                        0.0,
                    )
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
            reference_gap = max(
                0.0,
                reference_quality - quality,
            )

        utility_value = _optional_float(supplied.get("utility"))
        if utility_value is None and evaluation.feasible:
            utility_value = quality

        marginal_utility = _optional_float(supplied.get("marginal_utility"))
        if marginal_utility is None:
            marginal_utility = expected_improvement - execution_cost

        evidence: dict[str, Any] = {
            "quality": quality,
            "execution_cost": execution_cost,
            "confidence": confidence,
            "expected_improvement": expected_improvement,
            "reference_gap": reference_gap,
            "is_reference": self._is_reference(execution),
            "execution_status": execution.state.code,
        }
        evidence.update(supplied)

        return StrategyAssessment(
            strategy=execution.strategy.name,
            feasible=evaluation.feasible,
            quality=quality,
            utility=utility_value,
            marginal_utility=marginal_utility,
            expected_improvement=expected_improvement,
            execution_cost=execution_cost,
            confidence=confidence,
            reference_gap=reference_gap,
            evidence=evidence,
        )


# Backward-compatible public name.
OperationalUtilityModel = OperationalUtility
