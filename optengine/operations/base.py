from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Mapping

from optengine.compatibility import Compatibility
from optengine.mathematics import ValueType

if TYPE_CHECKING:
    from optengine.formulations.base import Model
    from optengine.solvers.base import Solver


class Operation(ABC):
    """Algorithmic action requested for a Model."""

    name: ClassVar[str]

    @dataclass(frozen=True, kw_only=True)
    class Capability:
        input_types: frozenset[ValueType]
        maximum_degree: int | None = None
        supports_constraints: bool = False
        maximum_inputs: int | None = None
        model_types: tuple[type[Any], ...] = ()

        def evaluate(self, model: Model) -> Compatibility:
            curve = model.curve
            reasons: list[str] = []

            if self.model_types and not isinstance(model, self.model_types):
                reasons.append("unsupported Model type")

            if not curve.distinct_input_types <= self.input_types:
                reasons.append("unsupported Model input value type")

            if self.maximum_degree is not None and curve.degree > self.maximum_degree:
                reasons.append("Model degree exceeds capability")

            if curve.constrained and not self.supports_constraints:
                reasons.append("constrained Models are not supported")

            if (
                self.maximum_inputs is not None
                and curve.input_count > self.maximum_inputs
            ):
                reasons.append("Model input count exceeds capability")

            evidence = {
                "curve": dict(curve.canonical),
                "accepted_input_types": sorted(
                    value.value for value in self.input_types
                ),
                "maximum_degree": self.maximum_degree,
                "supports_constraints": self.supports_constraints,
                "maximum_inputs": self.maximum_inputs,
                "model_types": tuple(
                    f"{value.__module__}.{value.__qualname__}"
                    for value in self.model_types
                ),
            }
            if reasons:
                return Compatibility.rejected(
                    *reasons,
                    evidence=evidence,
                )
            return Compatibility.accepted(evidence=evidence)

        def supports(self, model: Model) -> bool:
            return bool(self.evaluate(model))

    @dataclass(frozen=True, kw_only=True)
    class Request:
        model: Model
        operation: Operation
        budget: Mapping[str, Any] = field(default_factory=dict)
        metadata: Mapping[str, Any] = field(default_factory=dict)

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "model": self.model.to_dict(),
                "operation": self.operation.name,
                "budget": dict(self.budget),
                "metadata": dict(self.metadata),
            }

    @property
    @abstractmethod
    def capability(self) -> Capability:
        raise NotImplementedError  # pragma: no cover

    @property
    def configuration(self) -> Mapping[str, Any]:
        return {}

    @property
    def signature(self) -> Mapping[str, Any]:
        return {
            "name": self.name,
            "configuration": dict(self.configuration),
        }

    def compatibility(self, model: Model) -> Compatibility:
        return self.capability.evaluate(model)

    def prepare(self, model: Model) -> Request:
        compatibility = self.compatibility(model)
        if not compatibility:
            raise TypeError(
                f"{type(self).__name__} cannot prepare "
                f"{type(model).__name__}: {compatibility.reasons}"
            )
        return self.Request(
            model=model,
            operation=self,
            budget=dict(self.budget),
        )

    @property
    def budget(self) -> Mapping[str, Any]:
        return {}

    def solvers(
        self,
        model: Model,
        available: Iterable[Solver],
    ) -> tuple[Solver, ...]:
        return tuple(
            solver
            for solver in available
            if solver.compatibility(
                operation=self,
                model=model,
            )
        )
