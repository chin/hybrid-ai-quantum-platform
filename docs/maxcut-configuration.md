# Max-Cut Configuration and CLI

Run the included graph:

```bash
make run
```

Create and validate a custom configuration:

```bash
make maxcut-template MAXCUT_TEMPLATE=config/my-maxcut.json
make maxcut-validate MAXCUT_CONFIG=config/my-maxcut.json
make run MAXCUT_CONFIG=config/my-maxcut.json
```

Direct CLI input:

```bash
optengine maxcut run \
  --edge A:B \
  --edge B:C:2.5 \
  --edge A:C:1.0
```

Each edge uses:

```text
LEFT:RIGHT[:WEIGHT]
```

The result contains the selected partition, cut value, Stop/Switch/Scale decision, explanation, and Recommendation JSON path.
