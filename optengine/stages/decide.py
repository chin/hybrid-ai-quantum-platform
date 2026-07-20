from optengine.engine import OptEngine


def decide(engine: OptEngine) -> None:
    analysis = engine.recommendation.analysis

    if analysis is None:
        raise RuntimeError("OptEngine has no analysis.")

    engine.log("Decision started.")

    engine.recommendation.decision = engine.policy.apply(
        evaluations=engine.recommendation.evaluations,
        analysis=analysis,
    )

    engine.log(f"Decision completed: {engine.recommendation.decision.action}.")
