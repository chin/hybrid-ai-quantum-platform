from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence

from optengine import cli


TOOL_COMMANDS: dict[str, tuple[str, Sequence[str]]] = {
    "status": (
        "git.status",
        ("git", "status", "--short", "--branch"),
    ),
    "format": (
        "format.ruff",
        ("ruff", "format", "."),
    ),
    "format-check": (
        "format.ruff",
        ("ruff", "format", "--check", "."),
    ),
    "lint": (
        "lint.ruff",
        ("ruff", "check", "."),
    ),
    "test": (
        "test.pytest",
        ("pytest", "-v"),
    ),
    "coverage": (
        "coverage.pytest",
        (
            "pytest",
            "--cov=optengine",
            "--cov-branch",
            "--cov-report=term-missing",
            "--cov-report=html",
            "-v",
        ),
    ),
    "runtime-test": (
        "test.runtime",
        (
            "pytest",
            "tests/runtime",
            "-v",
        ),
    ),
    "regression-test": (
        "test.regression",
        (
            "pytest",
            "tests",
            "--cov=optengine",
            "--cov-branch",
            "--cov-report=term-missing",
            "-v",
        ),
    ),
    "build": (
        "build.package",
        (sys.executable, "-m", "build"),
    ),
    "version-next": (
        "version.next",
        (
            "semantic-release",
            "--strict",
            "--noop",
            "version",
            "--print",
        ),
    ),
    "version-tag": (
        "version.tag",
        (
            "semantic-release",
            "--strict",
            "--noop",
            "version",
            "--print-tag",
        ),
    ),
    "version-last-tag": (
        "version.last-tag",
        (
            "semantic-release",
            "version",
            "--print-last-released-tag",
        ),
    ),
}

COMMAND_GROUPS: dict[str, tuple[str, ...]] = {
    "ci": (
        "status",
        "format-check",
        "lint",
        "coverage",
    ),
    "release-check": (
        "ci",
        "build",
    ),
    "version": (
        "version-next",
        "version-tag",
        # "version-last-tag",
    ),
}


def run_tool(command_name: str) -> None:
    label, command = TOOL_COMMANDS[command_name]

    with cli.tool_block(label):
        subprocess.run(command, check=True)


def run_target(target_name: str) -> None:
    if target_name in TOOL_COMMANDS:
        run_tool(target_name)
        return

    for child_target in COMMAND_GROUPS[target_name]:
        run_target(child_target)

    cli.tool_result(f"{target_name}.result")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OptEngine development commands.")
    parser.add_argument(
        "target",
        choices=sorted(TOOL_COMMANDS.keys() | COMMAND_GROUPS.keys()),
        help="Development command or command group to execute.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        run_target(args.target)
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from None


if __name__ == "__main__":
    main()
