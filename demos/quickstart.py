from __future__ import annotations

import networkx as nx

import optengine
from optengine.domains.maxcut import MaxCut
from optengine.explainers.default import DefaultExplainer
from optengine.policy.chintropic_stop import ChintropicStopPolicy
from optengine.presets.maxcut import maxcut_catalog
from optengine.writers.json import JsonRecommendationWriter


def build_quickstart_graph() -> nx.Graph:
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


def build_quickstart_domain() -> MaxCut:
    return MaxCut.from_networkx(
        build_quickstart_graph(),
        name="quickstart-max-cut",
    )


# Transitional helper name retained for callers that imported it.
build_quickstart_input = build_quickstart_graph


def main() -> None:
    recommendation = optengine.run(
        build_quickstart_domain(),
        catalog=maxcut_catalog(),
        policy=ChintropicStopPolicy(),
        explainer=DefaultExplainer(),
        writer=JsonRecommendationWriter(),
        requested_strategies=(
            "max-cut:qubo:exact-search:dimod-exact",
            "max-cut:qubo:annealing:dwave-local",
        ),
        render=True,
        title="OptEngine :: Quickstart",
        run_name="quickstart",
    )
    if recommendation.output_path is None:
        raise RuntimeError("Quickstart completed without an output path.")


if __name__ == "__main__":
    main()
