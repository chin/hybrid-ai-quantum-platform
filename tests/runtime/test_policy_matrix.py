from __future__ import annotations

import pytest

from optengine.policy.chintropic_stop import ChintropicStopConfig, ChintropicStopPolicy
from optengine.utility.base import UtilityAssessment


def assessment(**overrides):
    values = {
        "selected_strategy": "candidate",
        "feasible": True,
        "utility": 1.0,
        "marginal_utility": 0.1,
        "expected_improvement": 0.2,
        "execution_cost": 1.0,
        "confidence": 0.9,
        "reference_gap": 1.0,
    }
    values.update(overrides)
    return UtilityAssessment(**values)


@pytest.mark.parametrize(
    ("value", "action", "reason"),
    [
        (
            assessment(feasible=False, selected_strategy=None),
            "switch",
            "NO_FEASIBLE_CANDIDATE",
        ),
        (
            assessment(reference_gap=0.0),
            "stop",
            "REFERENCE_TARGET_REACHED",
        ),
        (
            assessment(confidence=0.2),
            "switch",
            "LOW_CONFIDENCE",
        ),
        (
            assessment(expected_improvement=0.2, marginal_utility=0.1),
            "scale",
            "ADDITIONAL_SEARCH_JUSTIFIED",
        ),
        (
            assessment(expected_improvement=0.0, marginal_utility=0.0),
            "stop",
            "MARGINAL_UTILITY_EXHAUSTED",
        ),
    ],
)
def test_all_sss_branches_are_metric_derived(value, action, reason):
    decision = ChintropicStopPolicy().apply(value, analysis=None)
    assert decision.action == action
    assert decision.reason_code == reason
    assert decision.evidence["feasible"] == value.feasible


def test_policy_threshold_configuration_changes_decision_deterministically():
    policy = ChintropicStopPolicy(
        ChintropicStopConfig(
            confidence_threshold=0.5,
            improvement_threshold=0.5,
            minimum_marginal_utility=0.2,
            target_reference_gap=-1.0,
        )
    )
    decision = policy.apply(
        assessment(
            confidence=0.8,
            expected_improvement=0.4,
            marginal_utility=0.3,
        ),
        analysis=None,
    )
    assert decision.action == "stop"
    assert decision.reason_code == "MARGINAL_UTILITY_EXHAUSTED"
