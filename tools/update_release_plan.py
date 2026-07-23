from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Sequence


APPROVED_PREFIXES = ("feat:", "fix:", "test:", "docs:", "research:", "chore:")
APPROVED_LABELS = frozenset(
    {
        "initiative:vanguard",
        "area:core",
        "area:portfolio",
        "area:policy",
        "area:artifacts",
        "area:submission",
    }
)


@dataclass(frozen=True, slots=True)
class MilestonePlan:
    title: str
    description: str
    state: str = "open"
    due_on: str | None = None


@dataclass(frozen=True, slots=True)
class IssuePlan:
    title: str
    milestone: str
    labels: tuple[str, ...]
    body: str
    state: str = "open"


MILESTONES = (
    MilestonePlan(
        title="v0.2.0 — First Public Release",
        description=(
            "Publish the first public OptEngine release with the idempotent "
            "polymorphic runtime, domain-aware execution presentation, "
            "non-breaking utility canonicalization, exhaustive regression "
            "coverage, and semantic-release automation."
        ),
        due_on="2026-07-22T23:59:59Z",
    ),
    MilestonePlan(
        title="v0.3.0 — Model Entry Points and Hamiltonians",
        description=(
            "Extend OptEngine so callers can execute validated Model objects "
            "directly, then add a canonical Hamiltonian Model family and "
            "quantum solver capability path without regressing Domain input."
        ),
    ),
)


ISSUES = (
    IssuePlan(
        title="feat: complete idempotent polymorphic OptEngine refactor",
        milestone=MILESTONES[0].title,
        labels=("initiative:vanguard", "area:core"),
        state="closed",
        body=dedent(
            """
            ## Outcome

            Complete the canonical polymorphic collaboration chain:

            `Domain → Interpretation → Objective → Expression → Curve → Formulation → Model → Operation → Solver → Strategy → Execution → Utility → Decision → Recommendation`

            ## Acceptance criteria

            - [x] Preserve Domain as the aggregate root and semantic owner.
            - [x] Make interpretation, formulation, operation, solver, utility, and policy collaborators polymorphic.
            - [x] Make analysis and execution idempotent and retain failed strategy evidence.
            - [x] Canonicalize `UtilityModel` to `Utility` and utility results to `Assessment` without breaking existing imports.
            - [x] Use canonical concrete names such as `MaxCut(Domain)` and `Portfolio(Domain)` without redundant `*Domain` aliases.
            - [x] Preserve deterministic identities, fingerprints, artifacts, and public exports.

            ## Verification

            - `make test`
            - `make coverage`
            - `make contract-coverage`
            - `make runtime-test`
            - `make regression-test`
            """
        ).strip(),
    ),
    IssuePlan(
        title="feat: render domain-aware strategy execution in the terminal",
        milestone=MILESTONES[0].title,
        labels=("initiative:vanguard", "area:core"),
        state="closed",
        body=dedent(
            """
            ## Outcome

            Present OptEngine as a guided optimization run rather than an internal object dump.

            ## Acceptance criteria

            - [x] Show the problem interpretation, objective, expression, and curve once.
            - [x] Show each strategy's selected formulation, model, operation, and solver.
            - [x] Show an in-progress marker while each strategy executes.
            - [x] Show domain-specific results before moving to the next strategy.
            - [x] Show failed or partial strategies without hiding diagnostic evidence.
            - [x] Show utility ranking, decision, recommendation, and artifact location.
            - [x] Keep the complete structured trace available for tests and artifacts.

            ## Verification

            - `make run`
            - `make portfolio`
            - `make runtime-test`
            """
        ).strip(),
    ),
    IssuePlan(
        title="test: restore exhaustive regression and contract coverage",
        milestone=MILESTONES[0].title,
        labels=("initiative:vanguard", "area:core"),
        state="closed",
        body=dedent(
            """
            ## Outcome

            Restore the pre-refactor behavioral tests and extend them for reusable OOP contracts and domain-specific implementations.

            ## Acceptance criteria

            - [x] Preserve runtime, integration, solver, policy, utility, writer, registry, and public API regressions.
            - [x] Run the same reusable Domain contract against every configured Domain.
            - [x] Retain domain-specific validation, feasibility, decoding, and adapter tests.
            - [x] Require 100% statement and branch coverage for the reusable OOP contract modules.
            - [x] Exercise `ExecutionInstance.execute()` from the contract-coverage test selection.
            - [x] Keep optional backend behavior explicit and deterministic.

            ## Verification

            - `make contract-coverage`
            - `make coverage`
            - `make regression-test`
            """
        ).strip(),
    ),
    IssuePlan(
        title="fix: restore semantic-release preview and dynamic domain help",
        milestone=MILESTONES[0].title,
        labels=("initiative:vanguard", "area:submission"),
        state="closed",
        body=dedent(
            """
            ## Outcome

            Restore non-mutating semantic-version preview from feature branches while retaining the real `main` release guard, and derive Make help from configured Domain catalogs.

            ## Acceptance criteria

            - [x] `make version` calculates the next release from a feature branch using a temporary no-op release group.
            - [x] Preview leaves `pyproject.toml`, `_version.py`, and `CHANGELOG.md` unchanged.
            - [x] Actual releases remain restricted to `main`.
            - [x] `make help` groups Domain commands and derives formulations, operations, and solvers from each configured catalog.
            - [x] Semantic Release remains the only mutating version and changelog mechanism.

            ## Verification

            - `make version`
            - `make help`
            - `make ci`
            """
        ).strip(),
    ),
    IssuePlan(
        title="chore: clean the first-release repository surface",
        milestone=MILESTONES[0].title,
        labels=("initiative:vanguard", "area:submission"),
        state="closed",
        body=dedent(
            """
            ## Outcome

            Keep only intentional project content in the public release.

            ## Acceptance criteria

            - [x] Retain `AI_USAGE.md` as an intentionally authored project file.
            - [x] Remove generated delivery archives, migration reports, temporary manifests, caches, and runtime outputs from the release commit.
            - [x] Preserve only project documentation intentionally authored or approved for publication.
            - [x] Remove dead imports and redundant concrete-Domain aliases.
            - [x] Keep generated artifacts out of Git unless they are intentional regression fixtures.

            ## Verification

            - `make lint`
            - `git diff --check`
            - `git status --short`
            """
        ).strip(),
    ),
    IssuePlan(
        title="chore: publish the first OptEngine release",
        milestone=MILESTONES[0].title,
        labels=("initiative:vanguard", "area:submission"),
        body=dedent(
            """
            ## Goal

            Publish the first public OptEngine release from the completed polymorphic refactor.

            ## Acceptance criteria

            - [ ] `make release-check` passes from the release commit.
            - [ ] `make version` previews `0.2.0` and `v0.2.0` without modifying the tree.
            - [ ] The release commit is merged to `main` and local `main` matches `origin/main`.
            - [ ] `make release` dispatches the manual Semantic Release workflow.
            - [ ] Semantic Release updates `pyproject.toml`, `optengine/_version.py`, and `CHANGELOG.md` automatically.
            - [ ] The GitHub release contains the source distribution and wheel.
            - [ ] The installed wheel reports `optengine.__version__ == "0.2.0"`.
            """
        ).strip(),
    ),
    IssuePlan(
        title="feat: accept Model as a public OptEngine entry point",
        milestone=MILESTONES[1].title,
        labels=("initiative:vanguard", "area:core"),
        body=dedent(
            """
            ## Goal

            Allow callers to solve a validated `Model` directly while preserving the existing Domain entry point.

            ## Acceptance criteria

            - [ ] The public runtime accepts `Domain | Model` through one canonical dispatch path.
            - [ ] Domain input retains interpretation and formulation discovery exactly as it works today.
            - [ ] Model input starts from the supplied Model and discovers compatible operations and solvers without rebuilding it.
            - [ ] Every Model exposes or validates its owning Domain and Objective so candidate decoding and evaluation remain domain-correct.
            - [ ] Requested strategies, utility, policy, explanation, writing, provenance, and artifacts work for both entry paths.
            - [ ] Terminal tracing marks upstream stages as supplied and shows the executed `Model → Operation → Solver → Strategy` path.
            - [ ] Invalid, detached, or cross-domain Models fail at the public boundary with actionable errors.
            - [ ] Existing Domain callers and compatibility imports remain non-breaking.
            """
        ).strip(),
    ),
    IssuePlan(
        title="feat: add Hamiltonian as a canonical Model implementation",
        milestone=MILESTONES[1].title,
        labels=("initiative:vanguard", "area:core"),
        body=dedent(
            """
            ## Goal

            Represent quantum Hamiltonians as first-class solver-oriented Models rather than opaque payloads.

            ## Acceptance criteria

            - [ ] Add a backend-neutral operator expression with canonical qubit, coefficient, and Pauli-term ordering.
            - [ ] Add `Hamiltonian(Model)` using the canonical object naming convention.
            - [ ] Support real and complex coefficients with explicit Hermiticity validation.
            - [ ] Track qubit count, locality, term count, commutation metadata, and diagonal/non-diagonal structure.
            - [ ] Produce deterministic, order-independent fingerprints and serializable metadata.
            - [ ] Provide an exact bridge for diagonal Ising/QUBO Hamiltonians without claiming equivalence for general noncommuting operators.
            """
        ).strip(),
    ),
    IssuePlan(
        title="feat: add Hamiltonian operations and solver capability matching",
        milestone=MILESTONES[1].title,
        labels=("initiative:vanguard", "area:core"),
        body=dedent(
            """
            ## Goal

            Route Hamiltonian Models only to operations and solvers that can execute their operator structure.

            ## Acceptance criteria

            - [ ] Add operations for ground-state search and expectation estimation.
            - [ ] Match on qubit count, locality, coefficient type, diagonal structure, commutation requirements, and backend availability.
            - [ ] Retain compatibility evidence for every accepted and rejected Hamiltonian path.
            - [ ] Support exact/reference execution separately from variational or sampling execution.
            - [ ] Preserve failure isolation and utility assessment across mixed classical and quantum strategies.
            """
        ).strip(),
    ),
    IssuePlan(
        title="feat: add Hamiltonian framework adapters",
        milestone=MILESTONES[1].title,
        labels=("initiative:vanguard", "area:core"),
        body=dedent(
            """
            ## Goal

            Import common framework Hamiltonians without coupling the core object model to optional dependencies.

            ## Acceptance criteria

            - [ ] Add optional adapters for Qiskit `SparsePauliOp`.
            - [ ] Add optional adapters for PennyLane Hamiltonian/operator objects.
            - [ ] Add optional adapters for CUDA-Q spin operators.
            - [ ] Add optional adapters for OpenFermion operators.
            - [ ] Preserve canonical identity across equivalent adapter inputs.
            - [ ] Report unavailable optional dependencies without import-time failure.
            """
        ).strip(),
    ),
    IssuePlan(
        title="test: add Model-entrypoint and Hamiltonian regression matrices",
        milestone=MILESTONES[1].title,
        labels=("initiative:vanguard", "area:core"),
        body=dedent(
            """
            ## Goal

            Exhaustively validate direct Model execution and Hamiltonian interoperability.

            ## Acceptance criteria

            - [ ] Run reusable Model-entrypoint contracts against QUBO, CQM, and Hamiltonian Models.
            - [ ] Verify Domain and Model entry paths produce equivalent outcomes for the same represented problem.
            - [ ] Cover detached Models, cross-domain decoding, incompatible operations, incompatible solvers, and failed executions.
            - [ ] Cover Hamiltonian canonicalization, Hermiticity, locality, adapter equivalence, and diagonal QUBO/Ising bridges.
            - [ ] Add optional-backend integration tests without weakening portable contract coverage.
            - [ ] Preserve 100% reusable-contract coverage.
            """
        ).strip(),
    ),
    IssuePlan(
        title="docs: document direct Model execution and Hamiltonian support",
        milestone=MILESTONES[1].title,
        labels=("initiative:vanguard", "area:core"),
        body=dedent(
            """
            ## Goal

            Document the public distinction between Domain-driven discovery and direct Model execution.

            ## Acceptance criteria

            - [ ] Show when to provide a Domain versus a prebuilt Model.
            - [ ] Document the validated Model ownership and decoding contract.
            - [ ] Document diagonal Ising/QUBO support separately from general quantum Hamiltonians.
            - [ ] Include framework-adapter examples and optional dependency behavior.
            - [ ] Document terminal and artifact traces for supplied Models.
            """
        ).strip(),
    ),
)


def _run(
    argv: Sequence[str],
    *,
    capture: bool = False,
) -> str:
    completed = subprocess.run(
        tuple(argv),
        check=False,
        text=True,
        capture_output=capture,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(detail or f"Command failed: {' '.join(argv)}")
    return completed.stdout.strip() if capture else ""


def _json(argv: Sequence[str]) -> Any:
    output = _run(argv, capture=True)
    return json.loads(output) if output else None


def _repo() -> str:
    return _run(
        ("gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"),
        capture=True,
    )


def _existing_labels(repo: str) -> set[str]:
    values = _json(
        (
            "gh",
            "label",
            "list",
            "--repo",
            repo,
            "--limit",
            "200",
            "--json",
            "name",
        )
    )
    return {str(item["name"]) for item in values}


def _validate_repository_labels(repo: str) -> None:
    required = {label for issue in ISSUES for label in issue.labels}
    missing = sorted(required - _existing_labels(repo))
    if missing:
        raise RuntimeError(
            "Repository is missing required labels: " + ", ".join(missing)
        )


def _validate_plan() -> None:
    milestone_titles = {milestone.title for milestone in MILESTONES}
    issue_titles: set[str] = set()

    for issue in ISSUES:
        if not issue.title.startswith(APPROVED_PREFIXES):
            raise ValueError(f"Unapproved issue title prefix: {issue.title}")
        if issue.title in issue_titles:
            raise ValueError(f"Duplicate issue title: {issue.title}")
        issue_titles.add(issue.title)
        if issue.milestone not in milestone_titles:
            raise ValueError(f"Unknown milestone for issue: {issue.title}")
        if not set(issue.labels) <= APPROVED_LABELS:
            raise ValueError(f"Unapproved labels for issue: {issue.title}")
        if issue.state not in {"open", "closed"}:
            raise ValueError(f"Unsupported issue state: {issue.state}")


def _existing_milestones(repo: str) -> dict[str, dict[str, Any]]:
    values = _json(
        (
            "gh",
            "api",
            f"repos/{repo}/milestones?state=all&per_page=100",
        )
    )
    return {str(item["title"]): item for item in values}


def _existing_issues(repo: str) -> dict[str, dict[str, Any]]:
    values = _json(
        (
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "all",
            "--limit",
            "500",
            "--json",
            "number,title,state,milestone,labels,url",
        )
    )
    return {str(item["title"]): item for item in values}


def _print_action(kind: str, name: str, detail: str) -> None:
    print(f"{kind:<8} {name}")
    print(f"         {detail}")


def _sync_milestones(repo: str, *, apply: bool) -> None:
    existing = _existing_milestones(repo)
    for plan in MILESTONES:
        current = existing.get(plan.title)
        payload = [
            "-f",
            f"title={plan.title}",
            "-f",
            f"description={plan.description}",
            "-f",
            f"state={plan.state}",
        ]
        if plan.due_on is not None:
            payload.extend(("-f", f"due_on={plan.due_on}"))

        if current is None:
            _print_action("CREATE", plan.title, "milestone")
            if apply:
                _run(
                    (
                        "gh",
                        "api",
                        "--method",
                        "POST",
                        f"repos/{repo}/milestones",
                        *payload,
                    )
                )
            continue

        _print_action("UPDATE", plan.title, f"milestone #{current['number']}")
        if apply:
            _run(
                (
                    "gh",
                    "api",
                    "--method",
                    "PATCH",
                    f"repos/{repo}/milestones/{current['number']}",
                    *payload,
                )
            )


def _issue_labels(issue: dict[str, Any]) -> set[str]:
    return {str(label["name"]) for label in issue.get("labels") or ()}


def _issue_milestone(issue: dict[str, Any]) -> str | None:
    milestone = issue.get("milestone")
    return None if milestone is None else str(milestone["title"])


def _sync_issues(repo: str, *, apply: bool) -> None:
    existing = _existing_issues(repo)
    for plan in ISSUES:
        current = existing.get(plan.title)
        if current is None:
            _print_action("CREATE", plan.title, f"issue → {plan.milestone}")
            if apply:
                url = _run(
                    (
                        "gh",
                        "issue",
                        "create",
                        "--repo",
                        repo,
                        "--title",
                        plan.title,
                        "--body",
                        plan.body,
                        "--milestone",
                        plan.milestone,
                        "--label",
                        ",".join(plan.labels),
                    ),
                    capture=True,
                )
                number = url.rstrip("/").rsplit("/", 1)[-1]
                if not number.isdigit():
                    raise RuntimeError(
                        f"Unable to determine created issue number from: {url}"
                    )
                if plan.state == "closed":
                    _run(
                        (
                            "gh",
                            "issue",
                            "close",
                            number,
                            "--repo",
                            repo,
                            "--reason",
                            "completed",
                        )
                    )
            continue

        number = str(current["number"])
        changes: list[str] = []
        if _issue_milestone(current) != plan.milestone:
            changes.append(f"milestone={plan.milestone}")
        missing_labels = tuple(
            label for label in plan.labels if label not in _issue_labels(current)
        )
        if missing_labels:
            changes.append("labels=" + ",".join(missing_labels))
        if str(current["state"]).lower() != plan.state:
            changes.append(f"state={plan.state}")
        changes.append("body=canonical")

        _print_action("UPDATE", plan.title, f"issue #{number}: {'; '.join(changes)}")
        if not apply:
            continue

        edit = [
            "gh",
            "issue",
            "edit",
            number,
            "--repo",
            repo,
            "--body",
            plan.body,
            "--milestone",
            plan.milestone,
        ]
        for label in missing_labels:
            edit.extend(("--add-label", label))
        _run(tuple(edit))

        current_state = str(current["state"]).lower()
        if plan.state == "closed" and current_state != "closed":
            _run(
                (
                    "gh",
                    "issue",
                    "close",
                    number,
                    "--repo",
                    repo,
                    "--reason",
                    "completed",
                )
            )
        elif plan.state == "open" and current_state != "open":
            _run(("gh", "issue", "reopen", number, "--repo", repo))


def sync(*, apply: bool) -> None:
    _validate_plan()
    _run(("gh", "auth", "status"))
    repo = _repo()
    _validate_repository_labels(repo)

    mode = "APPLY" if apply else "PREVIEW"
    print(f"OptEngine release plan :: {mode}")
    print(f"Repository: {repo}")
    print()

    _sync_milestones(repo, apply=apply)
    _sync_issues(repo, apply=apply)

    print()
    if apply:
        print("Release plan synchronized.")
    else:
        print("Preview complete. Run with --apply to synchronize GitHub.")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview or apply OptEngine release milestones and issues."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create or update the configured GitHub milestones and issues.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    sync(apply=args.apply)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2) from error
