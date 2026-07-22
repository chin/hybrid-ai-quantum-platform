from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Mapping

from optengine.candidate import Candidate as BaseCandidate
from optengine.domains.base import Domain
from optengine.evaluation import Evaluation as BaseEvaluation
from optengine.interpretation import Interpretation
from optengine.mathematics import (
    Expression,
    LinearTerm,
    ValueType,
    Variable,
)
from optengine.objective import Objective as BaseObjective


@dataclass(frozen=True, kw_only=True)
class ExampleDomain(Domain):
    """Replace with the concrete aggregate for a new problem domain."""

    domain_type: ClassVar[str] = "example"

    @dataclass(frozen=True, kw_only=True)
    class Entity:
        name: str
        value: float

        @property
        def variable(self) -> Variable:
            return Variable(
                identifier=self.name,
                value_type=ValueType.BINARY,
                lower_bound=0,
                upper_bound=1,
            )

    @dataclass(frozen=True, kw_only=True)
    class Relationship:
        first: ExampleDomain.Entity
        second: ExampleDomain.Entity
        weight: float

    @dataclass(frozen=True, kw_only=True)
    class Parameters:
        threshold: float = 0.0

    @dataclass(frozen=True, kw_only=True)
    class Objective(BaseObjective):
        domain: ExampleDomain
        sense: ClassVar[str] = "maximize"

        @property
        def expression(self) -> Expression:
            return Expression(
                variables=tuple(entity.variable for entity in self.domain.entities),
                linear_terms=tuple(
                    LinearTerm(
                        variable=entity.variable,
                        coefficient=entity.value,
                    )
                    for entity in self.domain.entities
                ),
            )

        def decode(
            self,
            values: Mapping[Any, Any],
            *,
            result: Any,
            strategy: Any,
        ) -> BaseCandidate:
            return ExampleDomain.Candidate(
                _domain=self.domain,
                selected=tuple(
                    entity
                    for entity in self.domain.entities
                    if int(round(float(values.get(entity.name, 0)))) == 1
                ),
                native_score=result.native_score,
                strategy=strategy.name,
            )

    @dataclass(frozen=True, kw_only=True)
    class Candidate(BaseCandidate):
        _domain: ExampleDomain = field(repr=False)
        selected: tuple[ExampleDomain.Entity, ...]
        native_score: float | None
        strategy: str

        @property
        def domain(self) -> ExampleDomain:
            return self._domain

        def _interpret_in(
            self,
            domain: Domain,
        ) -> ExampleDomain.Evaluation:
            if domain is not self.domain:
                raise ValueError("Candidate belongs to another Domain aggregate.")
            return ExampleDomain.Evaluation(candidate=self)

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "domain_type": self.domain.domain_type,
                "strategy": self.strategy,
                "selected": [entity.name for entity in self.selected],
                "native_score": self.native_score,
            }

    @dataclass(frozen=True, kw_only=True)
    class Evaluation(BaseEvaluation):
        candidate: ExampleDomain.Candidate

        @property
        def feasible(self) -> bool:
            return all(
                entity in self.candidate.domain.entities
                for entity in self.candidate.selected
            )

        @property
        def quality(self) -> float | None:
            if not self.feasible:
                return None
            return sum(entity.value for entity in self.candidate.selected)

        @property
        def metrics(self) -> Mapping[str, Any]:
            return {
                "selected_count": len(self.candidate.selected),
                "quality": self.quality,
            }

        @property
        def utility_inputs(self) -> Mapping[str, Any]:
            return {
                "quality": self.quality,
            }

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "strategy": self.candidate.strategy,
                "state": self.state.code,
                "feasible": self.feasible,
                "quality": self.quality,
                "metrics": dict(self.metrics),
            }

    name: str
    entities: tuple[Entity, ...]
    relationships: tuple[Relationship, ...] = ()
    parameters: Parameters = field(default_factory=Parameters)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Domain name cannot be empty.")
        if not self.entities:
            raise ValueError("ExampleDomain requires at least one Entity.")

    @property
    def objective(self) -> Objective:
        return self.Objective(domain=self)

    @property
    def summary(self) -> Mapping[str, Any]:
        return {
            "name": self.name,
            "domain_type": self.domain_type,
            "entity_count": len(self.entities),
            "relationship_count": len(self.relationships),
        }

    def _interpret_in(
        self,
        domain: Domain,
    ) -> Interpretation:
        if domain is not self:
            raise ValueError("A Domain aggregate must interpret itself.")
        return Interpretation(
            domain=self,
            objective=self.objective,
            summary=self.summary,
        )
