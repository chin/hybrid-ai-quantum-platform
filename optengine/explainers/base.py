from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.execution import Execution
from optengine.explanation import Explanation
from optengine.utility.base import Assessment


class Explainer(ABC):
    """Behavior object that explains an Assessment-backed Decision."""

    @abstractmethod
    def explain(
        self,
        *,
        decision: Decision,
        executions: Sequence[Execution],
        assessment: Assessment,
        analysis: Analysis,
    ) -> Explanation:
        raise NotImplementedError  # pragma: no cover
