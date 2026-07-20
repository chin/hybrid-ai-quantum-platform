from __future__ import annotations

import time
from typing import Any, Mapping

import dimod

from optengine.candidate import Candidate
from optengine.formulations.base import Model
from optengine.formulations.qubo import QUBOModel
from optengine.operations.base import Operation
from optengine.operations.exact import ExactSearchOperation
from optengine.solvers.base import Solver


class DimodExactSolver(Solver):
    name = "dimod-exact"

    def supports(
        self,
        model: Model,
        operation: Operation,
    ) -> bool:
        return isinstance(model, QUBOModel) and isinstance(
            operation,
            ExactSearchOperation,
        )

    def execute(
        self,
        model: Model,
        operation: Operation,
        configuration: Mapping[str, Any],
        budget: Mapping[str, Any],
    ) -> Candidate:
        if not isinstance(model, QUBOModel):
            raise TypeError("DimodExactSolver requires a QUBOModel.")

        if not isinstance(operation, ExactSearchOperation):
            raise TypeError("DimodExactSolver requires ExactSearchOperation.")

        if model.payload.num_variables > operation.max_variables:
            raise ValueError("Model exceeds the exact-search variable limit.")

        started = time.perf_counter()
        sampleset = dimod.ExactSolver().sample(model.payload)
        best = sampleset.first
        runtime_s = time.perf_counter() - started

        sample = {node: int(bit) for node, bit in best.sample.items()}

        return Candidate(
            formulation=model.formulation,
            operation=operation.name,
            solver=self.name,
            values={"sample": sample},
            native_score=float(best.energy),
            status="complete",
            runtime_s=runtime_s,
            resource_cost=float(len(sampleset)),
            native_metrics={
                "evaluated_candidates": len(sampleset),
                "is_reference": True,
                "confidence": 1.0,
                "expected_improvement": 0.0,
            },
            metadata={
                "is_reference": True,
                "configuration": dict(configuration),
                "budget": dict(budget),
            },
            provenance={
                "library": "dimod",
                "solver": "ExactSolver",
                "execution": "local",
            },
        )
