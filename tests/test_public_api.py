from __future__ import annotations

import optengine

from optengine.engine import OptEngine
from optengine.recommendation import Recommendation
from optengine.utility import (
    OperationalUtilityModel,
    OptChinUtilityAdapter,
)


def test_public_api_exports_current_contracts() -> None:
    assert callable(optengine.run)
    assert optengine.OptEngine is OptEngine
    assert optengine.Recommendation is Recommendation
    assert optengine.OperationalUtilityModel is OperationalUtilityModel
    assert optengine.OptChinUtilityAdapter is OptChinUtilityAdapter
