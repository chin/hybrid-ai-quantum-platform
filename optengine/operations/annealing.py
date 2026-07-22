from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Mapping

from optengine.operations.base import Operation
from optengine.mathematics import ValueType


@dataclass(frozen=True, kw_only=True)
class Annealing(Operation):
    name: ClassVar[str] = "annealing"
    reads_per_iteration: int = 100
    num_sweeps: int = 1000
    iterations: int = 1
    seed: int | None = None

    def __post_init__(self) -> None:
        if self.reads_per_iteration <= 0:
            raise ValueError("reads_per_iteration must be positive.")
        if self.num_sweeps <= 0:
            raise ValueError("num_sweeps must be positive.")
        if self.iterations <= 0:
            raise ValueError("iterations must be positive.")

    @property
    def capability(self) -> Operation.Capability:
        return Operation.Capability(
            input_types=frozenset({ValueType.BINARY}),
            maximum_degree=2,
            supports_constraints=False,
        )

    @property
    def configuration(self) -> Mapping[str, Any]:
        return {
            "reads_per_iteration": self.reads_per_iteration,
            "num_sweeps": self.num_sweeps,
            "iterations": self.iterations,
            "seed": self.seed,
        }

    @property
    def budget(self) -> Mapping[str, Any]:
        return {
            "iterations": self.iterations,
            "total_reads": self.iterations * self.reads_per_iteration,
        }


AnnealingOperation = Annealing
