# Objective, Expression, and Curve

[Back to diagram atlas](../README.md)

## 06. Objective, Expression, and Curve

`Curve` is derived from the actual expression structure and drives compatibility without naming a concrete domain.

```mermaid
classDiagram
    class Objective {
        +sense
        +Expression expression
        +curve Curve
    }

    class Expression {
        +Variable[] variables
        +LinearTerm[] linear_terms
        +QuadraticTerm[] quadratic_terms
        +Constraint[] constraints
        +constant
        +degree
        +curve Curve
    }

    class Curve {
        +input_types
        +input_count
        +output_types
        +output_count
        +degree
        +constraint_count
        +constraint_degrees
        +bounds_and_metadata
    }

    class Variable {
        +name
        +value_type
        +lower_bound
        +upper_bound
    }

    class LinearTerm {
        +variable
        +coefficient
    }

    class QuadraticTerm {
        +first
        +second
        +coefficient
    }

    class Constraint {
        +name
        +variables
        +relation
        +bound
        +degree
    }

    Objective *-- Expression
    Expression *-- Variable
    Expression *-- LinearTerm
    Expression *-- QuadraticTerm
    Expression *-- Constraint
    Expression --> Curve : derives
```

