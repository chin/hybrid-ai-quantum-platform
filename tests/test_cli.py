import pytest
from optengine.cli import block, tool_block, tool_result


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


def test_tool_block_uses_success_color_when_forced(monkeypatch, capsys):
    monkeypatch.setenv("FORCE_COLOR", "1")

    with tool_block("test.command"):
        pass

    output = capsys.readouterr().out

    assert "\033[32m" in output
    assert "✓ test.command passed" in output


@pytest.mark.parametrize(
    ("name", "expected_color"),
    [
        ("decision", "\033[33m"),
        ("runtime.decision", "\033[33m"),
        ("artifact", "\033[36m"),
        ("runtime.artifact", "\033[36m"),
    ],
)
def test_colored_runtime_values(
    monkeypatch,
    capsys,
    name,
    expected_color,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    block(name, "example value")

    output = capsys.readouterr().out

    assert f"> {name}" in output
    assert f"{expected_color}example value" in output
    assert f"{expected_color}> {name}" not in output


@pytest.mark.parametrize("name", ["problem", "reason"])
def test_default_runtime_values_are_not_colored(
    monkeypatch,
    capsys,
    name,
):
    monkeypatch.setenv("FORCE_COLOR", "1")

    block(name, "example value")

    output = capsys.readouterr().out

    assert f"> {name}" in output
    assert "example value" in output
    assert "\033[33mexample value" not in output
    assert "\033[36mexample value" not in output


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
def test_tool_labels_are_cyan_when_color_is_forced(
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
