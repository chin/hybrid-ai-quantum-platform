from dataclasses import dataclass

from optengine.operations.base import Operation


@dataclass(frozen=True)
class QAOAOperation(Operation):
    name : str = "qaoa"