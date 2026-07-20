from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

import optengine
from optengine.domains.maxcut import MaxCutDomain
from optengine.explainers.default import DefaultExplainer
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.presets.maxcut import maxcut_registry
from optengine.writers.json import JsonRecommendationWriter


def test_maxcut_vertical_slice_end_to_end(
    tmp_path: Path,
) -> None:
    graph = nx.cycle_graph(4)
    nx.set_edge_attributes(graph, 1.0, "weight")

    recommendation = optengine.run(
        graph,
        domain=MaxCutDomain(),
        registry=maxcut_registry(),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        requested_strategies=(
            "maxcut-exact",
            "maxcut-local-annealing",
        ),
        output_dir=tmp_path,
        run_name="maxcut-integration",
    )

    evaluations = {
        evaluation.strategy: evaluation
        for evaluation in recommendation.evaluations
    }

    assert set(evaluations) == {
        "maxcut-exact",
        "maxcut-local-annealing",
    }
    assert evaluations["maxcut-exact"].quality == 4.0
    assert all(
        evaluation.feasible
        for evaluation in evaluations.values()
    )
    assert recommendation.decision is not None
    assert recommendation.explanation is not None
    assert recommendation.output_path is not None

    path = Path(recommendation.output_path)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["decision"]["action"] in {
        "stop",
        "switch",
        "scale",
    }
    assert len(payload["evaluations"]) == 2
    assert payload["output_path"] == str(path)
    assert payload["logs"][-1] == "OptEngine finished."
