from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.evaluation import Evaluation
from optengine.explanation import Explanation


class Explainer(ABC):
    @abstractmethod
    def explain(
        self,
        decision: Decision,
        evaluations: Sequence[Evaluation],
        analysis: Analysis,
    ) -> Explanation:
        """Explain a decision from its supporting evidence."""
