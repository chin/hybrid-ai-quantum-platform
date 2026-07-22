from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import TYPE_CHECKING, Any, Mapping

from optengine.identity import fingerprint

if TYPE_CHECKING:
    from optengine.domains.base import Domain
    from optengine.execution import Execution
    from optengine.formulations.base import Formulation, Model
    from optengine.operations.base import Operation
    from optengine.solvers.base import Solver


@dataclass(frozen=True, kw_only=True)
class Strategy:
    """One compatible Domain/Model/Operation/Solver collaboration."""

    domain: Domain
    formulation: Formulation
    model: Model
    operation: Operation
    solver: Solver
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return ":".join(
            (
                self.domain.domain_type,
                self.formulation.name,
                self.operation.name,
                self.solver.name,
            )
        )

    @property
    def reference(self) -> bool:
        return bool(self.metadata.get("role") == "reference" or self.solver.reference)

    @property
    def fingerprint(self) -> str:
        return fingerprint(
            {
                "domain_type": self.domain.domain_type,
                "model": self.model.fingerprint,
                "operation": self.operation.signature,
                "solver": self.solver.signature,
                "metadata": dict(self.metadata),
            }
        )

    def summary(self) -> Mapping[str, Any]:
        return {
            "name": self.name,
            "fingerprint": self.fingerprint,
            "domain": self.domain.domain_type,
            "formulation": self.formulation.name,
            "model": self.model.to_dict(),
            "operation": self.operation.name,
            "operation_configuration": dict(self.operation.configuration),
            "solver": self.solver.name,
            "solver_configuration": dict(self.solver.configuration),
            "reference": self.reference,
            "metadata": dict(self.metadata),
        }

    def execute(self) -> Execution:
        from optengine.execution import (
            Complete,
            Execution,
            Failed,
            Failure,
        )

        started = perf_counter()
        try:
            request = self.operation.prepare(self.model)
            result = self.solver.execute(request)
            if not result.complete:
                raise RuntimeError(
                    f"Solver returned non-complete status: {result.status}"
                )
            candidate = self.model.decode(result, self)
            evaluation = self.domain.interpret(candidate)
            return Execution(
                strategy=self,
                state=Complete(),
                result=result,
                candidate=candidate,
                evaluation=evaluation,
                runtime_s=perf_counter() - started,
            )
        except Exception as error:
            return Execution(
                strategy=self,
                state=Failed(),
                runtime_s=perf_counter() - started,
                failure=Failure(
                    error_type=type(error).__name__,
                    message=str(error),
                ),
            )
