# OptEngine Detailed Architecture

```text
runner.run(Domain)
│
├── create Recommendation and OptEngine live state
│
├── ANALYZE
│   └── Analyzer.analyze(Domain, Catalog)
│       ├── Domain.interpret()
│       │   └── Interpretation
│       │       └── Objective
│       │           └── Expression
│       │               └── Curve
│       ├── for each Formulation
│       │   ├── Formulation.Capability.evaluate(Curve)
│       │   └── Formulation.express(Objective) → Model
│       ├── for each Model and Operation
│       │   └── Operation.Capability.evaluate(Model)
│       ├── for each compatible Operation and Solver
│       │   └── Solver.Capability.evaluate(Operation, Model)
│       └── Analysis
│           ├── N Strategies
│           └── accepted/rejected CompatibilityRecords
│
├── EVALUATE
│   └── for each Strategy, independently
│       ├── Operation.prepare(Model) → Operation.Request
│       ├── Solver.execute(Request) → Solver.Result
│       ├── Model.decode(Result) → Domain Candidate
│       ├── Domain.interpret(Candidate) → Domain Evaluation
│       └── Execution
│           ├── complete: Result + Candidate + Evaluation
│           └── failed: Failure evidence
│
├── DECIDE
│   ├── Utility.assess(Executions, Analysis)
│   │   └── Assessment
│   └── Policy.apply(Assessment)
│       └── Stop | Switch | Scale
│
├── EXPLAIN
│   └── Explainer.explain(...)
│       └── Explanation
│
└── WRITE
    └── Writer.write(Recommendation)
        └── timestamped JSON artifact
```

## Responsibility boundaries

The engine owns sequence. It does not own problem mathematics, backend
compatibility, decoding, candidate meaning, or domain evaluation.

The Domain owns semantics. The Formulation owns mathematical translation. The
Operation owns the requested algorithmic action. The Solver owns backend
execution. Utility owns cross-execution comparison. Policy owns
Stop/Switch/Scale.

## Failure boundary

`Strategy.execute()` catches its own failure and returns a failed `Execution`.
The Evaluate stage always continues to the next Strategy. Utility receives the
complete execution set, including failures.
