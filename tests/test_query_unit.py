import pytest
from ink.ast_nodes import Proposition, SVOClause, ClassificationEdge, Rule, Query
from ink.interpreter import evaluate_query, fixpoint, Context


class TestEvaluateQuery:
    """Test evaluate_query function."""
    
    def test_query_on_asserted_proposition(self):
        """Test query on an asserted proposition fact."""
        # Create a context with an asserted fact
        fact = Proposition("天圓", False)
        context = Context(
            facts={fact},
            classification_edges=set(),
            rules=[],
            verb_lexicon=set()
        )
        
        # Query for the same fact
        query = Query(fact)
        result = evaluate_query(query, context)
        
        assert result == "⊤"
    
    def test_query_on_asserted_svo_clause(self):
        """Test query on an asserted SVO clause."""
        # Create a context with an SVO clause
        fact = SVOClause("人", False, "愛", False, "狗", False)
        context = Context(
            facts={fact},
            classification_edges=set(),
            rules=[],
            verb_lexicon=set()
        )
        
        # Query for the same fact
        query = Query(fact)
        result = evaluate_query(query, context)
        
        assert result == "⊤"
    
    def test_query_on_asserted_classification(self):
        """Test query on an asserted classification edge."""
        # Create a context with a classification edge
        fact = ClassificationEdge("狗", False, "動物", False)
        context = Context(
            facts={fact},
            classification_edges={fact},
            rules=[],
            verb_lexicon=set()
        )
        
        # Query for the same fact
        query = Query(fact)
        result = evaluate_query(query, context)
        
        assert result == "⊤"
    
    def test_query_on_derived_fact(self):
        """Test query on a fact derived through rules."""
        # Create facts and a rule: A → B
        fact_a = Proposition("A", False)
        fact_b = Proposition("B", False)
        rule = Rule([fact_a], fact_b)
        
        # Create context with A and the rule
        context = Context(
            facts={fact_a},
            classification_edges=set(),
            rules=[rule],
            verb_lexicon=set()
        )
        
        # Compute fixpoint to derive B
        final_context = fixpoint(context)
        
        # Query for B (which should be derived)
        query = Query(fact_b)
        result = evaluate_query(query, final_context)
        
        assert result == "⊤"
    
    def test_query_with_variable(self):
        """Test query with a variable that can bind to a fact."""
        # Create a concrete fact
        fact = Proposition("天圓", False)
        context = Context(
            facts={fact},
            classification_edges=set(),
            rules=[],
            verb_lexicon=set()
        )
        
        # Query with a variable
        query_expr = Proposition("其X", True)
        query = Query(query_expr)
        result = evaluate_query(query, context)
        
        # Should succeed because variable can bind to the fact
        assert result == "⊤"
    
    def test_query_with_svo_variable(self):
        """Test query with variables in SVO clause."""
        # Create a concrete SVO fact
        fact = SVOClause("人", False, "愛", False, "狗", False)
        context = Context(
            facts={fact},
            classification_edges=set(),
            rules=[],
            verb_lexicon=set()
        )
        
        # Query with variable in subject position
        query_expr = SVOClause("其X", True, "愛", False, "狗", False)
        query = Query(query_expr)
        result = evaluate_query(query, context)
        
        # Should succeed
        assert result == "⊤"
    
    def test_query_failure_on_non_existent_fact(self):
        """Test query that should fail because fact doesn't exist."""
        # Create a context with one fact
        fact_a = Proposition("A", False)
        context = Context(
            facts={fact_a},
            classification_edges=set(),
            rules=[],
            verb_lexicon=set()
        )
        
        # Query for a different fact
        fact_b = Proposition("B", False)
        query = Query(fact_b)
        result = evaluate_query(query, context)
        
        assert result == "?"
    
    def test_query_failure_on_non_derivable_fact(self):
        """Test query that fails because fact is not derivable."""
        # Create facts and a rule: A → B
        fact_a = Proposition("A", False)
        fact_b = Proposition("B", False)
        fact_c = Proposition("C", False)
        rule = Rule([fact_a], fact_b)
        
        # Create context with A and the rule (B will be derived, but not C)
        context = Context(
            facts={fact_a},
            classification_edges=set(),
            rules=[rule],
            verb_lexicon=set()
        )
        
        # Compute fixpoint
        final_context = fixpoint(context)
        
        # Query for C (which is not derivable)
        query = Query(fact_c)
        result = evaluate_query(query, final_context)
        
        assert result == "?"
    
    def test_query_on_transitive_classification(self):
        """Test query on a transitively derived classification edge."""
        # Create classification edges: 狗⊑動物, 動物⊑生物
        edge1 = ClassificationEdge("狗", False, "動物", False)
        edge2 = ClassificationEdge("動物", False, "生物", False)
        
        # Create context
        context = Context(
            facts={edge1, edge2},
            classification_edges={edge1, edge2},
            rules=[],
            verb_lexicon=set()
        )
        
        # Compute fixpoint (will derive 狗⊑生物)
        final_context = fixpoint(context)
        
        # Query for the transitive edge
        transitive_edge = ClassificationEdge("狗", False, "生物", False)
        query = Query(transitive_edge)
        result = evaluate_query(query, final_context)
        
        assert result == "⊤"
    
    def test_query_with_multiple_facts(self):
        """Test query in a context with multiple facts."""
        # Create multiple facts
        fact1 = Proposition("A", False)
        fact2 = Proposition("B", False)
        fact3 = Proposition("C", False)
        
        context = Context(
            facts={fact1, fact2, fact3},
            classification_edges=set(),
            rules=[],
            verb_lexicon=set()
        )
        
        # Query for one of them
        query = Query(fact2)
        result = evaluate_query(query, context)
        
        assert result == "⊤"
    
    def test_query_with_empty_context(self):
        """Test query in an empty context."""
        # Create empty context
        context = Context(
            facts=set(),
            classification_edges=set(),
            rules=[],
            verb_lexicon=set()
        )
        
        # Query for any fact
        fact = Proposition("A", False)
        query = Query(fact)
        result = evaluate_query(query, context)
        
        assert result == "?"
