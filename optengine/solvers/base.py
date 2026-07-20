from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from optengine.candidate import Candidate
from optengine.formulations.base import Model
from optengine.operations.base import Operation


class Solver(ABC):
    name: str

    @abstractmethod
    def supports(
        self,
        model: Model,
        operation: Operation,
    ) -> bool:
        """Return whether this solver can execute this combination."""

    @abstractmethod
    def execute(
        self,
        model: Model,
        operation: Operation,
        configuration: Mapping[str, Any],
        budget: Mapping[str, Any],
    ) -> Candidate:
        """Execute the operation against the model."""
