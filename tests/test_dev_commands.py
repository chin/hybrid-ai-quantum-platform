from __future__ import annotations

import json
from pathlib import Path

from tools import dev


def test_help_is_derived_from_configured_domain_catalogs() -> None:
    output = dev.render_help()

    assert "Domains\n  Max-Cut\n    Commands" in output
    assert "  Portfolio\n    Commands" in output

    for domain in dev._domain_commands():
        catalog = domain.catalog_factory()
        assert domain.display_name in output
        assert domain.run_target in output
        assert domain.artifact_target in output
        for name in catalog.formulation_names:
            assert f"      {name}" in output
        for name in catalog.operation_names:
            assert f"      {name}" in output
        for name in catalog.solver_names:
            assert f"      {name}" in output


def test_help_component_sections_are_typed_and_nested() -> None:
    output = dev.render_help()

    maxcut = output.index("  Max-Cut")
    portfolio = output.index("  Portfolio")
    assert maxcut < output.index("    Formulations", maxcut) < portfolio
    assert maxcut < output.index("    Operations", maxcut) < portfolio
    assert maxcut < output.index("    Solvers", maxcut) < portfolio


def test_make_help_delegates_to_the_development_registry() -> None:
    makefile = (dev.ROOT / "Makefile").read_text(encoding="utf-8")
    help_recipe = makefile.split("help:", 1)[1].split("\n\n", 1)[0]
    assert "$(DEV_COMMAND) help" in help_recipe
    assert "grep -E" not in help_recipe


def test_feature_branch_preview_adds_temporary_release_group() -> None:
    source = dev._load_pyproject()["tool"]["semantic_release"]
    branch = "feat/portfolio-domain-cli"

    preview = dev._preview_configuration(source, branch)

    assert preview["branches"]["preview"] == {
        "match": r"^feat/portfolio\-domain\-cli$",
        "prerelease": False,
    }
    assert preview["branches"]["main"] == source["branches"]["main"]
    assert source["branches"] == {"main": {"match": "main", "prerelease": False}}


def test_release_branch_uses_canonical_configuration() -> None:
    with dev._semantic_release_preview_config("main") as config:
        assert config == dev.PYPROJECT


def test_feature_branch_preview_file_is_temporary_and_non_mutating() -> None:
    pyproject_before = dev.PYPROJECT.read_bytes()
    preview_path: Path

    with dev._semantic_release_preview_config(
        "feat/portfolio-domain-cli"
    ) as preview_path:
        assert preview_path != dev.PYPROJECT
        assert preview_path.exists()
        payload = json.loads(preview_path.read_text(encoding="utf-8"))
        preview = payload["semantic_release"]["branches"]["preview"]
        assert preview["match"] == r"^feat/portfolio\-domain\-cli$"
        assert preview["prerelease"] is False

    assert not preview_path.exists()
    assert dev.PYPROJECT.read_bytes() == pyproject_before


def test_version_preview_calculates_on_feature_branch_without_changing_sources(
    monkeypatch,
    capsys,
) -> None:
    pyproject_before = dev.PYPROJECT.read_bytes()
    current_before = dev._load_pyproject()["project"]["version"]
    simulated_next_version = "9.9.9"
    seen: dict[str, object] = {}

    monkeypatch.setattr(dev, "_current_branch", lambda: "feat/portfolio-domain-cli")

    def fake_semantic_release_value(config: Path, option: str) -> str:
        seen["option"] = option
        seen["config"] = json.loads(config.read_text(encoding="utf-8"))
        return simulated_next_version

    monkeypatch.setattr(dev, "_semantic_release_value", fake_semantic_release_value)

    current, next_version, tag = dev.preview_version()

    assert current == current_before
    assert next_version == simulated_next_version
    assert tag == f"v{simulated_next_version}"
    assert seen["option"] == "--print"
    assert (
        seen["config"]["semantic_release"]["branches"]["preview"]["match"]
        == r"^feat/portfolio\-domain\-cli$"
    )
    assert dev.PYPROJECT.read_bytes() == pyproject_before

    output = capsys.readouterr().out
    assert "> version.current" in output
    assert "> version.next" in output
    assert "> version.tag" in output
    assert "> version.branch" in output


def test_dev_imports_tomli_when_tomllib_is_unavailable(monkeypatch) -> None:
    import builtins
    import runpy
    import sys
    import types

    fake_tomli = types.ModuleType("tomli")
    fake_tomli.loads = lambda value: {"value": value}
    monkeypatch.setitem(sys.modules, "tomli", fake_tomli)

    real_import = builtins.__import__

    def import_without_tomllib(
        name: str,
        globals=None,
        locals=None,
        fromlist=(),
        level: int = 0,
    ):
        if name == "tomllib":
            raise ModuleNotFoundError("No module named 'tomllib'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_tomllib)

    namespace = runpy.run_path(
        dev.ROOT / "tools" / "dev.py",
        run_name="tools.dev_python310_probe",
    )

    assert namespace["tomllib"] is fake_tomli
