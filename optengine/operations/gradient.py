from dataclasses import dataclass

from optengine.operations.base import Operation


@dataclass(frozen=True)
class GradientOperation(Operation):
    name: str = "gradient"