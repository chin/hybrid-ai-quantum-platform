from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.evaluation import Evaluation


class Policy(ABC):
    @abstractmethod
    def apply(
        self,
        evaluations: Sequence[Evaluation],
        analysis: Analysis,
    ) -> Decision:
        """Act on evaluated evidence and return a decision."""
