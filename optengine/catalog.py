from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from optengine.formulations.base import Formulation
from optengine.identity import fingerprint
from optengine.operations.base import Operation
from optengine.solvers.base import Solver


@dataclass(frozen=True, kw_only=True)
class Catalog:
    """Canonical collection of available polymorphic collaborators."""

    formulations: tuple[Formulation, ...]
    operations: tuple[Operation, ...]
    solvers: tuple[Solver, ...]

    def __post_init__(self) -> None:
        self._require_unique(
            "Formulation",
            tuple(item.name for item in self.formulations),
        )
        self._require_unique(
            "Operation",
            tuple(item.name for item in self.operations),
        )
        self._require_unique(
            "Solver",
            tuple(item.name for item in self.solvers),
        )

    @staticmethod
    def _require_unique(kind: str, names: tuple[str, ...]) -> None:
        if len(set(names)) != len(names):
            raise ValueError(f"{kind} names must be unique in a Catalog.")

    @property
    def formulation_names(self) -> tuple[str, ...]:
        return tuple(item.name for item in self.formulations)

    @property
    def operation_names(self) -> tuple[str, ...]:
        return tuple(item.name for item in self.operations)

    @property
    def solver_names(self) -> tuple[str, ...]:
        return tuple(item.name for item in self.solvers)

    @property
    def canonical(self) -> Mapping[str, Any]:
        return {
            "formulations": [item.signature for item in self.formulations],
            "operations": [item.signature for item in self.operations],
            "solvers": [item.signature for item in self.solvers],
        }

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.canonical)
