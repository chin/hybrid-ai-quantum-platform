from __future__ import annotations

import optengine.cli as cli
import optengine.trace as trace


def test_terminal_presentation_api_is_complete() -> None:
    for name in (
        "banner",
        "blank",
        "block",
        "detail",
        "heading",
        "item",
        "progress",
        "result",
        "step",
        "success",
        "tool_block",
        "tool_result",
        "value",
    ):
        assert name in cli.__all__
        assert callable(getattr(cli, name))

    for name in (
        "execution_result",
        "expression_formula",
        "render_analysis_chain",
        "render_strategy_start",
        "render_strategy_result",
        "render_strategy_utilities",
        "render_outcome_chain",
    ):
        assert name in trace.__all__
        assert callable(getattr(trace, name))
