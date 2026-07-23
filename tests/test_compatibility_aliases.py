from __future__ import annotations

import optengine
from optengine.utility import (
    Assessment,
    OperationalUtility,
    OperationalUtilityModel,
    OptChinUtility,
    OptChinUtilityAdapter,
    StrategyAssessment,
    StrategyUtility,
    Utility,
    UtilityAssessment,
    UtilityModel,
)


def test_legacy_utility_names_are_exact_type_aliases() -> None:
    assert UtilityModel is Utility
    assert UtilityAssessment is Assessment
    assert StrategyUtility is StrategyAssessment
    assert OperationalUtilityModel is OperationalUtility
    assert OptChinUtilityAdapter is OptChinUtility


def test_legacy_utility_names_remain_top_level_exports() -> None:
    assert optengine.UtilityModel is Utility
    assert optengine.UtilityAssessment is Assessment
    assert optengine.StrategyUtility is StrategyAssessment
    assert optengine.OperationalUtilityModel is OperationalUtility
    assert optengine.OptChinUtilityAdapter is OptChinUtility


def test_legacy_utility_names_are_declared_public_api() -> None:
    expected = {
        "UtilityModel",
        "UtilityAssessment",
        "StrategyUtility",
        "OperationalUtilityModel",
        "OptChinUtilityAdapter",
    }
    assert expected <= set(optengine.__all__)


def test_legacy_aliases_preserve_instantiation_and_subclass_checks() -> None:
    operational = OperationalUtilityModel()
    assert isinstance(operational, UtilityModel)
    assert isinstance(operational, OperationalUtility)
    assert issubclass(OperationalUtilityModel, Utility)
