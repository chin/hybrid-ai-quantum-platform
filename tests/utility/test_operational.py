from __future__ import annotations

from optengine.utility.operational import OperationalUtilityModel

from tests.conftest import make_evaluation


def test_no_evaluations_returns_infeasible_assessment() -> None:
    assessment = OperationalUtilityModel().assess(
        [],
        analysis=None,
    )

    assert assessment.selected_strategy is None
    assert assessment.feasible is False
    assert assessment.strategies == ()


def test_selects_highest_utility_feasible_strategy() -> None:
    assessment = OperationalUtilityModel().assess(
        [
            make_evaluation(strategy="lower", quality=1.0),
            make_evaluation(strategy="higher", quality=2.0),
        ],
        analysis=None,
    )

    assert assessment.selected_strategy == "higher"
    assert assessment.utility == 2.0


def test_reference_gap_uses_reference_evaluation() -> None:
    assessment = OperationalUtilityModel().assess(
        [
            make_evaluation(
                strategy="reference",
                quality=4.0,
                is_reference=True,
            ),
            make_evaluation(
                strategy="candidate",
                quality=3.0,
                confidence=0.8,
            ),
        ],
        analysis=None,
    )

    values = {item.strategy: item for item in assessment.strategies}

    assert values["reference"].reference_gap == 0.0
    assert values["candidate"].reference_gap == 1.0
    assert values["reference"].confidence == 1.0


def test_explicit_utility_inputs_are_preserved() -> None:
    assessment = OperationalUtilityModel().assess(
        [
            make_evaluation(
                strategy="candidate",
                quality=3.0,
                confidence=0.74,
                expected_improvement=0.06,
                estimated_cost=0.01,
            )
        ],
        analysis=None,
    )

    assert assessment.confidence == 0.74
    assert assessment.expected_improvement == 0.06
    assert assessment.execution_cost == 0.01
