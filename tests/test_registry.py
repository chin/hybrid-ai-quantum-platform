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


def test_requested_strategy_order_is_preserved() -> None:
    domain = StubDomain()
    interpretation = domain.interpret_input({})
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

    assert [item.name for item in selected] == [
        "second",
        "first",
    ]


def test_no_compatible_strategy_is_explicit() -> None:
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
