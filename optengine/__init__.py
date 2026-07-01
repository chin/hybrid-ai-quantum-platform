"""
Core platform execution for the OptEngine project.
"""

from optengine import cli
from optengine._version import __version__
from optengine.artifact import ArtifactRecord, ArtifactRegistry
from optengine.context import Context
from optengine.runner import run
from optengine.solution import Solution

__all__ = [
    "ArtifactRecord",
    "ArtifactRegistry",
    "Context",
    "Solution",
    "cli",
    "run",
    "__version__",
]
