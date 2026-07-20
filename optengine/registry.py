from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from optengine.domains.base import Domain
from optengine.interpretation import Interpretation
from optengine.strategy import Strategy
from optengine.errors import NoCompatibleStrategyError

class StrategyBuilder(Protocol):
    def __call__(
        self,
        domain: Domain,
        interpretation: Interpretation,
    ) -> Strategy: ...


@dataclass(frozen=True)
class StrategyFactory:
    name: str
    supports: Callable[[Domain, Interpretation], bool]
    build: StrategyBuilder


class StrategyRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, StrategyFactory] = {}

    def register(self, factory: StrategyFactory) -> None:
        if factory.name in self._factories:
            raise ValueError(f"Strategy already registered: {factory.name}")
        self._factories[factory.name] = factory

    def select(
        self,
        domain: Domain,
        interpretation: Interpretation,
        requested: tuple[str, ...] | None = None,
    ) -> list[Strategy]:
        names = requested or tuple(self._factories)

        strategies: list[Strategy] = []

    
        for name in names:
            try:
                factory = self._factories[name]
            except KeyError as error:
                raise KeyError(f"Unknown strategy: {name}") from error

            if factory.supports(domain, interpretation):
                strategies.append(factory.build(domain, interpretation))

        if not strategies:
            raise NoCompatibleStrategyError(
                "No compatible strategy was selected."
            )
            
        return strategies
