from __future__ import annotations


class OptEngineError(Exception):
    """Base exception for OptEngine failures."""


class NoCompatibleStrategyError(OptEngineError):
    """Raised when no available object collaboration produces a Strategy."""


class IncompatibleStrategyError(OptEngineError):
    """Raised when a Strategy is assembled from incompatible collaborators."""

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


class MissingDependencyError(OptEngineError):
    """Raised when a concrete plugin's external dependency is unavailable."""

    def __init__(self, dependency: str, plugin: str) -> None:
        self.dependency = dependency
        self.plugin = plugin
        super().__init__(
            f"{plugin} requires the optional runtime dependency {dependency!r}."
        )
