from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Mapping

if TYPE_CHECKING:
    from optengine.evaluation import Evaluation
    from optengine.interpretation import Interpretation
    from optengine.objective import Objective


class Domain(ABC):
    """Aggregate root and semantic owner for one optimization problem."""

    domain_type: ClassVar[str]
    name: str

    def interpret(
        self,
        subject: Any | None = None,
    ) -> Interpretation | Evaluation:
        target = self if subject is None else subject
        interpreter = getattr(target, "_interpret_in", None)
        if not callable(interpreter):
            raise TypeError(
                f"{type(target).__name__} cannot be interpreted by "
                f"{type(self).__name__}."
            )
        return interpreter(self)

    @property
    @abstractmethod
    def objective(self) -> Objective:
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def summary(self) -> Mapping[str, Any]:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def _interpret_in(
        self,
        domain: Domain,
    ) -> Interpretation:
        raise NotImplementedError  # pragma: no cover
