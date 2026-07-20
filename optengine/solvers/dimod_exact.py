from __future__ import annotations

from typing import Any, Mapping

import dimod

from optengine.candidate import Candidate
from optengine.formulations.base import Model
from optengine.formulations.qubo import QUBOModel
from optengine.operations.base import Operation
from optengine.operations.exact import (
    ExactSearchOperation,
)
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
            raise TypeError("Expected QUBOModel.")

        if model.payload.num_variables > operation.max_variables:
            raise ValueError("Model exceeds exact-search variable limit.")

        sampleset = dimod.ExactSolver().sample(model.payload)
        best = sampleset.first

        return Candidate(
            strategy="",
            formulation=model.formulation,
            operation=operation.name,
            solver=self.name,
            values={
                "sample": {node: int(bit) for node, bit in best.sample.items()},
            },
            native_score=float(best.energy),
            status="complete",
            metadata={
                "is_reference": True,
            },
            provenance={
                "library": "dimod",
            },
        )
