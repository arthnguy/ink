import pytest
from ink.lexer import tokenize, TokenType, LexerError, Token


class TestKeywords:
    """Test each keyword individually."""
    
    def test_keyword_yue(self):
        """Test 曰 keyword."""
        tokens = tokenize('曰')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == '曰'
        assert tokens[1].type == TokenType.EOF
    
    def test_keyword_wen(self):
        """Test 問 keyword."""
        tokens = tokenize('問')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == '問'
        assert tokens[1].type == TokenType.EOF
    
    def test_keyword_hu(self):
        """Test 乎 keyword."""
        tokens = tokenize('乎')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == '乎'
        assert tokens[1].type == TokenType.EOF
    
    def test_keyword_ruo(self):
        """Test 若 keyword."""
        tokens = tokenize('若')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == '若'
        assert tokens[1].type == TokenType.EOF
    
    def test_keyword_ze(self):
        """Test 則 keyword."""
        tokens = tokenize('則')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == '則'
        assert tokens[1].type == TokenType.EOF
    
    def test_keyword_qie(self):
        """Test 且 keyword."""
        tokens = tokenize('且')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == '且'
        assert tokens[1].type == TokenType.EOF
    
    def test_keyword_zhe(self):
        """Test 者 keyword."""
        tokens = tokenize('者')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == '者'
        assert tokens[1].type == TokenType.EOF
    
    def test_keyword_ye(self):
        """Test 也 keyword."""
        tokens = tokenize('也')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == '也'
        assert tokens[1].type == TokenType.EOF
    
    def test_keyword_yi(self):
        """Test 以 keyword."""
        tokens = tokenize('以')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == '以'
        assert tokens[1].type == TokenType.EOF
    
    def test_keyword_wei(self):
        """Test 為 keyword."""
        tokens = tokenize('為')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == '為'
        assert tokens[1].type == TokenType.EOF
    
    def test_keyword_dong(self):
        """Test 動 keyword."""
        tokens = tokenize('動')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == '動'
        assert tokens[1].type == TokenType.EOF
    
    def test_multiple_keywords(self):
        """Test multiple keywords in sequence."""
        tokens = tokenize('曰問乎')
        assert len(tokens) == 4  # 3 keywords + EOF
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == '曰'
        assert tokens[1].type == TokenType.KEYWORD
        assert tokens[1].value == '問'
        assert tokens[2].type == TokenType.KEYWORD
        assert tokens[2].value == '乎'
        assert tokens[3].type == TokenType.EOF


class TestVariables:
    """Test variable recognition with 其 prefix."""
    
    def test_simple_variable(self):
        """Test simple variable with 其 prefix."""
        tokens = tokenize('其X')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == '其X'
        assert tokens[1].type == TokenType.EOF
    
    def test_variable_with_chinese_chars(self):
        """Test variable with Chinese characters."""
        tokens = tokenize('其人')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == '其人'
        assert tokens[1].type == TokenType.EOF
    
    def test_variable_with_multiple_chars(self):
        """Test variable with multiple characters."""
        tokens = tokenize('其變量')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == '其變量'
        assert tokens[1].type == TokenType.EOF
    
    def test_variable_with_underscore(self):
        """Test variable with underscore."""
        tokens = tokenize('其_var')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == '其_var'
        assert tokens[1].type == TokenType.EOF
    
    def test_variable_with_digits(self):
        """Test variable with digits."""
        tokens = tokenize('其X1')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == '其X1'
        assert tokens[1].type == TokenType.EOF
    
    def test_variable_stops_at_keyword(self):
        """Test that variable tokenization stops at keywords."""
        tokens = tokenize('其X曰')
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == '其X'
        assert tokens[1].type == TokenType.KEYWORD
        assert tokens[1].value == '曰'
        assert tokens[2].type == TokenType.EOF
    
    def test_variable_with_whitespace(self):
        """Test variable followed by whitespace."""
        tokens = tokenize('其X ')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.VARIABLE
        assert tokens[0].value == '其X'
        assert tokens[1].type == TokenType.EOF


class TestIdentifiers:
    """Test identifier recognition."""
    
    def test_simple_identifier(self):
        """Test simple ASCII identifier."""
        tokens = tokenize('foo')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == 'foo'
        assert tokens[1].type == TokenType.EOF
    
    def test_chinese_identifier(self):
        """Test Chinese character identifier."""
        tokens = tokenize('人')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == '人'
        assert tokens[1].type == TokenType.EOF
    
    def test_identifier_with_underscore(self):
        """Test identifier with underscore."""
        tokens = tokenize('my_var')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == 'my_var'
        assert tokens[1].type == TokenType.EOF
    
    def test_identifier_with_digits(self):
        """Test identifier with digits."""
        tokens = tokenize('var123')
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == 'var123'
        assert tokens[1].type == TokenType.EOF
    
    def test_identifier_stops_at_keyword(self):
        """Test that identifier tokenization stops at keywords."""
        tokens = tokenize('foo曰')
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == 'foo'
        assert tokens[1].type == TokenType.KEYWORD
        assert tokens[1].value == '曰'
        assert tokens[2].type == TokenType.EOF


class TestErrorHandling:
    """Test error handling for invalid characters."""
    
    def test_invalid_character_exclamation(self):
        """Test that exclamation mark raises LexerError."""
        with pytest.raises(LexerError) as exc_info:
            tokenize('!')
        assert "Invalid character '!'" in str(exc_info.value)
        assert "line 1, column 1" in str(exc_info.value)
    
    def test_invalid_character_at_sign(self):
        """Test that @ sign raises LexerError."""
        with pytest.raises(LexerError) as exc_info:
            tokenize('@')
        assert "Invalid character '@'" in str(exc_info.value)
        assert "line 1, column 1" in str(exc_info.value)
    
    def test_invalid_character_hash(self):
        """Test that # sign raises LexerError."""
        with pytest.raises(LexerError) as exc_info:
            tokenize('#')
        assert "Invalid character '#'" in str(exc_info.value)
        assert "line 1, column 1" in str(exc_info.value)
    
    def test_invalid_character_dollar(self):
        """Test that $ sign raises LexerError."""
        with pytest.raises(LexerError) as exc_info:
            tokenize('$')
        assert "Invalid character '$'" in str(exc_info.value)
        assert "line 1, column 1" in str(exc_info.value)
    
    def test_invalid_character_percent(self):
        """Test that % sign raises LexerError."""
        with pytest.raises(LexerError) as exc_info:
            tokenize('%')
        assert "Invalid character '%'" in str(exc_info.value)
        assert "line 1, column 1" in str(exc_info.value)
    
    def test_invalid_character_position(self):
        """Test that error reports correct position."""
        with pytest.raises(LexerError) as exc_info:
            tokenize('foo!')
        assert "Invalid character '!'" in str(exc_info.value)
        assert "line 1, column 4" in str(exc_info.value)
    
    def test_invalid_character_after_newline(self):
        """Test that error reports correct line and column after newline."""
        with pytest.raises(LexerError) as exc_info:
            tokenize('foo\n!')
        assert "Invalid character '!'" in str(exc_info.value)
        assert "line 2, column 1" in str(exc_info.value)


class TestEdgeCases:
    """Test edge cases."""
    
    def test_empty_input(self):
        """Test that empty input produces only EOF token."""
        tokens = tokenize('')
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
        assert tokens[0].value == ''
    
    def test_only_whitespace(self):
        """Test that only whitespace produces only EOF token."""
        tokens = tokenize('   ')
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_only_tabs(self):
        """Test that only tabs produces INDENT tokens and EOF."""
        tokens = tokenize('\t\t')
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.INDENT
        assert tokens[1].type == TokenType.INDENT
        assert tokens[2].type == TokenType.EOF
    
    def test_only_newlines(self):
        """Test that only newlines produces NEWLINE tokens and EOF."""
        tokens = tokenize('\n\n')
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.NEWLINE
        assert tokens[1].type == TokenType.NEWLINE
        assert tokens[2].type == TokenType.EOF
    
    def test_mixed_whitespace(self):
        """Test mixed whitespace handling."""
        tokens = tokenize(' \t \n ')
        assert len(tokens) == 3  # INDENT, NEWLINE, EOF
        assert tokens[0].type == TokenType.INDENT
        assert tokens[1].type == TokenType.NEWLINE
        assert tokens[2].type == TokenType.EOF


class TestPositionTracking:
    """Test that tokens have correct line and column information."""
    
    def test_single_line_positions(self):
        """Test column positions on a single line."""
        tokens = tokenize('曰問乎')
        assert tokens[0].line == 1
        assert tokens[0].column == 1
        assert tokens[1].line == 1
        assert tokens[1].column == 2
        assert tokens[2].line == 1
        assert tokens[2].column == 3
    
    def test_multiline_positions(self):
        """Test line and column positions across multiple lines."""
        tokens = tokenize('曰\n問')
        assert tokens[0].line == 1
        assert tokens[0].column == 1
        assert tokens[1].line == 1
        assert tokens[1].column == 2
        assert tokens[2].line == 2
        assert tokens[2].column == 1
    
    def test_tab_position(self):
        """Test position tracking with tabs."""
        tokens = tokenize('\t曰')
        assert tokens[0].line == 1
        assert tokens[0].column == 1
        assert tokens[1].line == 1
        assert tokens[1].column == 2
