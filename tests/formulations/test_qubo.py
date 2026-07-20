from __future__ import annotations

import dimod
import networkx as nx
import pytest

from optengine.domains.maxcut import MaxCutDomain
from optengine.formulations.qubo import QUBOFormulation, QUBOModel
from optengine.interpretation import Interpretation


def test_single_edge_qubo_coefficients() -> None:
    graph = nx.Graph()
    graph.add_edge(0, 1, weight=2.0)
    interpretation = MaxCutDomain().interpret_input(graph)

    model = QUBOFormulation().build(interpretation, {})

    assert isinstance(model, QUBOModel)
    assert model.coefficients[(0, 0)] == -2.0
    assert model.coefficients[(1, 1)] == -2.0
    assert model.coefficients[(0, 1)] == 4.0


def test_better_cut_has_lower_energy() -> None:
    graph = nx.Graph()
    graph.add_edge(0, 1, weight=2.0)
    model = QUBOFormulation().build(
        MaxCutDomain().interpret_input(graph),
        {},
    )

    uncut_energy = model.payload.energy({0: 0, 1: 0})
    cut_energy = model.payload.energy({0: 0, 1: 1})

    assert cut_energy < uncut_energy
    assert cut_energy == -2.0


def test_exact_minimum_matches_known_max_cut() -> None:
    graph = nx.cycle_graph(4)
    nx.set_edge_attributes(graph, 1.0, "weight")
    model = QUBOFormulation().build(
        MaxCutDomain().interpret_input(graph),
        {},
    )

    result = dimod.ExactSolver().sample(model.payload).first

    assert float(result.energy) == -4.0


def test_unsupported_interpretation_is_rejected() -> None:
    interpretation = Interpretation(
        domain="unsupported",
        summary={},
    )
    formulation = QUBOFormulation()

    assert formulation.supports(interpretation) is False

    with pytest.raises(TypeError, match="quadratic binary"):
        formulation.build(interpretation, {})
