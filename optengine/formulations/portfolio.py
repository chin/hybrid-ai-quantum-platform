"""Compatibility exports for the previous portfolio-specific formulation module.

Portfolio now exposes a structural Objective. Generic CQM and QUBO formulations
determine compatibility from Objective.curve in real time.
"""

from optengine.formulations.cqm import CQM
from optengine.formulations.qubo import QUBO

PortfolioCQMFormulation = CQM
PortfolioQUBOFormulation = QUBO
PortfolioCQMModel = CQM.Model

__all__ = [
    "CQM",
    "PortfolioCQMFormulation",
    "PortfolioCQMModel",
    "PortfolioQUBOFormulation",
    "QUBO",
]
