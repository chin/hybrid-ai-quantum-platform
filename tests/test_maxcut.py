from __future__ import annotations

import dimod
import networkx as nx
import pytest

from optengine.domains.maxcut import MaxCutDomain
from optengine.formulations.qubo import QUBOFormulation
from optengine.operations.exact import ExactSearchOperation
from optengine.solvers.dimod_exact import DimodExactSolver
from optengine.strategy import Strategy


def test_single_edge_qubo_coefficients() -> None:
    graph = nx.Graph()
    graph.add_edge(0, 1, weight=2.0)
    interpretation = MaxCutDomain().interpret_input(graph)
    model = QUBOFormulation().build(interpretation, {})

    assert model.coefficients[(0, 0)] == -2.0
    assert model.coefficients[(1, 1)] == -2.0
    assert model.coefficients[(0, 1)] == 4.0
    assert model.payload.vartype is dimod.BINARY


def test_domain_rejects_malformed_candidate() -> None:
    graph = nx.Graph()
    graph.add_edge(0, 1)
    domain = MaxCutDomain()
    interpretation = domain.interpret_input(graph)
    strategy = Strategy(
        name="exact",
        domain=domain,
        formulation=QUBOFormulation(),
        operation=ExactSearchOperation(),
        solver=DimodExactSolver(),
    )
    model = strategy.formulation.build(interpretation, {})
    candidate = (
        strategy.solver.execute(
            model,
            strategy.operation,
            {},
            {},
        )
        .with_values({"sample": {0: 0}})
        .assigned_to("exact")
    )

    with pytest.raises(ValueError, match="candidate nodes"):
        domain.interpret_candidate(
            interpretation,
            candidate,
            strategy,
        )
