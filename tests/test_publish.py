from __future__ import annotations

import subprocess

import pytest

from tools import publish


def test_next_tag_extracts_semantic_release_tag(monkeypatch) -> None:
    result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="warning text\nv0.3.0\n",
        stderr="",
    )

    monkeypatch.setattr(
        publish,
        "_run",
        lambda *args, **kwargs: result,
    )

    assert publish._next_tag() == "v0.3.0"


def test_next_tag_rejects_no_release(monkeypatch) -> None:
    result = subprocess.CompletedProcess(
        args=[],
        returncode=2,
        stdout="",
        stderr="No release will be made\n",
    )

    monkeypatch.setattr(
        publish,
        "_run",
        lambda *args, **kwargs: result,
    )

    with pytest.raises(
        publish.PublishError,
        match="did not calculate a new release",
    ):
        publish._next_tag()


def test_verify_release_assets_requires_wheel_and_source(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        publish,
        "_release_details",
        lambda tag: {
            "tagName": tag,
            "url": "https://example.test/release",
            "isImmutable": True,
            "assets": [
                {"name": "optengine-0.3.0-py3-none-any.whl"},
            ],
        },
    )

    with pytest.raises(
        publish.PublishError,
        match="missing required distribution assets",
    ):
        publish._verify_release_assets("v0.3.0")


def test_verify_release_assets_accepts_complete_release(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        publish,
        "_release_details",
        lambda tag: {
            "tagName": tag,
            "url": "https://example.test/release",
            "isImmutable": True,
            "assets": [
                {"name": "optengine-0.3.0-py3-none-any.whl"},
                {"name": "optengine-0.3.0.tar.gz"},
            ],
        },
    )

    release = publish._verify_release_assets("v0.3.0")

    assert release["tagName"] == "v0.3.0"


def test_make_publish_delegates_to_publish_tool() -> None:
    makefile = (publish.ROOT / "Makefile").read_text(encoding="utf-8")
    recipe = makefile.split("publish:", 1)[1].split("\n\n", 1)[0]

    assert "release-check" in recipe
    assert "uv run python tools/publish.py" in recipe
