from optengine.analysis import Analysis
from optengine.engine import OptEngine


def analyze(engine: OptEngine) -> None:
    engine.log("Analysis started.")

    interpretation = engine.domain.interpret_input(engine.input_data)

    strategies = engine.registry.select(
        domain=engine.domain,
        interpretation=interpretation,
        requested=engine.requested_strategies,
    )

    engine.interpretation = interpretation
    engine.strategies = strategies

    engine.recommendation.input_summary = dict(interpretation.summary)

    engine.recommendation.analysis = Analysis(
        interpretation=dict(interpretation.summary),
        strategies=tuple(strategy.summary() for strategy in strategies),
    )

    engine.log("Analysis completed.")
