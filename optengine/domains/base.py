from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from optengine.candidate import Candidate
    from optengine.evaluation import Evaluation
    from optengine.interpretation import Interpretation
    from optengine.strategy import Strategy


class Domain(ABC):
    """Interpret input and candidates for one domain."""

    name: str

    @abstractmethod
    def interpret_input(
        self,
        input_data: Any,
    ) -> Interpretation:
        """Interpret the original input."""
        raise NotImplementedError

    @abstractmethod
    def interpret_candidate(
        self,
        interpretation: Interpretation,
        candidate: Candidate,
        strategy: Strategy,
    ) -> Evaluation:
        """Interpret one candidate in the original domain."""
        raise NotImplementedError
