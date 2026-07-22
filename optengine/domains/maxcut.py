from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from typing import Any, ClassVar, Hashable, Mapping

from optengine.candidate import Candidate as BaseCandidate
from optengine.domains.base import Domain
from optengine.evaluation import Evaluation as BaseEvaluation
from optengine.interpretation import Interpretation as BaseInterpretation
from optengine.mathematics import (
    Expression,
    LinearTerm,
    QuadraticTerm,
    ValueType,
    Variable,
)
from optengine.objective import Objective as BaseObjective


@dataclass(frozen=True, kw_only=True)
class MaxCut(Domain):
    """Weighted Max-Cut Domain aggregate.

    Input:
        G = (V, E)

    Output:
        S and V \\ S
    """

    domain_type: ClassVar[str] = "max-cut"

    @dataclass(frozen=True, kw_only=True)
    class Vertex:
        identifier: Hashable

        @property
        def variable(self) -> Variable:
            return Variable(
                identifier=self.identifier,
                value_type=ValueType.BINARY,
                lower_bound=0,
                upper_bound=1,
            )

        def to_dict(self) -> Mapping[str, Any]:
            return {"identifier": self.identifier}

    @dataclass(frozen=True, kw_only=True)
    class Edge:
        first: MaxCut.Vertex
        second: MaxCut.Vertex
        weight: float = 1.0

        def __post_init__(self) -> None:
            if self.first == self.second:
                raise ValueError("Max-Cut does not support self-loop edges.")
            if not isfinite(float(self.weight)):
                raise ValueError("Max-Cut edge weights must be finite.")

        @property
        def key(self) -> frozenset[MaxCut.Vertex]:
            return frozenset((self.first, self.second))

        def crosses(self, partition: MaxCut.Partition) -> bool:
            return partition.side_of(self.first) != partition.side_of(self.second)

        def cut_value(self, partition: MaxCut.Partition) -> float:
            return float(self.weight) if self.crosses(partition) else 0.0

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "first": self.first.identifier,
                "second": self.second.identifier,
                "weight": float(self.weight),
            }

    @dataclass(frozen=True, kw_only=True)
    class Graph:
        vertices: tuple[MaxCut.Vertex, ...]
        edges: tuple[MaxCut.Edge, ...]

        def __post_init__(self) -> None:
            if not self.vertices:
                raise ValueError("Max-Cut requires at least one vertex.")

            if len(set(self.vertices)) != len(self.vertices):
                raise ValueError("Max-Cut vertices must be unique.")

            if len({edge.key for edge in self.edges}) != len(self.edges):
                raise ValueError("Max-Cut edges must be unique.")

            known = set(self.vertices)
            for edge in self.edges:
                if edge.first not in known or edge.second not in known:
                    raise ValueError("Max-Cut edge references an unknown vertex.")

        @property
        def vertex_map(self) -> Mapping[Hashable, MaxCut.Vertex]:
            return {vertex.identifier: vertex for vertex in self.vertices}

        @property
        def total_weight(self) -> float:
            return sum(float(edge.weight) for edge in self.edges)

        @property
        def weighted(self) -> bool:
            return any(float(edge.weight) != 1.0 for edge in self.edges)

        def vertex(self, identifier: Hashable) -> MaxCut.Vertex:
            try:
                return self.vertex_map[identifier]
            except KeyError as error:
                raise KeyError(f"Unknown Max-Cut vertex: {identifier!r}") from error

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "vertices": [vertex.to_dict() for vertex in self.vertices],
                "edges": [edge.to_dict() for edge in self.edges],
            }

    @dataclass(frozen=True, kw_only=True)
    class Parameters:
        target_cut_value: float | None = None

        def __post_init__(self) -> None:
            if self.target_cut_value is not None and not isfinite(
                float(self.target_cut_value)
            ):
                raise ValueError("target_cut_value must be finite.")

        def to_dict(self) -> Mapping[str, Any]:
            return {"target_cut_value": self.target_cut_value}

    @dataclass(frozen=True, kw_only=True)
    class Objective(BaseObjective):
        domain: MaxCut
        sense: ClassVar[str] = "maximize"

        @property
        def expression(self) -> Expression:
            linear: dict[MaxCut.Vertex, float] = {
                vertex: 0.0 for vertex in self.domain.graph.vertices
            }
            quadratic: list[QuadraticTerm] = []

            for edge in self.domain.graph.edges:
                linear[edge.first] += float(edge.weight)
                linear[edge.second] += float(edge.weight)
                quadratic.append(
                    QuadraticTerm(
                        first=edge.first.variable,
                        second=edge.second.variable,
                        coefficient=-2.0 * float(edge.weight),
                    )
                )

            return Expression(
                variables=tuple(
                    vertex.variable for vertex in self.domain.graph.vertices
                ),
                linear_terms=tuple(
                    LinearTerm(
                        variable=vertex.variable,
                        coefficient=coefficient,
                    )
                    for vertex, coefficient in linear.items()
                ),
                quadratic_terms=tuple(quadratic),
            )

        def evaluate(self, partition: MaxCut.Partition) -> float:
            return sum(edge.cut_value(partition) for edge in self.domain.graph.edges)

        def decode(
            self,
            values: Mapping[Any, Any],
            *,
            result: Any,
            strategy: Any,
        ) -> BaseCandidate:
            assignments = {
                vertex: int(round(float(values.get(vertex.identifier, 0))))
                for vertex in self.domain.graph.vertices
            }
            return MaxCut.Candidate(
                _domain=self.domain,
                partition=MaxCut.Partition(assignments=assignments),
                native_score=result.native_score,
                strategy=strategy.name,
            )

    @dataclass(frozen=True, kw_only=True)
    class Interpretation(BaseInterpretation):
        domain: MaxCut
        objective: MaxCut.Objective

    @dataclass(frozen=True, kw_only=True)
    class Partition:
        assignments: Mapping[MaxCut.Vertex, int]

        def __post_init__(self) -> None:
            normalized = {
                vertex: int(value) for vertex, value in self.assignments.items()
            }
            if any(value not in (0, 1) for value in normalized.values()):
                raise ValueError("Max-Cut partition assignments must be binary.")
            object.__setattr__(self, "assignments", normalized)

        def side_of(self, vertex: MaxCut.Vertex) -> int:
            try:
                return int(self.assignments[vertex])
            except KeyError as error:
                raise ValueError(
                    f"Partition is missing vertex {vertex.identifier!r}."
                ) from error

        @property
        def selected(self) -> tuple[MaxCut.Vertex, ...]:
            return tuple(
                vertex for vertex, side in self.assignments.items() if side == 1
            )

        @property
        def unselected(self) -> tuple[MaxCut.Vertex, ...]:
            return tuple(
                vertex for vertex, side in self.assignments.items() if side == 0
            )

        def to_dict(self) -> Mapping[str, Any]:
            return {
                str(vertex.identifier): int(side)
                for vertex, side in self.assignments.items()
            }

    @dataclass(frozen=True, kw_only=True)
    class Candidate(BaseCandidate):
        _domain: MaxCut = field(repr=False)
        partition: MaxCut.Partition
        native_score: float | None
        strategy: str

        @property
        def domain(self) -> MaxCut:
            return self._domain

        def _interpret_in(self, domain: Domain) -> BaseEvaluation:
            if domain is not self._domain:
                raise ValueError(
                    "A MaxCut Candidate must be interpreted by its owning Domain."
                )
            return MaxCut.Evaluation(candidate=self)

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "domain_type": self.domain.domain_type,
                "strategy": self.strategy,
                "partition": self.partition.to_dict(),
                "selected": [vertex.identifier for vertex in self.partition.selected],
                "unselected": [
                    vertex.identifier for vertex in self.partition.unselected
                ],
                "native_score": self.native_score,
            }

    @dataclass(frozen=True, kw_only=True)
    class Evaluation(BaseEvaluation):
        candidate: MaxCut.Candidate

        @property
        def domain(self) -> MaxCut:
            return self.candidate.domain

        @property
        def feasible(self) -> bool:
            return set(self.candidate.partition.assignments) == set(
                self.domain.graph.vertices
            )

        @property
        def cut_edges(self) -> tuple[MaxCut.Edge, ...]:
            if not self.feasible:
                return ()
            return tuple(
                edge
                for edge in self.domain.graph.edges
                if edge.crosses(self.candidate.partition)
            )

        @property
        def cut_value(self) -> float | None:
            if not self.feasible:
                return None
            return self.domain.objective.evaluate(self.candidate.partition)

        @property
        def quality(self) -> float | None:
            return self.cut_value

        @property
        def target_reached(self) -> bool:
            target = self.domain.parameters.target_cut_value
            return (
                target is not None
                and self.cut_value is not None
                and self.cut_value >= target
            )

        @property
        def metrics(self) -> Mapping[str, Any]:
            return {
                "cut_value": self.cut_value,
                "cut_edges": [edge.to_dict() for edge in self.cut_edges],
                "target_reached": self.target_reached,
            }

        @property
        def utility_inputs(self) -> Mapping[str, Any]:
            return {
                "feasible": self.feasible,
                "quality": self.quality,
            }

        def to_dict(self) -> Mapping[str, Any]:
            return {
                "domain_type": self.domain.domain_type,
                "strategy": self.candidate.strategy,
                "state": self.state.code,
                "feasible": self.feasible,
                "quality": self.quality,
                "metrics": dict(self.metrics),
                "candidate": self.candidate.to_dict(),
                "utility_inputs": dict(self.utility_inputs),
            }

    name: str
    graph: Graph
    parameters: Parameters = field(default_factory=Parameters)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Max-Cut name cannot be empty.")

    @classmethod
    def from_networkx(
        cls,
        graph: Any,
        *,
        name: str = "max-cut",
        parameters: MaxCut.Parameters | None = None,
    ) -> MaxCut:
        try:
            import networkx as nx
        except ImportError as error:
            raise RuntimeError(
                "networkx is required to construct MaxCut from a graph."
            ) from error

        if not isinstance(graph, nx.Graph):
            raise TypeError("Max-Cut input must be a NetworkX graph.")
        if graph.is_directed():
            raise ValueError("Max-Cut requires an undirected graph.")
        if nx.number_of_selfloops(graph):
            raise ValueError("Max-Cut does not support self-loop edges.")

        vertices = {
            identifier: cls.Vertex(identifier=identifier) for identifier in graph.nodes
        }
        edges = tuple(
            cls.Edge(
                first=vertices[first],
                second=vertices[second],
                weight=float(data.get("weight", 1.0)),
            )
            for first, second, data in graph.edges(data=True)
        )
        return cls(
            name=name,
            graph=cls.Graph(
                vertices=tuple(vertices.values()),
                edges=edges,
            ),
            parameters=parameters or cls.Parameters(),
        )

    @property
    def V(self) -> tuple[Vertex, ...]:
        return self.graph.vertices

    @property
    def E(self) -> tuple[Edge, ...]:
        return self.graph.edges

    @property
    def objective(self) -> Objective:
        return self.Objective(domain=self)

    @property
    def summary(self) -> Mapping[str, Any]:
        return {
            "name": self.name,
            "domain_type": self.domain_type,
            "vertices": len(self.V),
            "edges": len(self.E),
            "weighted": self.graph.weighted,
            "total_weight": self.graph.total_weight,
            "parameters": self.parameters.to_dict(),
        }

    def _interpret_in(self, domain: Domain) -> Interpretation:
        if domain is not self:
            raise ValueError("A MaxCut aggregate must be interpreted by itself.")
        return self.Interpretation(
            domain=self,
            objective=self.objective,
            summary=self.summary,
        )


# Transitional public alias. New code should use MaxCut.
MaxCutDomain = MaxCut
