import pytest
from ink.ast_nodes import ClassificationEdge
from ink.interpreter import compute_classification_closure


class TestClassificationClosure:
    """Test compute_classification_closure function."""
    
    def test_simple_chain(self):
        """Test simple chain: A⊑B⊑C should derive A⊑C."""
        # Create edges A⊑B and B⊑C
        edge_ab = ClassificationEdge("A", False, "B", False)
        edge_bc = ClassificationEdge("B", False, "C", False)
        
        edges = {edge_ab, edge_bc}
        closure = compute_classification_closure(edges)
        
        # Should contain original edges
        assert edge_ab in closure
        assert edge_bc in closure
        
        # Should contain transitive edge A⊑C
        edge_ac = ClassificationEdge("A", False, "C", False)
        assert edge_ac in closure
        
        # Should have exactly 3 edges
        assert len(closure) == 3
    
    def test_diamond(self):
        """Test diamond: A⊑B, A⊑C, B⊑D, C⊑D should derive A⊑D."""
        # Create diamond structure
        edge_ab = ClassificationEdge("A", False, "B", False)
        edge_ac = ClassificationEdge("A", False, "C", False)
        edge_bd = ClassificationEdge("B", False, "D", False)
        edge_cd = ClassificationEdge("C", False, "D", False)
        
        edges = {edge_ab, edge_ac, edge_bd, edge_cd}
        closure = compute_classification_closure(edges)
        
        # Should contain all original edges
        assert edge_ab in closure
        assert edge_ac in closure
        assert edge_bd in closure
        assert edge_cd in closure
        
        # Should contain transitive edge A⊑D (derived from both paths)
        edge_ad = ClassificationEdge("A", False, "D", False)
        assert edge_ad in closure
        
        # Should have exactly 5 edges (4 original + 1 derived)
        # Note: A⊑D can be derived from both A⊑B⊑D and A⊑C⊑D, but should only appear once
        assert len(closure) == 5
    
    def test_cycle(self):
        """Test cycle: A⊑B⊑C⊑A should handle gracefully without infinite loop."""
        # Create a cycle
        edge_ab = ClassificationEdge("A", False, "B", False)
        edge_bc = ClassificationEdge("B", False, "C", False)
        edge_ca = ClassificationEdge("C", False, "A", False)
        
        edges = {edge_ab, edge_bc, edge_ca}
        closure = compute_classification_closure(edges)
        
        # Should contain all original edges
        assert edge_ab in closure
        assert edge_bc in closure
        assert edge_ca in closure
        
        # Should derive all transitive edges in the cycle
        edge_ac = ClassificationEdge("A", False, "C", False)
        edge_ba = ClassificationEdge("B", False, "A", False)
        edge_cb = ClassificationEdge("C", False, "B", False)
        
        assert edge_ac in closure
        assert edge_ba in closure
        assert edge_cb in closure
        
        # Should also derive self-loops (A⊑A, B⊑B, C⊑C)
        edge_aa = ClassificationEdge("A", False, "A", False)
        edge_bb = ClassificationEdge("B", False, "B", False)
        edge_cc = ClassificationEdge("C", False, "C", False)
        
        assert edge_aa in closure
        assert edge_bb in closure
        assert edge_cc in closure
        
        # Should have exactly 9 edges (3 original + 3 transitive + 3 self-loops)
        assert len(closure) == 9
    
    def test_empty_set(self):
        """Test empty set of edges."""
        edges = set()
        closure = compute_classification_closure(edges)
        assert len(closure) == 0
    
    def test_single_edge(self):
        """Test single edge with no transitive closure."""
        edge = ClassificationEdge("A", False, "B", False)
        edges = {edge}
        closure = compute_classification_closure(edges)
        
        assert edge in closure
        assert len(closure) == 1
    
    def test_disconnected_edges(self):
        """Test disconnected edges that don't form transitive relationships."""
        edge_ab = ClassificationEdge("A", False, "B", False)
        edge_cd = ClassificationEdge("C", False, "D", False)
        
        edges = {edge_ab, edge_cd}
        closure = compute_classification_closure(edges)
        
        # Should only contain original edges
        assert edge_ab in closure
        assert edge_cd in closure
        assert len(closure) == 2
    
    def test_long_chain(self):
        """Test longer chain: A⊑B⊑C⊑D⊑E."""
        edge_ab = ClassificationEdge("A", False, "B", False)
        edge_bc = ClassificationEdge("B", False, "C", False)
        edge_cd = ClassificationEdge("C", False, "D", False)
        edge_de = ClassificationEdge("D", False, "E", False)
        
        edges = {edge_ab, edge_bc, edge_cd, edge_de}
        closure = compute_classification_closure(edges)
        
        # Should contain all original edges
        assert edge_ab in closure
        assert edge_bc in closure
        assert edge_cd in closure
        assert edge_de in closure
        
        # Should contain all transitive edges
        edge_ac = ClassificationEdge("A", False, "C", False)
        edge_ad = ClassificationEdge("A", False, "D", False)
        edge_ae = ClassificationEdge("A", False, "E", False)
        edge_bd = ClassificationEdge("B", False, "D", False)
        edge_be = ClassificationEdge("B", False, "E", False)
        edge_ce = ClassificationEdge("C", False, "E", False)
        
        assert edge_ac in closure
        assert edge_ad in closure
        assert edge_ae in closure
        assert edge_bd in closure
        assert edge_be in closure
        assert edge_ce in closure
        
        # Should have 4 original + 6 derived = 10 edges
        assert len(closure) == 10
    
    def test_self_loop(self):
        """Test self-loop: A⊑A."""
        edge_aa = ClassificationEdge("A", False, "A", False)
        edges = {edge_aa}
        closure = compute_classification_closure(edges)
        
        # Should contain the self-loop
        assert edge_aa in closure
        assert len(closure) == 1
    
    def test_variables_not_processed(self):
        """Test that edges with variables can still participate in transitive closure."""
        # Create edges where one has a variable in the result
        edge_ab = ClassificationEdge("A", False, "B", False)
        edge_bc_var = ClassificationEdge("B", False, "其C", True)
        
        edges = {edge_ab, edge_bc_var}
        closure = compute_classification_closure(edges)
        
        # Should contain original edges
        assert edge_ab in closure
        assert edge_bc_var in closure
        
        # Should also derive A⊑其C (transitive edge with variable in supertype)
        edge_ac_var = ClassificationEdge("A", False, "其C", True)
        assert edge_ac_var in closure
        
        # Should have 3 edges total
        assert len(closure) == 3
