# Portfolio Vertical Slice

## Domain aggregate

`Portfolio` is the aggregate root:

```text
Portfolio
├── assets: tuple[Portfolio.Asset, ...]
├── covariances: tuple[Portfolio.Covariance, ...]
├── parameters: Portfolio.Parameters
├── Portfolio.Objective
├── Portfolio.Allocation
├── Portfolio.Candidate
└── Portfolio.Evaluation
```

`Portfolio.Covariance` references two `Portfolio.Asset` objects. The Domain
validates entity identity, relationship uniqueness, budget feasibility, and
cardinality.

## Mathematical representation

The current bounded-discrete objective uses one-hot binary allocation choices.
For each asset and allocation unit, a binary variable indicates whether that
allocation is selected.

The Objective contains:

- expected-return linear terms;
- risk quadratic terms;
- one-choice constraints per asset;
- full-budget equality;
- optional maximum-cardinality constraint.

The resulting Curve is binary, scalar, quadratic, and constrained.

## Strategies

The preset Catalog can discover:

```text
portfolio:cqm:exact-search:dimod-cqm-exact
portfolio:qubo:exact-search:dimod-exact
portfolio:qubo:annealing:dwave-local
```

Requested strategies in the example configuration are:

```text
portfolio:cqm:exact-search:dimod-cqm-exact
portfolio:qubo:annealing:dwave-local
```

The exact CQM path is the reference. The QUBO path converts constraints through
`dimod.cqm_to_bqm` and decodes the native result back through the Model.

## Domain evaluation

`Portfolio.Evaluation` independently derives:

- one-choice feasibility;
- total-budget feasibility;
- allocation-bound feasibility;
- allocation-increment feasibility;
- cardinality feasibility;
- expected return;
- risk;
- utility;
- active assets.

Solver-native energy is retained in Candidate provenance but is not treated as
domain quality.

## Run

```bash
make portfolio
```

Configuration:

```text
config/examples/portfolio.json
```

Output:

```text
outputs/portfolio-vertical-slice_<timestamp>.json
```
