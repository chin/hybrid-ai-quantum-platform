from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from optengine.candidate import Candidate
    from optengine.evaluation import Evaluation
    from optengine.interpretation import Interpretation
    from optengine.strategy import Strategy


class Domain(ABC):
    name: str

    @abstractmethod
    def interpret_input(
        self,
        input_data: Any,
    ) -> Interpretation:
        raise NotImplementedError

    @abstractmethod
    def interpret_candidate(
        self,
        interpretation: Interpretation,
        candidate: Candidate,
        strategy: Strategy,
    ) -> Evaluation:
        raise NotImplementedError
