from __future__ import annotations

from optengine.policy.chintropic_stop import ChintropicStopPolicy

from tests.conftest import make_evaluation


def test_no_evaluations_switches() -> None:
    decision = ChintropicStopPolicy().apply(
        [],
        analysis=None,
    )

    assert decision.action == "switch"
    assert decision.selected_strategy is None
    assert decision.reason_code


def test_no_feasible_evaluations_switches() -> None:
    decision = ChintropicStopPolicy().apply(
        [make_evaluation(feasible=False)],
        analysis=None,
    )

    assert decision.action == "switch"
    assert decision.selected_strategy is None


def test_high_confidence_and_improvement_scales() -> None:
    decision = ChintropicStopPolicy().apply(
        [
            make_evaluation(
                strategy="scale-candidate",
                confidence=0.74,
                expected_improvement=0.06,
            )
        ],
        analysis=None,
    )

    assert decision.action == "scale"
    assert decision.selected_strategy == "scale-candidate"


def test_low_confidence_switches() -> None:
    decision = ChintropicStopPolicy().apply(
        [
            make_evaluation(
                strategy="switch-candidate",
                confidence=0.60,
                expected_improvement=0.06,
            )
        ],
        analysis=None,
    )

    assert decision.action == "switch"
    assert decision.selected_strategy == "switch-candidate"


def test_low_marginal_improvement_stops() -> None:
    decision = ChintropicStopPolicy().apply(
        [
            make_evaluation(
                strategy="stop-candidate",
                confidence=0.80,
                expected_improvement=0.01,
            )
        ],
        analysis=None,
    )

    assert decision.action == "stop"
    assert decision.selected_strategy == "stop-candidate"


def test_best_feasible_evaluation_is_selected() -> None:
    decision = ChintropicStopPolicy().apply(
        [
            make_evaluation(
                strategy="lower",
                quality=1.0,
                confidence=0.8,
                expected_improvement=0.01,
            ),
            make_evaluation(
                strategy="higher",
                quality=2.0,
                confidence=0.8,
                expected_improvement=0.01,
            ),
        ],
        analysis=None,
    )

    assert decision.selected_strategy == "higher"


def test_tie_selection_is_deterministic() -> None:
    evaluations = [
        make_evaluation(strategy="first", quality=2.0),
        make_evaluation(strategy="second", quality=2.0),
    ]

    first = ChintropicStopPolicy().apply(evaluations, analysis=None)
    second = ChintropicStopPolicy().apply(evaluations, analysis=None)

    assert first.selected_strategy == "first"
    assert second == first
