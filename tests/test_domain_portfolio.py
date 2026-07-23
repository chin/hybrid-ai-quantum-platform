from __future__ import annotations

from math import inf

import pytest

from optengine.domains.base import Domain
from optengine.domains.portfolio import Portfolio
from optengine.mathematics import ValueType
from tests.contracts import DomainContract


def make_portfolio(
    *,
    maximum_assets: int | None = 2,
) -> Portfolio:
    return Portfolio.from_mapping(
        {
            "name": "balanced",
            "assets": ["Growth", "Income"],
            "expected_returns": [0.12, 0.08],
            "covariance": [
                [0.04, 0.006],
                [0.006, 0.02],
            ],
            "allocation_increment": 0.5,
            "risk_aversion": 1.0,
            "budget": 1.0,
            "max_assets": maximum_assets,
        }
    )


def make_candidate(
    portfolio: Portfolio,
    *,
    growth: float = 0.5,
    income: float = 0.5,
    valid_choices: bool = True,
) -> Portfolio.Candidate:
    growth_asset, income_asset = portfolio.assets
    values = {
        growth_asset: growth,
        income_asset: income,
    }
    raw = {}
    for asset, amount in values.items():
        selected = int(round(amount / portfolio.parameters.allocation_increment))
        for units in range(portfolio.parameters.total_units + 1):
            raw[asset.choice_identifier(units)] = int(
                valid_choices and units == selected
            )
    return Portfolio.Candidate(
        _domain=portfolio,
        allocation=Portfolio.Allocation(values=values),
        raw_choices=raw,
        native_score=-0.07,
        strategy="contract",
    )


class TestPortfolioDomainContract(DomainContract):
    def make_domain(self) -> Domain:
        return make_portfolio()

    def make_candidate(self, domain: Domain):
        assert isinstance(domain, Portfolio)
        return make_candidate(domain)


def test_portfolio_object_collaboration_and_objective() -> None:
    portfolio = make_portfolio()
    growth, income = portfolio.assets
    assert portfolio.asset("Growth") is growth
    assert portfolio.covariance_value(growth, growth) == 0.04
    assert portfolio.covariance_value(growth, income) == 0.006
    assert portfolio.parameters.total_units == 2
    assert growth.choice_identifier(1) == "choice::Growth::1"
    assert growth.choice_variable(1).value_type is ValueType.BINARY
    assert portfolio.covariances[0].key == frozenset((growth, income))

    expression = portfolio.objective.expression
    assert expression.curve.input_count == 6
    assert expression.curve.degree == 2
    assert expression.curve.constraint_count == 4
    assert expression.curve.constrained
    assert set(expression.curve.input_types) == {ValueType.BINARY}

    candidate = make_candidate(portfolio)
    evaluation = portfolio.interpret(candidate)
    expected_return = 0.5 * 0.12 + 0.5 * 0.08
    risk = 0.5 * 0.04 * 0.5 + 0.5 * 0.006 * 0.5 + 0.5 * 0.006 * 0.5 + 0.5 * 0.02 * 0.5
    assert evaluation.expected_return == pytest.approx(expected_return)
    assert evaluation.risk == pytest.approx(risk)
    assert evaluation.utility == pytest.approx(expected_return - risk)
    assert evaluation.quality == evaluation.utility
    assert portfolio.objective.evaluate(candidate.allocation) == pytest.approx(
        evaluation.utility
    )
    assert evaluation.feasible
    assert evaluation.one_choice_feasible
    assert evaluation.budget_feasible
    assert evaluation.bounds_feasible
    assert evaluation.increment_feasible
    assert evaluation.cardinality_feasible
    assert candidate.to_dict()["allocation"] == {
        "Growth": 0.5,
        "Income": 0.5,
    }
    assert evaluation.to_dict()["metrics"]["active_assets"] == 2


def test_portfolio_evaluation_independent_failure_dimensions() -> None:
    portfolio = make_portfolio(maximum_assets=1)

    cardinality = portfolio.interpret(make_candidate(portfolio))
    assert not cardinality.cardinality_feasible
    assert not cardinality.feasible

    budget = portfolio.interpret(
        make_candidate(
            portfolio,
            growth=0.5,
            income=0.0,
        )
    )
    assert not budget.budget_feasible
    assert not budget.feasible

    bad_choices = portfolio.interpret(
        make_candidate(
            portfolio,
            valid_choices=False,
        )
    )
    assert not bad_choices.one_choice_feasible
    assert not bad_choices.feasible

    growth, income = portfolio.assets
    out_of_bounds = Portfolio.Candidate(
        _domain=portfolio,
        allocation=Portfolio.Allocation(values={growth: 1.1, income: -0.1}),
        raw_choices={},
        native_score=None,
        strategy="bounds",
    )
    evaluation = portfolio.interpret(out_of_bounds)
    assert not evaluation.bounds_feasible
    assert not evaluation.increment_feasible
    assert not evaluation.feasible


def test_portfolio_entity_and_parameter_validation() -> None:
    with pytest.raises(ValueError, match="name"):
        Portfolio.Asset(
            name=" ",
            expected_return=0.1,
            variance=0.1,
        )
    with pytest.raises(ValueError, match="finite"):
        Portfolio.Asset(
            name="A",
            expected_return=inf,
            variance=0.1,
        )
    with pytest.raises(ValueError, match="variance"):
        Portfolio.Asset(
            name="A",
            expected_return=0.1,
            variance=-0.1,
        )
    with pytest.raises(ValueError, match="bounds"):
        Portfolio.Asset(
            name="A",
            expected_return=0.1,
            variance=0.1,
            minimum_allocation=0.8,
            maximum_allocation=0.2,
        )

    a = Portfolio.Asset(
        name="A",
        expected_return=0.1,
        variance=0.1,
    )
    b = Portfolio.Asset(
        name="B",
        expected_return=0.1,
        variance=0.1,
    )
    with pytest.raises(ValueError, match="distinct"):
        Portfolio.Covariance(first=a, second=a, value=0.1)
    with pytest.raises(ValueError, match="finite"):
        Portfolio.Covariance(first=a, second=b, value=inf)

    invalid_parameters = [
        dict(risk_aversion=-1.0),
        dict(allocation_increment=0.0),
        dict(allocation_increment=1.1),
        dict(budget=0.0),
        dict(allocation_increment=0.3, budget=1.0),
        dict(maximum_assets=0),
    ]
    for values in invalid_parameters:
        with pytest.raises(ValueError):
            Portfolio.Parameters(**values)


def test_portfolio_aggregate_validation() -> None:
    a = Portfolio.Asset(
        name="A",
        expected_return=0.1,
        variance=0.1,
    )
    duplicate_name = Portfolio.Asset(
        name="A",
        expected_return=0.2,
        variance=0.2,
    )
    b = Portfolio.Asset(
        name="B",
        expected_return=0.1,
        variance=0.1,
    )
    covariance = Portfolio.Covariance(
        first=a,
        second=b,
        value=0.01,
    )

    with pytest.raises(ValueError, match="name"):
        Portfolio(
            name=" ",
            assets=(a,),
            covariances=(),
        )
    with pytest.raises(ValueError, match="at least one"):
        Portfolio(name="empty", assets=(), covariances=())
    with pytest.raises(ValueError, match="Assets must be unique"):
        Portfolio(
            name="duplicate",
            assets=(a, a),
            covariances=(),
        )
    with pytest.raises(ValueError, match="names must be unique"):
        Portfolio(
            name="duplicate-name",
            assets=(a, duplicate_name),
            covariances=(),
        )
    with pytest.raises(ValueError, match="relationships"):
        Portfolio(
            name="duplicate-covariance",
            assets=(a, b),
            covariances=(covariance, covariance),
        )
    outsider = Portfolio.Asset(
        name="outside",
        expected_return=0.1,
        variance=0.1,
    )
    with pytest.raises(ValueError, match="unknown Asset"):
        Portfolio(
            name="unknown",
            assets=(a, b),
            covariances=(
                Portfolio.Covariance(
                    first=a,
                    second=outsider,
                    value=0.0,
                ),
            ),
        )
    with pytest.raises(ValueError, match="cannot exceed"):
        Portfolio(
            name="cardinality",
            assets=(a, b),
            covariances=(),
            parameters=Portfolio.Parameters(maximum_assets=3),
        )
    constrained = Portfolio.Asset(
        name="constrained",
        expected_return=0.1,
        variance=0.1,
        maximum_allocation=0.25,
    )
    with pytest.raises(ValueError, match="cannot satisfy"):
        Portfolio(
            name="bounds",
            assets=(constrained,),
            covariances=(),
        )


def test_portfolio_mapping_validation_and_access_errors() -> None:
    base = {
        "assets": ["A", "B"],
        "expected_returns": [0.1, 0.2],
        "covariance": [[0.1, 0.01], [0.01, 0.2]],
    }
    portfolio = Portfolio.from_mapping(base, name="mapped")
    assert portfolio.name == "mapped"
    assert portfolio.summary["assets"][0]["name"] == "A"
    assert portfolio.covariance_map

    with pytest.raises(KeyError, match="Unknown"):
        portfolio.asset("missing")
    with pytest.raises(ValueError, match="Expected returns"):
        Portfolio.from_mapping({**base, "expected_returns": [0.1]})
    with pytest.raises(ValueError, match="dimensions"):
        Portfolio.from_mapping({**base, "covariance": [[0.1]]})
    with pytest.raises(ValueError, match="symmetric"):
        Portfolio.from_mapping(
            {
                **base,
                "covariance": [[0.1, 0.02], [0.01, 0.2]],
            }
        )
    with pytest.raises(ValueError, match="finite"):
        Portfolio.from_mapping(
            {
                **base,
                "covariance": [[0.1, inf], [inf, 0.2]],
            }
        )
    with pytest.raises(ValueError, match="allocations"):
        Portfolio.Allocation(values={portfolio.assets[0]: inf})
