from __future__ import annotations

import pytest

from optengine.utility.optchin import OptChinUtilityAdapter

from tests.conftest import make_evaluation


def test_adapter_calls_actual_optchin_callable() -> None:
    received = {}

    def optchin_assess(payload):
        received.update(payload)
        return {
            "selected_strategy": "candidate",
            "feasible": True,
            "utility": 7.5,
            "marginal_utility": 0.4,
            "expected_improvement": 0.5,
            "execution_cost": 0.1,
            "confidence": 0.9,
            "reference_gap": 0.0,
            "evidence": {"source": "actual-optchin"},
        }

    assessment = OptChinUtilityAdapter(optchin_assess).assess(
        [make_evaluation(strategy="candidate")],
        analysis=None,
    )

    assert received["evaluations"][0]["strategy"] == "candidate"
    assert assessment.selected_strategy == "candidate"
    assert assessment.utility == 7.5
    assert assessment.evidence["source"] == "actual-optchin"


def test_adapter_rejects_invalid_return_type() -> None:
    adapter = OptChinUtilityAdapter(lambda payload: "invalid")

    with pytest.raises(TypeError, match="must return"):
        adapter.assess(
            [make_evaluation()],
            analysis=None,
        )
