from __future__ import annotations

import networkx as nx
import pytest

from optengine.domains.maxcut import MaxCutDomain
from optengine.formulations.qubo import QUBOFormulation
from optengine.operations.annealing import AnnealingOperation
from optengine.operations.exact import ExactSearchOperation
from optengine.solvers.dimod_exact import DimodExactSolver


def make_model(nodes: int = 2):
    graph = nx.path_graph(nodes)
    nx.set_edge_attributes(graph, 1.0, "weight")
    interpretation = MaxCutDomain().interpret_input(graph)
    return QUBOFormulation().build(interpretation, {})


def test_supports_qubo_exact_search() -> None:
    solver = DimodExactSolver()
    model = make_model()

    assert solver.supports(model, ExactSearchOperation()) is True
    assert solver.supports(model, AnnealingOperation()) is False


def test_returns_known_optimum_and_python_scalars() -> None:
    solver = DimodExactSolver()
    candidate = solver.execute(
        make_model(),
        ExactSearchOperation(max_variables=18),
        {},
        {},
    )

    assert candidate.status == "complete"
    assert candidate.native_score == -1.0
    assert set(candidate.values["sample"].values()) <= {0, 1}
    assert all(
        type(value) is int
        for value in candidate.values["sample"].values()
    )
    assert type(candidate.native_score) is float
    assert "cut_value" not in candidate.metadata


def test_rejects_model_over_exact_limit() -> None:
    solver = DimodExactSolver()

    with pytest.raises(ValueError, match="variable limit"):
        solver.execute(
            make_model(nodes=3),
            ExactSearchOperation(max_variables=2),
            {},
            {},
        )
