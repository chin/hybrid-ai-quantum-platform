from __future__ import annotations

import time
from typing import Any, Mapping

from dwave.samplers import SimulatedAnnealingSampler

from optengine.candidate import Candidate
from optengine.formulations.base import Model
from optengine.formulations.qubo import QUBOModel
from optengine.operations.annealing import AnnealingOperation
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
            raise TypeError("DWaveLocalSolver requires a QUBOModel.")

        if not isinstance(operation, AnnealingOperation):
            raise TypeError("DWaveLocalSolver requires AnnealingOperation.")

        iterations = int(budget.get("iterations", 1))
        if iterations <= 0:
            raise ValueError("iterations must be greater than zero")

        if operation.reads_per_iteration <= 0:
            raise ValueError("reads_per_iteration must be greater than zero")

        if operation.num_sweeps <= 0:
            raise ValueError("num_sweeps must be greater than zero")

        sampler = SimulatedAnnealingSampler()
        best_sample: dict[Any, int] = {}
        best_energy = float("inf")
        history: list[dict[str, Any]] = []
        started = time.perf_counter()
        previous_best = float("inf")

        for iteration in range(iterations):
            batch_started = time.perf_counter()
            sample_kwargs: dict[str, Any] = {
                "num_reads": operation.reads_per_iteration,
                "num_sweeps": operation.num_sweeps,
            }

            if operation.seed is not None:
                sample_kwargs["seed"] = operation.seed + iteration

            sampleset = sampler.sample(
                model.payload,
                **sample_kwargs,
            )
            batch_runtime_s = time.perf_counter() - batch_started

            batch_best = sampleset.first
            batch_energy = float(batch_best.energy)
            energies = [float(value) for value in sampleset.record.energy]
            mean_energy = sum(energies) / len(energies)
            variance = sum((value - mean_energy) ** 2 for value in energies) / len(
                energies
            )

            improved = batch_energy < best_energy
            improvement = 0.0

            if improved:
                improvement = (
                    0.0
                    if previous_best == float("inf")
                    else previous_best - batch_energy
                )
                previous_best = batch_energy
                best_energy = batch_energy
                best_sample = {
                    node: int(bit) for node, bit in batch_best.sample.items()
                }

            history.append(
                {
                    "iteration": iteration + 1,
                    "elapsed_s": time.perf_counter() - started,
                    "batch_time_s": batch_runtime_s,
                    "batch_best_energy": batch_energy,
                    "batch_mean_energy": mean_energy,
                    "batch_min_energy": min(energies),
                    "batch_max_energy": max(energies),
                    "batch_energy_variance": variance,
                    "best_so_far_energy": best_energy,
                    "improved": improved,
                    "improvement_in_native_score": improvement,
                }
            )

        runtime_s = time.perf_counter() - started
        recent_improvement = float(history[-1]["improvement_in_native_score"])

        return Candidate(
            formulation=model.formulation,
            operation=operation.name,
            solver=self.name,
            values={"sample": best_sample},
            native_score=best_energy,
            status="complete",
            runtime_s=runtime_s,
            resource_cost=None,
            native_metrics={
                "history": history,
                "iterations": iterations,
                "reads_per_iteration": operation.reads_per_iteration,
                "num_sweeps": operation.num_sweeps,
                "total_reads": (iterations * operation.reads_per_iteration),
                "expected_improvement": recent_improvement,
                "confidence": 0.75,
            },
            metadata={
                "configuration": dict(configuration),
                "budget": dict(budget),
            },
            provenance={
                "library": "dwave-samplers",
                "sampler": "SimulatedAnnealingSampler",
                "execution": "local",
            },
        )
