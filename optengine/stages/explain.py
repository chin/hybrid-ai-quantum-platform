from __future__ import annotations

from optengine.engine import OptEngine


def explain(engine: OptEngine) -> None:
    analysis = engine.recommendation.analysis
    assessment = engine.recommendation.utility_assessment
    decision = engine.recommendation.decision

    if analysis is None or assessment is None or decision is None:
        raise RuntimeError(
            "OptEngine requires analysis, utility, and decision before explanation."
        )

    engine.recommendation.explanation = engine.explainer.explain(
        decision=decision,
        evaluations=engine.recommendation.evaluations,
        assessment=assessment,
        analysis=analysis,
    )
