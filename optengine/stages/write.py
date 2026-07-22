from __future__ import annotations

from pathlib import Path

from optengine.engine import OptEngine


def write(engine: OptEngine) -> Path:
    """Persist the complete Recommendation through the configured Writer."""

    if engine.recommendation.explanation is None:
        raise RuntimeError("OptEngine requires an explanation before writing.")
    engine.log("Write started.")
    path = engine.writer.write(
        recommendation=engine.recommendation,
        output_dir=engine.output_dir,
        run_name=engine.run_name,
    )
    engine.log(f"Write completed: {path}.")
    return path
