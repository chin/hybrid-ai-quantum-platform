from __future__ import annotations

from typing import Any

from optengine.engine import OptEngine
from optengine.errors import IncompatibleStrategyError


def _decode_candidate(model: Any, candidate: Any) -> Any:
    sample = candidate.values.get("sample")
    if sample is None:
        return candidate

    decoded = model.decode(sample)
    values = dict(candidate.values)
    values["sample"] = decoded
    return candidate.with_values(values)


def evaluate(engine: OptEngine) -> None:
    if engine.interpretation is None:
        raise RuntimeError("OptEngine has not been analyzed.")

    engine.log("Evaluation started.")

    for strategy in engine.strategies:
        model = strategy.formulation.build(
            interpretation=engine.interpretation,
            configuration=strategy.configuration,
        )

        if not strategy.solver.supports(
            model=model,
            operation=strategy.operation,
        ):
            raise IncompatibleStrategyError(
                strategy=strategy.name,
                formulation=strategy.formulation.name,
                operation=strategy.operation.name,
                solver=strategy.solver.name,
            )

        try:
            candidate = strategy.solver.execute(
                model=model,
                operation=strategy.operation,
                configuration=strategy.configuration,
                budget=strategy.budget,
            )
            candidate = candidate.assigned_to(strategy.name)
            candidate = _decode_candidate(model, candidate)

            evaluation = strategy.domain.interpret_candidate(
                interpretation=engine.interpretation,
                candidate=candidate,
                strategy=strategy,
            )
            engine.recommendation.evaluations.append(evaluation)
        except Exception as error:
            failure = {
                "strategy": strategy.name,
                "error_type": type(error).__name__,
                "message": str(error),
            }
            engine.recommendation.failures.append(failure)
            engine.log(f"Strategy failed: {strategy.name}: {error}")

    engine.log("Evaluation completed.")
