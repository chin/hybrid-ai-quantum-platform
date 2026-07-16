# OptEngine Makefile Execution Guide

This guide defines the supported `make` commands for OptEngine, what each command executes, whether it changes the working tree, and when it should be used.

The Makefile is the public command interface for local development, continuous-integration parity, release preparation, artifact promotion, and official release dispatch. The underlying development commands are centralized in `tools/dev.py` so local execution and GitHub Actions can use the same implementations.

## Command model

OptEngine separates five kinds of work:

1. **Execution** — run the platform demonstration.
2. **Mutation** — intentionally format or clean local files.
3. **Verification** — check the repository without changing tracked source.
4. **Release preparation** — verify that the package builds from a clean generated state.
5. **Official operations** — create or publish release artifacts through GitHub.

This separation prevents CI from silently fixing files, keeps release actions explicit, and makes every command's side effects predictable.

## Command summary

| Command | Purpose | Changes tracked source? | Generates or deletes local files? |
|---|---|---:|---:|
| `make help` | Show the supported command interface | No | No |
| `make bootstrap` | Verify tools and synchronize the environment | No | May update the local virtual environment |
| `make run` | Run the OptEngine quickstart | No | Writes a disposable output JSON |
| `make dev` | Format and run the complete pre-merge gate | Formatting only | Builds distributions |
| `make format` | Apply Ruff formatting | Possibly | No |
| `make format-check` | Verify formatting without fixing it | No | No |
| `make lint` | Run Ruff static analysis | No | No |
| `make test` | Run the pytest suite | No | Test caches may be created |
| `make status` | Show branch and working-tree state | No | No |
| `make ci` | Run the complete non-mutating quality gate | No | Test caches may be created |
| `make build` | Build the wheel and source distribution | No | Writes `dist/` and build metadata |
| `make release-check` | Clean generated state, then run CI and build | No | Deletes and regenerates disposable build files |
| `make version` | Preview the next semantic version and Git tag | No | No |
| `make release` | Dispatch the official GitHub release workflow | No | Remote GitHub workflow creates release artifacts |
| `make artifact` | Promote a selected output into the artifact registry | Possibly | Writes curated artifact content |
| `make clean` | Remove disposable outputs, caches, and build products | No | Deletes disposable local files |
| `make docs` | Reserved documentation validation command | No | Not implemented yet |
| `make benchmark` | Reserved performance benchmark command | No | Not implemented yet |
| `make validate` | Reserved research-validation command | No | Not implemented yet |
| `make publish` | Reserved package-registry publication command | No | Not implemented yet |

## Execution graph

```text
make run
└── bootstrap
    └── OptEngine quickstart

make ci
└── bootstrap
    └── status
        └── format-check
            └── lint
                └── test

make dev
└── bootstrap
    └── format
        └── release-check command group
            └── ci
                ├── status
                ├── format-check
                ├── lint
                └── test
            └── build

make release-check
└── bootstrap
    └── clean
        └── release-check command group
            └── ci
                ├── status
                ├── format-check
                ├── lint
                └── test
            └── build

make version
└── bootstrap
    ├── next semantic version
    └── next Git tag

make release
├── require `main`
├── require a clean working tree
├── require synchronized `origin/main`
├── require authenticated GitHub CLI
├── preview the semantic version and tag
└── dispatch `.github/workflows/release.yml`
```

## Why the commands are separated

### `make run`

`make run` executes the public quickstart:

```bash
make run
```

It is intentionally separate from development validation. Running the platform should not automatically format source, execute the entire test suite, or build distributions.

The quickstart writes a disposable JSON result under `outputs/`.

### `make dev`

`make dev` is the canonical local command before committing code or updating a pull request:

```bash
make dev
```

It performs:

```text
format
status
format-check
lint
test
build
```

The formatter runs first because this is the developer-preparation path. After formatting, the same non-mutating checks used by CI verify that the repository is compliant. The package build is included because a change should not be considered merge-ready if the distributable package cannot be built.

`make dev` does not run `clean`. Repeated development checks should not delete quickstart outputs and caches on every execution.

### `make ci`

`make ci` is the canonical non-mutating quality gate:

```bash
make ci
```

It performs:

```text
status
format-check
lint
test
```

CI checks formatting but never fixes it. A CI system must report that committed files are incorrectly formatted rather than silently rewriting them.

The repository state before and after `make ci` should be equivalent except for disposable test caches:

```bash
git status --short
make ci
git status --short
```

### `make release-check`

`make release-check` verifies release readiness from a clean generated state:

```bash
make release-check
```

It performs:

```text
clean
status
format-check
lint
test
build
```

The clean step removes stale `dist/`, `build/`, caches, generated outputs, and package metadata before the package is rebuilt. This proves that the wheel and source distribution were produced from the current source rather than left over from an earlier execution.

This command is stricter than `make ci`, but it does not create a Git tag or GitHub Release.

### `make version`

`make version` previews what Python Semantic Release will produce:

```bash
make version
```

It prints:

- the next semantic version;
- the corresponding Git tag.

The command succeeds only on a branch configured as a release branch, normally `main`. A feature branch should fail cleanly because feature branches are not allowed to create official releases.

Before the first release, the required result is:

```text
0.1.0
v0.1.0
```

### `make release`

`make release` starts the official GitHub release process:

```bash
make release
```

It is intentionally not a local quality-gate bundle. Quality and build checks have already been performed through:

- `make dev`;
- GitHub Actions;
- protected-branch checks;
- `make release-check`.

The release target should verify:

- the current branch is `main`;
- the working tree is clean;
- local `main` matches `origin/main`;
- the GitHub CLI is installed and authenticated;
- the semantic version and tag can be calculated.

It then dispatches `.github/workflows/release.yml`.

### `make clean`

`make clean` removes disposable generated state:

```bash
make clean
```

It removes:

- generated files under `outputs/`, except `.gitkeep`;
- `.pytest_cache`;
- `.ruff_cache`;
- `build/`;
- `dist/`;
- top-level `*.egg-info`;
- Python `__pycache__` directories.

It is used automatically by `make release-check`, where a clean package build is important. It is not used automatically by `make dev`, because normal iteration should not repeatedly erase quickstart outputs and caches.

### `make artifact`

`make artifact` promotes a selected disposable output into the curated artifact registry:

```bash
make artifact
```

Artifact promotion remains explicit because it changes curated evidence. A normal test, CI, or release check must not automatically decide that an output should become a retained artifact.

The intended workflow is:

```bash
make run
make artifact
```

### `make bootstrap`

Most executable commands depend on `bootstrap`.

It verifies:

- Python 3.10 or newer;
- Git;
- Make;
- `uv`.

It then synchronizes the development environment with:

```bash
uv sync
```

Centralizing this behavior means contributors do not need to manually activate a virtual environment before using the public Makefile commands.

### `make help`

Run:

```bash
make help
```

The help target reads target descriptions directly from the Makefile. Every public target should therefore include a concise `##` description.

## Reserved commands

### `make docs`

This target is reserved for automated documentation checks. It should not be added to `ci` until it executes a real command and returns a nonzero status when documentation is invalid.

A practical first implementation could check Markdown formatting and links.

### `make benchmark`

This target is reserved for reproducible performance benchmarks. A meaningful implementation requires:

- a stable benchmark workload;
- controlled inputs and random seeds;
- warm-up behavior;
- repeated measurements;
- recorded environment metadata;
- a policy for regressions or comparison baselines.

A benchmark that only times the quickstart once is not a reliable performance gate.

### `make validate`

This target is reserved for research and model validation. A meaningful implementation requires:

- a stated validation claim;
- reference inputs or datasets;
- expected invariants or acceptance thresholds;
- deterministic configuration;
- retained validation evidence;
- explicit failure conditions.

Validation should not be treated as another name for unit testing.

### `make publish`

This target is reserved for package-registry publication. It is distinct from creating a GitHub Release.

A future implementation may publish a previously built and verified distribution to a package registry through trusted publishing. It must not publish directly from an arbitrary developer branch.

## Standard workflows

### Run OptEngine

```bash
make run
```

### Work on a feature

```bash
make run
make test
```

Use the narrow commands during iteration.

### Prepare a branch for commit or pull-request update

```bash
make dev
git status --short
git add <intentional-files>
git commit -m "feat: describe the change"
git push
```

### Reproduce the non-mutating CI gate locally

```bash
make ci
```

### Perform a clean release-readiness check

```bash
make release-check
```

### Create an official release

After every intended pull request has merged:

```bash
git checkout main
git pull --ff-only origin main
make release-check
make version
make release
```

### Promote an execution result

```bash
make run
make artifact
```

## Design invariants

The Makefile should preserve these rules:

1. `make ci` never fixes source files.
2. `make dev` is the single complete pre-merge developer command.
3. `make release-check` proves a clean package build without creating a release.
4. `make release` performs only the official release operation and its preconditions.
5. `make artifact` remains an explicit curation action.
6. Placeholder commands are not included in gates until they perform real validation.
7. The Makefile remains the public interface; `tools/dev.py` remains the centralized command implementation.
