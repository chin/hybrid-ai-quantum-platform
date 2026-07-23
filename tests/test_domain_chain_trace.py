from __future__ import annotations

from pathlib import Path

from optengine.analysis import Analyzer
from optengine.catalog import Catalog
from optengine.explainers.default import DefaultExplainer
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.runner import run
from optengine.trace import (
    analysis_chain,
    full_strategy_chain,
    outcome_chain,
    strategy_chain,
)
from optengine.writers.json import JsonRecommendationWriter
from tests.support import (
    ExampleDomain,
    ExampleFormulation,
    ExampleOperation,
    ExampleSolver,
)


def _catalog() -> Catalog:
    return Catalog(
        formulations=(ExampleFormulation(),),
        operations=(ExampleOperation(limit=2),),
        solvers=(ExampleSolver(name="reference", reference_flag=True),),
    )


def test_complete_domain_chain_is_structurally_exposed(tmp_path: Path) -> None:
    recommendation = run(
        ExampleDomain(name="chain"),
        catalog=_catalog(),
        analyzer=Analyzer(),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        output_dir=tmp_path,
    )
    assert recommendation.analysis is not None
    assert recommendation.assessment is not None
    assert recommendation.decision is not None

    assert tuple(name for name, _ in analysis_chain(recommendation.analysis)) == (
        "domain",
        "interpretation",
        "objective",
        "expression",
        "curve",
    )
    assert tuple(name for name, _ in strategy_chain(recommendation.executions[0])) == (
        "formulation",
        "model",
        "operation",
        "solver",
        "strategy",
        "execution",
    )
    assert tuple(name for name, _ in outcome_chain(recommendation)) == (
        "utility",
        "decision",
        "recommendation",
    )
    assert tuple(
        name
        for name, _ in full_strategy_chain(
            recommendation.analysis,
            recommendation.executions[0],
            recommendation.assessment,
        )
    ) == (
        "domain",
        "interpretation",
        "objective",
        "expression",
        "curve",
        "formulation",
        "model",
        "operation",
        "solver",
        "strategy",
        "execution",
        "utility",
    )


def test_rendered_runtime_shows_full_chain_and_strategy_results(
    tmp_path: Path,
    capsys,
) -> None:
    run(
        ExampleDomain(name="chain"),
        catalog=_catalog(),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        output_dir=tmp_path,
        render=True,
    )
    output = capsys.readouterr().out
    expected = (
        "Problem",
        "  Domain          Example :: chain",
        "  Interpretation  ExampleDomain → Objective",
        "  Objective       maximize Objective",
        "  Expression      x + 2·y",
        "  Curve           2 binary inputs → real • linear • unconstrained",
        "Strategy plan (1)",
        "Strategy 1/1",
        "  Formulation     Example Formulation",
        "  Operation       Example Operation",
        "  Solver          Reference • reference",
        "  … Running Reference ...",
        "  ✓ Execution complete — quality 3 • feasible",
        "    Candidate       x=1 • y=1",
        "Utility ranking",
        "Recommendation",
        "  Decision        STOP",
        "Artifact",
        "  Output",
    )
    positions = [output.index(marker) for marker in expected]
    assert positions == sorted(positions)
    strategy_start = output.index("Strategy 1/1")
    assert (
        output.index(
            "  Model           2 binary inputs → real • linear • unconstrained",
            strategy_start,
        )
        > strategy_start
    )
    assert "{'status': 'complete'" not in output
    assert "'strategy':" not in output
