# Problem Domain Extension Guide

A Domain is the aggregate root. Do not create a parallel generic input object.

## Required object graph

```text
NewDomain
├── entity value objects
├── relationship value objects that reference entities
├── Parameters
├── Objective
├── Candidate
└── Evaluation
```

The concrete Domain must own:

- populated entities and relationships;
- aggregate validation;
- domain parameters;
- Objective construction;
- Candidate interpretation;
- Domain Evaluation;
- user-facing summary.

## Required public behavior

```python
interpretation = domain.interpret()
evaluation = domain.interpret(candidate)
```

The engine must not import or branch on the new Domain type.

## Objective requirements

The Objective must expose:

```python
sense
expression
decode(values, result, strategy)
```

`Expression.curve` is derived automatically and used for compatibility.

The Objective should describe the actual mathematics. It must not emit a named
objective type solely to route Formulations.

## Candidate requirements

The Candidate must:

- retain its owning Domain;
- expose `_interpret_in(domain)`;
- reject interpretation by another aggregate instance;
- provide an explicit `to_dict()`.

## Evaluation requirements

The Evaluation must calculate domain meaning independently from solver-native
scores:

```python
feasible
quality
metrics
utility_inputs
to_dict()
```

## Reusable contract tests

Create a Domain contract test:

```python
class TestNewDomainContract(DomainContract):
    def make_domain(self) -> Domain:
        return NewDomain(...)

    def make_candidate(self, domain: Domain) -> Candidate:
        return NewDomain.Candidate(...)
```

Then add concrete tests for entity validation, relationship behavior,
Objective mathematics, Candidate decoding, and every independent feasibility
dimension.

See [`templates/problem_domain.py`](../templates/problem_domain.py).
