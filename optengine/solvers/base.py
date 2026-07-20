from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
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
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        model: Model,
        operation: Operation,
        configuration: Mapping[str, Any],
        budget: Mapping[str, Any],
    ) -> Candidate:
        raise NotImplementedError
