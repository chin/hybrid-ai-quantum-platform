from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from optengine.analysis import StrategySummary
    from optengine.domains.base import Domain
    from optengine.formulations.base import Formulation
    from optengine.operations.base import Operation
    from optengine.solvers.base import Solver


@dataclass(frozen=True, kw_only=True)
class Strategy:
    """One modular Domain/Formulation/Operation/Solver composition."""

    name: str
    domain: Domain
    formulation: Formulation
    operation: Operation
    solver: Solver
    configuration: Mapping[str, Any] = field(default_factory=dict)
    budget: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def summary(self) -> StrategySummary:
        from optengine.analysis import StrategySummary

        return StrategySummary(
            name=self.name,
            domain=self.domain.name,
            formulation=self.formulation.name,
            operation=self.operation.name,
            solver=self.solver.name,
            metadata=dict(self.metadata),
        )
