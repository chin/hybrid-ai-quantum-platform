from __future__ import annotations

import json
from pathlib import Path

import pytest

from optengine.artifact import ArtifactRegistry


def test_promotes_non_destructively_with_metadata(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text('{"value": 1}\n', encoding="utf-8")
    registry = ArtifactRegistry(tmp_path / "artifacts")
    record = registry.promote(
        source,
        "baselines",
        "run",
        "v1",
        metadata={"seed": 7},
    )
    destination = Path(record.path)
    assert source.exists()
    assert destination.read_bytes() == source.read_bytes()
    assert record.category == "baselines"
    assert record.name == "run"
    assert record.version == "v1"
    metadata = json.loads(
        (tmp_path / "artifacts" / "baselines" / "run_v1.metadata.json").read_text()
    )
    assert metadata["metadata"]["seed"] == 7


@pytest.mark.parametrize("value", ["", "../escape", "a/b", "a\\b"])
def test_rejects_unsafe_names(tmp_path: Path, value: str) -> None:
    source = tmp_path / "source.json"
    source.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        ArtifactRegistry(tmp_path / "artifacts").promote(
            source,
            "baselines",
            value,
            "v1",
        )


def test_artifact_registry_rejects_invalid_sources_categories_and_overwrite(
    tmp_path: Path,
) -> None:
    registry = ArtifactRegistry(tmp_path / "artifacts")
    missing = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError):
        registry.promote(
            missing,
            "baselines",
            "run",
            "v1",
        )

    directory = tmp_path / "directory"
    directory.mkdir()
    with pytest.raises(ValueError, match="must be a file"):
        registry.promote(
            directory,
            "baselines",
            "run",
            "v1",
        )

    source = tmp_path / "source.json"
    source.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="category"):
        registry.promote(
            source,
            "invalid",
            "run",
            "v1",
        )

    registry.promote(source, "baselines", "run", "v1")
    with pytest.raises(FileExistsError):
        registry.promote(source, "baselines", "run", "v1")
