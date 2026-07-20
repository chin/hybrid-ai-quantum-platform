from __future__ import annotations

from optengine.analysis import Analysis
from optengine.decision import Decision
from optengine.explainers.default import DefaultExplainer

from tests.conftest import make_evaluation


def test_explanation_retains_action_strategy_and_evidence() -> None:
    decision = Decision(
        action="stop",
        selected_strategy="exact",
        reason_code="REFERENCE_REACHED",
        evidence={"quality": 4.0},
    )

    explanation = DefaultExplainer().explain(
        decision=decision,
        evaluations=[make_evaluation(strategy="exact", quality=4.0)],
        analysis=Analysis(interpretation={}, strategies=()),
    )

    assert "stop" in explanation.summary.lower()
    assert "exact" in explanation.summary
    assert explanation.selected_strategy == "exact"
    assert explanation.evidence == {"quality": 4.0}


def test_explanation_handles_no_selected_strategy() -> None:
    decision = Decision(
        action="switch",
        selected_strategy=None,
        reason_code="NO_FEASIBLE_CANDIDATE",
    )

    explanation = DefaultExplainer().explain(
        decision=decision,
        evaluations=[],
        analysis=Analysis(interpretation={}, strategies=()),
    )

    assert "switch" in explanation.summary.lower()
    assert explanation.selected_strategy is None
