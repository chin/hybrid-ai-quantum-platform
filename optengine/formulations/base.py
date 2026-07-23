from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Mapping

from optengine.compatibility import Compatibility
from optengine.identity import fingerprint
from optengine.mathematics import Curve, ValueType
from optengine.objective import Objective

if TYPE_CHECKING:
    from optengine.candidate import Candidate
    from optengine.operations.base import Operation
    from optengine.solvers.base import Solver
    from optengine.strategy import Strategy


SampleDecoder = Callable[[Mapping[Any, Any]], Mapping[Any, Any]]


@dataclass(frozen=True, kw_only=True)
class Model:
    """Solver-oriented mathematical model produced by a Formulation."""

    formulation: Formulation
    objective: Objective
    payload: Any = field(repr=False, compare=False)
    curve: Curve
    sample_decoder: SampleDecoder | None = field(
        default=None,
        repr=False,
        compare=False,
    )
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def fingerprint(self) -> str:
        return fingerprint(
            {
                "formulation": self.formulation.signature,
                "objective": self.objective.canonical,
                "curve": self.curve.canonical,
            }
        )

    def compatibility(self, operation: Operation) -> Compatibility:
        return operation.compatibility(self)

    def operations(
        self,
        available: Iterable[Operation],
    ) -> tuple[Operation, ...]:
        return tuple(
            operation for operation in available if self.compatibility(operation)
        )

    def decode(
        self,
        result: Solver.Result,
        strategy: Strategy,
    ) -> Candidate:
        values = dict(result.values)
        if self.sample_decoder is not None:
            values = dict(self.sample_decoder(values))
        return self.objective.decode(
            values,
            result=result,
            strategy=strategy,
        )

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "formulation": self.formulation.name,
            "curve": dict(self.curve.canonical),
            "fingerprint": self.fingerprint,
            "metadata": dict(self.metadata),
        }


class Formulation(ABC):
    """A transformation from a Domain Objective to a solver-oriented Model."""

    name: ClassVar[str]

    @dataclass(frozen=True, kw_only=True)
    class Capability:
        input_types: frozenset[ValueType]
        output_types: frozenset[ValueType] = frozenset({ValueType.REAL})
        maximum_degree: int = 2
        supports_constraints: bool = False
        maximum_constraint_degree: int | None = None
        maximum_inputs: int | None = None
        maximum_outputs: int | None = 1

        def evaluate(self, curve: Curve) -> Compatibility:
            reasons: list[str] = []

            if not curve.distinct_input_types <= self.input_types:
                reasons.append("unsupported input value type")

            if not curve.distinct_output_types <= self.output_types:
                reasons.append("unsupported output value type")

            if curve.degree > self.maximum_degree:
                reasons.append("objective degree exceeds capability")

            if curve.constrained and not self.supports_constraints:
                reasons.append("constraints are not supported")

            if (
                curve.constrained
                and self.maximum_constraint_degree is not None
                and max(curve.constraint_degrees, default=0)
                > self.maximum_constraint_degree
            ):
                reasons.append("constraint degree exceeds capability")

            if (
                self.maximum_inputs is not None
                and curve.input_count > self.maximum_inputs
            ):
                reasons.append("input count exceeds capability")

            if (
                self.maximum_outputs is not None
                and curve.output_count > self.maximum_outputs
            ):
                reasons.append("output count exceeds capability")

            evidence = {
                "curve": dict(curve.canonical),
                "accepted_input_types": sorted(
                    value.value for value in self.input_types
                ),
                "accepted_output_types": sorted(
                    value.value for value in self.output_types
                ),
                "maximum_degree": self.maximum_degree,
                "supports_constraints": self.supports_constraints,
                "maximum_constraint_degree": self.maximum_constraint_degree,
                "maximum_inputs": self.maximum_inputs,
                "maximum_outputs": self.maximum_outputs,
            }
            if reasons:
                return Compatibility.rejected(
                    *reasons,
                    evidence=evidence,
                )
            return Compatibility.accepted(evidence=evidence)

        def supports(self, curve: Curve) -> bool:
            return bool(self.evaluate(curve))

    capability: ClassVar[Capability]

    @property
    def available(self) -> bool:
        return True

    @property
    def configuration(self) -> Mapping[str, Any]:
        return {}

    @property
    def signature(self) -> Mapping[str, Any]:
        return {
            "name": self.name,
            "configuration": dict(self.configuration),
        }

    def compatibility(self, objective: Objective) -> Compatibility:
        capability = self.capability.evaluate(objective.curve)
        if not self.available:
            return Compatibility.rejected(
                "Formulation is unavailable",
                evidence={
                    **dict(capability.evidence),
                    "available": False,
                },
            )
        return capability

    def express(self, objective: Objective) -> Model | None:
        if not self.compatibility(objective):
            return None
        return self._express(objective)

    @abstractmethod
    def _express(self, objective: Objective) -> Model:
        raise NotImplementedError  # pragma: no cover
