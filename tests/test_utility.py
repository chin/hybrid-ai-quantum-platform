from __future__ import annotations

from optengine.utility.operational import OperationalUtilityModel
from optengine.utility.optchin import OptChinUtilityAdapter

from tests.conftest import make_evaluation


def test_operational_utility_selects_best_feasible_result() -> None:
    assessment = OperationalUtilityModel().assess(
        [
            make_evaluation(strategy="lower", quality=1.0),
            make_evaluation(strategy="higher", quality=2.0),
        ],
        analysis=None,
    )

    assert assessment.selected_strategy == "higher"
    assert assessment.utility == 2.0


def test_operational_utility_calculates_reference_gap() -> None:
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
            ),
        ],
        analysis=None,
    )

    by_strategy = {item.strategy: item for item in assessment.strategies}
    assert by_strategy["candidate"].reference_gap == 1.0


def test_optchin_adapter_invokes_external_assessor() -> None:
    captured = {}

    def assessor(payload):
        captured.update(payload)
        return {
            "selected_strategy": "candidate",
            "feasible": True,
            "utility": 2.0,
            "marginal_utility": 0.5,
            "expected_improvement": 0.6,
            "execution_cost": 0.1,
            "confidence": 0.9,
            "reference_gap": 0.0,
            "evidence": {"source": "optchin"},
        }

    assessment = OptChinUtilityAdapter(assessor).assess(
        [make_evaluation(strategy="candidate", quality=2.0)],
        analysis=None,
    )

    assert captured["evaluations"][0]["strategy"] == "candidate"
    assert assessment.evidence == {"source": "optchin"}
