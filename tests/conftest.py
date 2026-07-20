from __future__ import annotations

from typing import Any

import networkx as nx
import pytest

from optengine.analysis import Analysis
from optengine.candidate import Candidate
from optengine.evaluation import Evaluation


@pytest.fixture
def maxcut_graph() -> nx.Graph:
    graph = nx.Graph()
    graph.add_weighted_edges_from(
        [
            (0, 1, 1.0),
            (1, 2, 1.0),
            (2, 3, 1.0),
            (3, 0, 1.0),
            (0, 2, 1.0),
        ]
    )
    return graph


@pytest.fixture
def empty_analysis() -> Analysis:
    return Analysis(
        interpretation={},
        strategies=(),
    )


def make_candidate(
    *,
    strategy: str = "candidate",
    sample: dict[Any, int] | None = None,
    native_score: float = 0.0,
    runtime_s: float = 0.01,
) -> Candidate:
    return Candidate(
        strategy=strategy,
        formulation="qubo",
        operation="annealing",
        solver="test-solver",
        values={"sample": sample or {0: 0, 1: 1}},
        native_score=native_score,
        status="complete",
        runtime_s=runtime_s,
        metadata={},
        provenance={},
    )


def make_evaluation(
    *,
    strategy: str = "candidate",
    quality: float = 1.0,
    feasible: bool = True,
    confidence: float = 0.8,
    expected_improvement: float = 0.0,
    estimated_cost: float = 0.01,
) -> Evaluation:
    return Evaluation(
        strategy=strategy,
        candidate=make_candidate(strategy=strategy),
        feasible=feasible,
        quality=quality,
        metrics={"quality": quality},
        reference={},
        policy_evidence={
            "feasible": feasible,
            "quality": quality,
            "confidence": confidence,
            "expected_improvement": expected_improvement,
            "estimated_cost": estimated_cost,
        },
        provenance={},
    )
