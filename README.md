# Ink

Ink is a logic programming language built around Classical Chinese semantics.

---

## Overview

In Ink, you write:

- Facts
- Classification relationships
- SVO clauses
- Rules
- Queries

The runtime repeatedly applies rules and classification relationships until no new information can be derived. Queries are answered based on what can be inferred from the current program.

Ink does not include:

- Functions
- Control flow
- Mutation
- Backtracking

It is a deterministic rule-based system.

---

## Quick Example

    以愛為動
    以敬為動

    孔子愛顏回

    若其甲愛其乙則其乙敬其甲

    問顏回敬孔子乎

Result:

    ⊤

---

## Language Structure

### Statements

- Each line is a statement.
- There is no whitespace in a statement.
- Indentation exists for future features that require nesting.

Comments can be made with the full-width hash: ＃

---

### Propositions

Zero-argument facts can be asserted:

    曰雨

---

### Classification

Classification uses the form:

    X者Y也

Example:

    孔子者人也
    人者需食者也

Classification relationships are transitive. In the example above, Ink will infer:

    孔子者需食者也

---

### Verb Declarations

Verbs must be declared before use:

    以愛為動

Form:

    以V為動

Only declared verbs may appear in SVO clauses.

---

### SVO Clauses

Any non-keyword line is parsed as:

    Subject Verb Object

Example:

    孔子愛顏回

This asserts a binary relation between two identifiers.

---

### Variables

Variables begin with:

    其

Example:

    若其甲愛其乙則其乙敬其甲

Rules for variables:

- May appear in subject or object positions.
- Must bind consistently within a rule.
- Do not appear in stored ground facts.

---

### Rules

Rules appear as if-else statements.

Single condition:

    若A則B

Multiple conditions:

    若A且B且C則D

If the premises can be satisfied, the conclusion is added to the knowledge base.

---

### Queries

Queries use the form:

    問E乎

Results:

- ⊤ — true
- ? — unknown

---

## Execution Model

Ink maintains:

- A set of asserted facts
- A set of classification relationships
- A set of rules
- A verb lexicon

It repeatedly:

1. Expands classification relationships transitively.
2. Applies rules to derive new facts.
3. Stops when no new information can be produced.

Evaluation is global and deterministic.

---

## Future features

- Turing completeness
- Negation
- Advanced logic
- Assumptions
- Nominalization