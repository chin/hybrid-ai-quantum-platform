# Domain CLI Extension Template

Each problem domain may provide a `DomainCLI` subclass so users can enter domain-specific data without changing the engine.

## Required commands

A domain CLI should normally provide:

- `run` — validate input, build an `ExecutionInstance`, execute, and display the domain result;
- `validate` — validate a configuration without solving;
- `template` — write an editable configuration file;
- `describe` — explain required inputs and output metrics;
- `strategies` — list registered strategies.

## Implementation checklist

- [ ] Extend `DomainCLI`
- [ ] Keep parsing and prompts in the domain CLI
- [ ] Convert CLI data into the domain Input type
- [ ] Validate with a JSON Schema and the Domain
- [ ] Build an `ExecutionInstance`
- [ ] Render the domain-specific result
- [ ] Register the CLI in `default_domain_cli_registry()`
- [ ] Add config, direct-argument, interactive, validation, and end-to-end tests

Start with [`templates/domain_cli.py`](../templates/domain_cli.py).
