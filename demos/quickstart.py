from __future__ import annotations

import networkx as nx

import optengine
from optengine.domains.maxcut import MaxCutDomain
from optengine.explainers.default import DefaultExplainer
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.presets.maxcut import maxcut_registry
from optengine.writers.json import JsonRecommendationWriter


def build_quickstart_input() -> nx.Graph:
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


def main() -> None:
    recommendation = optengine.run(
        build_quickstart_input(),
        domain=MaxCutDomain(),
        registry=maxcut_registry(),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        requested_strategies=(
            "maxcut-exact",
            "maxcut-local-annealing",
        ),
        render=True,
        title="OptEngine :: Quickstart",
        run_name="quickstart",
    )

    if recommendation.output_path is None:
        raise RuntimeError("Quickstart completed without an output path.")


if __name__ == "__main__":
    main()
