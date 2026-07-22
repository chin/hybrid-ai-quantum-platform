from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Mapping

from optengine.compatibility import Compatibility
from optengine.mathematics import ValueType

if TYPE_CHECKING:
    from optengine.formulations.base import Model
    from optengine.operations.base import Operation


class Solver(ABC):
    """Concrete executor for one Operation and Model combination."""

    name: ClassVar[str]

    @dataclass(frozen=True, kw_only=True)
    class Capability:
        operation_types: tuple[type[Any], ...]
        model_types: tuple[type[Any], ...]
        input_types: frozenset[ValueType]
        maximum_inputs: int | None = None
        supports_constraints: bool = False

        def evaluate(
            self,
            *,
            solver: Solver,
            operation: Operation,
            model: Model,
        ) -> Compatibility:
            reasons: list[str] = []

            if not solver.available:
                reasons.append("Solver is unavailable")

            if self.operation_types and not isinstance(
                operation,
                self.operation_types,
            ):
                reasons.append("unsupported Operation type")

            if self.model_types and not isinstance(model, self.model_types):
                reasons.append("unsupported Model type")

            if not model.curve.distinct_input_types <= self.input_types:
                reasons.append("unsupported Model input value type")

            if (
                self.maximum_inputs is not None
                and model.curve.input_count > self.maximum_inputs
            ):
                reasons.append("Model input count exceeds Solver capability")

            if model.curve.constrained and not self.supports_constraints:
                reasons.append("constrained Models are not supported")

            evidence = {
                "available": solver.available,
                "operation": operation.name,
                "model": type(model).__name__,
                "curve": dict(model.curve.canonical),
                "operation_types": tuple(
                    f"{value.__module__}.{value.__qualname__}"
                    for value in self.operation_types
                ),
                "model_types": tuple(
                    f"{value.__module__}.{value.__qualname__}"
                    for value in self.model_types
                ),
                "accepted_input_types": sorted(
                    value.value for value in self.input_types
                ),
                "maximum_inputs": self.maximum_inputs,
                "supports_constraints": self.supports_constraints,
            }
            if reasons:
                return Compatibility.rejected(
                    *reasons,
                    evidence=evidence,
                )
            return Compatibility.accepted(evidence=evidence)

        def supports(
            self,
            *,
            solver: Solver,
            operation: Operation,
            model: Model,
        ) -> bool:
            return bool(
                self.evaluate(
                    solver=solver,
                    operation=operation,
                    model=model,
                )
            )

    @dataclass(frozen=True, kw_only=True)
    class Result:
        values: Mapping[Any, Any]
        native_score: float | None
        status: str
        runtime_s: float | None = None
        resource_cost: float | None = None
        metrics: Mapping[str, Any] = field(default_factory=dict)
        metadata: Mapping[str, Any] = field(default_factory=dict)
        provenance: Mapping[str, Any] = field(default_factory=dict)

        @property
        def complete(self) -> bool:
            return self.status == "complete"

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "values": dict(self.values),
                "native_score": self.native_score,
                "status": self.status,
                "runtime_s": self.runtime_s,
                "resource_cost": self.resource_cost,
                "metrics": dict(self.metrics),
                "metadata": dict(self.metadata),
                "provenance": dict(self.provenance),
            }

    capability: ClassVar[Capability]

    @property
    def available(self) -> bool:
        return True

    @property
    def reference(self) -> bool:
        return False

    @property
    def configuration(self) -> Mapping[str, Any]:
        return {}

    @property
    def signature(self) -> Mapping[str, Any]:
        return {
            "name": self.name,
            "configuration": dict(self.configuration),
        }

    def compatibility(
        self,
        *,
        operation: Operation,
        model: Model,
    ) -> Compatibility:
        return self.capability.evaluate(
            solver=self,
            operation=operation,
            model=model,
        )

    @abstractmethod
    def execute(
        self,
        request: Operation.Request,
    ) -> Result:
        raise NotImplementedError  # pragma: no cover
