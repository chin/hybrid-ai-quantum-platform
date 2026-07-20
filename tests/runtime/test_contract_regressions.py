from __future__ import annotations

import pytest

from optengine.candidate import Candidate
from optengine.formulations.base import Model
from optengine.registry import StrategyFactory, StrategyRegistry


def test_candidate_assignment_is_immutable_and_single_owner():
    candidate = Candidate(
        formulation="qubo",
        operation="exact",
        solver="solver",
        values={"sample": {0: 0}},
        native_score=0.0,
        status="complete",
    )
    assigned = candidate.assigned_to("first")
    assert candidate.strategy == ""
    assert assigned.strategy == "first"
    assert assigned.assigned_to("first") == assigned
    with pytest.raises(ValueError, match="different strategy"):
        assigned.assigned_to("second")


def test_model_decoder_is_applied_without_mutating_input():
    values = {"x": 1}
    model = Model(
        formulation="test",
        payload=object(),
        decoder=lambda sample: {"decoded": sample["x"]},
    )
    assert model.decode(values) == {"decoded": 1}
    assert values == {"x": 1}


def test_registry_rejects_duplicate_names():
    registry = StrategyRegistry()
    factory = StrategyFactory(
        name="same",
        supports=lambda domain, interpretation: False,
        build=lambda domain, interpretation: None,
    )
    registry.register(factory)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(factory)
