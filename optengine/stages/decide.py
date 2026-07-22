from __future__ import annotations

from optengine.engine import OptEngine


def decide(engine: OptEngine) -> None:
    """Assess all executions and apply Stop/Switch/Scale policy."""

    if engine.analysis is None:
        raise RuntimeError("OptEngine has no analysis.")

    engine.log("Decision started.")
    assessment = engine.utility.assess(
        engine.executions,
        engine.analysis,
    )
    engine.recommendation.assessment = assessment
    engine.recommendation.decision = engine.policy.apply(
        assessment=assessment,
        analysis=engine.analysis,
    )
    engine.log(f"Decision completed: {engine.recommendation.decision.action}.")
