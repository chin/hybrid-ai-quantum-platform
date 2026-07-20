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
    ) -> QuadraticBinaryInterpretation:
        if not isinstance(input_data, nx.Graph):
            raise TypeError("Max-Cut input must be a NetworkX graph.")

        if input_data.is_directed():
            raise ValueError("Max-Cut requires an undirected graph.")

        if nx.number_of_selfloops(input_data):
            raise ValueError("Max-Cut does not support self-loop edges.")

        linear: dict[Any, float] = {node: 0.0 for node in input_data.nodes}
        quadratic: dict[tuple[Any, Any], float] = {}

        weighted = False

        for u, v, data in input_data.edges(data=True):
            weight = float(data.get("weight", 1.0))
            if not weight == weight or weight in (float("inf"), float("-inf")):
                raise ValueError("Max-Cut edge weights must be finite.")

            weighted = weighted or weight != 1.0
            linear[u] += weight
            linear[v] += weight

            pair = tuple(sorted((u, v), key=repr))
            quadratic[pair] = quadratic.get(pair, 0.0) - (2.0 * weight)

        return QuadraticBinaryInterpretation(
            domain=self.name,
            summary={
                "nodes": input_data.number_of_nodes(),
                "edges": input_data.number_of_edges(),
                "weighted": weighted,
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
        sample = candidate.values.get("sample")

        if not isinstance(sample, dict):
            sample = dict(sample or {})

        expected_nodes = set(graph.nodes)
        actual_nodes = set(sample)

        if actual_nodes != expected_nodes:
            raise ValueError(
                "Invalid Max-Cut candidate assignment: "
                "candidate nodes do not match graph nodes."
            )

        normalized_sample = {node: int(value) for node, value in sample.items()}

        if any(value not in (0, 1) for value in normalized_sample.values()):
            raise ValueError(
                "Invalid Max-Cut candidate assignment: values must be binary."
            )

        cut_value = 0.0
        cut_edges: list[tuple[Any, Any]] = []

        for u, v, data in graph.edges(data=True):
            if normalized_sample[u] != normalized_sample[v]:
                cut_value += float(data.get("weight", 1.0))
                cut_edges.append((u, v))

        is_reference = bool(
            candidate.metadata.get("is_reference")
            or candidate.native_metrics.get("is_reference")
        )

        confidence = (
            1.0
            if is_reference
            else float(candidate.native_metrics.get("confidence", 0.75))
        )
        expected_improvement = float(
            candidate.native_metrics.get("expected_improvement", 0.0)
        )
        execution_cost = (
            candidate.resource_cost
            if candidate.resource_cost is not None
            else candidate.runtime_s
        )

        return Evaluation(
            strategy=strategy.name,
            candidate=candidate,
            feasible=True,
            quality=cut_value,
            metrics={
                "cut_value": cut_value,
                "cut_edges": cut_edges,
                "runtime_s": candidate.runtime_s,
            },
            reference={
                "is_reference": is_reference,
            },
            utility_inputs={
                "feasible": True,
                "quality": cut_value,
                "confidence": confidence,
                "expected_improvement": expected_improvement,
                "execution_cost": execution_cost,
                "is_reference": is_reference,
            },
            provenance={
                "domain": self.name,
            },
        )
