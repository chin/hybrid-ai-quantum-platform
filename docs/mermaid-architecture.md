# OptEngine Architecture — Mermaid View

This document provides the compact control-flow representation of the same
platform architecture shown in the
[detailed architecture](detailed-architecture.md).

```mermaid
flowchart TD

    A[User] --> B[NeMo Switchyard]

    B --> C1[Small LLM]
    B --> C2[Large LLM]
    B --> C3[Code Agent]

    C1 --> D
    C2 --> D
    C3 --> D

    D[Workflow Controller]

    D --> E[Problem Formulation]

    E --> F[FNO Surrogate<br/>PhysicsNeMo]
    E --> G[Classical Optimizer]
    E --> H[Quantum Solver]

    F --> I[Evaluation Metrics]
    G --> I
    H --> I

    I --> J[Decision Engine]

    J --> K[Stop]
    J --> L[Switch]
    J --> M[Scale]

    L --> D
    M --> D

    K --> N[Verification]
    N --> O[Solution]
```

## Architectural Role

This Mermaid view emphasizes the platform’s control flow and decision loop.

The detailed ASCII view expands the same architecture with example providers,
solver technologies, evaluated metrics, and decision semantics.

## Current Implementation Status

The `v0.1.x` platform foundation implements the execution lifecycle, software
contracts, package boundaries, deterministic demonstration stages, output and
artifact handling, tests, CI, packaging, and release automation.

Named external model-routing, PhysicsNeMo, classical-optimization, and
quantum-optimization integrations remain planned functional implementations.