from dataclasses import dataclass

from optengine.operations.base import Operation


@dataclass(frozen=True)
class InferenceOperation(Operation):
    name: str = "inference"