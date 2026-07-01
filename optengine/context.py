from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Context:
    problem: str
    output_dir: Path = Path("outputs")
    output_path: Path | None = None

    analysis: dict[str, Any] = field(default_factory=dict)
    optimization_results: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    decision: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)

    def log(self, message: str) -> None:
        self.logs.append(message)
