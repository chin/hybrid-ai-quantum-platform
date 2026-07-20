from __future__ import annotations

from optengine.analysis import Analysis, StrategySummary
from optengine.candidate import Candidate
from optengine.evaluation import Evaluation
from optengine.utility.base import UtilityAssessment
from optengine.utility.optchin import OptChinUtilityAdapter


def _evaluation() -> Evaluation:
    candidate = Candidate(
        strategy="candidate",
        formulation="qubo",
        operation="annealing",
        solver="local",
        values={"sample": {0: 0, 1: 1}},
        native_score=-1.0,
        status="complete",
        runtime_s=0.25,
        resource_cost=10.0,
        native_metrics={"confidence": 0.8},
        provenance={"library": "test"},
    )
    return Evaluation(
        strategy="candidate",
        candidate=candidate,
        feasible=True,
        quality=1.0,
        metrics={"objective": 1.0},
        utility_inputs={"expected_improvement": 0.2},
    )


def _analysis() -> Analysis:
    return Analysis(
        interpretation={"kind": "test"},
        strategies=(
            StrategySummary(
                name="candidate",
                domain="test",
                formulation="qubo",
                operation="annealing",
                solver="local",
            ),
        ),
    )


def test_adapter_passes_structured_evidence_to_mock_assessor():
    captured = {}

    def assessor(payload):
        captured.update(payload)
        return {
            "selected_strategy": "candidate",
            "feasible": True,
            "utility": 0.9,
            "marginal_utility": 0.1,
            "expected_improvement": 0.2,
            "execution_cost": 10.0,
            "confidence": 0.8,
            "reference_gap": 0.0,
            "evidence": {"source": "mock-optchin"},
        }

    result = OptChinUtilityAdapter(assessor).assess([_evaluation()], _analysis())

    assert result.selected_strategy == "candidate"
    assert result.evidence == {"source": "mock-optchin"}
    assert captured["analysis"]["interpretation"] == {"kind": "test"}
    assert captured["evaluations"][0]["candidate"]["solver"] == "local"
    assert captured["evaluations"][0]["utility_inputs"] == {"expected_improvement": 0.2}


def test_adapter_accepts_native_utility_assessment():
    expected = UtilityAssessment(
        selected_strategy="candidate",
        feasible=True,
        utility=1.0,
        marginal_utility=0.0,
        expected_improvement=0.0,
        execution_cost=1.0,
        confidence=1.0,
        reference_gap=0.0,
    )
    adapter = OptChinUtilityAdapter(lambda payload: expected)
    assert adapter.assess([_evaluation()], _analysis()) is expected


def test_adapter_rejects_invalid_result_type():
    adapter = OptChinUtilityAdapter(lambda payload: object())
    try:
        adapter.assess([_evaluation()], _analysis())
    except TypeError as error:
        assert "UtilityAssessment or a mapping" in str(error)
    else:
        raise AssertionError("invalid assessor result was accepted")
