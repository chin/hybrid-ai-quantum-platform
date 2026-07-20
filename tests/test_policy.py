from __future__ import annotations

from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.utility.base import UtilityAssessment


def assessment(**overrides):
    values = {
        "selected_strategy": "candidate",
        "feasible": True,
        "utility": 1.0,
        "marginal_utility": 0.1,
        "expected_improvement": 0.06,
        "execution_cost": 0.01,
        "confidence": 0.8,
        "reference_gap": None,
    }
    values.update(overrides)
    return UtilityAssessment(**values)


def test_stop_when_reference_target_is_reached() -> None:
    decision = ChintropicStopPolicy().apply(
        assessment(reference_gap=0.0),
        analysis=None,
    )
    assert decision.action == "stop"
    assert decision.reason_code == "REFERENCE_TARGET_REACHED"


def test_switch_when_confidence_is_low() -> None:
    decision = ChintropicStopPolicy().apply(
        assessment(confidence=0.5),
        analysis=None,
    )
    assert decision.action == "switch"


def test_scale_when_expected_improvement_is_high() -> None:
    decision = ChintropicStopPolicy().apply(
        assessment(),
        analysis=None,
    )
    assert decision.action == "scale"


def test_stop_when_marginal_utility_is_exhausted() -> None:
    decision = ChintropicStopPolicy().apply(
        assessment(
            expected_improvement=0.01,
            marginal_utility=-0.1,
        ),
        analysis=None,
    )
    assert decision.action == "stop"
