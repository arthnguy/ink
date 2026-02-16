import pytest
from ink.ast_nodes import Proposition, SVOClause, ClassificationEdge, Rule
from ink.interpreter import apply_rule, fixpoint, Context


def test_simple_transitive_inference():
    """Test simple transitive inference: A→B, B→C, derive C."""
    # Create facts and rules
    a = Proposition("A", False)
    b = Proposition("B", False)
    c = Proposition("C", False)
    
    # Rules: A→B and B→C
    rule1 = Rule([a], b)
    rule2 = Rule([b], c)
    
    # Initial context with only A
    context = Context(
        facts={a},
        classification_edges=set(),
        rules=[rule1, rule2],
        verb_lexicon=set()
    )
    
    # Run fixpoint
    final_context = fixpoint(context)
    
    # Should derive B and C
    assert a in final_context.facts
    assert b in final_context.facts
    assert c in final_context.facts


def test_classification_closure_with_rules():
    """Test that classification closure is computed before rule application."""
    # Create classification edges: Dog⊑Animal, Animal⊑Thing
    dog = ClassificationEdge("Dog", False, "Animal", False)
    animal = ClassificationEdge("Animal", False, "Thing", False)
    
    # Create a rule that matches on the derived transitive edge
    # If Dog⊑Thing then derive Result
    dog_thing = ClassificationEdge("Dog", False, "Thing", False)
    result = Proposition("Result", False)
    rule = Rule([dog_thing], result)
    
    # Initial context
    context = Context(
        facts={dog, animal},
        classification_edges={dog, animal},
        rules=[rule],
        verb_lexicon=set()
    )
    
    # Run fixpoint
    final_context = fixpoint(context)
    
    # Should derive Result because Dog⊑Thing is in the closure
    assert result in final_context.facts


def test_multi_premise_rule():
    """Test rule with multiple premises."""
    # Create facts
    a = Proposition("A", False)
    b = Proposition("B", False)
    c = Proposition("C", False)
    
    # Rule: A ∧ B → C
    rule = Rule([a, b], c)
    
    # Context with both premises
    context = Context(
        facts={a, b},
        classification_edges=set(),
        rules=[rule],
        verb_lexicon=set()
    )
    
    # Run fixpoint
    final_context = fixpoint(context)
    
    # Should derive C
    assert c in final_context.facts


def test_multi_premise_rule_missing_premise():
    """Test that rule doesn't fire when a premise is missing."""
    # Create facts
    a = Proposition("A", False)
    b = Proposition("B", False)
    c = Proposition("C", False)
    
    # Rule: A ∧ B → C
    rule = Rule([a, b], c)
    
    # Context with only one premise
    context = Context(
        facts={a},  # Missing B
        classification_edges=set(),
        rules=[rule],
        verb_lexicon=set()
    )
    
    # Run fixpoint
    final_context = fixpoint(context)
    
    # Should NOT derive C
    assert c not in final_context.facts


def test_program_with_no_derivable_facts():
    """Test program where no rules fire."""
    # Create facts
    a = Proposition("A", False)
    b = Proposition("B", False)
    c = Proposition("C", False)
    
    # Rule: B → C (but B is not in context)
    rule = Rule([b], c)
    
    # Context with only A
    context = Context(
        facts={a},
        classification_edges=set(),
        rules=[rule],
        verb_lexicon=set()
    )
    
    # Run fixpoint
    final_context = fixpoint(context)
    
    # Should only have A
    assert a in final_context.facts
    assert b not in final_context.facts
    assert c not in final_context.facts


def test_rule_with_variables():
    """Test rule with variables that binds to multiple facts."""
    # Create facts
    dog = Proposition("Dog", False)
    cat = Proposition("Cat", False)
    
    # Rule: 其X → 其X (identity rule with variable)
    var_x = Proposition("其X", True)
    rule = Rule([var_x], var_x)
    
    # Context with concrete facts
    context = Context(
        facts={dog, cat},
        classification_edges=set(),
        rules=[rule],
        verb_lexicon=set()
    )
    
    # Apply rule
    derived = apply_rule(rule, context)
    
    # Should not derive anything new (facts already exist)
    assert len(derived) == 0


def test_svo_rule_application():
    """Test rule application with SVO clauses."""
    # Create SVO facts
    john_loves_mary = SVOClause("John", False, "loves", False, "Mary", False)
    mary_loves_pizza = SVOClause("Mary", False, "loves", False, "Pizza", False)
    
    # Rule: If John loves Mary, then derive result
    result = Proposition("Result", False)
    rule = Rule([john_loves_mary], result)
    
    # Context
    context = Context(
        facts={john_loves_mary, mary_loves_pizza},
        classification_edges=set(),
        rules=[rule],
        verb_lexicon=set()
    )
    
    # Run fixpoint
    final_context = fixpoint(context)
    
    # Should derive Result
    assert result in final_context.facts


def test_empty_context():
    """Test fixpoint with empty context."""
    context = Context(
        facts=set(),
        classification_edges=set(),
        rules=[],
        verb_lexicon=set()
    )
    
    # Run fixpoint
    final_context = fixpoint(context)
    
    # Should remain empty
    assert len(final_context.facts) == 0


def test_fixpoint_idempotence():
    """Test that running fixpoint twice gives same result."""
    # Create simple context
    a = Proposition("A", False)
    b = Proposition("B", False)
    rule = Rule([a], b)
    
    context = Context(
        facts={a},
        classification_edges=set(),
        rules=[rule],
        verb_lexicon=set()
    )
    
    # Run fixpoint twice
    context1 = fixpoint(context)
    context2 = fixpoint(context1)
    
    # Should be identical
    assert context1.facts == context2.facts
