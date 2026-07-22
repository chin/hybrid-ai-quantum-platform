from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping


class EvaluationState(ABC):
    code: str
    feasible: bool
    utility_weight: float
    should_continue: bool

    @property
    def message(self) -> str:
        return self.code.replace("-", " ")


class Feasible(EvaluationState):
    code = "feasible"
    feasible = True
    utility_weight = 1.0
    should_continue = True


class Infeasible(EvaluationState):
    code = "infeasible"
    feasible = False
    utility_weight = 0.0
    should_continue = False


class Evaluation(ABC):
    """Domain-owned semantic evaluation of one Candidate."""

    @property
    @abstractmethod
    def feasible(self) -> bool:
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def quality(self) -> float | None:
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def metrics(self) -> Mapping[str, Any]:
        raise NotImplementedError  # pragma: no cover

    @property
    def utility_inputs(self) -> Mapping[str, Any]:
        return {}

    @property
    def policy_evidence(self) -> Mapping[str, Any]:
        return {}

    @property
    def state(self) -> EvaluationState:
        return Feasible() if self.feasible else Infeasible()

    def evidence_for_utility(self) -> dict[str, Any]:
        evidence = dict(self.policy_evidence)
        evidence.update(self.utility_inputs)
        return evidence

    @abstractmethod
    def to_dict(self) -> Mapping[str, Any]:
        raise NotImplementedError  # pragma: no cover
