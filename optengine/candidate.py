from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from optengine.domains.base import Domain
    from optengine.evaluation import Evaluation


class Candidate(ABC):
    """Base protocol for a Domain-owned proposed result."""

    @property
    @abstractmethod
    def domain(self) -> Domain:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def _interpret_in(
        self,
        domain: Domain,
    ) -> Evaluation:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def to_dict(self) -> Mapping[str, Any]:
        raise NotImplementedError  # pragma: no cover
