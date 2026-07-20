"""
Core platform execution for the OptEngine project.
"""

from optengine import cli
from optengine._version import __version__
from optengine.artifact import ArtifactRecord, ArtifactRegistry
from optengine.engine import OptEngine
from optengine.recommendation import Recommendation
from optengine.runner import run

__all__ = [
    "ArtifactRecord",
    "ArtifactRegistry",
    "OptEngine",
    "Recommendation",
    "run",
    "cli",
    "__version__",
]
