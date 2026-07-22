from __future__ import annotations

import importlib.util
import time
from typing import ClassVar

from optengine.errors import MissingDependencyError
from optengine.formulations.cqm import CQM
from optengine.mathematics import ValueType
from optengine.operations.base import Operation
from optengine.operations.exact import ExactSearch
from optengine.solvers.base import Solver


class DimodCQMExact(Solver):
    name: ClassVar[str] = "dimod-cqm-exact"

    capability = Solver.Capability(
        operation_types=(ExactSearch,),
        model_types=(CQM.Model,),
        input_types=frozenset(
            {
                ValueType.BINARY,
                ValueType.INTEGER,
            }
        ),
        supports_constraints=True,
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
            raise TypeError("DimodCQMExact received an incompatible Request.")

        try:
            import dimod
        except ImportError as error:
            raise MissingDependencyError("dimod", self.name) from error

        model = request.model
        operation = request.operation
        if not isinstance(model, CQM.Model):
            raise TypeError("DimodCQMExact requires CQM.Model.")
        if not isinstance(operation, ExactSearch):
            raise TypeError("DimodCQMExact requires ExactSearch.")
        if len(model.payload.variables) > operation.max_variables:
            raise ValueError("Model exceeds the exact-search variable limit.")

        started = time.perf_counter()
        sampleset = dimod.ExactCQMSolver().sample_cqm(model.payload)
        feasible = sampleset.filter(lambda row: bool(row.is_feasible))
        runtime_s = time.perf_counter() - started

        if len(feasible) == 0:
            raise ValueError("Exact CQM execution produced no feasible candidate.")

        best = feasible.first
        return Solver.Result(
            values={
                name: int(round(float(value))) for name, value in best.sample.items()
            },
            native_score=float(best.energy),
            status="complete",
            runtime_s=runtime_s,
            resource_cost=float(len(sampleset)),
            metrics={
                "evaluated_candidates": len(sampleset),
                "feasible_candidates": len(feasible),
                "is_reference": True,
                "confidence": 1.0,
                "expected_improvement": 0.0,
            },
            metadata={
                "budget": dict(request.budget),
            },
            provenance={
                "library": "dimod",
                "solver": "ExactCQMSolver",
                "execution": "local",
            },
        )


DimodCQMExactSolver = DimodCQMExact
