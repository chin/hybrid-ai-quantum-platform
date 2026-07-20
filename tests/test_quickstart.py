from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

import optengine as ope
from optengine.domains.maxcut import MaxCutDomain
from optengine.explainers.default import DefaultExplainer
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.presets.maxcut import maxcut_registry
from optengine.recommendation import Recommendation
from optengine.writers.json import JsonRecommendationWriter


def build_test_graph() -> nx.Graph:
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


def test_quickstart_run_returns_recommendation(
    tmp_path: Path,
) -> None:
    recommendation = ope.run(
        build_test_graph(),
        domain=MaxCutDomain(),
        registry=maxcut_registry(),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        requested_strategies=("maxcut-exact",),
        output_dir=tmp_path,
        run_name="test",
    )

    assert isinstance(recommendation, Recommendation)
    assert recommendation.analysis is not None
    assert len(recommendation.evaluations) == 1
    assert recommendation.evaluations[0].strategy == "maxcut-exact"
    assert recommendation.evaluations[0].feasible is True
    assert recommendation.decision is not None
    assert recommendation.explanation is not None
    assert recommendation.output_path is not None

    output_path = Path(recommendation.output_path)
    assert output_path.exists()
    assert output_path.parent == tmp_path

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    sample = payload["evaluations"][0]["candidate"]["values"]["sample"]
    assert sample
    assert set(sample.values()) <= {0, 1}


def test_quickstart_runs_exact_and_local_annealing(
    tmp_path: Path,
) -> None:
    recommendation = ope.run(
        build_test_graph(),
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
        run_name="two-strategies",
    )

    assert {
        evaluation.strategy
        for evaluation in recommendation.evaluations
    } == {
        "maxcut-exact",
        "maxcut-local-annealing",
    }
    assert all(
        evaluation.feasible
        for evaluation in recommendation.evaluations
    )
    assert recommendation.decision is not None
    assert recommendation.decision.selected_strategy in {
        evaluation.strategy
        for evaluation in recommendation.evaluations
    }

    payload = json.loads(
        Path(recommendation.output_path).read_text(encoding="utf-8")
    )
    assert len(payload["evaluations"]) == 2
