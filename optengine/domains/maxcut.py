from __future__ import annotations

from typing import Any

import networkx as nx

from optengine.candidate import Candidate
from optengine.domains.base import Domain
from optengine.evaluation import Evaluation
from optengine.interpretation import (
    Interpretation,
    QuadraticBinaryInterpretation,
)
from optengine.strategy import Strategy


class MaxCutDomain(Domain):
    name = "max-cut"

    def interpret_input(
        self,
        input_data: Any,
    ) -> Interpretation:
        if not isinstance(input_data, nx.Graph):
            raise TypeError("Max-Cut input must be a NetworkX graph.")

        if input_data.is_directed():
            raise ValueError("Max-Cut requires an undirected graph.")

        linear: dict[Any, float] = {node: 0.0 for node in input_data.nodes}
        quadratic: dict[tuple[Any, Any], float] = {}

        for u, v, data in input_data.edges(data=True):
            weight = float(data.get("weight", 1.0))

            linear[u] += weight
            linear[v] += weight

            key = tuple(sorted((u, v)))
            quadratic[key] = quadratic.get(key, 0.0) - 2.0 * weight

        return QuadraticBinaryInterpretation(
            domain=self.name,
            summary={
                "nodes": input_data.number_of_nodes(),
                "edges": input_data.number_of_edges(),
                "weighted": True,
            },
            capabilities=frozenset(
                {
                    "qubo",
                    "exact-search",
                    "annealing",
                    "qaoa",
                }
            ),
            variables=tuple(input_data.nodes),
            linear=linear,
            quadratic=quadratic,
            objective_sense="maximize",
            domain_data=input_data,
        )

    def interpret_candidate(
        self,
        interpretation: Interpretation,
        candidate: Candidate,
        strategy: Strategy,
    ) -> Evaluation:
        if not isinstance(
            interpretation,
            QuadraticBinaryInterpretation,
        ):
            raise TypeError("Max-Cut requires a quadratic binary interpretation.")

        graph: nx.Graph = interpretation.domain_data
        sample = candidate.values["sample"]
        expected_nodes = set(graph.nodes)
        actual_nodes = set(sample)

        if actual_nodes != expected_nodes:
            raise ValueError(
                "Invalid Max-Cut candidate assignment: "
                "candidate nodes do not match graph nodes."
            )

        if any(int(value) not in (0, 1) for value in sample.values()):
            raise ValueError(
                "Invalid Max-Cut candidate assignment: "
                "values must be binary."
            )

        cut = 0.0

        for u, v, data in graph.edges(data=True):
            if int(sample[u]) != int(sample[v]):
                cut += float(data.get("weight", 1.0))

        feasible = set(sample) == set(graph.nodes) and all(
            int(value) in (0, 1) for value in sample.values()
        )

        return Evaluation(
            strategy=strategy.name,
            candidate=candidate,
            feasible=feasible,
            quality=cut,
            metrics={
                "cut_value": cut,
                "runtime_s": candidate.runtime_s,
            },
            policy_evidence={
                "feasible": feasible,
                "quality": cut,
                "runtime_s": candidate.runtime_s,
            },
            provenance={
                "domain": self.name,
            },
        )
