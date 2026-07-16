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


def test_tool_block_reports_success(capsys):
    with tool_block("test.command"):
        pass

    output = capsys.readouterr().out

    assert "> test.command" in output
    assert "✓ test.command passed" in output


def test_tool_block_reports_failure(capsys):
    with pytest.raises(RuntimeError):
        with tool_block("test.command"):
            raise RuntimeError("expected failure")

    output = capsys.readouterr().out

    assert "> test.command" in output
    assert "✗ test.command failed" in output


def test_tool_block_uses_success_style_when_forced(
    monkeypatch,
    capsys,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    with tool_block("test.command"):
        pass

    output = capsys.readouterr().out

    assert "\033[32m" in output
    assert "✓ test.command passed" in output


@pytest.mark.parametrize(
    ("name", "expected_style"),
    [
        ("decision", "\033[33m"),
        ("runtime.decision", "\033[33m"),
        ("artifact", "\033[36m"),
        ("runtime.artifact", "\033[36m"),
    ],
)
def test_runtime_values_use_expected_style(
    monkeypatch,
    capsys,
    name,
    expected_style,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    block(name, "example value")

    output = capsys.readouterr().out

    assert output == (f"> {name}\n{expected_style}example value\033[0m\n\n")


@pytest.mark.parametrize("name", ["problem", "reason"])
def test_default_runtime_values_use_default_style(
    monkeypatch,
    capsys,
    name,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    block(name, "example value")

    output = capsys.readouterr().out

    assert output == f"> {name}\nexample value\n\n"
    assert ANSI_ESCAPE.search(output) is None


@pytest.mark.parametrize(
    "label",
    [
        "git.status",
        "format.ruff",
        "lint.ruff",
        "test.pytest",
        "build.package",
    ],
)
def test_tool_labels_use_cyan_style_when_forced(
    monkeypatch,
    capsys,
    label,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    with tool_block(label):
        pass

    output = capsys.readouterr().out

    assert f"\033[36m> {label}\033[0m" in output
    assert f"\033[32m✓ {label} passed\033[0m" in output


def test_tool_result_uses_cyan_label_and_green_status(
    monkeypatch,
    capsys,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    tool_result("ci.result")

    output = capsys.readouterr().out

    assert "\033[36m> ci.result\033[0m" in output
    assert "\033[32m✓ ci.result passed\033[0m" in output


def test_tool_block_preserves_original_exception(capsys):
    expected = RuntimeError("expected failure")

    with pytest.raises(RuntimeError, match="expected failure") as raised:
        with tool_block("test.command"):
            raise expected

    assert raised.value is expected

    output = capsys.readouterr().out

    assert "> test.command" in output
    assert "✗ test.command failed" in output


def test_tool_output_has_no_ansi_without_forced_style(
    monkeypatch,
    capsys,
):
    monkeypatch.delenv("FORCE_COLOR", raising=False)

    with tool_block("test.command"):
        pass

    output = capsys.readouterr().out

    assert "\033[" not in output
    assert "> test.command" in output
    assert "✓ test.command passed" in output


def test_tool_block_failure_uses_cyan_label_and_red_status(
    monkeypatch,
    capsys,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    with pytest.raises(RuntimeError, match="expected failure"):
        with tool_block("test.command"):
            raise RuntimeError("expected failure")

    output = capsys.readouterr().out

    assert "\033[36m> test.command\033[0m" in output
    assert "\033[31m✗ test.command failed\033[0m" in output


def test_block_ok_uses_success_rendering(
    monkeypatch,
    capsys,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    block("decision", "complete", ok=True)

    output = capsys.readouterr().out

    assert "> decision" in output
    assert "\033[32m✓ complete\033[0m" in output
    assert "\033[33mcomplete" not in output


@pytest.mark.parametrize(
    ("name", "expected_style"),
    [
        ("workflow.runtime.decision", "\033[33m"),
        ("workflow.runtime.artifact", "\033[36m"),
    ],
)
def test_block_style_uses_last_qualified_name_segment(
    monkeypatch,
    capsys,
    name,
    expected_style,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    block(name, "example value")

    output = capsys.readouterr().out

    assert output == (f"> {name}\n{expected_style}example value\033[0m\n\n")


def test_unknown_block_value_uses_default_style(
    monkeypatch,
    capsys,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    block("runtime.analysis", "example value")

    output = capsys.readouterr().out

    assert output == "> runtime.analysis\nexample value\n\n"
    assert ANSI_ESCAPE.search(output) is None


def test_tool_result_supports_custom_message(
    monkeypatch,
    capsys,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    tool_result("release-check.result", "complete")

    output = capsys.readouterr().out

    assert "\033[36m> release-check.result\033[0m" in output
    assert "\033[32m✓ release-check.result complete\033[0m" in output


def test_banner_uses_expected_width_and_title_color(
    monkeypatch,
    capsys,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    banner("OptEngine :: Quickstart")

    output = capsys.readouterr().out
    nonempty_lines = [line for line in output.splitlines() if line]

    assert strip_ansi(nonempty_lines[0]) == "━" * BANNER_WIDTH
    assert strip_ansi(nonempty_lines[1]) == "OptEngine :: Quickstart".center(
        BANNER_WIDTH
    )
    assert strip_ansi(nonempty_lines[2]) == "━" * BANNER_WIDTH
    assert "\033[38;2;118;185;0m" in nonempty_lines[1]


def test_success_and_failure_default_messages_use_status_styles(
    monkeypatch,
    capsys,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    success()
    failure()

    output = capsys.readouterr().out

    assert "\033[32m✓ complete\033[0m" in output
    assert "\033[31m✗ failed\033[0m" in output


def test_step_value_and_blank_render_in_order(
    monkeypatch,
    capsys,
):
    monkeypatch.delenv("FORCE_COLOR", raising=False)

    step("runtime.value")
    value(42)
    blank()

    output = capsys.readouterr().out

    assert output == "> runtime.value\n42\n\n"


def test_footer_uses_expected_width_and_centered_title(
    monkeypatch,
    capsys,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    footer("Runtime Complete")

    output = capsys.readouterr().out
    nonempty_lines = [line for line in output.splitlines() if line]

    assert len(nonempty_lines) == 3
    assert strip_ansi(nonempty_lines[0]) == "━" * BANNER_WIDTH
    assert strip_ansi(nonempty_lines[1]) == "Runtime Complete".center(BANNER_WIDTH)
    assert strip_ansi(nonempty_lines[2]) == "━" * BANNER_WIDTH
