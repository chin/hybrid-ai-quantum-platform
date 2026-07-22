from __future__ import annotations

import platform
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from optengine._version import __version__
from optengine.analysis import Analyzer
from optengine.catalog import Catalog
from optengine.cli import banner, block, footer
from optengine.domains.base import Domain
from optengine.engine import OptEngine
from optengine.explainers.base import Explainer
from optengine.policy.base import Policy
from optengine.recommendation import Recommendation
from optengine.stages import analyze, decide, evaluate, explain, write
from optengine.trace import (
    render_analysis_chain,
    render_execution_chain,
    render_outcome_chain,
    render_strategy_utilities,
)
from optengine.utility.base import Utility
from optengine.utility.operational import OperationalUtility
from optengine.writers.base import RecommendationWriter


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(
    domain: Domain,
    *,
    catalog: Catalog,
    policy: Policy,
    explainer: Explainer,
    writer: RecommendationWriter,
    utility: Utility | None = None,
    analyzer: Analyzer | None = None,
    requested_strategies: tuple[str, ...] | None = None,
    output_dir: Path = Path("outputs"),
    render: bool = False,
    title: str = "OptEngine :: Runtime",
    run_name: str = "run",
) -> Recommendation:
    """Run the invariant OptEngine collaboration pattern for one Domain."""

    if not isinstance(domain, Domain):
        raise TypeError("run() requires a populated Domain aggregate.")

    recommendation = Recommendation(
        run_id=str(uuid4()),
        domain_summary=dict(domain.summary),
        started_at=_utc_now(),
        provenance={
            "optengine_version": __version__,
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
    )
    engine = OptEngine(
        domain=domain,
        catalog=catalog,
        analyzer=analyzer or Analyzer(),
        utility=utility or OperationalUtility(),
        policy=policy,
        explainer=explainer,
        writer=writer,
        recommendation=recommendation,
        requested_strategies=requested_strategies,
        output_dir=output_dir,
        render=render,
        title=title,
        run_name=run_name,
    )

    if engine.render:
        banner(engine.title)
        block("domain", f"{domain.domain_type} :: {domain.name}")

    engine.started = True
    engine.log("OptEngine started.")

    analyze(engine)
    if engine.render:
        assert engine.analysis is not None
        block(
            "analysis",
            f"{len(engine.analysis.strategies)} compatible strategies",
            ok=True,
        )
        render_analysis_chain(engine.analysis)

    evaluate(engine)
    if engine.render:
        block(
            "evaluation",
            (
                f"{sum(item.succeeded for item in engine.executions)} complete / "
                f"{sum(item.failed for item in engine.executions)} failed"
            ),
            ok=any(item.succeeded for item in engine.executions),
        )
        render_execution_chain(engine.executions)

    decide(engine)
    if engine.render:
        assert engine.recommendation.assessment is not None
        render_strategy_utilities(
            engine.executions,
            engine.recommendation.assessment,
        )
        render_outcome_chain(engine.recommendation)
    explain(engine)

    decision = engine.recommendation.decision
    explanation = engine.recommendation.explanation
    if decision is None:
        raise RuntimeError("OptEngine completed without a Decision.")
    if explanation is None:
        raise RuntimeError("OptEngine completed without an Explanation.")

    if engine.render:
        block("decision", decision.action)
        block("reason", explanation.summary)

    engine.completed = True
    engine.recommendation.completed_at = _utc_now()
    engine.log("OptEngine finished.")
    output_path = write(engine)

    if engine.render:
        block("output", output_path)
        footer("Runtime Complete")

    return engine.recommendation
