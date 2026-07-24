from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]

RELEASE_WORKFLOW = "release.yml"
PACKAGE_WORKFLOW = "publish-package.yml"
RELEASE_BRANCH = "main"

RUN_POLL_ATTEMPTS = 30
PACKAGE_TRIGGER_ATTEMPTS = 15
POLL_INTERVAL_SECONDS = 2

TAG_PATTERN = re.compile(r"^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


class PublishError(RuntimeError):
    """Raised when publication cannot complete safely."""


def _run(
    command: Sequence[str],
    *,
    capture: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )

    if check and result.returncode != 0:
        if capture:
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)

        raise PublishError(
            f"command failed with exit code {result.returncode}: {' '.join(command)}"
        )

    return result


def _output(*command: str) -> str:
    return _run(command, capture=True).stdout.strip()


def _step(name: str) -> None:
    print(f"\033[36m> {name}\033[0m", flush=True)


def _pass(name: str) -> None:
    print(f"\033[32m✓ {name} passed\033[0m\n", flush=True)


def _require_command(name: str) -> None:
    if shutil.which(name) is None:
        raise PublishError(f"required command is not installed: {name}")


def _require_main() -> None:
    branch = _output("git", "branch", "--show-current")
    if branch != RELEASE_BRANCH:
        raise PublishError(f"current branch is {branch!r}; expected {RELEASE_BRANCH!r}")


def _require_clean_tree() -> None:
    status = _output("git", "status", "--porcelain")
    if status:
        raise PublishError("working tree is not clean")


def _require_synchronized_main() -> None:
    _run("git", "fetch", "origin", RELEASE_BRANCH, "--tags")

    local_sha = _output("git", "rev-parse", "HEAD")
    remote_sha = _output("git", "rev-parse", f"origin/{RELEASE_BRANCH}")

    if local_sha != remote_sha:
        raise PublishError(
            f"local {RELEASE_BRANCH} does not match origin/{RELEASE_BRANCH}"
        )


def _next_tag() -> str:
    result = _run(
        "uv",
        "run",
        "semantic-release",
        "version",
        "--print-tag",
        capture=True,
        check=False,
    )

    combined = "\n".join(part for part in (result.stdout, result.stderr) if part)

    if result.returncode != 0:
        if combined:
            print(combined, end="" if combined.endswith("\n") else "\n")

        raise PublishError(
            "semantic-release did not calculate a new release; "
            "there may be no release-triggering commits"
        )

    for line in reversed(result.stdout.splitlines()):
        candidate = line.strip()
        if TAG_PATTERN.fullmatch(candidate):
            return candidate

    raise PublishError("semantic-release did not return a valid release tag")


def _workflow_runs(workflow: str) -> list[dict[str, Any]]:
    payload = _output(
        "gh",
        "run",
        "list",
        "--workflow",
        workflow,
        "--limit",
        "20",
        "--json",
        "databaseId,headBranch,event,status,conclusion,createdAt,url",
    )
    return json.loads(payload)


def _run_ids(workflow: str) -> set[int]:
    return {int(item["databaseId"]) for item in _workflow_runs(workflow)}


def _wait_for_new_run(
    workflow: str,
    previous_ids: set[int],
    *,
    attempts: int = RUN_POLL_ATTEMPTS,
) -> dict[str, Any] | None:
    for _ in range(attempts):
        for run in _workflow_runs(workflow):
            if int(run["databaseId"]) not in previous_ids:
                return run

        time.sleep(POLL_INTERVAL_SECONDS)

    return None


def _watch_run(label: str, run: dict[str, Any]) -> None:
    run_id = str(run["databaseId"])
    url = run.get("url", "")

    print(f"{label} run: {run_id}")
    if url:
        print(url)

    _run("gh", "run", "watch", run_id, "--exit-status")


def _release_details(tag: str) -> dict[str, Any]:
    payload = _output(
        "gh",
        "release",
        "view",
        tag,
        "--json",
        "tagName,url,isImmutable,assets",
    )
    return json.loads(payload)


def _verify_release_assets(tag: str) -> dict[str, Any]:
    release = _release_details(tag)
    version = tag.removeprefix("v")

    assets = release.get("assets", [])
    names = [str(asset["name"]) for asset in assets]

    wheel_present = any(version in name and name.endswith(".whl") for name in names)
    source_present = any(version in name and name.endswith(".tar.gz") for name in names)

    if not wheel_present or not source_present:
        formatted = "\n".join(f"  - {name}" for name in names) or "  - none"
        raise PublishError(
            f"release {tag} is missing required distribution assets:\n{formatted}"
        )

    print(f"release: {release['url']}")
    for name in names:
        print(f"  - {name}")

    return release


def _dispatch_release() -> dict[str, Any]:
    previous_ids = _run_ids(RELEASE_WORKFLOW)

    _run(
        "gh",
        "workflow",
        "run",
        RELEASE_WORKFLOW,
        "--ref",
        RELEASE_BRANCH,
    )

    run = _wait_for_new_run(RELEASE_WORKFLOW, previous_ids)
    if run is None:
        raise PublishError("new Release workflow run did not appear")

    return run


def _resolve_package_run(
    previous_ids: set[int],
    tag: str,
) -> dict[str, Any]:
    # The release-published event should normally trigger this workflow.
    automatic_run = _wait_for_new_run(
        PACKAGE_WORKFLOW,
        previous_ids,
        attempts=PACKAGE_TRIGGER_ATTEMPTS,
    )
    if automatic_run is not None:
        return automatic_run

    # Fall back to an explicit dispatch so publication is deterministic.
    _run(
        "gh",
        "workflow",
        "run",
        PACKAGE_WORKFLOW,
        "--ref",
        RELEASE_BRANCH,
        "-f",
        f"tag={tag}",
    )

    manual_run = _wait_for_new_run(PACKAGE_WORKFLOW, previous_ids)
    if manual_run is None:
        raise PublishError("new GitHub Packages workflow run did not appear")

    return manual_run


def publish() -> None:
    _step("publish.preflight")

    for command in ("git", "gh", "uv"):
        _require_command(command)

    _run("gh", "auth", "status")
    _require_main()
    _require_clean_tree()
    _require_synchronized_main()

    tag = _next_tag()

    existing = _run(
        "gh",
        "release",
        "view",
        tag,
        capture=True,
        check=False,
    )
    if existing.returncode == 0:
        raise PublishError(f"GitHub Release {tag} already exists")

    print(f"release.tag={tag}")
    _pass("publish.preflight")

    package_run_ids = _run_ids(PACKAGE_WORKFLOW)

    _step("publish.release")
    release_run = _dispatch_release()
    _watch_run("Release", release_run)
    _pass("publish.release")

    _step("publish.assets")
    _verify_release_assets(tag)
    _pass("publish.assets")

    _step("publish.package")
    package_run = _resolve_package_run(package_run_ids, tag)
    _watch_run("GitHub Package", package_run)
    _pass("publish.package")

    version = tag.removeprefix("v")

    print("\033[32m✓ publication completed\033[0m")
    print(f"release={tag}")
    print(f"container=ghcr.io/chin/optengine:{version}")


def main() -> int:
    try:
        publish()
    except PublishError as error:
        print(f"\033[31m✗ publish failed: {error}\033[0m", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(
            "\n\033[31m✗ publish interrupted\033[0m",
            file=sys.stderr,
        )
        return 130

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
