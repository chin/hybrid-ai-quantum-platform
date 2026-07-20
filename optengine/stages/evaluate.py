from optengine.errors import IncompatibleStrategyError
from optengine.engine import OptEngine


def evaluate(engine: OptEngine) -> None:
    if engine.interpretation is None:
        raise RuntimeError("OptEngine has not been analyzed.")

    engine.log("Strategy evaluation started.")

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

        candidate = strategy.solver.execute(
            model=model,
            operation=strategy.operation,
            configuration=strategy.configuration,
            budget=strategy.budget,
        )

        evaluation = strategy.domain.interpret_candidate(
            interpretation=engine.interpretation,
            candidate=candidate,
            strategy=strategy,
        )

        engine.recommendation.evaluations.append(evaluation)

    engine.log("Strategy evaluation completed.")
