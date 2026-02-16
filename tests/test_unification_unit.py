import pytest
from ink.ast_nodes import Proposition, SVOClause, ClassificationEdge
from ink.interpreter import unify, apply_substitution


class TestApplySubstitution:
    """Test apply_substitution function."""
    
    def test_apply_substitution_to_proposition_variable(self):
        """Test substitution application to a proposition variable."""
        prop = Proposition("其X", True)
        subst = {"其X": "A"}
        result = apply_substitution(prop, subst)
        assert result == Proposition("A", False)
    
    def test_apply_substitution_to_proposition_concrete(self):
        """Test substitution application to a concrete proposition."""
        prop = Proposition("A", False)
        subst = {"其X": "B"}
        result = apply_substitution(prop, subst)
        assert result == prop  # No change
    
    def test_apply_substitution_to_svo_clause(self):
        """Test substitution application to SVO clause."""
        svo = SVOClause("其X", True, "愛", False, "其Y", True)
        subst = {"其X": "人", "其Y": "狗"}
        result = apply_substitution(svo, subst)
        assert result == SVOClause("人", False, "愛", False, "狗", False)
    
    def test_apply_substitution_to_classification_edge(self):
        """Test substitution application to classification edge."""
        edge = ClassificationEdge("其X", True, "動物", False)
        subst = {"其X": "狗"}
        result = apply_substitution(edge, subst)
        assert result == ClassificationEdge("狗", False, "動物", False)


class TestUnifyProposition:
    """Test unification of propositions."""
    
    def test_unify_identical_concrete_propositions(self):
        """Test unifying two identical concrete propositions."""
        prop1 = Proposition("A", False)
        prop2 = Proposition("A", False)
        result = unify(prop1, prop2, {})
        assert result == {}
    
    def test_unify_different_concrete_propositions(self):
        """Test unifying two different concrete propositions."""
        prop1 = Proposition("A", False)
        prop2 = Proposition("B", False)
        result = unify(prop1, prop2, {})
        assert result is None
    
    def test_unify_variable_with_concrete(self):
        """Test unifying a variable with a concrete proposition."""
        var_prop = Proposition("其X", True)
        concrete_prop = Proposition("A", False)
        result = unify(var_prop, concrete_prop, {})
        assert result == {"其X": "A"}
    
    def test_unify_with_existing_consistent_substitution(self):
        """Test unifying with an existing consistent substitution."""
        var_prop = Proposition("其X", True)
        concrete_prop = Proposition("A", False)
        existing_subst = {"其X": "A"}
        result = unify(var_prop, concrete_prop, existing_subst)
        assert result == {"其X": "A"}
    
    def test_unify_with_existing_inconsistent_substitution(self):
        """Test unifying with an existing inconsistent substitution."""
        var_prop = Proposition("其X", True)
        concrete_prop = Proposition("B", False)
        existing_subst = {"其X": "A"}
        result = unify(var_prop, concrete_prop, existing_subst)
        assert result is None


class TestUnifySVOClause:
    """Test unification of SVO clauses."""
    
    def test_unify_identical_svo_clauses(self):
        """Test unifying two identical SVO clauses."""
        svo1 = SVOClause("人", False, "愛", False, "狗", False)
        svo2 = SVOClause("人", False, "愛", False, "狗", False)
        result = unify(svo1, svo2, {})
        assert result == {}
    
    def test_unify_svo_with_subject_variable(self):
        """Test unifying SVO clause with variable in subject position."""
        pattern = SVOClause("其X", True, "愛", False, "狗", False)
        fact = SVOClause("人", False, "愛", False, "狗", False)
        result = unify(pattern, fact, {})
        assert result == {"其X": "人"}
    
    def test_unify_svo_with_multiple_variables(self):
        """Test unifying SVO clause with multiple variables."""
        pattern = SVOClause("其X", True, "愛", False, "其Y", True)
        fact = SVOClause("人", False, "愛", False, "狗", False)
        result = unify(pattern, fact, {})
        assert result == {"其X": "人", "其Y": "狗"}
    
    def test_unify_svo_with_verb_mismatch(self):
        """Test unifying SVO clauses with different verbs."""
        svo1 = SVOClause("人", False, "愛", False, "狗", False)
        svo2 = SVOClause("人", False, "恨", False, "狗", False)
        result = unify(svo1, svo2, {})
        assert result is None
    
    def test_unify_svo_threading_substitutions(self):
        """Test that substitutions are threaded through SVO unification."""
        pattern = SVOClause("其X", True, "愛", False, "其X", True)
        fact = SVOClause("人", False, "愛", False, "人", False)
        result = unify(pattern, fact, {})
        assert result == {"其X": "人"}
    
    def test_unify_svo_threading_substitutions_failure(self):
        """Test that inconsistent variable bindings fail."""
        pattern = SVOClause("其X", True, "愛", False, "其X", True)
        fact = SVOClause("人", False, "愛", False, "狗", False)
        result = unify(pattern, fact, {})
        assert result is None


class TestUnifyClassificationEdge:
    """Test unification of classification edges."""
    
    def test_unify_identical_classification_edges(self):
        """Test unifying two identical classification edges."""
        edge1 = ClassificationEdge("狗", False, "動物", False)
        edge2 = ClassificationEdge("狗", False, "動物", False)
        result = unify(edge1, edge2, {})
        assert result == {}
    
    def test_unify_classification_with_subtype_variable(self):
        """Test unifying classification edge with variable in subtype."""
        pattern = ClassificationEdge("其X", True, "動物", False)
        fact = ClassificationEdge("狗", False, "動物", False)
        result = unify(pattern, fact, {})
        assert result == {"其X": "狗"}
    
    def test_unify_classification_with_supertype_variable(self):
        """Test unifying classification edge with variable in supertype."""
        pattern = ClassificationEdge("狗", False, "其Y", True)
        fact = ClassificationEdge("狗", False, "動物", False)
        result = unify(pattern, fact, {})
        assert result == {"其Y": "動物"}
    
    def test_unify_classification_with_both_variables(self):
        """Test unifying classification edge with variables in both positions."""
        pattern = ClassificationEdge("其X", True, "其Y", True)
        fact = ClassificationEdge("狗", False, "動物", False)
        result = unify(pattern, fact, {})
        assert result == {"其X": "狗", "其Y": "動物"}
    
    def test_unify_classification_with_mismatch(self):
        """Test unifying classification edges with different values."""
        edge1 = ClassificationEdge("狗", False, "動物", False)
        edge2 = ClassificationEdge("貓", False, "動物", False)
        result = unify(edge1, edge2, {})
        assert result is None


class TestUnifyMixedTypes:
    """Test unification of different AST node types."""
    
    def test_unify_proposition_with_svo_fails(self):
        """Test that unifying different node types fails."""
        prop = Proposition("A", False)
        svo = SVOClause("人", False, "愛", False, "狗", False)
        result = unify(prop, svo, {})
        assert result is None
    
    def test_unify_proposition_with_classification_fails(self):
        """Test that unifying different node types fails."""
        prop = Proposition("A", False)
        edge = ClassificationEdge("狗", False, "動物", False)
        result = unify(prop, edge, {})
        assert result is None
