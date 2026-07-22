from __future__ import annotations

from optengine.engine import OptEngine


def evaluate(engine: OptEngine) -> None:
    """Execute every Strategy independently and retain every result."""

    if engine.analysis is None:
        raise RuntimeError("OptEngine has not been analyzed.")

    engine.log("Evaluation started.")
    for strategy in engine.analysis.strategies:
        execution = strategy.execute()
        engine.executions.append(execution)
        engine.recommendation.executions.append(execution)
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
