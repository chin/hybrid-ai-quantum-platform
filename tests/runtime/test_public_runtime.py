from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

import optengine
from optengine.domains.maxcut import MaxCutDomain
from optengine.explainers.default import DefaultExplainer
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.presets.maxcut import maxcut_registry
from optengine.recommendation import Recommendation
from optengine.writers.json import JsonRecommendationWriter


def test_public_run_returns_complete_recommendation_and_final_json(tmp_path: Path):
    recommendation = optengine.run(
        nx.cycle_graph(4),
        domain=MaxCutDomain(),
        registry=maxcut_registry(),
        requested_strategies=("maxcut-exact",),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        output_dir=tmp_path,
        run_name="public-runtime",
    )

    assert isinstance(recommendation, Recommendation)
    assert recommendation.analysis is not None
    assert recommendation.evaluations
    assert recommendation.utility_assessment is not None
    assert recommendation.decision is not None
    assert recommendation.explanation is not None
    assert recommendation.started_at is not None
    assert recommendation.completed_at is not None
    assert recommendation.output_path is not None

    path = Path(recommendation.output_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["run_id"] == recommendation.run_id
    assert payload["completed_at"] == recommendation.completed_at
    assert payload["output_path"] == str(path)
    assert payload["decision"]["action"] in {"stop", "switch", "scale"}
    assert payload["explanation"]["summary"]
    assert payload["logs"][0] == "OptEngine started."
    assert payload["logs"][-1] == "OptEngine finished."
