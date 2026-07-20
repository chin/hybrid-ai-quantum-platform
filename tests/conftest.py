from __future__ import annotations

from typing import Any

from optengine.candidate import Candidate
from optengine.evaluation import Evaluation


def make_candidate(
    *,
    strategy: str = "candidate",
    sample: dict[Any, int] | None = None,
    native_score: float = 0.0,
) -> Candidate:
    return Candidate(
        strategy=strategy,
        formulation="qubo",
        operation="annealing",
        solver="test-solver",
        values={"sample": sample or {0: 0, 1: 1}},
        native_score=native_score,
        status="complete",
        runtime_s=0.01,
    )


def make_evaluation(
    *,
    strategy: str = "strategy",
    feasible: bool = True,
    quality: float | None = 1.0,
    utility: float | None = None,
    marginal_utility: float | None = None,
    expected_improvement: float | None = None,
    execution_cost: float | None = None,
    estimated_cost: float | None = None,
    confidence: float | None = None,
    reference_gap: float | None = None,
    is_reference: bool = False,
) -> Evaluation:
    utility_inputs = {
        key: value
        for key, value in {
            "utility": utility,
            "marginal_utility": marginal_utility,
            "expected_improvement": expected_improvement,
            "execution_cost": execution_cost,
            "estimated_cost": estimated_cost,
            "confidence": confidence,
            "reference_gap": reference_gap,
        }.items()
        if value is not None
    }

    candidate = Candidate(
        strategy=strategy,
        formulation="test-formulation",
        operation="test-operation",
        solver="test-solver",
        values={},
        native_score=None,
        status="complete",
        resource_cost=execution_cost,
        native_metrics={
            "is_reference": is_reference,
        },
        metadata={
            "is_reference": is_reference,
        },
    )

    return Evaluation(
        strategy=strategy,
        candidate=candidate,
        feasible=feasible,
        quality=quality,
        metrics={},
        reference={
            "is_reference": is_reference,
        },
        utility_inputs=utility_inputs,
    )
