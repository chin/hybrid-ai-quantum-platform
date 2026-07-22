from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from optengine.analysis import Analysis
from optengine.cli import block
from optengine.decision import Decision
from optengine.execution import Execution
from optengine.recommendation import Recommendation
from optengine.utility.base import Assessment, StrategyAssessment


def _compact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _compact(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_compact(item) for item in value]
    if isinstance(value, list):
        return [_compact(item) for item in value]
    return value


def analysis_chain(analysis: Analysis) -> tuple[tuple[str, Any], ...]:
    """Return the canonical pre-execution domain chain."""

    objective = analysis.interpretation.objective
    return (
        ("domain", dict(analysis.domain.summary)),
        ("interpretation", analysis.interpretation.to_dict()),
        ("objective", dict(objective.canonical)),
        ("expression", dict(objective.expression.canonical)),
        ("curve", dict(objective.curve.canonical)),
    )


def strategy_chain(execution: Execution) -> tuple[tuple[str, Any], ...]:
    """Return one Strategy's formulation-through-execution chain."""

    strategy = execution.strategy
    return (
        ("formulation", strategy.formulation.signature),
        ("model", strategy.model.to_dict()),
        ("operation", strategy.operation.signature),
        ("solver", strategy.solver.signature),
        ("strategy", strategy.summary()),
        ("execution", execution.to_dict()),
    )


def assessment_for_execution(
    assessment: Assessment,
    execution: Execution,
) -> StrategyAssessment:
    return assessment.for_strategy(execution.strategy.name)


def outcome_chain(
    recommendation: Recommendation,
) -> tuple[tuple[str, Any], ...]:
    """Return the workflow outcome chain after all Strategies execute."""

    assessment = recommendation.assessment
    decision = recommendation.decision
    if assessment is None:
        raise RuntimeError("Recommendation has no Assessment.")
    if decision is None:
        raise RuntimeError("Recommendation has no Decision.")
    return (
        ("utility", assessment.to_dict()),
        ("decision", decision.to_dict()),
        ("recommendation", recommendation.to_dict()),
    )


def render_analysis_chain(analysis: Analysis) -> None:
    for name, value in analysis_chain(analysis):
        block(f"analysis.{name}", _compact(value))

    for index, strategy in enumerate(analysis.strategies, start=1):
        prefix = f"analysis.strategy[{index}]"
        block(f"{prefix}.formulation", strategy.formulation.signature)
        block(f"{prefix}.model", strategy.model.to_dict())
        block(f"{prefix}.operation", strategy.operation.signature)
        block(f"{prefix}.solver", strategy.solver.signature)
        block(f"{prefix}.strategy", strategy.summary(), ok=True)


def render_execution_chain(
    executions: Iterable[Execution],
    assessment: Assessment | None = None,
) -> None:
    for index, execution in enumerate(executions, start=1):
        prefix = f"execution.strategy[{index}]"
        for name, value in strategy_chain(execution):
            block(
                f"{prefix}.{name}",
                _compact(value),
                ok=name == "execution" and execution.succeeded,
            )
        if assessment is not None:
            strategy_assessment = assessment_for_execution(assessment, execution)
            block(
                f"{prefix}.utility",
                strategy_assessment.to_dict(),
                ok=strategy_assessment.feasible,
            )


def render_strategy_utilities(
    executions: Iterable[Execution],
    assessment: Assessment,
) -> None:
    for index, execution in enumerate(executions, start=1):
        strategy_assessment = assessment_for_execution(assessment, execution)
        block(
            f"utility.strategy[{index}]",
            strategy_assessment.to_dict(),
            ok=strategy_assessment.feasible,
        )


def render_outcome_chain(
    recommendation: Recommendation,
    *,
    include_recommendation: bool = False,
) -> None:
    assessment = recommendation.assessment
    decision: Decision | None = recommendation.decision
    if assessment is None or decision is None:
        raise RuntimeError("Recommendation outcome is incomplete.")

    block("outcome.utility", assessment.to_dict(), ok=assessment.feasible)
    block("outcome.decision", decision.to_dict())
    if include_recommendation:
        block("outcome.recommendation", recommendation.to_dict(), ok=True)
