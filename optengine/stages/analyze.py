from __future__ import annotations

from optengine.engine import OptEngine


def analyze(engine: OptEngine) -> None:
    """Interpret the Domain and discover every compatible Strategy."""

    engine.log("Analysis started.")
    analysis = engine.analyzer.analyze(
        engine.domain,
        engine.catalog,
        requested=engine.requested_strategies,
    )
    engine.analysis = analysis
    engine.recommendation.domain_summary = dict(engine.domain.summary)
    engine.recommendation.analysis = analysis
    engine.log(f"Analysis completed: {len(analysis.strategies)} compatible strategies.")
