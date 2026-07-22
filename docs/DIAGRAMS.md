# OptEngine Mature Object-Collaboration Diagrams

[Back to package index](./README.md)

## A. Domain behavior and aggregates

### 1. Generic domain self-interpretation

The same public behavior supports two semantic calls. The private sentinel preserves the difference between omission and an explicitly supplied `None`.

![Generic domain self-interpretation](./svg/01_generic_domain_self_interpretation.svg)

### 2. Generic aggregate construction

Domain aggregates are constructed in two passes so relationships hold object references rather than identifiers.

![Domain aggregate construction](./svg/02_domain_aggregate_construction.svg)

### 3. Max-Cut aggregate self-interpretation

`MaxCut.interpret()` produces the mathematical objective. `MaxCut.interpret(candidate)` validates and evaluates a partition.

![Max-Cut aggregate](./svg/03_maxcut_domain_aggregate.svg)

### 4. Portfolio aggregate self-interpretation

The portfolio aggregate owns assets, covariance relationships, guardrails, and current holdings. It interprets itself into a constrained utility objective and interprets candidates into finance-domain evidence.

![Portfolio aggregate](./svg/04_portfolio_domain_aggregate.svg)

### 5. Scientific-domain extension boundary

This planned domain demonstrates where the polynomial expression contract must be extended rather than overloaded with inaccurate FNO semantics.

![Scientific extension](./svg/05_scientific_domain_extension.svg)

## B. Objective and expression structure

### 6. Generic Objective → Expression → Curve

`Curve` is the normalized compatibility profile derived from the actual expression structure.

![Objective expression curve](./svg/06_objective_expression_curve.svg)

### 7. Max-Cut expression

![Max-Cut expression](./svg/07_maxcut_expression.svg)

### 8. Bounded discrete portfolio expression

This is the natural MVP portfolio form: allocation units, a quadratic utility, and explicit constraints.

![Discrete portfolio expression](./svg/08_portfolio_discrete_expression.svg)

### 9. Continuous mean–variance portfolio expression

This is the trusted continuous classical baseline used by the Vanguard extension.

![Continuous portfolio expression](./svg/09_portfolio_continuous_expression.svg)

## C. Formulation collaboration

### 10. Generic formulation collaboration

A formulation evaluates source compatibility, then creates an immutable model with payload, decoder, source curve, target curve, and transformation metadata.

![Generic formulation](./svg/10_formulation_collaboration.svg)

### 11. QUBO formulation family

The diagram distinguishes direct QUBO from penalty/discretization QUBO. Penalty transformations require independent validation before any quantum-benefit claim.

![QUBO formulation family](./svg/11_qubo_formulation_family.svg)

### 12. CQM / quadratic-program formulation

CQM preserves explicit constraints and can support binary, integer, and real variables.

![CQM formulation](./svg/12_cqm_formulation.svg)

### 13. Hamiltonian / Ising formulation

Hamiltonian formulation maps binary decision semantics into a cost operator used by QAOA-style operations.

![Hamiltonian formulation](./svg/13_hamiltonian_formulation.svg)

## D. Operation collaboration

### 14. Generic operation collaboration

An operation decides whether it can act on a model, filters compatible solvers, and prepares the native request.

![Generic operation](./svg/14_operation_collaboration.svg)

### 15. Exact-search operation

![Exact search](./svg/15_exact_search_operation.svg)

### 16. Continuous-optimization operation

![Continuous optimization](./svg/16_continuous_optimization_operation.svg)

### 17. Annealing operation

![Annealing](./svg/17_annealing_operation.svg)

### 18. QAOA operation

![QAOA](./svg/18_qaoa_operation.svg)

## E. Strategy, workflow, and ownership

### 19. Capability-driven strategy construction

Analysis produces immutable strategies by filtering injected plugin catalogs. No domain-specific branch is required.

![Strategy construction](./svg/19_strategy_construction.svg)

### 20. Max-Cut reference vertical slice

![Max-Cut end to end](./svg/20_maxcut_end_to_end.svg)

### 21. Portfolio / Vanguard end-to-end path

The classical continuous and bounded exact paths establish references before annealing or QAOA evidence is interpreted.

![Portfolio end to end](./svg/21_portfolio_end_to_end.svg)

### 22. Object ownership boundaries

![Ownership boundaries](./svg/22_ownership_boundary_map.svg)

### 23. Compatibility lattice

This summarizes the intended domain-to-formulation-to-operation paths. Dashed scientific paths are planned extensions.

![Compatibility lattice](./svg/23_compatibility_lattice.svg)

## Compact compatibility table

| Source objective | Formulation | Target model | Typical operations |
|---|---|---|---|
| Max-Cut binary quadratic unconstrained | Direct QUBO | Binary quadratic unconstrained | Exact search, annealing |
| Max-Cut binary quadratic | Hamiltonian / Ising | Qubit cost Hamiltonian | QAOA |
| Bounded discrete portfolio | CQM | Integer/binary constrained quadratic | Bounded exact, constrained hybrid |
| Bounded discrete portfolio | Penalty QUBO | Binary quadratic unconstrained | Exact search, annealing |
| Binary-mapped portfolio | Hamiltonian / Ising | Qubit cost Hamiltonian | QAOA |
| Continuous portfolio | CQM / quadratic program | Real constrained quadratic | Continuous optimization |
| Scientific field problem | Operator/surrogate formulation | Tensor/operator model | Training or inference operation, planned |
