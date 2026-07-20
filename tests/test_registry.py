from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from optengine.domains.base import Domain
from optengine.errors import NoCompatibleStrategyError
from optengine.interpretation import Interpretation
from optengine.registry import StrategyFactory, StrategyRegistry
from optengine.strategy import Strategy


class StubDomain(Domain):
    name = "stub"

    def interpret_input(self, input_data: Any) -> Interpretation:
        return Interpretation(domain=self.name, summary={})

    def interpret_candidate(self, interpretation, candidate, strategy):
        raise NotImplementedError


def make_strategy(domain: Domain, name: str) -> Strategy:
    return Strategy(
        name=name,
        domain=domain,
        formulation=SimpleNamespace(name="formulation"),
        operation=SimpleNamespace(name="operation"),
        solver=SimpleNamespace(name="solver"),
    )


def test_register_and_select_strategy() -> None:
    domain = StubDomain()
    interpretation = Interpretation(domain="stub", summary={})
    registry = StrategyRegistry()
    registry.register(
        StrategyFactory(
            name="first",
            supports=lambda selected_domain, selected_interpretation: True,
            build=lambda selected_domain, selected_interpretation: make_strategy(
                selected_domain,
                "first",
            ),
        )
    )

    selected = registry.select(domain, interpretation, requested=("first",))

    assert [strategy.name for strategy in selected] == ["first"]


def test_duplicate_strategy_name_is_rejected() -> None:
    registry = StrategyRegistry()
    factory = StrategyFactory(
        name="duplicate",
        supports=lambda domain, interpretation: True,
        build=lambda domain, interpretation: make_strategy(
            domain,
            "duplicate",
        ),
    )
    registry.register(factory)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(factory)


def test_requested_order_is_preserved() -> None:
    domain = StubDomain()
    interpretation = Interpretation(domain="stub", summary={})
    registry = StrategyRegistry()

    for name in ("first", "second"):
        registry.register(
            StrategyFactory(
                name=name,
                supports=lambda selected_domain, selected_interpretation: True,
                build=lambda selected_domain, selected_interpretation, name=name: (
                    make_strategy(selected_domain, name)
                ),
            )
        )

    selected = registry.select(
        domain,
        interpretation,
        requested=("second", "first"),
    )

    assert [strategy.name for strategy in selected] == [
        "second",
        "first",
    ]


def test_unknown_requested_strategy_is_rejected() -> None:
    registry = StrategyRegistry()

    with pytest.raises(KeyError, match="Unknown strategy"):
        registry.select(
            StubDomain(),
            Interpretation(domain="stub", summary={}),
            requested=("missing",),
        )


def test_no_compatible_strategy_is_explicit_failure() -> None:
    registry = StrategyRegistry()
    registry.register(
        StrategyFactory(
            name="unsupported",
            supports=lambda domain, interpretation: False,
            build=lambda domain, interpretation: make_strategy(
                domain,
                "unsupported",
            ),
        )
    )

    with pytest.raises(NoCompatibleStrategyError):
        registry.select(
            StubDomain(),
            Interpretation(domain="stub", summary={}),
        )


def test_strategy_summary_records_modular_components() -> None:
    strategy = make_strategy(StubDomain(), "summary")

    summary = strategy.summary()

    assert summary.name == "summary"
    assert summary.domain == "stub"
    assert summary.formulation == "formulation"
    assert summary.operation == "operation"
    assert summary.solver == "solver"
