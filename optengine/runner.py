from __future__ import annotations

from pathlib import Path
from uuid import uuid4

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
from optengine.writers.base import RecommendationWriter


def run(
    input_data: object,
    *,
    domain: Domain,
    registry: StrategyRegistry,
    policy: Policy,
    explainer: Explainer,
    writer: RecommendationWriter,
    requested_strategies: tuple[str, ...] | None = None,
    output_dir: Path = Path("outputs"),
    render: bool = False,
    title: str = "OptEngine :: Runtime",
    run_name: str = "run",
) -> Recommendation:
    recommendation = Recommendation(
        run_id=str(uuid4()),
    )

    engine = OptEngine(
        input_data=input_data,
        domain=domain,
        registry=registry,
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
        # Retain the existing public label until any CLI change
        # is made deliberately and its tests are updated.
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
    engine.log("OptEngine finished.")

    output_path = engine.writer.write(
        recommendation=engine.recommendation,
        output_dir=engine.output_dir,
        run_name=engine.run_name,
    )
    engine.recommendation.output_path = str(output_path)

    if engine.render:
        block("artifact", output_path)
        footer("Runtime Complete")

    return engine.recommendation
