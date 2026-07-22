from __future__ import annotations

from pathlib import Path

from optengine.analysis import Analyzer
from optengine.catalog import Catalog
from optengine.explainers.default import DefaultExplainer
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.runner import run
from optengine.trace import analysis_chain, outcome_chain, strategy_chain
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
        "> domain",
        "> analysis.domain",
        "> analysis.interpretation",
        "> analysis.objective",
        "> analysis.expression",
        "> analysis.curve",
        "> analysis.strategy[1].formulation",
        "> analysis.strategy[1].model",
        "> analysis.strategy[1].operation",
        "> analysis.strategy[1].solver",
        "> analysis.strategy[1].strategy",
        "> execution.strategy[1].execution",
        "> utility.strategy[1]",
        "> outcome.utility",
        "> outcome.decision",
        "> decision",
        "> reason",
        "> output",
    )
    positions = [output.index(marker) for marker in expected]
    assert positions == sorted(positions)
    assert "'status': 'complete'" in output
    assert (
        "'strategy': 'example:example-formulation:example-operation:reference'"
        in output
    )
