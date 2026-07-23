from __future__ import annotations

from pathlib import Path

from optengine.catalog import Catalog
from optengine.domains.maxcut import MaxCut
from optengine.domains.portfolio import Portfolio
from optengine.execution import Complete, Execution
from optengine.explainers.default import DefaultExplainer
from optengine.formulations.base import Model
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.runner import run
from optengine.strategy import Strategy
from optengine.trace import execution_result, expression_formula
from optengine.writers.json import JsonRecommendationWriter
from tests.support import ExampleFormulation, ExampleOperation, ExampleSolver


def _triangle() -> MaxCut:
    first = MaxCut.Vertex(identifier="A")
    second = MaxCut.Vertex(identifier="B")
    third = MaxCut.Vertex(identifier="C")
    return MaxCut(
        name="triangle",
        graph=MaxCut.Graph(
            vertices=(first, second, third),
            edges=(
                MaxCut.Edge(first=first, second=second),
                MaxCut.Edge(first=second, second=third),
                MaxCut.Edge(first=first, second=third),
            ),
        ),
        parameters=MaxCut.Parameters(target_cut_value=2.0),
    )


def _portfolio() -> Portfolio:
    return Portfolio.from_mapping(
        {
            "name": "balanced",
            "assets": ["Growth", "Income"],
            "expected_returns": [0.12, 0.08],
            "covariance": [[0.04, 0.006], [0.006, 0.02]],
            "allocation_increment": 0.5,
            "risk_aversion": 1.0,
            "budget": 1.0,
            "max_assets": 2,
        }
    )


def test_maxcut_runtime_is_domain_specific_and_human_readable(
    tmp_path: Path,
    capsys,
) -> None:
    domain = _triangle()
    catalog = Catalog(
        formulations=(ExampleFormulation(),),
        operations=(ExampleOperation(limit=5),),
        solvers=(
            ExampleSolver(
                name="reference",
                values={"A": 1, "B": 0, "C": 0},
                reference_flag=True,
            ),
        ),
    )

    run(
        domain,
        catalog=catalog,
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        output_dir=tmp_path,
        render=True,
    )

    output = capsys.readouterr().out
    assert "Max-Cut :: triangle" in output
    assert "3 vertices • 3 edges • unweighted • target ≥ 2" in output
    assert "maximize the weight of edges crossing the two" in output
    assert "2·A + 2·B + 2·C − 2·A·B − 2·B·C − 2·A·C" in output
    assert "… Running Reference ..." in output
    assert "cut value 2 • 2 crossing edges • feasible" in output
    assert "side 1 [A] • side 0 [B, C]" in output
    assert "{'domain_type':" not in output


def test_portfolio_result_reports_allocation_return_risk_and_utility() -> None:
    domain = _portfolio()
    growth, income = domain.assets
    formulation = ExampleFormulation()
    model = Model(
        formulation=formulation,
        objective=domain.objective,
        payload={},
        curve=domain.objective.curve,
    )
    operation = ExampleOperation(limit=20)
    solver = ExampleSolver(name="portfolio-reference", reference_flag=True)
    strategy = Strategy(
        domain=domain,
        formulation=formulation,
        model=model,
        operation=operation,
        solver=solver,
    )
    raw_choices = {
        asset.choice_identifier(units): int(units == 1)
        for asset in domain.assets
        for units in range(domain.parameters.total_units + 1)
    }
    candidate = Portfolio.Candidate(
        _domain=domain,
        allocation=Portfolio.Allocation(values={growth: 0.5, income: 0.5}),
        raw_choices=raw_choices,
        native_score=-0.07,
        strategy=strategy.name,
    )
    evaluation = domain.interpret(candidate)
    execution = Execution(
        strategy=strategy,
        state=Complete(),
        candidate=candidate,
        evaluation=evaluation,
        runtime_s=0.001,
    )

    summary, allocation = execution_result(execution)
    assert summary.startswith("utility 0.082")
    assert "return 0.1" in summary
    assert "risk 0.018" in summary
    assert summary.endswith("feasible")
    assert allocation == "Growth 50.0% • Income 50.0%"


def test_expression_renderer_truncates_large_polynomials_with_term_count() -> None:
    expression = _portfolio().objective.expression
    rendered = expression_formula(expression, maximum_terms=4)
    assert "more terms" in rendered
    assert len(rendered) < 180
