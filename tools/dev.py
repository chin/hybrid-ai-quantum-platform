from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Callable, Iterable, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_CYAN = "\033[36m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_RESET = "\033[0m"


@dataclass(frozen=True, slots=True)
class Command:
    name: str
    label: str
    argv: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class HelpCommand:
    name: str
    description: str


@dataclass(frozen=True, slots=True)
class DomainCommand:
    key: str
    display_name: str
    run_target: str
    run_description: str
    artifact_target: str
    artifact_description: str
    catalog_factory: Callable[[], Any]


COMMANDS: Mapping[str, Command] = {
    "format": Command("format", "format.write", ("ruff", "format", ".")),
    "format-check": Command(
        "format-check",
        "format.check",
        ("ruff", "format", "--check", "."),
    ),
    "lint": Command("lint", "lint.ruff", ("ruff", "check", ".")),
    "test": Command("test", "test.pytest", ("pytest",)),
    "coverage": Command(
        "coverage",
        "coverage.pytest",
        (
            "pytest",
            "-v",
            "--cov=optengine",
            "--cov-branch",
            "--cov-report=term-missing",
            "--cov-report=html",
        ),
    ),
    "contract-coverage": Command(
        "contract-coverage",
        "coverage.contracts",
        (
            "pytest",
            "-v",
            "tests/test_base_contracts.py",
            "tests/test_base_contract_coverage.py",
            "tests/test_analysis_execution.py",
            "tests/test_mathematics.py",
            "tests/test_domain_maxcut.py",
            "tests/test_domain_portfolio.py",
            "tests/test_utility_policy.py",
            "--cov=optengine.analysis",
            "--cov=optengine.candidate",
            "--cov=optengine.catalog",
            "--cov=optengine.compatibility",
            "--cov=optengine.domains.base",
            "--cov=optengine.evaluation",
            "--cov=optengine.execution",
            "--cov=optengine.formulations.base",
            "--cov=optengine.interpretation",
            "--cov=optengine.mathematics",
            "--cov=optengine.objective",
            "--cov=optengine.operations.base",
            "--cov=optengine.solvers.base",
            "--cov=optengine.strategy",
            "--cov=optengine.utility.base",
            "--cov-branch",
            "--cov-report=term-missing",
            "--cov-fail-under=100",
        ),
    ),
    "runtime-test": Command(
        "runtime-test",
        "test.runtime",
        (
            "pytest",
            "-v",
            "tests/runtime",
            "tests/stages",
            "tests/test_analysis_execution.py",
            "tests/test_engine_workflow.py",
            "tests/test_domain_chain_trace.py",
        ),
    ),
    "regression-test": Command(
        "regression-test",
        "test.regression",
        (
            "pytest",
            "-v",
            "tests/domains",
            "tests/formulations",
            "tests/integration",
            "tests/solvers",
            "tests/utility",
            "tests/writers",
            "tests/test_domain_maxcut.py",
            "tests/test_domain_portfolio.py",
            "tests/test_external_integrations.py",
            "tests/test_release_refactor_regressions.py",
        ),
    ),
    "build": Command(
        "build",
        "build.distributions",
        (sys.executable, "-m", "build"),
    ),
}

COMPOSITES: Mapping[str, tuple[str, ...]] = {
    "ci": (
        "format-check",
        "lint",
        "test",
        "contract-coverage",
        "build",
    ),
    "release-check": (
        "format-check",
        "lint",
        "coverage",
        "contract-coverage",
        "runtime-test",
        "regression-test",
        "build",
    ),
}

HELP_GROUPS: tuple[tuple[str, tuple[HelpCommand, ...]], ...] = (
    (
        "Development",
        (
            HelpCommand("help", "Show available commands"),
            HelpCommand(
                "bootstrap",
                "Verify the toolchain and synchronize the development environment",
            ),
            HelpCommand("dev", "Clean, format, and run all pre-merge checks"),
            HelpCommand("clean", "Remove disposable generated files and caches"),
        ),
    ),
    (
        "Quality",
        (
            HelpCommand("format", "Format source code"),
            HelpCommand(
                "format-check",
                "Verify formatting without modifying source code",
            ),
            HelpCommand("lint", "Run static analysis"),
            HelpCommand("test", "Execute the software test suite"),
            HelpCommand("coverage", "Execute the test suite with branch coverage"),
            HelpCommand(
                "contract-coverage",
                "Require 100% coverage of reusable OOP contracts",
            ),
            HelpCommand(
                "runtime-test",
                "Execute runtime lifecycle and failure-path tests",
            ),
            HelpCommand(
                "regression-test",
                "Execute exhaustive foundation regression tests",
            ),
            HelpCommand("ci", "Run the local CI quality gate"),
        ),
    ),
    (
        "Project",
        (
            HelpCommand(
                "project-plan",
                "Preview release milestones and issue updates",
            ),
            HelpCommand(
                "project-update",
                "Apply release milestones and issue updates",
            ),
        ),
    ),
    (
        "Research and validation",
        (
            HelpCommand("benchmark", "Run performance benchmarks"),
            HelpCommand("validate", "Run research validation"),
        ),
    ),
    (
        "Documentation",
        (HelpCommand("docs", "Build or validate documentation"),),
    ),
    (
        "Release",
        (
            HelpCommand("build", "Build source and wheel distributions"),
            HelpCommand("version", "Preview the next semantic version and Git tag"),
            HelpCommand(
                "release-check",
                "Clean and run all local release-readiness checks",
            ),
            HelpCommand("release", "Trigger the official GitHub release workflow"),
            HelpCommand("publish", "Publish distributions to a package registry"),
        ),
    ),
)


def _domain_commands() -> tuple[DomainCommand, ...]:
    from optengine.presets.maxcut import maxcut_catalog
    from optengine.presets.portfolio import portfolio_catalog

    return (
        DomainCommand(
            key="maxcut",
            display_name="Max-Cut",
            run_target="run",
            run_description="Run the Max-Cut OptEngine quickstart",
            artifact_target="artifact",
            artifact_description="Run and promote the latest Max-Cut quickstart output",
            catalog_factory=maxcut_catalog,
        ),
        DomainCommand(
            key="portfolio",
            display_name="Portfolio",
            run_target="portfolio",
            run_description="Run the bounded portfolio vertical slice",
            artifact_target="portfolio-artifact",
            artifact_description="Run and promote the latest portfolio output",
            catalog_factory=portfolio_catalog,
        ),
    )


def _color(message: str, code: str) -> str:
    if os.getenv("NO_COLOR") is not None:
        return message
    if os.getenv("FORCE_COLOR") is not None or sys.stdout.isatty():
        return f"{code}{message}{_RESET}"
    return message


def _step(name: str) -> None:
    print(_color(f"> {name}", _CYAN), flush=True)


def _passed(name: str) -> None:
    print(_color(f"✓ {name} passed", _GREEN))
    print()


def _failed(name: str) -> None:
    print(_color(f"✗ {name} failed", _RED))
    print()


@contextmanager
def _tool_step(name: str) -> Iterable[None]:
    _step(name)
    try:
        yield
    except Exception:
        _failed(name)
        raise
    else:
        _passed(name)


def _run(argv: Sequence[str], *, cwd: Path = ROOT) -> None:
    subprocess.run(tuple(argv), cwd=cwd, check=True)


def _run_capture(argv: Sequence[str], *, cwd: Path = ROOT) -> str:
    completed = subprocess.run(
        tuple(argv),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(
            detail or f"Command failed with status {completed.returncode}"
        )
    return completed.stdout.strip()


def _run_named(name: str) -> None:
    command = COMMANDS[name]
    with _tool_step(command.label):
        _run(command.argv)


def _run_composite(name: str) -> None:
    for command_name in COMPOSITES[name]:
        _run_named(command_name)


def _format_rows(rows: Sequence[tuple[str, str]], *, indent: int) -> list[str]:
    if not rows:
        return []
    width = max(len(name) for name, _ in rows)
    prefix = " " * indent
    return [f"{prefix}{name.ljust(width)}  {description}" for name, description in rows]


def render_help() -> str:
    lines = ["OptEngine commands", ""]

    for title, commands in HELP_GROUPS[:2]:
        lines.append(title)
        lines.extend(
            _format_rows(
                tuple((command.name, command.description) for command in commands),
                indent=2,
            )
        )
        lines.append("")

    lines.append("Domains")
    for domain in _domain_commands():
        catalog = domain.catalog_factory()
        lines.extend((f"  {domain.display_name}", "    Commands"))
        lines.extend(
            _format_rows(
                (
                    (domain.run_target, domain.run_description),
                    (domain.artifact_target, domain.artifact_description),
                ),
                indent=6,
            )
        )

        lines.append("    Formulations")
        lines.extend(
            _format_rows(
                tuple((name, "configured") for name in catalog.formulation_names),
                indent=6,
            )
        )
        lines.append("    Operations")
        lines.extend(
            _format_rows(
                tuple((name, "configured") for name in catalog.operation_names),
                indent=6,
            )
        )
        lines.append("    Solvers")
        lines.extend(
            _format_rows(
                tuple((name, "configured") for name in catalog.solver_names),
                indent=6,
            )
        )
        lines.append("")

    for title, commands in HELP_GROUPS[2:]:
        lines.append(title)
        lines.extend(
            _format_rows(
                tuple((command.name, command.description) for command in commands),
                indent=2,
            )
        )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _load_pyproject() -> dict[str, Any]:
    with PYPROJECT.open("rb") as handle:
        return tomllib.load(handle)


def _current_branch() -> str:
    configured = os.getenv("GITHUB_REF_NAME")
    if configured:
        return configured
    return _run_capture(("git", "branch", "--show-current"))


def _branch_matches(pattern: str, branch: str) -> bool:
    if pattern == "*":
        pattern = ".*"
    return re.compile(pattern).match(branch) is not None


def _is_release_branch(config: Mapping[str, Any], branch: str) -> bool:
    branches = config.get("branches", {})
    return any(
        _branch_matches(str(options.get("match", "")), branch)
        for options in branches.values()
        if isinstance(options, Mapping)
    )


def _preview_configuration(
    semantic_release: Mapping[str, Any],
    branch: str,
) -> dict[str, Any]:
    config = copy.deepcopy(dict(semantic_release))
    if _is_release_branch(config, branch):
        return config

    existing = dict(config.get("branches", {}))
    config["branches"] = {
        "preview": {
            "match": rf"^{re.escape(branch)}$",
            "prerelease": False,
        },
        **existing,
    }
    config["repo_dir"] = str(ROOT)
    return config


@contextmanager
def _semantic_release_preview_config(branch: str) -> Iterable[Path]:
    project = _load_pyproject()
    semantic_release = project["tool"]["semantic_release"]
    if _is_release_branch(semantic_release, branch):
        yield PYPROJECT
        return

    payload = {
        "semantic_release": _preview_configuration(semantic_release, branch),
    }
    descriptor, filename = tempfile.mkstemp(
        prefix="optengine-semantic-release-preview-",
        suffix=".json",
    )
    path = Path(filename)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        yield path
    finally:
        path.unlink(missing_ok=True)


def _semantic_release_value(config: Path, option: str) -> str:
    return _run_capture(
        (
            "semantic-release",
            "--strict",
            "--noop",
            "--config",
            str(config),
            "version",
            option,
        )
    )


def preview_version() -> tuple[str, str, str]:
    project = _load_pyproject()
    current = str(project["project"]["version"])
    branch = _current_branch()

    with _semantic_release_preview_config(branch) as config:
        next_version = _semantic_release_value(config, "--print")

    tag_format = str(
        project["tool"]["semantic_release"].get("tag_format", "v{version}")
    )
    tag = tag_format.format(version=next_version)

    for name, value in (
        ("version.current", current),
        ("version.next", next_version),
        ("version.tag", tag),
        ("version.branch", branch),
    ):
        with _tool_step(name):
            print(value)

    return current, next_version, tag


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OptEngine development command runner")
    parser.add_argument(
        "command",
        choices=(
            "help",
            *COMMANDS.keys(),
            *COMPOSITES.keys(),
            "version",
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "help":
        print(render_help(), end="")
        return 0
    if args.command == "version":
        preview_version()
        return 0
    if args.command in COMPOSITES:
        _run_composite(args.command)
        return 0
    _run_named(args.command)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        message = str(error).strip()
        if message:
            print(message, file=sys.stderr)
        raise SystemExit(2) from error
