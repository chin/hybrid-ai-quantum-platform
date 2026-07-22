# Portfolio Configuration and CLI

## Fastest path

Create an editable configuration:

```bash
make portfolio-template PORTFOLIO_TEMPLATE=config/my-portfolio.json
```

Edit the file, validate it, and run it:

```bash
make portfolio-validate PORTFOLIO_CONFIG=config/my-portfolio.json
make portfolio PORTFOLIO_CONFIG=config/my-portfolio.json
```

For guided prompts:

```bash
make portfolio-interactive
```

## Installed CLI

```bash
optengine portfolio run --config config/my-portfolio.json
optengine portfolio validate --config config/my-portfolio.json
optengine portfolio template --output config/my-portfolio.json
optengine portfolio strategies
optengine portfolio describe
```

Direct input is also supported:

```bash
optengine portfolio run \
  --asset Growth:0.12:0.04 \
  --asset Income:0.08:0.02 \
  --asset Defense:0.05:0.01 \
  --covariance Growth:Income:0.006 \
  --covariance Growth:Defense:0.002 \
  --covariance Income:Defense:0.003 \
  --allocation-increment 0.25 \
  --risk-aversion 1.0 \
  --max-assets 3
```

Each `--asset` value is:

```text
NAME:EXPECTED_RETURN:VARIANCE
```

Each optional `--covariance` value is:

```text
LEFT_ASSET:RIGHT_ASSET:COVARIANCE
```

Unspecified off-diagonal covariances default to zero.

## Configuration fields

| Field | Meaning |
|---|---|
| `name` | Execution name and output filename prefix |
| `problem.assets` | Unique asset names |
| `problem.expected_returns` | Expected return for each asset, in matching order |
| `problem.covariance` | Square symmetric covariance matrix aligned with the assets |
| `problem.allocation_increment` | Allowed allocation step; must divide 1.0 exactly |
| `problem.risk_aversion` | Non-negative penalty applied to portfolio variance |
| `problem.max_assets` | Optional maximum number of nonzero allocations |
| `execution.strategies` | Registered portfolio strategies to run |
| `execution.render` | Whether to print the business-readable recommendation |
| `execution.output_dir` | Directory for disposable Recommendation JSON |

The JSON Schema is [`config/schemas/portfolio.schema.json`](../config/schemas/portfolio.schema.json). Cross-field mathematical checks are performed by `PortfolioDomain`.
