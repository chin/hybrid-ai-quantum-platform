from __future__ import annotations

from pathlib import Path

import pytest

from tools import dev
from tools import update_release_plan as plan


def test_release_plan_uses_approved_titles_labels_and_unique_identity() -> None:
    milestone_titles = [milestone.title for milestone in plan.MILESTONES]
    issue_titles = [issue.title for issue in plan.ISSUES]

    assert len(milestone_titles) == len(set(milestone_titles))
    assert len(issue_titles) == len(set(issue_titles))
    assert all(title.startswith(plan.APPROVED_PREFIXES) for title in issue_titles)
    assert all(set(issue.labels) <= plan.APPROVED_LABELS for issue in plan.ISSUES)
    assert all(issue.milestone in milestone_titles for issue in plan.ISSUES)
    plan._validate_plan()


def test_first_release_and_next_model_release_are_separated() -> None:
    first_release = "v0.2.0 — First Public Release"
    model_release = "v0.3.0 — Model Entry Points and Hamiltonians"

    current = [issue for issue in plan.ISSUES if issue.milestone == first_release]
    future = [issue for issue in plan.ISSUES if issue.milestone == model_release]

    assert current
    assert future
    assert all(issue.state == "closed" for issue in current[:-1])
    assert current[-1].title == "chore: publish the first OptEngine release"
    assert current[-1].state == "open"

    future_titles = {issue.title for issue in future}
    assert "feat: accept Model as a public OptEngine entry point" in future_titles
    assert "feat: add Hamiltonian as a canonical Model implementation" in future_titles
    assert all(issue.state == "open" for issue in future)


def test_model_entrypoint_issue_preserves_domain_path_and_model_ownership() -> None:
    issue = next(
        item
        for item in plan.ISSUES
        if item.title == "feat: accept Model as a public OptEngine entry point"
    )

    assert "Domain | Model" in issue.body
    assert "Domain input retains" in issue.body
    assert "owning Domain and Objective" in issue.body
    assert "cross-domain Models" in issue.body
    assert "remain non-breaking" in issue.body


def test_hamiltonian_issue_uses_canonical_model_name() -> None:
    issue = next(
        item
        for item in plan.ISSUES
        if item.title == "feat: add Hamiltonian as a canonical Model implementation"
    )

    assert "`Hamiltonian(Model)`" in issue.body
    assert "HamiltonianModel" not in issue.body
    assert "diagonal Ising/QUBO" in issue.body
    assert "noncommuting" in issue.body


def test_make_exposes_preview_and_apply_project_commands() -> None:
    root = Path(__file__).parents[1]
    makefile = (root / "Makefile").read_text(encoding="utf-8")
    help_output = dev.render_help()

    assert "project-plan:" in makefile
    assert "tools/update_release_plan.py" in makefile
    assert "project-update:" in makefile
    assert "tools/update_release_plan.py --apply" in makefile
    assert "Project\n  project-plan" in help_output
    assert "project-update" in help_output


def test_sync_preview_never_mutates(monkeypatch: pytest.MonkeyPatch) -> None:
    actions: list[tuple[str, bool]] = []

    monkeypatch.setattr(plan, "_run", lambda *args, **kwargs: "owner/repo")
    monkeypatch.setattr(plan, "_repo", lambda: "owner/repo")
    monkeypatch.setattr(plan, "_validate_repository_labels", lambda repo: None)
    monkeypatch.setattr(
        plan,
        "_sync_milestones",
        lambda repo, *, apply: actions.append(("milestones", apply)),
    )
    monkeypatch.setattr(
        plan,
        "_sync_issues",
        lambda repo, *, apply: actions.append(("issues", apply)),
    )

    plan.sync(apply=False)

    assert actions == [("milestones", False), ("issues", False)]
