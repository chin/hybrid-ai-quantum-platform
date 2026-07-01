from dataclasses import dataclass
from typing import Any

from optengine.context import Context


@dataclass
class Solution:
    problem: str
    decision: dict[str, Any]
    results: dict[str, Any]
    metrics: dict[str, Any]
    logs: list[str]
    output_path: str | None

    @classmethod
    def from_context(cls, context: Context) -> "Solution":
        return cls(
            problem=context.problem,
            decision=context.decision,
            results=context.optimization_results,
            metrics=context.metrics,
            logs=context.logs,
            output_path=str(context.output_path) if context.output_path else None,
        )
