from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Protocol

from optengine.utility.base import (
    Assessment,
    StrategyAssessment,
    Utility,
)

if TYPE_CHECKING:
    from optengine.analysis import Analysis
    from optengine.execution import Execution


class OptChinAssessor(Protocol):
    def __call__(
        self,
        payload: Mapping[str, Any],
    ) -> Assessment | Mapping[str, Any]:
        raise NotImplementedError


class OptChinUtility(Utility):
    """Connect a private OptChin assessor to the public Utility contract."""

    def __init__(self, assessor: OptChinAssessor) -> None:
        self._assessor = assessor

    def assess(
        self,
        executions: Sequence[Execution],
        analysis: Analysis | None,
    ) -> Assessment:
        result = self._assessor(self._payload(executions, analysis))

        if isinstance(result, Assessment):
            return result

        if not isinstance(result, Mapping):
            raise TypeError("OptChin assessor must return Assessment or a mapping.")

        return Assessment(
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
        executions: Sequence[Execution],
        analysis: Analysis | None,
    ) -> Mapping[str, Any]:
        return {
            "analysis": (None if analysis is None else analysis.to_dict()),
            "executions": [execution.to_dict() for execution in executions],
        }

    @staticmethod
    def _strategy_from_mapping(
        value: Any,
    ) -> StrategyAssessment:
        if not isinstance(value, Mapping):
            raise TypeError("OptChin Strategy assessment must be a mapping.")

        return StrategyAssessment(
            strategy=str(value["strategy"]),
            feasible=bool(value.get("feasible", False)),
            quality=OptChinUtility._optional_float(value.get("quality")),
            utility=OptChinUtility._optional_float(value.get("utility")),
            marginal_utility=OptChinUtility._optional_float(
                value.get("marginal_utility")
            ),
            expected_improvement=OptChinUtility._optional_float(
                value.get("expected_improvement")
            ),
            execution_cost=OptChinUtility._optional_float(value.get("execution_cost")),
            confidence=OptChinUtility._optional_float(value.get("confidence")),
            reference_gap=OptChinUtility._optional_float(value.get("reference_gap")),
            evidence=dict(value.get("evidence", {})),
        )

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        return None if value is None else float(value)


OptChinUtilityAdapter = OptChinUtility
