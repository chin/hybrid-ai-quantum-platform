from __future__ import annotations

from types import SimpleNamespace

import pytest

from optengine.candidate import Candidate
from optengine.errors import IncompatibleStrategyError
from optengine.evaluation import Evaluation
from optengine.formulations.base import Model
from optengine.interpretation import Interpretation
from optengine.recommendation import Recommendation
from optengine.stages.evaluate import evaluate
from optengine.strategy import Strategy


class FakeFormulation:
    name = "fake-formulation"

    def build(self, interpretation, configuration):
        return Model(
            formulation=self.name,
            payload={"model": True},
            metadata={},
        )


class FakeSolver:
    name = "fake-solver"

    def __init__(self, compatible: bool) -> None:
        self.compatible = compatible
        self.executed = False

    def supports(self, model, operation) -> bool:
        return self.compatible

    def execute(
        self,
        model,
        operation,
        configuration,
        budget,
    ):
        self.executed = True
        return Candidate(
            strategy="",
            formulation=model.formulation,
            operation=operation.name,
            solver=self.name,
            values={"sample": {0: 0, 1: 1}},
            native_score=-1.0,
            status="complete",
        )


class FakeDomain:
    name = "fake-domain"

    def __init__(self) -> None:
        self.interpreted = False

    def interpret_candidate(
        self,
        interpretation,
        candidate,
        strategy,
    ):
        self.interpreted = True
        assert candidate.strategy == strategy.name
        return Evaluation(
            strategy=strategy.name,
            candidate=candidate,
            feasible=True,
            quality=1.0,
            metrics={"quality": 1.0},
            utility_inputs={"quality": 1.0},
        )


class FakeEngine:
    def __init__(self, strategy: Strategy) -> None:
        self.interpretation = Interpretation(
            domain="fake-domain",
            summary={},
        )
        self.strategies = [strategy]
        self.recommendation = Recommendation(run_id="test")
        self.logs: list[str] = []

    def log(self, message: str) -> None:
        self.logs.append(message)


def test_evaluate_builds_executes_and_interprets() -> None:
    domain = FakeDomain()
    solver = FakeSolver(compatible=True)
    strategy = Strategy(
        name="fake-strategy",
        domain=domain,
        formulation=FakeFormulation(),
        operation=SimpleNamespace(name="fake-operation"),
        solver=solver,
    )
    engine = FakeEngine(strategy)

    evaluate(engine)

    assert solver.executed is True
    assert domain.interpreted is True
    assert len(engine.recommendation.evaluations) == 1


def test_evaluate_rejects_incompatible_strategy() -> None:
    strategy = Strategy(
        name="invalid",
        domain=FakeDomain(),
        formulation=FakeFormulation(),
        operation=SimpleNamespace(name="unsupported-operation"),
        solver=FakeSolver(compatible=False),
    )

    with pytest.raises(IncompatibleStrategyError):
        evaluate(FakeEngine(strategy))
