from __future__ import annotations

import optengine

from optengine.engine import OptEngine
from optengine.recommendation import Recommendation


def test_public_api_exports_current_runtime_contracts() -> None:
    assert callable(optengine.run)
    assert optengine.OptEngine is OptEngine
    assert optengine.Recommendation is Recommendation


def test_core_modules_import() -> None:
    from optengine.domains.maxcut import MaxCutDomain
    from optengine.formulations.qubo import QUBOFormulation
    from optengine.solvers.dimod_exact import DimodExactSolver
    from optengine.solvers.dwave_local import DWaveLocalSolver

    assert MaxCutDomain.name == "max-cut"
    assert QUBOFormulation.name == "qubo"
    assert DimodExactSolver.name == "dimod-exact"
    assert DWaveLocalSolver.name == "dwave-local"
