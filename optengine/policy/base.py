from __future__ import annotations

from abc import ABC, abstractmethod

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.utility.base import Assessment


class Policy(ABC):
    @abstractmethod
    def apply(
        self,
        assessment: Assessment,
        analysis: Analysis | None = None,
    ) -> Decision:
        raise NotImplementedError  # pragma: no cover
