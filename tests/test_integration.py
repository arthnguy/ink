import pytest
from ink.lexer import tokenize
from ink.parser import parse_program
from ink.interpreter import eval_program
from io import StringIO
import sys


def test_transitive_inference_from_main_ink():
    """Test the example from main.ink (transitive inference)."""
    source = """若A則B
若B則C
曰A
問C乎
"""
    
    # Parse the program
    ast = parse_program(source)
    
    # Capture output
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        # Evaluate the program
        eval_program(ast)
        
        # Get the output
        output = captured_output.getvalue()
        
        # Should output ⊤ (C is derivable from A→B→C)
        assert output.strip() == "⊤"
    finally:
        sys.stdout = sys.__stdout__


def test_classification_closure():
    """Test classification closure with transitive type relationships."""
    source = """A者B也
C者A也
問C者B也乎
"""
    
    ast = parse_program(source)
    
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        eval_program(ast)
        output = captured_output.getvalue()
        
        # Should output ⊤ (C⊑B is derived from C⊑A and A⊑B)
        assert output.strip() == "⊤"
    finally:
        sys.stdout = sys.__stdout__


def test_multi_premise_rule():
    """Test rules with multiple premises."""
    source = """以喜歡為動
曰下雨
曰週末
若下雨且週末則在家
問在家乎
"""
    
    ast = parse_program(source)
    
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        eval_program(ast)
        output = captured_output.getvalue()
        
        # Should output ⊤ (在家 is derived from 下雨 and 週末)
        assert output.strip() == "⊤"
    finally:
        sys.stdout = sys.__stdout__


def test_query_with_variables():
    """Test queries with variables."""
    source = """以喜歡為動
小明喜歡蘋果
問其X喜歡蘋果乎
"""
    
    ast = parse_program(source)
    
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        eval_program(ast)
        output = captured_output.getvalue()
        
        # Should output ⊤ (其X can be bound to 小明)
        assert output.strip() == "⊤"
    finally:
        sys.stdout = sys.__stdout__


def test_failed_query():
    """Test query that should fail."""
    source = """曰A
問B乎
"""
    
    ast = parse_program(source)
    
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        eval_program(ast)
        output = captured_output.getvalue()
        
        # Should output ? (B is not derivable)
        assert output.strip() == "?"
    finally:
        sys.stdout = sys.__stdout__


def test_multiple_queries():
    """Test program with multiple queries."""
    source = """曰A
曰B
問A乎
問B乎
問C乎
"""
    
    ast = parse_program(source)
    
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        eval_program(ast)
        output = captured_output.getvalue()
        lines = output.strip().split('\n')
        
        # First two queries should succeed, third should fail
        assert lines[0] == "⊤"
        assert lines[1] == "⊤"
        assert lines[2] == "?"
    finally:
        sys.stdout = sys.__stdout__


def test_complex_rule_chain():
    """Test complex chain of rules with classification."""
    source = """以是為動
哺乳類者生物也
貓者哺乳類也
若其X者生物也則其X是活的
問貓是活的乎
"""
    
    ast = parse_program(source)
    
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        eval_program(ast)
        output = captured_output.getvalue()
        
        # Should output ⊤
        # 1. 貓⊑哺乳類 and 哺乳類⊑生物 derive 貓⊑生物 (closure)
        # 2. Rule fires with 其X=貓, deriving 貓是活的
        assert output.strip() == "⊤"
    finally:
        sys.stdout = sys.__stdout__


def test_empty_program():
    """Test empty program."""
    source = ""
    
    ast = parse_program(source)
    
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        eval_program(ast)
        output = captured_output.getvalue()
        
        # Should produce no output
        assert output == ""
    finally:
        sys.stdout = sys.__stdout__


def test_program_with_only_assertions():
    """Test program with only assertions (no queries)."""
    source = """曰A
曰B
曰C
"""
    
    ast = parse_program(source)
    
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        eval_program(ast)
        output = captured_output.getvalue()
        
        # Should produce no output (no queries)
        assert output == ""
    finally:
        sys.stdout = sys.__stdout__


def test_lexer_to_interpreter_pipeline():
    """Test complete pipeline from lexer through interpreter."""
    source = "曰A\n問A乎\n"
    
    # Tokenize
    tokens = tokenize(source)
    assert len(tokens) > 0
    
    # Parse
    ast = parse_program(source)
    assert len(ast) == 2
    
    # Evaluate
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        eval_program(ast)
        output = captured_output.getvalue()
        assert output.strip() == "⊤"
    finally:
        sys.stdout = sys.__stdout__
