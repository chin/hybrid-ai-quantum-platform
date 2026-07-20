from dataclasses import dataclass

from optengine.operations.base import Operation


@dataclass(frozen=True)
class ExactSearchOperation(Operation):
    name: str = "exact-search"
    max_variables: int = 18
