from __future__ import annotations

import re

import pytest

from optengine.cli import (
    BANNER_WIDTH,
    banner,
    blank,
    block,
    failure,
    footer,
    step,
    success,
    tool_block,
    tool_result,
    value,
)


ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)


def test_tool_block_success_failure_and_exception_identity(capsys) -> None:
    with tool_block("test.command"):
        pass
    output = capsys.readouterr().out
    assert "> test.command" in output
    assert "✓ test.command passed" in output

    expected = RuntimeError("expected failure")
    with pytest.raises(RuntimeError) as raised:
        with tool_block("test.command"):
            raise expected
    assert raised.value is expected
    output = capsys.readouterr().out
    assert "✗ test.command failed" in output


@pytest.mark.parametrize(
    ("name", "style"),
    [
        ("decision", "\033[33m"),
        ("runtime.decision", "\033[33m"),
        ("workflow.runtime.decision", "\033[33m"),
        ("output", "\033[36m"),
        ("runtime.artifact", "\033[36m"),
    ],
)
def test_block_styles_are_terminal_segment_driven(
    monkeypatch,
    capsys,
    name: str,
    style: str,
) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")
    block(name, "value")
    output = capsys.readouterr().out
    assert style in output


def test_block_success_and_default_rendering(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")
    block("analysis", "complete", ok=True)
    output = capsys.readouterr().out
    assert "\033[32m✓ complete\033[0m" in output

    block("problem", "example")
    output = capsys.readouterr().out
    assert output == "> problem\nexample\n\n"


def test_tool_result_and_status_helpers(monkeypatch, capsys) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")
    tool_result("ci.result", "complete")
    success()
    failure()
    output = capsys.readouterr().out
    assert "\033[36m> ci.result\033[0m" in output
    assert "\033[32m✓ ci.result complete\033[0m" in output
    assert "\033[32m✓ complete\033[0m" in output
    assert "\033[31m✗ failed\033[0m" in output


def test_step_value_blank_order_without_ansi(monkeypatch, capsys) -> None:
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    step("runtime.value")
    value(42)
    blank()
    assert capsys.readouterr().out == "> runtime.value\n42\n\n"


def test_banner_and_footer_geometry(monkeypatch, capsys) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")
    banner("OptEngine :: Quickstart")
    output = capsys.readouterr().out
    lines = [line for line in output.splitlines() if line]
    assert strip_ansi(lines[0]) == "━" * BANNER_WIDTH
    assert strip_ansi(lines[1]) == ("OptEngine :: Quickstart".center(BANNER_WIDTH))
    assert strip_ansi(lines[2]) == "━" * BANNER_WIDTH

    footer("Runtime Complete")
    output = capsys.readouterr().out
    lines = [line for line in output.splitlines() if line]
    assert strip_ansi(lines[0]) == "━" * BANNER_WIDTH
    assert strip_ansi(lines[1]) == ("Runtime Complete".center(BANNER_WIDTH))
    assert strip_ansi(lines[2]) == "━" * BANNER_WIDTH
