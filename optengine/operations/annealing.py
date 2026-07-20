from __future__ import annotations

from dataclasses import dataclass

from optengine.operations.base import Operation


@dataclass(frozen=True, kw_only=True)
class AnnealingOperation(Operation):
    name: str = "annealing"
    reads_per_iteration: int = 100
    num_sweeps: int = 1000
    seed: int | None = None
