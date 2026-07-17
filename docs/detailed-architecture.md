# Detailed OptEngine Architecture

This document provides the expanded ASCII representation of the same platform
architecture shown in [the Mermaid view](mermaid-architecture.md).

```text
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                           Feasibility-Aware Hybrid AI–Quantum Platform               │
└──────────────────────────────────────────────────────────────────────────────────────┘

        USER
          │
          ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                        AI ORCHESTRATION (NeMo Switchyard)                            │
│                                                                                      │
│  Local LLM     NVIDIA NIM      Cloud LLM      Code Agent      Tool Calling           │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐    ▲
│                          WORKFLOW CONTROLLER                                         │    │
│                                                                                      │    │
│  • Parse optimization problem                                                        │    │
│  • Generate mathematical formulation                                                 │    │
│  • Select optimization strategy                                                      │    │
│  • Manage iterative workflow                                                         │    │
└──────────────────────────────────────────────────────────────────────────────────────┘    │
                                      │                                                     │
                ┌─────────────────────┼─────────────────────┐          Iterative execution  │
                ▼                     ▼                     ▼               SWITCH / SCALE  │
                                                                                            │
┌────────────────────┐    ┌────────────────────┐    ┌─────────────────────┐                 │
│ PhysicsNeMo        │    │ Classical          │    │ Quantum / Hybrid    │                 │
│ Fourier Neural     │    │ Optimization       │    │ Optimization        │                 │
│ Operator           │    │                    │    │                     │                 │
│                    │    │ • SciPy            │    │ • CUDA-Q            │                 │
│ Fast surrogate     │    │ • PyTorch          │    │ • QAOA              │                 │
│ physics model      │    │ • Heuristics       │    │ • Annealing         │                 │
└─────────┬──────────┘    └─────────┬──────────┘    └──────────┬──────────┘                 │
          │                         │                          │                            │
          └──────────────┬──────────┴──────────────┬───────────┘                            │
                         ▼                                                                  │
┌──────────────────────────────────────────────────────────────────────────────────────┐    │
│                    PERFORMANCE & UNCERTAINTY ANALYTICS                               │    │
│                                                                                      │    │
│   Accuracy │ Confidence │ Latency │ Compute Cost │ Energy │ Expected Improvement     │    │
└──────────────────────────────────────────────────────────────────────────────────────┘    │
                                      │                                                     │
                                      ▼                                                     │
┌──────────────────────────────────────────────────────────────────────────────────────┐    │
│              FEASIBILITY DECISION ENGINE (Dissertation Research)                     │    │
│                                                                                      ├────┘
│        STOP              SWITCH                    SCALE                             │
│                                                                                      │
│  Marginal utility     Better algorithm        Allocate more                          │
│  exhausted            available               computational resources                │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                     HIGH-FIDELITY VERIFICATION                                       │
│                                                                                      │
│      Simulation │ Exact Solver │ Experimental Validation                             │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                           FINAL RECOMMENDATION
```

## Execution Flow

A **Switch** or **Scale** decision returns control to the workflow controller
for reformulation, strategy selection, or another execution round. A **Stop**
decision proceeds to high-fidelity verification and the final recommendation.

## Current Implementation Status

The `v0.1.x` platform foundation currently implements:

- centralized execution through the runner;
- shared execution context and returned solution contracts;
- AI, optimization, and policy package boundaries;
- deterministic demonstration stages;
- runtime presentation;
- disposable output generation;
- explicit artifact promotion;
- testing, packaging, CI, and release automation.

The following diagram elements represent planned functional integrations:

- NeMo Switchyard and production model routing;
- NVIDIA NIM and cloud-model adapters;
- PhysicsNeMo and FNO execution;
- production classical optimization backends;
- CUDA-Q, QAOA, and annealing backends;
- full performance and uncertainty analytics;
- high-fidelity simulation or experimental verification.