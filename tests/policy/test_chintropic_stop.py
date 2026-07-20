from __future__ import annotations

from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.utility.operational import OperationalUtilityModel

from tests.conftest import make_evaluation


def decide_for(*evaluations):
    assessment = OperationalUtilityModel().assess(
        list(evaluations),
        analysis=None,
    )
    return ChintropicStopPolicy().apply(
        assessment,
        analysis=None,
    )


def test_no_evaluations_switches() -> None:
    decision = decide_for()

    assert decision.action == "switch"
    assert decision.selected_strategy is None


def test_no_feasible_evaluations_switches() -> None:
    decision = decide_for(make_evaluation(feasible=False))

    assert decision.action == "switch"
    assert decision.selected_strategy is None


def test_high_confidence_and_improvement_scales() -> None:
    decision = decide_for(
        make_evaluation(
            strategy="scale-candidate",
            confidence=0.74,
            expected_improvement=0.06,
        )
    )

    assert decision.action == "scale"
    assert decision.selected_strategy == "scale-candidate"


def test_low_confidence_switches() -> None:
    decision = decide_for(
        make_evaluation(
            strategy="switch-candidate",
            confidence=0.60,
            expected_improvement=0.06,
        )
    )

    assert decision.action == "switch"
    assert decision.selected_strategy == "switch-candidate"


def test_low_marginal_improvement_stops() -> None:
    decision = decide_for(
        make_evaluation(
            strategy="stop-candidate",
            confidence=0.80,
            expected_improvement=0.01,
        )
    )

    assert decision.action == "stop"
    assert decision.selected_strategy == "stop-candidate"


def test_legacy_evaluation_input_remains_supported() -> None:
    decision = ChintropicStopPolicy().apply(
        [
            make_evaluation(
                strategy="legacy",
                confidence=0.8,
                expected_improvement=0.01,
            )
        ],
        analysis=None,
    )

    assert decision.action == "stop"
    assert decision.selected_strategy == "legacy"
