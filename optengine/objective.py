from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Mapping

from optengine.identity import fingerprint
from optengine.mathematics import Curve, Expression, ObjectiveSense

if TYPE_CHECKING:
    from optengine.candidate import Candidate
    from optengine.solvers.base import Solver
    from optengine.strategy import Strategy


class Objective(ABC):
    """Mathematical intent owned by a Domain aggregate."""

    sense: ObjectiveSense

    @property
    @abstractmethod
    def expression(self) -> Expression:
        raise NotImplementedError  # pragma: no cover

    @property
    def curve(self) -> Curve:
        return self.expression.curve

    @abstractmethod
    def decode(
        self,
        values: Mapping[Any, Any],
        *,
        result: Solver.Result,
        strategy: Strategy,
    ) -> Candidate:
        """Decode Model values into the owning Domain's Candidate."""
        raise NotImplementedError  # pragma: no cover

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.canonical)

    @property
    def canonical(self) -> Mapping[str, Any]:
        return {
            "sense": self.sense,
            "expression": self.expression.canonical,
            "curve": self.curve.canonical,
        }
