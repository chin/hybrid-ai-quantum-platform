from optengine.engine import OptEngine


def explain(engine: OptEngine) -> None:
    analysis = engine.recommendation.analysis
    decision = engine.recommendation.decision

    if analysis is None or decision is None:
        raise RuntimeError(
            "OptEngine requires analysis and decision before explanation."
        )

    engine.recommendation.explanation = engine.explainer.explain(
        decision=decision,
        evaluations=engine.recommendation.evaluations,
        analysis=analysis,
    )
