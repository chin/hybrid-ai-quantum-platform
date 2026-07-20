from dataclasses import dataclass

from optengine.operations.base import Operation


@dataclass(frozen=True)
class BenchmarkOperation(Operation):
    name: str = "benchmark"