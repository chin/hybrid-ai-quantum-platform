from __future__ import annotations

import time
from typing import Any, Mapping

from dwave.samplers import (
    SimulatedAnnealingSampler,
)

from optengine.candidate import Candidate
from optengine.formulations.base import Model
from optengine.formulations.qubo import QUBOModel
from optengine.operations.annealing import (
    AnnealingOperation,
)
from optengine.operations.base import Operation
from optengine.solvers.base import Solver


class DWaveLocalSolver(Solver):
    name = "dwave-local"

    def supports(
        self,
        model: Model,
        operation: Operation,
    ) -> bool:
        return isinstance(model, QUBOModel) and isinstance(
            operation,
            AnnealingOperation,
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

        if not isinstance(
            operation,
            AnnealingOperation,
        ):
            raise TypeError("Expected AnnealingOperation.")

        iterations = int(budget.get("iterations", 1))
        if iterations <= 0:
            raise ValueError("iterations must be greater than zero")

        sampler = SimulatedAnnealingSampler()

        best_sample: dict[Any, int] = {}
        best_energy = float("inf")
        history: list[dict[str, Any]] = []

        started = time.perf_counter()

        for iteration in range(iterations):
            kwargs: dict[str, Any] = {
                "num_reads": (operation.reads_per_iteration),
                "num_sweeps": operation.num_sweeps,
            }

            if operation.seed is not None:
                kwargs["seed"] = operation.seed + iteration

            sampleset = sampler.sample(
                model.payload,
                **kwargs,
            )

            batch_best = sampleset.first
            batch_energy = float(batch_best.energy)

            if batch_energy < best_energy:
                best_energy = batch_energy
                best_sample = {
                    node: int(bit) for node, bit in batch_best.sample.items()
                }

            history.append(
                {
                    "iteration": iteration + 1,
                    "batch_best_energy": batch_energy,
                    "best_so_far_energy": best_energy,
                }
            )

        runtime_s = time.perf_counter() - started

        return Candidate(
            strategy="",
            formulation=model.formulation,
            operation=operation.name,
            solver=self.name,
            values={
                "sample": best_sample,
            },
            native_score=best_energy,
            status="complete",
            runtime_s=runtime_s,
            metadata={
                "history": history,
                "iterations": iterations,
                "reads_per_iteration": (operation.reads_per_iteration),
                "num_sweeps": operation.num_sweeps,
            },
            provenance={
                "library": "dwave-samplers",
                "execution": "local",
            },
        )
