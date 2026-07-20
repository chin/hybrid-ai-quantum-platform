from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.evaluation import Evaluation
from optengine.explanation import Explanation
from optengine.utility.base import UtilityAssessment


class Explainer(ABC):
    @abstractmethod
    def explain(
        self,
        decision: Decision,
        evaluations: Sequence[Evaluation],
        assessment: UtilityAssessment | None = None,
        analysis: Analysis | None = None,
    ) -> Explanation:
        raise NotImplementedError
