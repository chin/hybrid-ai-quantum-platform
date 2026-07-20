from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from optengine.recommendation import Recommendation
from optengine.writers.base import RecommendationWriter


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, Enum):
        return _json_safe(value.value)

    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}

    if isinstance(
        value,
        (list, tuple, set, frozenset),
    ):
        return [_json_safe(item) for item in value]

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
        "Recommendation contains a value that cannot be "
        f"serialized to JSON: {type(value).__name__}"
    )


class JsonRecommendationWriter(RecommendationWriter):
    def write(
        self,
        recommendation: Recommendation,
        output_dir: Path,
        run_name: str,
    ) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
        path = output_dir / f"{run_name}_{timestamp}.json"
        recommendation.output_path = str(path)

        payload = _json_safe(asdict(recommendation))
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
