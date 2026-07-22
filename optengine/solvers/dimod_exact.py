from __future__ import annotations

import importlib.util
import time
from typing import Any, ClassVar

from optengine.errors import MissingDependencyError
from optengine.formulations.qubo import QUBO
from optengine.mathematics import ValueType
from optengine.operations.base import Operation
from optengine.operations.exact import ExactSearch
from optengine.solvers.base import Solver


class DimodExact(Solver):
    name: ClassVar[str] = "dimod-exact"

    capability = Solver.Capability(
        operation_types=(ExactSearch,),
        model_types=(QUBO.Model,),
        input_types=frozenset({ValueType.BINARY}),
        supports_constraints=False,
    )

    @property
    def reference(self) -> bool:
        return True

    @property
    def available(self) -> bool:
        return importlib.util.find_spec("dimod") is not None

    def execute(self, request: Operation.Request) -> Solver.Result:
        if not self.compatibility(
            operation=request.operation,
            model=request.model,
        ):
            raise TypeError("DimodExact received an incompatible Request.")

        try:
            import dimod
        except ImportError as error:
            raise MissingDependencyError("dimod", self.name) from error

        model = request.model
        operation = request.operation
        if not isinstance(model, QUBO.Model):
            raise TypeError("DimodExact requires QUBO.Model.")
        if not isinstance(operation, ExactSearch):
            raise TypeError("DimodExact requires ExactSearch.")
        if model.payload.num_variables > operation.max_variables:
            raise ValueError("Model exceeds the exact-search variable limit.")

        started = time.perf_counter()
        sampleset = dimod.ExactSolver().sample(model.payload)
        best = sampleset.first
        runtime_s = time.perf_counter() - started

        return Solver.Result(
            values={node: int(bit) for node, bit in best.sample.items()},
            native_score=float(best.energy),
            status="complete",
            runtime_s=runtime_s,
            resource_cost=float(len(sampleset)),
            metrics={
                "evaluated_candidates": len(sampleset),
                "is_reference": True,
                "confidence": 1.0,
                "expected_improvement": 0.0,
            },
            metadata={
                "budget": dict(request.budget),
            },
            provenance={
                "library": "dimod",
                "solver": "ExactSolver",
                "execution": "local",
            },
        )


DimodExactSolver = DimodExact
