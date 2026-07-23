from __future__ import annotations

import importlib.util
import time
from typing import Any, ClassVar

from optengine.errors import MissingDependencyError
from optengine.formulations.qubo import QUBO
from optengine.mathematics import ValueType
from optengine.operations.annealing import Annealing
from optengine.operations.base import Operation
from optengine.solvers.base import Solver


class DWaveLocal(Solver):
    name: ClassVar[str] = "dwave-local"

    capability = Solver.Capability(
        operation_types=(Annealing,),
        model_types=(QUBO.Model,),
        input_types=frozenset({ValueType.BINARY}),
        supports_constraints=False,
    )

    @property
    def available(self) -> bool:
        try:
            return importlib.util.find_spec("dwave.samplers") is not None
        except ModuleNotFoundError:
            return False

    def execute(self, request: Operation.Request) -> Solver.Result:
        if not self.compatibility(
            operation=request.operation,
            model=request.model,
        ):
            raise TypeError("DWaveLocal received an incompatible Request.")

        try:
            from dwave.samplers import SimulatedAnnealingSampler
        except ImportError as error:
            raise MissingDependencyError(
                "dwave-samplers",
                self.name,
            ) from error

        model = request.model
        operation = request.operation
        if not isinstance(model, QUBO.Model):
            raise TypeError("DWaveLocal requires QUBO.Model.")
        if not isinstance(operation, Annealing):
            raise TypeError("DWaveLocal requires Annealing.")

        sampler = SimulatedAnnealingSampler()
        best_sample: dict[Any, int] = {}
        best_energy = float("inf")
        previous_best = float("inf")
        history: list[dict[str, Any]] = []
        started = time.perf_counter()

        for iteration in range(operation.iterations):
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

        return Solver.Result(
            values=best_sample,
            native_score=best_energy,
            status="complete",
            runtime_s=runtime_s,
            resource_cost=None,
            metrics={
                "history": history,
                "iterations": operation.iterations,
                "reads_per_iteration": operation.reads_per_iteration,
                "num_sweeps": operation.num_sweeps,
                "total_reads": (operation.iterations * operation.reads_per_iteration),
                "expected_improvement": recent_improvement,
                "confidence": 0.75,
            },
            metadata={
                "budget": dict(request.budget),
            },
            provenance={
                "library": "dwave-samplers",
                "sampler": "SimulatedAnnealingSampler",
                "execution": "local",
            },
        )


DWaveLocalSolver = DWaveLocal
