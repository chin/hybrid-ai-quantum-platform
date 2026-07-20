import argparse
import subprocess

import pytest

from tools import dev


def test_ci_group_preserves_gate_order():
    assert dev.COMMAND_GROUPS["ci"] == (
        "status",
        "format-check",
        "lint",
        "coverage",
    )


def test_release_check_extends_ci_with_build():
    assert dev.COMMAND_GROUPS["release-check"] == (
        "ci",
        "build",
    )


def test_version_group_contains_preview_commands():
    assert dev.COMMAND_GROUPS["version"] == (
        "version-next",
        "version-tag",
    )


def test_release_check_expands_commands_in_order(monkeypatch):
    commands = []
    results = []

    monkeypatch.setattr(
        dev,
        "run_tool",
        commands.append,
    )
    monkeypatch.setattr(
        dev.cli,
        "tool_result",
        results.append,
    )

    dev.run_target("release-check")

    assert commands == [
        "status",
        "format-check",
        "lint",
        "coverage",
        "build",
    ]
    assert results == [
        "ci.result",
        "release-check.result",
    ]


def test_main_converts_command_failure_to_clean_exit(
    monkeypatch,
):
    monkeypatch.setattr(
        dev,
        "parse_args",
        lambda: argparse.Namespace(target="ci"),
    )

    def fail_target(_target):
        raise subprocess.CalledProcessError(
            returncode=2,
            cmd=("example-command",),
        )

    monkeypatch.setattr(dev, "run_target", fail_target)

    with pytest.raises(SystemExit) as raised:
        dev.main()

    assert raised.value.code == 2
    assert raised.value.__suppress_context__ is True


def test_version_expands_commands_in_order(monkeypatch):
    commands = []
    results = []

    monkeypatch.setattr(
        dev,
        "run_tool",
        commands.append,
    )
    monkeypatch.setattr(
        dev.cli,
        "tool_result",
        results.append,
    )

    dev.run_target("version")

    assert commands == [
        "version-next",
        "version-tag",
    ]
    assert results == [
        "version.result",
    ]


def test_run_tool_executes_configured_command(
    monkeypatch,
    capsys,
):
    calls = []

    def record_run(command, *, check):
        calls.append((command, check))

    monkeypatch.setattr(
        dev.subprocess,
        "run",
        record_run,
    )

    expected_label, expected_command = dev.TOOL_COMMANDS["test"]

    dev.run_tool("test")

    assert calls == [
        (expected_command, True),
    ]

    output = capsys.readouterr().out

    assert f"> {expected_label}" in output
    assert f"✓ {expected_label} passed" in output


def test_run_tool_preserves_command_failure(
    monkeypatch,
    capsys,
):
    expected_label, expected_command = dev.TOOL_COMMANDS["test"]
    expected_error = subprocess.CalledProcessError(
        returncode=7,
        cmd=expected_command,
    )

    def fail_run(command, *, check):
        assert command == expected_command
        assert check is True
        raise expected_error

    monkeypatch.setattr(
        dev.subprocess,
        "run",
        fail_run,
    )

    with pytest.raises(subprocess.CalledProcessError) as raised:
        dev.run_tool("test")

    assert raised.value is expected_error

    output = capsys.readouterr().out

    assert f"> {expected_label}" in output
    assert f"✗ {expected_label} failed" in output


def test_version_preview_commands_are_strict_and_non_mutating():
    assert dev.TOOL_COMMANDS["version-next"] == (
        "version.next",
        (
            "semantic-release",
            "--strict",
            "--noop",
            "version",
            "--print",
        ),
    )

    assert dev.TOOL_COMMANDS["version-tag"] == (
        "version.tag",
        (
            "semantic-release",
            "--strict",
            "--noop",
            "version",
            "--print-tag",
        ),
    )
