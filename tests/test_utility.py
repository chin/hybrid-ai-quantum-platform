from __future__ import annotations

from dataclasses import replace

import pytest

from optengine.analysis import Analyzer
from optengine.catalog import Catalog
from optengine.decision import Scale, Stop, Switch
from optengine.policy.chintropic_stop import (
    ChintropicStopConfig,
    ChintropicStopPolicy,
)
from optengine.utility.base import Assessment, StrategyAssessment
from optengine.utility.operational import OperationalUtility
from optengine.utility.optchin import OptChinUtility
from tests.support import (
    ExampleDomain,
    ExampleFormulation,
    ExampleOperation,
    ExampleSolver,
)


def _analysis_and_executions(*solvers: ExampleSolver):
    analysis = Analyzer().analyze(
        ExampleDomain(),
        Catalog(
            formulations=(ExampleFormulation(),),
            operations=(ExampleOperation(limit=2),),
            solvers=solvers,
        ),
    )
    return analysis, tuple(strategy.execute() for strategy in analysis.strategies)


def test_operational_utility_ranks_reference_and_candidate() -> None:
    analysis, executions = _analysis_and_executions(
        ExampleSolver(
            name="reference",
            values={"x": 1, "y": 1},
            reference_flag=True,
            confidence=1.0,
            expected_improvement=0.0,
            cost=0.02,
        ),
        ExampleSolver(
            name="candidate",
            values={"x": 0, "y": 1},
            confidence=0.8,
            expected_improvement=0.1,
            cost=0.01,
        ),
    )
    assessment = OperationalUtility().assess(
        executions,
        analysis,
    )

    assert assessment.feasible
    assert assessment.selected_strategy is not None
    assert assessment.best is not None
    assert assessment.best.strategy == assessment.selected_strategy
    reference = assessment.for_strategy(
        "example:example-formulation:example-operation:reference"
    )
    candidate = assessment.for_strategy(
        "example:example-formulation:example-operation:candidate"
    )
    assert reference.reference_gap == 0.0
    assert candidate.reference_gap == 1.0
    assert reference.confidence == 1.0
    assert candidate.marginal_utility == pytest.approx(0.09)
    assert assessment.dominates(
        reference.strategy,
        candidate.strategy,
    )
    assert not assessment.dominates(
        candidate.strategy,
        reference.strategy,
    )
    assert assessment.to_dict()["strategies"]


def test_operational_utility_retains_failed_execution() -> None:
    analysis, executions = _analysis_and_executions(
        ExampleSolver(name="failed", fail=True),
    )
    assessment = OperationalUtility().assess(
        executions,
        analysis,
    )
    assert not assessment.feasible
    assert assessment.selected_strategy is None
    assert assessment.utility is None
    assert assessment.strategies[0].evidence["execution_status"] == "failed"
    assert assessment.evidence == {
        "execution_count": 1,
        "successful_count": 0,
        "feasible_count": 0,
    }


def test_assessment_helpers_are_deterministic_and_exhaustive() -> None:
    first = StrategyAssessment(
        strategy="b",
        feasible=True,
        quality=1.0,
        utility=1.0,
        marginal_utility=0.0,
        expected_improvement=0.0,
        execution_cost=0.0,
        confidence=1.0,
        reference_gap=0.0,
    )
    second = replace(first, strategy="a")
    missing = replace(
        first,
        strategy="missing",
        feasible=False,
        utility=None,
    )
    assessment = Assessment(
        selected_strategy="a",
        feasible=True,
        utility=1.0,
        marginal_utility=0.0,
        expected_improvement=0.0,
        execution_cost=0.0,
        confidence=1.0,
        reference_gap=0.0,
        strategies=(first, missing, second),
    )
    assert tuple(item.strategy for item in assessment.ranked) == (
        "a",
        "b",
        "missing",
    )
    assert assessment.best == second
    assert assessment.for_strategy("b") == first
    assert assessment.dominates("a", "missing")
    assert not assessment.dominates("missing", "a")
    with pytest.raises(KeyError, match="Unknown"):
        assessment.for_strategy("unknown")
    assert first.to_dict()["strategy"] == "b"


def test_optchin_utility_accepts_assessment_or_mapping() -> None:
    analysis, executions = _analysis_and_executions(
        ExampleSolver(name="one"),
    )
    expected = OperationalUtility().assess(
        executions,
        analysis,
    )
    assert (
        OptChinUtility(lambda payload: expected).assess(
            executions,
            analysis,
        )
        is expected
    )

    captured = {}

    def assessor(payload):
        captured.update(payload)
        return {
            "selected_strategy": "private",
            "feasible": True,
            "utility": "4.5",
            "marginal_utility": "0.5",
            "expected_improvement": "0.6",
            "execution_cost": "0.1",
            "confidence": "0.9",
            "reference_gap": "0.0",
            "strategies": [
                {
                    "strategy": "private",
                    "feasible": True,
                    "quality": 4.5,
                    "utility": 4.5,
                }
            ],
            "evidence": {"source": "optchin"},
        }

    assessment = OptChinUtility(assessor).assess(
        executions,
        analysis,
    )
    assert assessment.selected_strategy == "private"
    assert assessment.utility == 4.5
    assert assessment.strategies[0].quality == 4.5
    assert captured["analysis"]["fingerprint"] == analysis.fingerprint
    assert len(captured["executions"]) == 1

    payload_without_analysis = OptChinUtility._payload(
        executions,
        None,
    )
    assert payload_without_analysis["analysis"] is None

    with pytest.raises(TypeError, match="Assessment or a mapping"):
        OptChinUtility(lambda payload: object()).assess(
            executions,
            analysis,
        )
    with pytest.raises(TypeError, match="must be a mapping"):
        OptChinUtility(
            lambda payload: {
                "strategies": ["invalid"],
            }
        ).assess(executions, analysis)


@pytest.mark.parametrize(
    ("assessment", "decision_type", "reason"),
    [
        (
            Assessment(
                selected_strategy=None,
                feasible=False,
                utility=None,
                marginal_utility=None,
                expected_improvement=None,
                execution_cost=None,
                confidence=None,
                reference_gap=None,
            ),
            Switch,
            "NO_FEASIBLE_CANDIDATE",
        ),
        (
            Assessment(
                selected_strategy="s",
                feasible=True,
                utility=1.0,
                marginal_utility=0.0,
                expected_improvement=0.0,
                execution_cost=0.0,
                confidence=1.0,
                reference_gap=0.0,
            ),
            Stop,
            "REFERENCE_TARGET_REACHED",
        ),
        (
            Assessment(
                selected_strategy="s",
                feasible=True,
                utility=1.0,
                marginal_utility=0.2,
                expected_improvement=0.2,
                execution_cost=0.0,
                confidence=0.1,
                reference_gap=None,
            ),
            Switch,
            "LOW_CONFIDENCE",
        ),
        (
            Assessment(
                selected_strategy="s",
                feasible=True,
                utility=1.0,
                marginal_utility=0.1,
                expected_improvement=0.1,
                execution_cost=0.0,
                confidence=0.9,
                reference_gap=None,
            ),
            Scale,
            "ADDITIONAL_SEARCH_JUSTIFIED",
        ),
        (
            Assessment(
                selected_strategy="s",
                feasible=True,
                utility=1.0,
                marginal_utility=-0.1,
                expected_improvement=0.01,
                execution_cost=0.1,
                confidence=0.9,
                reference_gap=None,
            ),
            Stop,
            "MARGINAL_UTILITY_EXHAUSTED",
        ),
    ],
)
def test_chintropic_policy_full_decision_matrix(
    assessment: Assessment,
    decision_type: type,
    reason: str,
) -> None:
    policy = ChintropicStopPolicy(
        ChintropicStopConfig(
            confidence_threshold=0.7,
            improvement_threshold=0.05,
            minimum_marginal_utility=0.0,
            target_reference_gap=0.0,
        )
    )
    decision = policy.apply(assessment)
    assert isinstance(decision, decision_type)
    assert decision.reason_code == reason
    assert decision.render() == decision.action
    assert decision.next_action == decision.action
    assert decision.to_dict()["should_continue"] == (decision.action != "stop")
