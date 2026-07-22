from __future__ import annotations

from optengine.engine import OptEngine


def explain(engine: OptEngine) -> None:
    """Explain the Assessment-backed Decision."""

    analysis = engine.analysis
    assessment = engine.recommendation.assessment
    decision = engine.recommendation.decision
    if analysis is None or assessment is None or decision is None:
        raise RuntimeError(
            "OptEngine requires analysis, assessment, and decision before explanation."
        )

    engine.log("Explanation started.")
    engine.recommendation.explanation = engine.explainer.explain(
        decision=decision,
        executions=engine.executions,
        assessment=assessment,
        analysis=analysis,
    )
    engine.log("Explanation completed.")
