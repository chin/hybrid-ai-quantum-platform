from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from typing import Any, ClassVar, Mapping

from optengine.candidate import Candidate as BaseCandidate
from optengine.domains.base import Domain
from optengine.evaluation import Evaluation as BaseEvaluation
from optengine.interpretation import Interpretation as BaseInterpretation
from optengine.mathematics import (
    Constraint,
    Expression,
    LinearTerm,
    QuadraticTerm,
    ValueType,
    Variable,
)
from optengine.objective import Objective as BaseObjective


@dataclass(frozen=True, kw_only=True)
class Portfolio(Domain):
    """Bounded discrete portfolio Domain aggregate."""

    domain_type: ClassVar[str] = "portfolio"
    tolerance: ClassVar[float] = 1e-9

    @dataclass(frozen=True, kw_only=True)
    class Asset:
        name: str
        expected_return: float
        variance: float
        minimum_allocation: float = 0.0
        maximum_allocation: float = 1.0

        def __post_init__(self) -> None:
            if not self.name.strip():
                raise ValueError("Asset name cannot be empty.")
            values = (
                self.expected_return,
                self.variance,
                self.minimum_allocation,
                self.maximum_allocation,
            )
            if not all(isfinite(float(value)) for value in values):
                raise ValueError("Asset numeric values must be finite.")
            if self.variance < 0.0:
                raise ValueError("Asset variance cannot be negative.")
            if not (0.0 <= self.minimum_allocation <= self.maximum_allocation <= 1.0):
                raise ValueError("Asset allocation bounds are invalid.")

        def choice_identifier(self, units: int) -> str:
            return f"choice::{self.name}::{units}"

        def choice_variable(self, units: int) -> Variable:
            return Variable(
                identifier=self.choice_identifier(units),
                value_type=ValueType.BINARY,
                lower_bound=0,
                upper_bound=1,
            )

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "name": self.name,
                "expected_return": float(self.expected_return),
                "variance": float(self.variance),
                "minimum_allocation": float(self.minimum_allocation),
                "maximum_allocation": float(self.maximum_allocation),
            }

    @dataclass(frozen=True, kw_only=True)
    class Covariance:
        first: Portfolio.Asset
        second: Portfolio.Asset
        value: float

        def __post_init__(self) -> None:
            if self.first == self.second:
                raise ValueError(
                    "An Asset owns its variance; Covariance relates distinct assets."
                )
            if not isfinite(float(self.value)):
                raise ValueError("Covariance must be finite.")

        @property
        def key(self) -> frozenset[Portfolio.Asset]:
            return frozenset((self.first, self.second))

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "first": self.first.name,
                "second": self.second.name,
                "value": float(self.value),
            }

    @dataclass(frozen=True, kw_only=True)
    class Parameters:
        risk_aversion: float = 0.5
        allocation_increment: float = 0.25
        budget: float = 1.0
        maximum_assets: int | None = None

        def __post_init__(self) -> None:
            values = (
                self.risk_aversion,
                self.allocation_increment,
                self.budget,
            )
            if not all(isfinite(float(value)) for value in values):
                raise ValueError("Portfolio parameters must be finite.")
            if self.risk_aversion < 0.0:
                raise ValueError("risk_aversion must be non-negative.")
            if not 0.0 < self.allocation_increment <= 1.0:
                raise ValueError("allocation_increment must be in (0, 1].")
            if self.budget <= 0.0:
                raise ValueError("budget must be positive.")
            units = self.budget / self.allocation_increment
            if abs(units - round(units)) > Portfolio.tolerance:
                raise ValueError("allocation_increment must divide the budget exactly.")
            if self.maximum_assets is not None and self.maximum_assets <= 0:
                raise ValueError("maximum_assets must be positive.")

        @property
        def total_units(self) -> int:
            return int(round(self.budget / self.allocation_increment))

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "risk_aversion": float(self.risk_aversion),
                "allocation_increment": float(self.allocation_increment),
                "budget": float(self.budget),
                "maximum_assets": self.maximum_assets,
                "total_units": self.total_units,
            }

    @dataclass(frozen=True, kw_only=True)
    class Objective(BaseObjective):
        domain: Portfolio
        sense: ClassVar[str] = "maximize"

        def choice_variable(
            self,
            asset: Portfolio.Asset,
            units: int,
        ) -> Variable:
            return asset.choice_variable(units)

        @property
        def expression(self) -> Expression:
            total_units = self.domain.parameters.total_units
            increment = self.domain.parameters.allocation_increment
            variables = tuple(
                self.choice_variable(asset, units)
                for asset in self.domain.assets
                for units in range(total_units + 1)
            )

            linear_terms: list[LinearTerm] = []
            for asset in self.domain.assets:
                for units in range(total_units + 1):
                    amount = units * increment
                    linear_terms.append(
                        LinearTerm(
                            variable=self.choice_variable(asset, units),
                            coefficient=float(asset.expected_return) * amount,
                        )
                    )

            quadratic_terms: list[QuadraticTerm] = []
            risk_aversion = self.domain.parameters.risk_aversion
            if risk_aversion:
                for first in self.domain.assets:
                    for second in self.domain.assets:
                        covariance = self.domain.covariance_value(first, second)
                        if covariance == 0.0:
                            continue
                        for first_units in range(total_units + 1):
                            first_amount = first_units * increment
                            if first_amount == 0.0:
                                continue
                            for second_units in range(total_units + 1):
                                second_amount = second_units * increment
                                coefficient = (
                                    -risk_aversion
                                    * covariance
                                    * first_amount
                                    * second_amount
                                )
                                if coefficient == 0.0:
                                    continue
                                quadratic_terms.append(
                                    QuadraticTerm(
                                        first=self.choice_variable(
                                            first,
                                            first_units,
                                        ),
                                        second=self.choice_variable(
                                            second,
                                            second_units,
                                        ),
                                        coefficient=coefficient,
                                    )
                                )

            constraints: list[Constraint] = []
            for asset in self.domain.assets:
                constraints.append(
                    Constraint(
                        name=f"one-allocation::{asset.name}",
                        relation="eq",
                        bound=1.0,
                        linear_terms=tuple(
                            LinearTerm(
                                variable=self.choice_variable(asset, units),
                                coefficient=1.0,
                            )
                            for units in range(total_units + 1)
                        ),
                    )
                )

            constraints.append(
                Constraint(
                    name="full-allocation",
                    relation="eq",
                    bound=float(total_units),
                    linear_terms=tuple(
                        LinearTerm(
                            variable=self.choice_variable(asset, units),
                            coefficient=float(units),
                        )
                        for asset in self.domain.assets
                        for units in range(total_units + 1)
                    ),
                )
            )

            if self.domain.parameters.maximum_assets is not None:
                constraints.append(
                    Constraint(
                        name="maximum-cardinality",
                        relation="le",
                        bound=float(self.domain.parameters.maximum_assets),
                        linear_terms=tuple(
                            LinearTerm(
                                variable=self.choice_variable(asset, units),
                                coefficient=1.0,
                            )
                            for asset in self.domain.assets
                            for units in range(1, total_units + 1)
                        ),
                    )
                )

            return Expression(
                variables=variables,
                linear_terms=tuple(linear_terms),
                quadratic_terms=tuple(quadratic_terms),
                constraints=tuple(constraints),
            )

        def evaluate(self, allocation: Portfolio.Allocation) -> float:
            return allocation.expected_return(self.domain) - (
                self.domain.parameters.risk_aversion * allocation.risk(self.domain)
            )

        def decode(
            self,
            values: Mapping[Any, Any],
            *,
            result: Any,
            strategy: Any,
        ) -> BaseCandidate:
            total_units = self.domain.parameters.total_units
            raw_choices: dict[str, int] = {}
            selected_units: dict[Portfolio.Asset, int] = {}

            for asset in self.domain.assets:
                choices = {
                    units: int(
                        round(
                            float(
                                values.get(
                                    self.choice_variable(
                                        asset,
                                        units,
                                    ).identifier,
                                    0,
                                )
                            )
                        )
                    )
                    for units in range(total_units + 1)
                }
                raw_choices.update(
                    {
                        asset.choice_identifier(units): value
                        for units, value in choices.items()
                    }
                )
                selected = [units for units, chosen in choices.items() if chosen == 1]
                selected_units[asset] = selected[0] if selected else 0

            allocation = Portfolio.Allocation(
                values={
                    asset: (
                        selected_units[asset]
                        * self.domain.parameters.allocation_increment
                    )
                    for asset in self.domain.assets
                }
            )
            return Portfolio.Candidate(
                _domain=self.domain,
                allocation=allocation,
                raw_choices=raw_choices,
                native_score=result.native_score,
                strategy=strategy.name,
            )

    @dataclass(frozen=True, kw_only=True)
    class Interpretation(BaseInterpretation):
        domain: Portfolio
        objective: Portfolio.Objective

    @dataclass(frozen=True, kw_only=True)
    class Allocation:
        values: Mapping[Portfolio.Asset, float]

        def __post_init__(self) -> None:
            normalized = {asset: float(value) for asset, value in self.values.items()}
            if not all(isfinite(value) for value in normalized.values()):
                raise ValueError("Portfolio allocations must be finite.")
            object.__setattr__(self, "values", normalized)

        def amount_for(self, asset: Portfolio.Asset) -> float:
            return float(self.values.get(asset, 0.0))

        @property
        def total(self) -> float:
            return sum(self.values.values())

        @property
        def active_assets(self) -> int:
            return sum(value > Portfolio.tolerance for value in self.values.values())

        def expected_return(self, portfolio: Portfolio) -> float:
            return sum(
                self.amount_for(asset) * float(asset.expected_return)
                for asset in portfolio.assets
            )

        def risk(self, portfolio: Portfolio) -> float:
            return sum(
                self.amount_for(first)
                * portfolio.covariance_value(first, second)
                * self.amount_for(second)
                for first in portfolio.assets
                for second in portfolio.assets
            )

        def to_dict(self) -> Mapping[str, float]:
            return {asset.name: float(value) for asset, value in self.values.items()}

    @dataclass(frozen=True, kw_only=True)
    class Candidate(BaseCandidate):
        _domain: Portfolio = field(repr=False)
        allocation: Portfolio.Allocation
        raw_choices: Mapping[str, int]
        native_score: float | None
        strategy: str

        @property
        def domain(self) -> Portfolio:
            return self._domain

        def _interpret_in(self, domain: Domain) -> BaseEvaluation:
            if domain is not self._domain:
                raise ValueError(
                    "A Portfolio Candidate must be interpreted by its owning Domain."
                )
            return Portfolio.Evaluation(candidate=self)

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "domain_type": self.domain.domain_type,
                "strategy": self.strategy,
                "allocation": self.allocation.to_dict(),
                "raw_choices": dict(self.raw_choices),
                "native_score": self.native_score,
            }

    @dataclass(frozen=True, kw_only=True)
    class Evaluation(BaseEvaluation):
        candidate: Portfolio.Candidate

        @property
        def domain(self) -> Portfolio:
            return self.candidate.domain

        @property
        def one_choice_feasible(self) -> bool:
            total_units = self.domain.parameters.total_units
            return all(
                sum(
                    int(
                        self.candidate.raw_choices.get(
                            asset.choice_identifier(units),
                            0,
                        )
                    )
                    for units in range(total_units + 1)
                )
                == 1
                for asset in self.domain.assets
            )

        @property
        def budget_feasible(self) -> bool:
            return (
                abs(self.candidate.allocation.total - self.domain.parameters.budget)
                <= self.domain.tolerance
            )

        @property
        def bounds_feasible(self) -> bool:
            return all(
                (
                    asset.minimum_allocation - self.domain.tolerance
                    <= self.candidate.allocation.amount_for(asset)
                    <= asset.maximum_allocation + self.domain.tolerance
                )
                for asset in self.domain.assets
            )

        @property
        def increment_feasible(self) -> bool:
            increment = self.domain.parameters.allocation_increment
            return all(
                abs(
                    (self.candidate.allocation.amount_for(asset) / increment)
                    - round(self.candidate.allocation.amount_for(asset) / increment)
                )
                <= self.domain.tolerance
                for asset in self.domain.assets
            )

        @property
        def cardinality_feasible(self) -> bool:
            maximum = self.domain.parameters.maximum_assets
            return maximum is None or self.candidate.allocation.active_assets <= maximum

        @property
        def feasible(self) -> bool:
            return all(
                (
                    self.one_choice_feasible,
                    self.budget_feasible,
                    self.bounds_feasible,
                    self.increment_feasible,
                    self.cardinality_feasible,
                )
            )

        @property
        def expected_return(self) -> float:
            return self.candidate.allocation.expected_return(self.domain)

        @property
        def risk(self) -> float:
            return self.candidate.allocation.risk(self.domain)

        @property
        def utility(self) -> float:
            return self.domain.objective.evaluate(self.candidate.allocation)

        @property
        def quality(self) -> float:
            return self.utility

        @property
        def metrics(self) -> Mapping[str, Any]:
            return {
                "allocations": self.candidate.allocation.to_dict(),
                "expected_return": self.expected_return,
                "risk": self.risk,
                "utility": self.utility,
                "total_allocation": self.candidate.allocation.total,
                "active_assets": self.candidate.allocation.active_assets,
                "one_choice_feasible": self.one_choice_feasible,
                "budget_feasible": self.budget_feasible,
                "bounds_feasible": self.bounds_feasible,
                "increment_feasible": self.increment_feasible,
                "cardinality_feasible": self.cardinality_feasible,
            }

        @property
        def utility_inputs(self) -> Mapping[str, Any]:
            return {
                "feasible": self.feasible,
                "quality": self.quality,
                "utility": self.utility,
            }

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "domain_type": self.domain.domain_type,
                "strategy": self.candidate.strategy,
                "state": self.state.code,
                "feasible": self.feasible,
                "quality": self.quality,
                "metrics": dict(self.metrics),
                "candidate": self.candidate.to_dict(),
                "utility_inputs": dict(self.utility_inputs),
            }

    name: str
    assets: tuple[Asset, ...]
    covariances: tuple[Covariance, ...]
    parameters: Parameters = field(default_factory=Parameters)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Portfolio name cannot be empty.")
        if not self.assets:
            raise ValueError("Portfolio requires at least one Asset.")
        if len(set(self.assets)) != len(self.assets):
            raise ValueError("Portfolio Assets must be unique.")
        names = tuple(asset.name for asset in self.assets)
        if len(set(names)) != len(names):
            raise ValueError("Portfolio Asset names must be unique.")
        if len({covariance.key for covariance in self.covariances}) != len(
            self.covariances
        ):
            raise ValueError("Portfolio Covariance relationships must be unique.")
        known = set(self.assets)
        for covariance in self.covariances:
            if covariance.first not in known or covariance.second not in known:
                raise ValueError("Portfolio Covariance references an unknown Asset.")
        if (
            self.parameters.maximum_assets is not None
            and self.parameters.maximum_assets > len(self.assets)
        ):
            raise ValueError("maximum_assets cannot exceed the number of Assets.")
        minimum = sum(asset.minimum_allocation for asset in self.assets)
        maximum = sum(asset.maximum_allocation for asset in self.assets)
        if (
            minimum > self.parameters.budget + self.tolerance
            or maximum < self.parameters.budget - self.tolerance
        ):
            raise ValueError("Portfolio allocation bounds cannot satisfy the budget.")

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, Any],
        *,
        name: str | None = None,
    ) -> Portfolio:
        names = tuple(str(item) for item in value["assets"])
        expected_returns = tuple(float(item) for item in value["expected_returns"])
        covariance_matrix = tuple(
            tuple(float(item) for item in row) for row in value["covariance"]
        )
        if len(expected_returns) != len(names):
            raise ValueError("Expected returns must align with Assets.")
        if len(covariance_matrix) != len(names) or any(
            len(row) != len(names) for row in covariance_matrix
        ):
            raise ValueError("Covariance matrix dimensions must align with Assets.")
        for row, values in enumerate(covariance_matrix):
            for column, item in enumerate(values):
                if not isfinite(item):
                    raise ValueError("Covariance values must be finite.")
                if abs(item - covariance_matrix[column][row]) > cls.tolerance:
                    raise ValueError("Covariance matrix must be symmetric.")

        assets = tuple(
            cls.Asset(
                name=asset_name,
                expected_return=expected_returns[index],
                variance=covariance_matrix[index][index],
            )
            for index, asset_name in enumerate(names)
        )
        covariances = tuple(
            cls.Covariance(
                first=assets[first],
                second=assets[second],
                value=covariance_matrix[first][second],
            )
            for first in range(len(assets))
            for second in range(first + 1, len(assets))
        )
        parameters = cls.Parameters(
            risk_aversion=float(value.get("risk_aversion", 0.5)),
            allocation_increment=float(value.get("allocation_increment", 0.25)),
            budget=float(value.get("budget", 1.0)),
            maximum_assets=(
                None if value.get("max_assets") is None else int(value["max_assets"])
            ),
        )
        return cls(
            name=name or str(value.get("name", "portfolio")),
            assets=assets,
            covariances=covariances,
            parameters=parameters,
        )

    @property
    def asset_map(self) -> Mapping[str, Asset]:
        return {asset.name: asset for asset in self.assets}

    @property
    def covariance_map(self) -> Mapping[frozenset[Asset], float]:
        return {
            covariance.key: float(covariance.value) for covariance in self.covariances
        }

    def asset(self, name: str) -> Asset:
        try:
            return self.asset_map[name]
        except KeyError as error:
            raise KeyError(f"Unknown Portfolio Asset: {name!r}") from error

    def covariance_value(
        self,
        first: Asset,
        second: Asset,
    ) -> float:
        if first == second:
            return float(first.variance)
        return self.covariance_map.get(
            frozenset((first, second)),
            0.0,
        )

    @property
    def objective(self) -> Objective:
        return self.Objective(domain=self)

    @property
    def summary(self) -> Mapping[str, Any]:
        return {
            "name": self.name,
            "domain_type": self.domain_type,
            "assets": [asset.to_dict() for asset in self.assets],
            "covariances": [covariance.to_dict() for covariance in self.covariances],
            "parameters": self.parameters.to_dict(),
        }

    def _interpret_in(self, domain: Domain) -> Interpretation:
        if domain is not self:
            raise ValueError("A Portfolio aggregate must be interpreted by itself.")
        return self.Interpretation(
            domain=self,
            objective=self.objective,
            summary=self.summary,
        )


# Transitional aliases. New code should use Portfolio.
PortfolioDomain = Portfolio
