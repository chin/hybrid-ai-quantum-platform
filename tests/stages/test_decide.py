from __future__ import annotations

from types import SimpleNamespace

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.recommendation import Recommendation
from optengine.stages.decide import decide
from optengine.utility.base import UtilityAssessment


class FakeUtilityModel:
    def __init__(self) -> None:
        self.called = False

    def assess(self, evaluations, analysis):
        self.called = True
        return UtilityAssessment(
            selected_strategy="selected",
            feasible=True,
            utility=1.0,
            marginal_utility=0.0,
            expected_improvement=0.0,
            execution_cost=0.0,
            confidence=1.0,
            reference_gap=0.0,
        )


class FakePolicy:
    def __init__(self) -> None:
        self.received = None

    def apply(self, assessment, analysis):
        self.received = assessment
        return Decision(
            action="stop",
            selected_strategy=assessment.selected_strategy,
            reason_code="TEST",
        )


def test_decide_stores_utility_assessment_before_decision() -> None:
    utility_model = FakeUtilityModel()
    policy = FakePolicy()
    recommendation = Recommendation(
        run_id="test",
        analysis=Analysis(
            interpretation={},
            strategies=(),
        ),
    )
    engine = SimpleNamespace(
        utility_model=utility_model,
        policy=policy,
        recommendation=recommendation,
        log=lambda message: None,
    )

    decide(engine)

    assert utility_model.called is True
    assert recommendation.utility_assessment is policy.received
    assert recommendation.decision is not None
    assert recommendation.decision.action == "stop"
