from __future__ import annotations

import networkx as nx
import pytest

from optengine.candidate import Candidate
from optengine.domains.maxcut import MaxCutDomain
from optengine.formulations.qubo import QUBOFormulation
from optengine.operations.exact import ExactSearchOperation
from optengine.solvers.dimod_exact import DimodExactSolver
from optengine.strategy import Strategy


def make_strategy(domain: MaxCutDomain) -> Strategy:
    return Strategy(
        name="maxcut-test",
        domain=domain,
        formulation=QUBOFormulation(),
        operation=ExactSearchOperation(),
        solver=DimodExactSolver(),
    )


def make_candidate(sample: dict[int, int]) -> Candidate:
    return Candidate(
        strategy="maxcut-test",
        formulation="qubo",
        operation="exact-search",
        solver="dimod-exact",
        values={"sample": sample},
        native_score=None,
        status="complete",
        metadata={},
        provenance={},
    )


def test_interpret_input_accepts_weighted_undirected_graph() -> None:
    graph = nx.Graph()
    graph.add_weighted_edges_from([(0, 1, 2.0), (1, 2, 3.0)])

    interpretation = MaxCutDomain().interpret_input(graph)

    assert interpretation.domain == "max-cut"
    assert interpretation.summary["nodes"] == 3
    assert interpretation.summary["edges"] == 2
    assert interpretation.objective_sense == "maximize"
    assert interpretation.domain_data is graph


def test_interpret_input_rejects_non_graph() -> None:
    with pytest.raises(TypeError, match="NetworkX graph"):
        MaxCutDomain().interpret_input({"not": "a graph"})


def test_interpret_input_rejects_directed_graph() -> None:
    graph = nx.DiGraph()
    graph.add_edge(0, 1)

    with pytest.raises(ValueError, match="undirected"):
        MaxCutDomain().interpret_input(graph)


def test_empty_graph_has_empty_interpretation() -> None:
    interpretation = MaxCutDomain().interpret_input(nx.Graph())

    assert interpretation.summary["nodes"] == 0
    assert interpretation.summary["edges"] == 0
    assert interpretation.variables == ()


def test_default_and_custom_edge_weights_are_interpreted() -> None:
    graph = nx.Graph()
    graph.add_edge(0, 1)
    graph.add_edge(1, 2, weight=3.0)

    interpretation = MaxCutDomain().interpret_input(graph)

    assert interpretation.linear[0] == 1.0
    assert interpretation.linear[1] == 4.0
    assert interpretation.linear[2] == 3.0
    assert interpretation.quadratic[(0, 1)] == -2.0
    assert interpretation.quadratic[(1, 2)] == -6.0


def test_interpret_candidate_calculates_weighted_cut() -> None:
    graph = nx.Graph()
    graph.add_weighted_edges_from([(0, 1, 2.0), (1, 2, 3.0)])
    domain = MaxCutDomain()
    interpretation = domain.interpret_input(graph)

    evaluation = domain.interpret_candidate(
        interpretation,
        make_candidate({0: 0, 1: 1, 2: 0}),
        make_strategy(domain),
    )

    assert evaluation.feasible is True
    assert evaluation.quality == 5.0
    assert evaluation.metrics["cut_value"] == 5.0


@pytest.mark.parametrize(
    "sample",
    [
        {0: 0},
        {0: 0, 1: 1, 2: 0},
        {0: 0, 1: 2},
    ],
)
def test_interpret_candidate_rejects_invalid_assignment(
    sample: dict[int, int],
) -> None:
    graph = nx.Graph()
    graph.add_edge(0, 1)
    domain = MaxCutDomain()
    interpretation = domain.interpret_input(graph)

    with pytest.raises(ValueError, match="candidate assignment"):
        domain.interpret_candidate(
            interpretation,
            make_candidate(sample),
            make_strategy(domain),
        )


def test_complementary_partitions_have_equal_cut_value() -> None:
    graph = nx.Graph()
    graph.add_weighted_edges_from(
        [(0, 1, 1.0), (1, 2, 2.0), (0, 2, 3.0)]
    )
    domain = MaxCutDomain()
    interpretation = domain.interpret_input(graph)
    strategy = make_strategy(domain)

    first = domain.interpret_candidate(
        interpretation,
        make_candidate({0: 0, 1: 1, 2: 0}),
        strategy,
    )
    complement = domain.interpret_candidate(
        interpretation,
        make_candidate({0: 1, 1: 0, 2: 1}),
        strategy,
    )

    assert first.quality == complement.quality
