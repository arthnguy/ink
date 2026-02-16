from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Token types for the Ink language lexer."""
    INDENT = auto()
    NEWLINE = auto()
    KEYWORD = auto()
    VARIABLE = auto()
    IDENTIFIER = auto()
    EOF = auto()


@dataclass
class Token:
    """Represents a token in the Ink language."""
    type: TokenType
    value: str
    line: int
    column: int


class LexerError(Exception):
    """Exception raised for lexical errors."""
    pass


# Classical Chinese keywords
KEYWORDS = {'曰', '問', '乎', '若', '則', '且', '者', '也', '以', '為', '動'}


def tokenize(source: str) -> list[Token]:
    """
    Tokenize Ink source code.
    
    Args:
        source: The source code string
        
    Returns:
        List of tokens including EOF
        
    Raises:
        LexerError: If an invalid character is encountered
    """
    tokens = []
    line = 1
    column = 1
    i = 0
    
    while i < len(source):
        char = source[i]
        
        # Handle tabs (INDENT)
        if char == '\t':
            tokens.append(Token(TokenType.INDENT, '\t', line, column))
            column += 1
            i += 1
        
        # Handle newlines (NEWLINE)
        elif char == '\n':
            tokens.append(Token(TokenType.NEWLINE, '\n', line, column))
            line += 1
            column = 1
            i += 1
        
        # Ignore spaces and carriage returns
        elif char == ' ' or char == '\r':
            column += 1
            i += 1
        
        # Handle comments (＃ to end of line)
        elif char == '＃':
            # Skip everything until newline
            while i < len(source) and source[i] != '\n':
                column += 1
                i += 1
            # Don't consume the newline, let the newline handler process it
        
        # Handle identifiers, keywords, and variables
        else:
            # Check if this is a keyword (single character)
            if char in KEYWORDS:
                tokens.append(Token(TokenType.KEYWORD, char, line, column))
                column += 1
                i += 1
            
            # Check if this starts an identifier or variable
            elif is_identifier_char(char):
                start_column = column
                identifier = ''
                
                # Collect identifier characters, but stop at keywords
                while i < len(source):
                    current_char = source[i]
                    # Stop if we hit a keyword
                    if current_char in KEYWORDS:
                        break
                    # Stop if we hit whitespace or special characters
                    if not is_identifier_char(current_char):
                        break
                    identifier += current_char
                    column += 1
                    i += 1
                
                # Check if it's a variable (starts with 其)
                if identifier.startswith('其'):
                    tokens.append(Token(TokenType.VARIABLE, identifier, line, start_column))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, identifier, line, start_column))
            
            else:
                # Invalid character
                raise LexerError(f"Invalid character '{char}' at line {line}, column {column}")
    
    # Emit EOF token
    tokens.append(Token(TokenType.EOF, '', line, column))
    
    return tokens


def is_identifier_char(char: str) -> bool:
    """
    Check if a character is valid in an identifier.
    
    Identifiers can contain:
    - Chinese characters (including Classical Chinese)
    - ASCII letters
    - Digits
    - Underscores
    """
    if char.isalnum():
        return True
    if char == '_':
        return True
    # Check if it's a Chinese character (broad range)
    code = ord(char)
    # CJK Unified Ideographs: U+4E00 to U+9FFF
    # CJK Extension A: U+3400 to U+4DBF
    if 0x3400 <= code <= 0x4DBF or 0x4E00 <= code <= 0x9FFF:
        return True
    return False
