from __future__ import annotations

from math import inf

import networkx as nx
import pytest

from optengine.domains.base import Domain
from optengine.domains.maxcut import MaxCut
from optengine.mathematics import ValueType
from tests.contracts import DomainContract


def make_triangle(*, target: float | None = None) -> MaxCut:
    a = MaxCut.Vertex(identifier="A")
    b = MaxCut.Vertex(identifier="B")
    c = MaxCut.Vertex(identifier="C")
    return MaxCut(
        name="triangle",
        graph=MaxCut.Graph(
            vertices=(a, b, c),
            edges=(
                MaxCut.Edge(first=a, second=b),
                MaxCut.Edge(first=b, second=c),
                MaxCut.Edge(first=a, second=c),
            ),
        ),
        parameters=MaxCut.Parameters(
            target_cut_value=target,
        ),
    )


class TestMaxCutDomainContract(DomainContract):
    def make_domain(self) -> Domain:
        return make_triangle()

    def make_candidate(self, domain: Domain):
        assert isinstance(domain, MaxCut)
        a, b, c = domain.V
        return MaxCut.Candidate(
            _domain=domain,
            partition=MaxCut.Partition(assignments={a: 1, b: 0, c: 0}),
            native_score=-2.0,
            strategy="contract",
        )


def test_maxcut_object_collaboration_and_objective() -> None:
    domain = make_triangle(target=2.0)
    a, b, c = domain.V
    assert domain.graph.vertex("A") is a
    assert domain.graph.total_weight == 3.0
    assert not domain.graph.weighted
    assert domain.graph.to_dict()["edges"][0]["first"] == "A"
    assert domain.summary["vertices"] == 3
    assert domain.summary["parameters"]["target_cut_value"] == 2.0

    expression = domain.objective.expression
    assert expression.curve.input_types == (
        ValueType.BINARY,
        ValueType.BINARY,
        ValueType.BINARY,
    )
    assert expression.curve.input_count == 3
    assert expression.curve.degree == 2
    assert not expression.curve.constrained
    assert expression.evaluate({"A": 1, "B": 0, "C": 0}) == 2.0

    partition = MaxCut.Partition(assignments={a: 1, b: 0, c: 0})
    assert domain.objective.evaluate(partition) == 2.0
    assert domain.E[0].crosses(partition)
    assert domain.E[0].cut_value(partition) == 1.0
    assert not domain.E[1].crosses(partition)
    assert domain.E[1].cut_value(partition) == 0.0

    candidate = MaxCut.Candidate(
        _domain=domain,
        partition=partition,
        native_score=-2.0,
        strategy="manual",
    )
    evaluation = domain.interpret(candidate)
    assert evaluation.feasible
    assert evaluation.cut_value == 2.0
    assert evaluation.quality == 2.0
    assert evaluation.target_reached
    assert len(evaluation.cut_edges) == 2
    assert evaluation.state.code == "feasible"
    assert candidate.to_dict()["selected"] == ["A"]
    assert set(candidate.to_dict()["unselected"]) == {"B", "C"}


def test_maxcut_infeasible_candidate_and_partition_errors() -> None:
    domain = make_triangle()
    a, b, _ = domain.V
    partial = MaxCut.Candidate(
        _domain=domain,
        partition=MaxCut.Partition(assignments={a: 1, b: 0}),
        native_score=None,
        strategy="partial",
    )
    evaluation = domain.interpret(partial)
    assert not evaluation.feasible
    assert evaluation.cut_value is None
    assert evaluation.cut_edges == ()
    assert evaluation.quality is None
    assert not evaluation.target_reached
    assert evaluation.state.code == "infeasible"

    with pytest.raises(ValueError, match="binary"):
        MaxCut.Partition(assignments={a: 2})
    with pytest.raises(ValueError, match="missing"):
        MaxCut.Partition(assignments={a: 1}).side_of(b)


def test_maxcut_validation_errors() -> None:
    a = MaxCut.Vertex(identifier="A")
    b = MaxCut.Vertex(identifier="B")
    outsider = MaxCut.Vertex(identifier="outside")

    with pytest.raises(ValueError, match="self-loop"):
        MaxCut.Edge(first=a, second=a)
    with pytest.raises(ValueError, match="finite"):
        MaxCut.Edge(first=a, second=b, weight=inf)
    with pytest.raises(ValueError, match="at least one"):
        MaxCut.Graph(vertices=(), edges=())
    with pytest.raises(ValueError, match="vertices must be unique"):
        MaxCut.Graph(vertices=(a, a), edges=())
    edge = MaxCut.Edge(first=a, second=b)
    with pytest.raises(ValueError, match="edges must be unique"):
        MaxCut.Graph(vertices=(a, b), edges=(edge, edge))
    with pytest.raises(ValueError, match="unknown vertex"):
        MaxCut.Graph(
            vertices=(a, b),
            edges=(MaxCut.Edge(first=a, second=outsider),),
        )
    graph = MaxCut.Graph(vertices=(a, b), edges=(edge,))
    with pytest.raises(KeyError, match="Unknown"):
        graph.vertex("missing")
    with pytest.raises(ValueError, match="target_cut_value"):
        MaxCut.Parameters(target_cut_value=inf)
    with pytest.raises(ValueError, match="name"):
        MaxCut(name=" ", graph=graph)


def test_maxcut_networkx_adapter_and_rejections() -> None:
    graph = nx.Graph()
    graph.add_edge("A", "B", weight=2.5)
    domain = MaxCut.from_networkx(graph, name="weighted")
    assert domain.graph.weighted
    assert domain.graph.total_weight == 2.5
    assert domain.graph.vertex("A").variable.value_type is ValueType.BINARY

    with pytest.raises(TypeError, match="NetworkX"):
        MaxCut.from_networkx(object())
    directed = nx.DiGraph()
    directed.add_edge(1, 2)
    with pytest.raises(ValueError, match="undirected"):
        MaxCut.from_networkx(directed)
    loop = nx.Graph()
    loop.add_edge(1, 1)
    with pytest.raises(ValueError, match="self-loop"):
        MaxCut.from_networkx(loop)
