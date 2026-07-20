from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from optengine.interpretation import Interpretation


Decoder = Callable[[Mapping[Any, Any]], Mapping[Any, Any]]


@dataclass(frozen=True, kw_only=True)
class Model:
    """A library-native mathematical model built by a formulation."""

    formulation: str
    payload: Any
    decoder: Decoder | None = field(default=None, repr=False, compare=False)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def decode(
        self,
        values: Mapping[Any, Any],
    ) -> Mapping[Any, Any]:
        if self.decoder is None:
            return dict(values)
        return dict(self.decoder(values))


class Formulation(ABC):
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
