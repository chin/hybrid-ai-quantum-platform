from dataclasses import dataclass

from optengine.operations.base import Operation


@dataclass(frozen=True)
class FNOOperation(Operation):   
    name: str = "fno"