from __future__ import annotations

import argparse
from pathlib import Path

from optengine import ArtifactRegistry
from optengine.cli import banner, blank, footer, step, value


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote the latest OptEngine output.")
    parser.add_argument("--run-name", default="quickstart")
    parser.add_argument("--category", default="baselines")
    args = parser.parse_args()

    banner("OptEngine :: Artifact")
    outputs = sorted(Path("outputs").glob(f"{args.run_name}_*.json"))
    if not outputs:
        raise SystemExit(
            f"No {args.run_name} output found. Run the corresponding Make target first."
        )
    latest = outputs[-1]
    version = latest.stem.removeprefix(f"{args.run_name}_")

    step("artifact.source")
    value(latest)
    blank()
    record = ArtifactRegistry().promote(
        source=latest,
        category=args.category,
        name=args.run_name,
        version=version,
        description=f"Curated OptEngine output for {args.run_name}.",
        metadata={"artifact_type": "run-output", "promoted_from": "outputs"},
    )
    step("artifact.category")
    value(record.category)
    blank()
    step("artifact.version")
    value(record.version)
    blank()
    step("artifact.destination")
    value(record.path)
    footer("Artifact Promoted")


if __name__ == "__main__":
    main()
