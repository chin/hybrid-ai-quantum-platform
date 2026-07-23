from __future__ import annotations

from optengine.engine import OptEngine
from optengine.trace import render_strategy_result, render_strategy_start


def evaluate(engine: OptEngine) -> None:
    """Execute every Strategy independently and retain every result."""

    if engine.analysis is None:
        raise RuntimeError("OptEngine has not been analyzed.")

    engine.log("Evaluation started.")
    strategies = engine.analysis.strategies
    total = len(strategies)
    for index, strategy in enumerate(strategies, start=1):
        if engine.render:
            render_strategy_start(
                strategy,
                index=index,
                total=total,
            )

        execution = strategy.execute()
        engine.executions.append(execution)
        engine.recommendation.executions.append(execution)

        if engine.render:
            render_strategy_result(
                execution,
                index=index,
                total=total,
            )

        if execution.failed and execution.failure is not None:
            engine.log(
                "Strategy failed: "
                f"{strategy.name}: {execution.failure.error_type}: "
                f"{execution.failure.message}"
            )
        else:
            engine.log(f"Strategy completed: {strategy.name}.")

    engine.log(
        "Evaluation completed: "
        f"{sum(execution.succeeded for execution in engine.executions)} "
        "succeeded, "
        f"{sum(execution.failed for execution in engine.executions)} failed."
    )
