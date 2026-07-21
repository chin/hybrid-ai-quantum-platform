from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2
from typing import Any

VALID_CATEGORIES = {
    "architecture",
    "baselines",
    "benchmarks",
    "validation",
    "reports",
    "figures",
    "releases",
}


@dataclass
class ArtifactRecord:
    category: str
    name: str
    version: str
    path: str
    created_utc: str
    description: str = ""
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ArtifactRegistry:
    def __init__(self, root: str | Path = "artifacts") -> None:
        self.root = Path(root)

    @staticmethod
    def _validate_segment(value: str, label: str) -> None:
        if not value or not value.strip():
            raise ValueError(f"Artifact {label} must not be empty.")
        if Path(value).name != value or "/" in value or "\\" in value or ".." in value:
            raise ValueError(f"Artifact {label} must be a safe path segment.")

    def promote(
        self,
        source: str | Path,
        category: str,
        name: str,
        version: str,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ArtifactRecord:
        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid artifact category '{category}'. Expected one of: {sorted(VALID_CATEGORIES)}"
            )
        self._validate_segment(name, "name")
        self._validate_segment(version, "version")
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"Source artifact does not exist: {source_path}")
        if not source_path.is_file():
            raise ValueError("Source artifact must be a file.")

        artifact_dir = self.root / category
        artifact_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = artifact_dir / f"{name}_{version}{source_path.suffix}"
        metadata_path = artifact_dir / f"{name}_{version}.metadata.json"
        if artifact_path.exists() or metadata_path.exists():
            raise FileExistsError("Artifact destination already exists.")

        copy2(source_path, artifact_path)
        record = ArtifactRecord(
            category=category,
            name=name,
            version=version,
            path=str(artifact_path),
            created_utc=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ"),
            description=description,
            source=str(source_path),
            metadata=metadata or {},
        )
        metadata_path.write_text(
            json.dumps(asdict(record), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return record
