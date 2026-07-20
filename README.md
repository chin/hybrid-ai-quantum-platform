# OptEngine by OptChin

## A Feasibility-Aware Hybrid AI–Quantum Optimization Platform

**Quantifying operational optimality to simplify decision optionality**

---

## Quickstart

The current quickstart executes deterministic implementations of the platform
stage interfaces. It validates the end-to-end OptEngine lifecycle without yet
invoking the planned external AI, FNO, classical, or quantum backends.

```bash
make run             #Run the quickstart.
make test            #Run the test suite.
make dev             #Format and run the complete pre-merge gate.
make ci              #Run the non-mutating CI-equivalent gate.
make release-check   #Clean and verify release readiness.
```

Run:

```bash
make run
```

Or run the demonstration directly through the managed environment:

```bash
uv run python demos/quickstart.py
```

Expected output:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                   OptEngine :: Quickstart                    
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> problem
Graph with 4 nodes and 5 edges

> analysis
✓ complete

> evaluation
✓ complete

> decision
stop

> reason
OptEngine selected maxcut-exact and decided to stop.

> artifact
outputs/quickstart_<YYYYMMDD_HHMMSSZ>.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                       Runtime Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Terminal colors distinguish the runtime information:

* successful stages appear in green;
* the decision value appears in yellow;
* the generated artifact path appears in cyan.

## Outputs and Artifacts

Files under `outputs/` are disposable execution results.

Files under `artifacts/` are deliberately promoted, curated evidence. Artifact
promotion is explicit and is performed with:

```bash
make artifact
```

## Development Documentation

- [Detailed architecture](docs/detailed-architecture.md)
- [Mermaid architecture](docs/mermaid-architecture.md)
- [Release roadmap](docs/ROADMAP.md)
- [Makefile execution guide](docs/MAKEFILE.md) — command behavior, execution paths, side effects, and release workflow.

---

## License

OptEngine is licensed under the Apache License, Version 2.0. See
[`LICENSE`](LICENSE) for the complete license terms.

Copyright © 2026 Chinyere "Chin" Isaac-Heslop.

Third-party projects, libraries, services, product names, and trademarks remain
subject to their respective licenses and ownership. References to third parties do not imply sponsorship, endorsement, or
affiliation.
