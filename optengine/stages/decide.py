from __future__ import annotations

from optengine.engine import OptEngine


def decide(engine: OptEngine) -> None:
    analysis = engine.recommendation.analysis
    if analysis is None:
        raise RuntimeError("OptEngine has no analysis.")

    engine.log("Decision started.")

    assessment = engine.utility_model.assess(
        evaluations=engine.recommendation.evaluations,
        analysis=analysis,
    )
    engine.recommendation.utility_assessment = assessment
    engine.recommendation.decision = engine.policy.apply(
        assessment=assessment,
        analysis=analysis,
    )

    engine.log(f"Decision completed: {engine.recommendation.decision.action}.")
