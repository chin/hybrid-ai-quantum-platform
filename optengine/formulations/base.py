from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from optengine.interpretation import Interpretation


@dataclass(frozen=True, kw_only=True)
class Model:
    """Concrete mathematical model built by a formulation."""

    formulation: str
    payload: Any
    metadata: Mapping[str, Any] = field(default_factory=dict)


class Formulation(ABC):
    """Build a mathematical model from a domain interpretation."""

    name: str

    @abstractmethod
    def supports(
        self,
        interpretation: Interpretation,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def build(
        self,
        interpretation: Interpretation,
        configuration: Mapping[str, Any],
    ) -> Model:
        raise NotImplementedError
