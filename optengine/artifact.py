from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2
from typing import Any
import json


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
                f"Invalid artifact category '{category}'. "
                f"Expected one of: {sorted(VALID_CATEGORIES)}"
            )

        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"Source artifact does not exist: {source_path}")

        ext = source_path.suffix
        artifact_dir = self.root / category
        artifact_dir.mkdir(parents=True, exist_ok=True)

        artifact_name = f"{name}_{version}{ext}"
        artifact_path = artifact_dir / artifact_name

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

        metadata_path = artifact_dir / f"{name}_{version}.metadata.json"
        metadata_path.write_text(
            json.dumps(asdict(record), indent=2),
            encoding="utf-8",
        )

        return record
