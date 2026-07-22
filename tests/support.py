from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Mapping

from optengine.candidate import Candidate
from optengine.domains.base import Domain
from optengine.evaluation import Evaluation
from optengine.formulations.base import Formulation, Model
from optengine.interpretation import Interpretation
from optengine.mathematics import (
    Expression,
    LinearTerm,
    ValueType,
    Variable,
)
from optengine.objective import Objective
from optengine.operations.base import Operation
from optengine.solvers.base import Solver


@dataclass(frozen=True, kw_only=True)
class ExampleDomain(Domain):
    domain_type: ClassVar[str] = "example"
    name: str = "example"
    offset: float = 0.0

    @dataclass(frozen=True, kw_only=True)
    class Objective(Objective):
        domain: ExampleDomain
        sense: ClassVar[str] = "maximize"

        @property
        def expression(self) -> Expression:
            x = Variable(
                identifier="x",
                value_type=ValueType.BINARY,
                lower_bound=0,
                upper_bound=1,
            )
            y = Variable(
                identifier="y",
                value_type=ValueType.BINARY,
                lower_bound=0,
                upper_bound=1,
            )
            return Expression(
                variables=(x, y),
                linear_terms=(
                    LinearTerm(variable=x, coefficient=1.0),
                    LinearTerm(variable=y, coefficient=2.0),
                ),
            )

        def decode(
            self,
            values: Mapping[Any, Any],
            *,
            result: Solver.Result,
            strategy: Any,
        ) -> Candidate:
            return ExampleDomain.Candidate(
                _domain=self.domain,
                values={
                    "x": int(values.get("x", 0)),
                    "y": int(values.get("y", 0)),
                },
                strategy=strategy.name,
                native_score=result.native_score,
                confidence=float(result.metrics.get("confidence", 0.0)),
                expected_improvement=float(
                    result.metrics.get(
                        "expected_improvement",
                        0.0,
                    )
                ),
                execution_cost=float(result.resource_cost or 0.0),
            )

    @dataclass(frozen=True, kw_only=True)
    class Candidate(Candidate):
        _domain: ExampleDomain
        values: Mapping[str, int]
        strategy: str
        native_score: float | None = None
        confidence: float = 0.0
        expected_improvement: float = 0.0
        execution_cost: float = 0.0

        @property
        def domain(self) -> ExampleDomain:
            return self._domain

        def _interpret_in(
            self,
            domain: Domain,
        ) -> ExampleDomain.Evaluation:
            if domain is not self.domain:
                raise ValueError("Example Candidate belongs to another Domain.")
            return ExampleDomain.Evaluation(candidate=self)

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "domain_type": self.domain.domain_type,
                "strategy": self.strategy,
                "values": dict(self.values),
                "native_score": self.native_score,
            }

    @dataclass(frozen=True, kw_only=True)
    class Evaluation(Evaluation):
        candidate: ExampleDomain.Candidate

        @property
        def feasible(self) -> bool:
            return set(self.candidate.values) == {"x", "y"} and all(
                value in (0, 1) for value in self.candidate.values.values()
            )

        @property
        def quality(self) -> float | None:
            if not self.feasible:
                return None
            return (
                float(self.candidate.values["x"])
                + 2.0 * float(self.candidate.values["y"])
                + self.candidate.domain.offset
            )

        @property
        def metrics(self) -> Mapping[str, Any]:
            return {
                "score": self.quality,
                "native_score": self.candidate.native_score,
            }

        @property
        def utility_inputs(self) -> Mapping[str, Any]:
            return {
                "quality": self.quality,
                "confidence": self.candidate.confidence,
                "expected_improvement": (self.candidate.expected_improvement),
                "execution_cost": self.candidate.execution_cost,
            }

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "strategy": self.candidate.strategy,
                "state": self.state.code,
                "feasible": self.feasible,
                "quality": self.quality,
                "metrics": dict(self.metrics),
                "utility_inputs": dict(self.utility_inputs),
            }

    @property
    def objective(self) -> ExampleDomain.Objective:
        return self.Objective(domain=self)

    @property
    def summary(self) -> Mapping[str, Any]:
        return {
            "domain_type": self.domain_type,
            "name": self.name,
            "offset": self.offset,
        }

    def _interpret_in(self, domain: Domain) -> Interpretation:
        if domain is not self:
            raise ValueError("Example Domain must interpret itself.")
        return Interpretation(
            domain=self,
            objective=self.objective,
            summary=self.summary,
        )


@dataclass(frozen=True, kw_only=True)
class ExampleFormulation(Formulation):
    name: ClassVar[str] = "example-formulation"

    capability = Formulation.Capability(
        input_types=frozenset({ValueType.BINARY}),
        maximum_degree=2,
        supports_constraints=False,
    )

    tag: str = "default"

    @property
    def configuration(self) -> Mapping[str, Any]:
        return {"tag": self.tag}

    def _express(self, objective: Objective) -> Model:
        return Model(
            formulation=self,
            objective=objective,
            payload={"tag": self.tag},
            curve=objective.curve,
            metadata={"tag": self.tag},
        )


class RejectingFormulation(Formulation):
    name = "rejecting-formulation"
    capability = Formulation.Capability(
        input_types=frozenset({ValueType.REAL}),
    )

    def _express(self, objective: Objective) -> Model:
        raise AssertionError("Rejected Formulation must not express.")


class ExplodingFormulation(ExampleFormulation):
    name = "exploding-formulation"

    def _express(self, objective: Objective) -> Model:
        raise RuntimeError("expression failed")


class NoneFormulation(ExampleFormulation):
    name = "none-formulation"

    def express(self, objective: Objective) -> Model | None:
        return None


@dataclass(frozen=True, kw_only=True)
class ExampleOperation(Operation):
    name: ClassVar[str] = "example-operation"
    limit: int = 10

    @property
    def capability(self) -> Operation.Capability:
        return Operation.Capability(
            input_types=frozenset({ValueType.BINARY}),
            maximum_degree=2,
            supports_constraints=False,
            maximum_inputs=self.limit,
        )

    @property
    def configuration(self) -> Mapping[str, Any]:
        return {"limit": self.limit}

    @property
    def budget(self) -> Mapping[str, Any]:
        return {"attempts": 1}


@dataclass(frozen=True, kw_only=True)
class ExampleSolver(Solver):
    name: str = "example-solver"
    values: Mapping[str, int] = field(default_factory=lambda: {"x": 1, "y": 1})
    score: float = -3.0
    confidence: float = 0.8
    expected_improvement: float = 0.1
    cost: float = 0.01
    fail: bool = False
    available_flag: bool = True
    reference_flag: bool = False
    status: str = "complete"

    capability: ClassVar[Solver.Capability] = Solver.Capability(
        operation_types=(ExampleOperation,),
        model_types=(Model,),
        input_types=frozenset({ValueType.BINARY}),
        maximum_inputs=10,
        supports_constraints=False,
    )

    @property
    def available(self) -> bool:
        return self.available_flag

    @property
    def reference(self) -> bool:
        return self.reference_flag

    @property
    def configuration(self) -> Mapping[str, Any]:
        return {
            "values": dict(self.values),
            "score": self.score,
            "confidence": self.confidence,
            "expected_improvement": self.expected_improvement,
            "cost": self.cost,
            "fail": self.fail,
            "available": self.available_flag,
            "reference": self.reference_flag,
            "status": self.status,
        }

    def execute(
        self,
        request: Operation.Request,
    ) -> Solver.Result:
        if self.fail:
            raise RuntimeError(f"{self.name} failed")
        compatibility = self.compatibility(
            operation=request.operation,
            model=request.model,
        )
        if not compatibility:
            raise TypeError(f"Incompatible request: {compatibility.reasons}")
        return Solver.Result(
            values=dict(self.values),
            native_score=self.score,
            status=self.status,
            runtime_s=0.002,
            resource_cost=self.cost,
            metrics={
                "confidence": self.confidence,
                "expected_improvement": (self.expected_improvement),
                "is_reference": self.reference,
            },
            metadata={"request": request.to_dict()},
            provenance={"solver": self.name},
        )
