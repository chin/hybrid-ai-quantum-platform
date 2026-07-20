from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.evaluation import Evaluation
from optengine.utility.base import UtilityAssessment


class Policy(ABC):
    @abstractmethod
    def apply(
        self,
        assessment: UtilityAssessment | Sequence[Evaluation],
        analysis: Analysis | None = None,
    ) -> Decision:
        raise NotImplementedError
