from dataclasses import dataclass

from optengine.operations.base import Operation


@dataclass(frozen=True)
class SimulationOperation(Operation):
    name: str = "simulation"