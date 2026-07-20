from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict
from typing import Any, Protocol

from optengine.analysis import Analysis
from optengine.evaluation import Evaluation
from optengine.utility.base import (
    StrategyUtility,
    UtilityAssessment,
    UtilityModel,
)


class OptChinAssessor(Protocol):
    def __call__(
        self,
        payload: Mapping[str, Any],
    ) -> UtilityAssessment | Mapping[str, Any]:
        raise NotImplementedError


class OptChinUtilityAdapter(UtilityModel):
    """Connect a private OptChin assessor to the public utility contract."""

    def __init__(self, assessor: OptChinAssessor) -> None:
        self._assessor = assessor

    def assess(
        self,
        evaluations: Sequence[Evaluation],
        analysis: Analysis | None,
    ) -> UtilityAssessment:
        result = self._assessor(self._payload(evaluations, analysis))

        if isinstance(result, UtilityAssessment):
            return result

        if not isinstance(result, Mapping):
            raise TypeError(
                "OptChin assessor must return UtilityAssessment or a mapping."
            )

        return UtilityAssessment(
            selected_strategy=result.get("selected_strategy"),
            feasible=bool(result.get("feasible", False)),
            utility=self._optional_float(result.get("utility")),
            marginal_utility=self._optional_float(result.get("marginal_utility")),
            expected_improvement=self._optional_float(
                result.get("expected_improvement")
            ),
            execution_cost=self._optional_float(result.get("execution_cost")),
            confidence=self._optional_float(result.get("confidence")),
            reference_gap=self._optional_float(result.get("reference_gap")),
            strategies=tuple(
                self._strategy_from_mapping(value)
                for value in result.get("strategies", ())
            ),
            evidence=dict(result.get("evidence", {})),
        )

    @staticmethod
    def _payload(
        evaluations: Sequence[Evaluation],
        analysis: Analysis | None,
    ) -> Mapping[str, Any]:
        return {
            "analysis": None if analysis is None else asdict(analysis),
            "evaluations": [
                {
                    "strategy": evaluation.strategy,
                    "feasible": evaluation.feasible,
                    "quality": evaluation.quality,
                    "metrics": dict(evaluation.metrics),
                    "reference": dict(evaluation.reference),
                    "utility_inputs": (evaluation.evidence_for_utility()),
                    "candidate": {
                        "formulation": evaluation.candidate.formulation,
                        "operation": evaluation.candidate.operation,
                        "solver": evaluation.candidate.solver,
                        "native_score": evaluation.candidate.native_score,
                        "native_metrics": dict(evaluation.candidate.native_metrics),
                        "runtime_s": evaluation.candidate.runtime_s,
                        "resource_cost": (evaluation.candidate.resource_cost),
                        "status": evaluation.candidate.status,
                        "provenance": dict(evaluation.candidate.provenance),
                    },
                }
                for evaluation in evaluations
            ],
        }

    @staticmethod
    def _strategy_from_mapping(value: Any) -> StrategyUtility:
        if not isinstance(value, Mapping):
            raise TypeError("OptChin strategy utility must be a mapping.")

        return StrategyUtility(
            strategy=str(value["strategy"]),
            feasible=bool(value.get("feasible", False)),
            quality=OptChinUtilityAdapter._optional_float(value.get("quality")),
            utility=OptChinUtilityAdapter._optional_float(value.get("utility")),
            marginal_utility=OptChinUtilityAdapter._optional_float(
                value.get("marginal_utility")
            ),
            expected_improvement=OptChinUtilityAdapter._optional_float(
                value.get("expected_improvement")
            ),
            execution_cost=OptChinUtilityAdapter._optional_float(
                value.get("execution_cost")
            ),
            confidence=OptChinUtilityAdapter._optional_float(value.get("confidence")),
            reference_gap=OptChinUtilityAdapter._optional_float(
                value.get("reference_gap")
            ),
            evidence=dict(value.get("evidence", {})),
        )

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        return None if value is None else float(value)
