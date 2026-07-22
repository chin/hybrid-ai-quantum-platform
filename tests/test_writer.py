from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

import pytest

from optengine.recommendation import Recommendation
from optengine.writers.json import (
    JsonRecommendationWriter,
    _json_safe,
)


class ExampleEnum(Enum):
    VALUE = "value"


class ItemObject:
    def item(self):
        return 3


class ListObject:
    def tolist(self):
        return [1, 2]


class DictObject:
    def to_dict(self):
        return {"x": 1}


class BadItemObject:
    def item(self):
        raise ValueError("bad")

    def tolist(self):
        raise TypeError("bad")


def test_json_safe_supported_types_and_conversion_protocols(
    tmp_path: Path,
) -> None:
    assert _json_safe(None) is None
    assert _json_safe(1) == 1
    assert _json_safe(tmp_path) == str(tmp_path)
    assert _json_safe(ExampleEnum.VALUE) == "value"
    assert _json_safe({1: {2, 3}}) in (
        {"1": [2, 3]},
        {"1": [3, 2]},
    )
    assert _json_safe(ItemObject()) == 3
    assert _json_safe(ListObject()) == [1, 2]
    assert _json_safe(DictObject()) == {"x": 1}
    with pytest.raises(TypeError, match="cannot be serialized"):
        _json_safe(BadItemObject())
    with pytest.raises(TypeError, match="cannot be serialized"):
        _json_safe(object())


def test_json_writer_uses_collision_safe_paths_and_explicit_schema(
    tmp_path: Path,
) -> None:
    writer = JsonRecommendationWriter()
    first = Recommendation(run_id="1", domain_summary={"name": "one"})
    second = Recommendation(run_id="2", domain_summary={"name": "two"})
    first_path = writer.write(first, tmp_path, "run")
    second_path = writer.write(second, tmp_path, "run")
    assert first_path != second_path
    assert first.output_path == str(first_path)
    assert second.output_path == str(second_path)
    assert json.loads(first_path.read_text())["assessment"] is None
    assert json.loads(second_path.read_text())["domain"]["name"] == "two"
