from __future__ import annotations

from abc import ABC, abstractmethod

import pytest

from optengine.candidate import Candidate
from optengine.domains.base import Domain
from optengine.evaluation import Evaluation
from optengine.interpretation import Interpretation


class DomainContract(ABC):
    """Reusable base contract for every concrete OptEngine Domain."""

    @abstractmethod
    def make_domain(self) -> Domain:
        raise NotImplementedError

    @abstractmethod
    def make_candidate(self, domain: Domain) -> Candidate:
        raise NotImplementedError

    def test_domain_is_the_aggregate_root(self) -> None:
        domain = self.make_domain()
        assert isinstance(domain, Domain)
        assert not hasattr(domain, "input")
        assert domain.summary["domain_type"] == domain.domain_type

    def test_self_interpretation_is_idempotent(self) -> None:
        domain = self.make_domain()
        first = domain.interpret()
        second = domain.interpret()
        assert isinstance(first, Interpretation)
        assert first.to_dict() == second.to_dict()
        assert first.fingerprint == second.fingerprint
        assert first.domain is domain
        assert first.objective.canonical == domain.objective.canonical

    def test_canonical_domain_chain_is_complete_and_idempotent(self) -> None:
        domain = self.make_domain()
        interpretation = domain.interpret()
        objective = interpretation.objective
        expression = objective.expression
        curve = expression.curve

        assert interpretation.domain is domain
        assert objective is not None
        assert objective.expression.canonical == expression.canonical
        assert objective.curve.canonical == curve.canonical
        assert expression.curve.canonical == curve.canonical
        assert objective.fingerprint == domain.objective.fingerprint
        assert expression.fingerprint == domain.objective.expression.fingerprint
        assert curve.fingerprint == domain.objective.curve.fingerprint
        assert interpretation.to_dict() == domain.interpret().to_dict()

    def test_candidate_interpretation_is_polymorphic_and_idempotent(
        self,
    ) -> None:
        domain = self.make_domain()
        candidate = self.make_candidate(domain)
        first = domain.interpret(candidate)
        second = domain.interpret(candidate)
        assert isinstance(first, Evaluation)
        assert first.to_dict() == second.to_dict()

    def test_uninterpretable_subject_fails_explicitly(self) -> None:
        domain = self.make_domain()
        with pytest.raises(TypeError, match="cannot be interpreted"):
            domain.interpret(object())

    def test_candidate_cannot_cross_domain_aggregate_boundary(self) -> None:
        domain = self.make_domain()
        candidate = self.make_candidate(domain)
        another = self.make_domain()
        with pytest.raises(ValueError):
            another.interpret(candidate)
