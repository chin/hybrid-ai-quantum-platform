from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from optengine.recommendation import Recommendation
from optengine.writers.base import RecommendationWriter


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Enum):
        return _json_safe(value.value)
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_safe(item) for item in value]

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return _json_safe(to_dict())

    item_method = getattr(value, "item", None)
    if callable(item_method):
        try:
            return _json_safe(item_method())
        except (TypeError, ValueError):
            pass

    tolist_method = getattr(value, "tolist", None)
    if callable(tolist_method):
        try:
            return _json_safe(tolist_method())
        except (TypeError, ValueError):
            pass

    raise TypeError(
        "Recommendation contains a value that cannot be serialized to JSON: "
        f"{type(value).__name__}"
    )


class JsonRecommendationWriter(RecommendationWriter):
    """Write a cycle-free, explicit Recommendation artifact."""

    def write(
        self,
        recommendation: Recommendation,
        output_dir: Path,
        run_name: str,
    ) -> Path:
        if not run_name.strip():
            raise ValueError("run_name cannot be empty.")

        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%fZ")
        path = output_dir / f"{run_name}_{timestamp}.json"
        recommendation.output_path = str(path)

        payload = _json_safe(recommendation.to_dict())
        path.write_text(
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n",
            encoding="utf-8",
        )
        return path
