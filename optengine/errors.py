from __future__ import annotations


class OptEngineError(Exception):
    """Base exception for OptEngine failures."""


class NoCompatibleStrategyError(OptEngineError):
    """Raised when no registered strategy supports an interpretation."""


class IncompatibleStrategyError(OptEngineError):
    """Raised when a strategy's formulation, operation, and solver conflict."""

    def __init__(
        self,
        *,
        strategy: str,
        formulation: str,
        operation: str,
        solver: str,
    ) -> None:
        self.strategy = strategy
        self.formulation = formulation
        self.operation = operation
        self.solver = solver

        super().__init__(
            "Incompatible strategy components: "
            f"strategy={strategy!r}, "
            f"formulation={formulation!r}, "
            f"operation={operation!r}, "
            f"solver={solver!r}."
        )
