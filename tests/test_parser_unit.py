import pytest
from ink.parser import parse_program, ParseError
from ink.ast_nodes import (
    Proposition, SVOClause, ClassificationEdge, Rule, Query, VerbDeclaration
)


def test_verb_declaration():
    """Test parsing a verb declaration."""
    program = "以愛為動"
    ast = parse_program(program)
    
    assert len(ast) == 1
    assert isinstance(ast[0], VerbDeclaration)
    assert ast[0].verb == "愛"


def test_proposition_concrete():
    """Test parsing a concrete proposition."""
    program = "曰天圓"
    ast = parse_program(program)
    
    assert len(ast) == 1
    assert isinstance(ast[0], Proposition)
    assert ast[0].identifier == "天圓"
    assert ast[0].is_variable is False


def test_proposition_variable():
    """Test parsing a proposition with a variable."""
    program = "曰其物"
    ast = parse_program(program)
    
    assert len(ast) == 1
    assert isinstance(ast[0], Proposition)
    assert ast[0].identifier == "其物"
    assert ast[0].is_variable is True


def test_svo_clause():
    """Test parsing an SVO clause."""
    program = "以愛為動\n人愛狗"
    ast = parse_program(program)
    
    assert len(ast) == 2
    assert isinstance(ast[0], VerbDeclaration)
    assert isinstance(ast[1], SVOClause)
    assert ast[1].subject == "人"
    assert ast[1].verb == "愛"
    assert ast[1].object == "狗"
    assert ast[1].subject_is_var is False
    assert ast[1].verb_is_var is False
    assert ast[1].object_is_var is False


def test_svo_clause_with_variables():
    """Test parsing an SVO clause with variables."""
    program = "以愛為動\n其人愛其物"
    ast = parse_program(program)
    
    assert len(ast) == 2
    assert isinstance(ast[1], SVOClause)
    assert ast[1].subject == "其人"
    assert ast[1].subject_is_var is True
    assert ast[1].object == "其物"
    assert ast[1].object_is_var is True


def test_svo_undeclared_verb_error():
    """Test that using an undeclared verb raises an error."""
    program = "人愛狗"
    
    with pytest.raises(ParseError) as exc_info:
        parse_program(program)
    
    assert "Undeclared verb" in str(exc_info.value)


def test_classification_edge():
    """Test parsing a classification edge."""
    program = "狗者動物也"
    ast = parse_program(program)
    
    assert len(ast) == 1
    assert isinstance(ast[0], ClassificationEdge)
    assert ast[0].subtype == "狗"
    assert ast[0].supertype == "動物"
    assert ast[0].subtype_is_var is False
    assert ast[0].supertype_is_var is False


def test_classification_edge_with_variables():
    """Test parsing a classification edge with variables."""
    program = "其物者動物也"
    ast = parse_program(program)
    
    assert len(ast) == 1
    assert isinstance(ast[0], ClassificationEdge)
    assert ast[0].subtype == "其物"
    assert ast[0].subtype_is_var is True
    assert ast[0].supertype == "動物"
    assert ast[0].supertype_is_var is False


def test_single_premise_rule():
    """Test parsing a rule with a single premise."""
    program = "若曰A則曰B"
    ast = parse_program(program)
    
    assert len(ast) == 1
    assert isinstance(ast[0], Rule)
    assert len(ast[0].premises) == 1
    assert isinstance(ast[0].premises[0], Proposition)
    assert ast[0].premises[0].identifier == "A"
    assert isinstance(ast[0].conclusion, Proposition)
    assert ast[0].conclusion.identifier == "B"


def test_multi_premise_rule():
    """Test parsing a rule with multiple premises."""
    program = "若曰A且曰B且曰C則曰D"
    ast = parse_program(program)
    
    assert len(ast) == 1
    assert isinstance(ast[0], Rule)
    assert len(ast[0].premises) == 3
    assert ast[0].premises[0].identifier == "A"
    assert ast[0].premises[1].identifier == "B"
    assert ast[0].premises[2].identifier == "C"
    assert ast[0].conclusion.identifier == "D"


def test_rule_with_mixed_expressions():
    """Test parsing a rule with different expression types."""
    program = "若曰A且狗者動物也則曰B"
    ast = parse_program(program)
    
    assert len(ast) == 1
    assert isinstance(ast[0], Rule)
    assert len(ast[0].premises) == 2
    assert isinstance(ast[0].premises[0], Proposition)
    assert isinstance(ast[0].premises[1], ClassificationEdge)
    assert isinstance(ast[0].conclusion, Proposition)


def test_query_proposition():
    """Test parsing a query with a proposition."""
    program = "問A乎"
    ast = parse_program(program)
    
    assert len(ast) == 1
    assert isinstance(ast[0], Query)
    assert isinstance(ast[0].expression, Proposition)
    assert ast[0].expression.identifier == "A"


def test_query_classification():
    """Test parsing a query with a classification edge."""
    program = "問狗者動物也乎"
    ast = parse_program(program)
    
    assert len(ast) == 1
    assert isinstance(ast[0], Query)
    assert isinstance(ast[0].expression, ClassificationEdge)


def test_query_svo():
    """Test parsing a query with an SVO clause."""
    program = "以愛為動\n問人愛狗乎"
    ast = parse_program(program)
    
    assert len(ast) == 2
    assert isinstance(ast[1], Query)
    assert isinstance(ast[1].expression, SVOClause)


def test_empty_program():
    """Test parsing an empty program."""
    program = ""
    ast = parse_program(program)
    
    assert len(ast) == 0


def test_program_with_newlines():
    """Test parsing a program with multiple statements separated by newlines."""
    program = "曰A\n曰B\n曰C"
    ast = parse_program(program)
    
    assert len(ast) == 3
    assert all(isinstance(node, Proposition) for node in ast)
    assert ast[0].identifier == "A"
    assert ast[1].identifier == "B"
    assert ast[2].identifier == "C"


def test_complex_program():
    """Test parsing a complete program with multiple statement types."""
    program = """以愛為動
曰天圓
人愛狗
狗者動物也
若曰天圓則人愛狗
問曰天圓乎"""
    
    ast = parse_program(program)
    
    assert len(ast) == 6
    assert isinstance(ast[0], VerbDeclaration)
    assert isinstance(ast[1], Proposition)
    assert isinstance(ast[2], SVOClause)
    assert isinstance(ast[3], ClassificationEdge)
    assert isinstance(ast[4], Rule)
    assert isinstance(ast[5], Query)


def test_malformed_verb_declaration():
    """Test error handling for malformed verb declaration."""
    program = "以愛為"  # Missing 動
    
    with pytest.raises(ParseError):
        parse_program(program)


def test_malformed_proposition():
    """Test error handling for malformed proposition."""
    program = "曰"  # Missing identifier
    
    with pytest.raises(ParseError):
        parse_program(program)


def test_malformed_classification():
    """Test error handling for malformed classification."""
    program = "狗者動物"  # Missing 也
    
    with pytest.raises(ParseError):
        parse_program(program)


def test_malformed_rule():
    """Test error handling for malformed rule."""
    program = "若曰A則"  # Missing conclusion
    
    with pytest.raises(ParseError):
        parse_program(program)


def test_malformed_query():
    """Test error handling for malformed query."""
    program = "問A"  # Missing 乎
    
    with pytest.raises(ParseError):
        parse_program(program)
