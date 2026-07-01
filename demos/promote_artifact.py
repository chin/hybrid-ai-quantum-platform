from pathlib import Path

from optengine import ArtifactRegistry
from optengine.cli import banner, blank, footer, step, value


def main() -> None:
    banner("OptEngine :: Artifact")

    outputs = sorted(Path("outputs").glob("quickstart_*.json"))

    if not outputs:
        raise SystemExit("No quickstart output found. Run `make dev` first.")

    latest = outputs[-1]

    step("artifact.source")
    value(latest)
    blank()

    registry = ArtifactRegistry()

    record = registry.promote(
        source=latest,
        category="baselines",
        name="quickstart",
        version="v0.1",
        description="Baseline quickstart output for the initial OptEngine skeleton.",
        metadata={
            "artifact_type": "baseline",
            "promoted_from": "outputs",
        },
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
