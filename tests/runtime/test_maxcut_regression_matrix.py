from __future__ import annotations

from pathlib import Path

import networkx as nx
import pytest

from optengine.domains.maxcut import MaxCutDomain
from optengine.explainers.default import DefaultExplainer
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.presets.maxcut import maxcut_registry
from optengine.runner import run
from optengine.writers.json import JsonRecommendationWriter


@pytest.mark.parametrize(
    ("graph", "expected"),
    [
        (nx.Graph([(0, 1)]), 1.0),
        (nx.cycle_graph(3), 2.0),
        (nx.cycle_graph(4), 4.0),
        (nx.complete_graph(4), 4.0),
        (nx.disjoint_union(nx.Graph([(0, 1)]), nx.Graph([(0, 1)])), 2.0),
    ],
)
def test_exact_reference_matrix(graph: nx.Graph, expected: float, tmp_path: Path):
    recommendation = run(
        graph,
        domain=MaxCutDomain(),
        registry=maxcut_registry(),
        requested_strategies=("maxcut-exact",),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        output_dir=tmp_path,
        run_name="maxcut-matrix",
    )
    assert recommendation.evaluations[0].quality == expected
    assert recommendation.evaluations[0].feasible is True


def test_weighted_triangle_reference(tmp_path: Path):
    graph = nx.Graph()
    graph.add_weighted_edges_from([(0, 1, 4.0), (1, 2, 2.0), (0, 2, 1.0)])
    recommendation = run(
        graph,
        domain=MaxCutDomain(),
        registry=maxcut_registry(),
        requested_strategies=("maxcut-exact",),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        output_dir=tmp_path,
        run_name="weighted-maxcut",
    )
    assert recommendation.evaluations[0].quality == 6.0


def test_isolated_node_is_retained_in_assignment(tmp_path: Path):
    graph = nx.Graph([(0, 1)])
    graph.add_node(2)
    recommendation = run(
        graph,
        domain=MaxCutDomain(),
        registry=maxcut_registry(),
        requested_strategies=("maxcut-exact",),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        output_dir=tmp_path,
        run_name="isolated-node",
    )
    sample = recommendation.evaluations[0].candidate.values["sample"]
    assert set(sample) == {0, 1, 2}
    assert recommendation.evaluations[0].quality == 1.0
