from __future__ import annotations

import platform
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from optengine._version import __version__
from optengine.cli import banner, block, footer
from optengine.domains.base import Domain
from optengine.engine import OptEngine
from optengine.explainers.base import Explainer
from optengine.policy.base import Policy
from optengine.recommendation import Recommendation
from optengine.registry import StrategyRegistry
from optengine.stages.analyze import analyze
from optengine.stages.decide import decide
from optengine.stages.evaluate import evaluate
from optengine.stages.explain import explain
from optengine.utility.base import UtilityModel
from optengine.utility.operational import OperationalUtilityModel
from optengine.writers.base import RecommendationWriter


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(
    input_data: object,
    *,
    domain: Domain,
    registry: StrategyRegistry,
    policy: Policy,
    explainer: Explainer,
    writer: RecommendationWriter,
    utility_model: UtilityModel | None = None,
    requested_strategies: tuple[str, ...] | None = None,
    output_dir: Path = Path("outputs"),
    render: bool = False,
    title: str = "OptEngine :: Runtime",
    run_name: str = "run",
) -> Recommendation:
    recommendation = Recommendation(
        run_id=str(uuid4()),
        started_at=_utc_now(),
        provenance={
            "optengine_version": __version__,
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
    )

    engine = OptEngine(
        input_data=input_data,
        domain=domain,
        registry=registry,
        utility_model=(
            utility_model if utility_model is not None else OperationalUtilityModel()
        ),
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
        block("problem", str(engine.input_data))

    engine.started = True
    engine.log("OptEngine started.")

    analyze(engine)
    if engine.render:
        block("analysis", "complete", ok=True)

    evaluate(engine)
    if engine.render:
        block("evaluation", "complete", ok=True)

    decide(engine)
    explain(engine)

    decision = engine.recommendation.decision
    explanation = engine.recommendation.explanation
    if decision is None:
        raise RuntimeError("OptEngine completed without a decision.")
    if explanation is None:
        raise RuntimeError("OptEngine completed without an explanation.")

    if engine.render:
        block("decision", decision.action)
        block("reason", explanation.summary)

    engine.completed = True
    engine.recommendation.completed_at = _utc_now()
    engine.log("OptEngine finished.")

    output_path = engine.writer.write(
        recommendation=engine.recommendation,
        output_dir=engine.output_dir,
        run_name=engine.run_name,
    )

    if engine.render:
        block("artifact", output_path)
        footer("Runtime Complete")

    return engine.recommendation
