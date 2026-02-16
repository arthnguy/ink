from ink.lexer import Token, TokenType, tokenize
from ink.ast_nodes import (
    Proposition, SVOClause, ClassificationEdge, Rule, Query, VerbDeclaration
)


class ParseError(Exception):
    """Exception raised for parse errors."""
    pass


class Parser:
    """Parser for Ink language with verb lexicon state."""
    
    def __init__(self, tokens: list[Token]):
        """
        Initialize parser with token list.
        
        Args:
            tokens: List of tokens from lexer
        """
        self.tokens = tokens
        self.position = 0
        self.verb_lexicon = set()
    
    def peek(self, offset: int = 0) -> Token:
        """
        Peek at a token without consuming it.
        
        Args:
            offset: How many tokens ahead to peek (default 0 = current)
            
        Returns:
            Token at position + offset, or EOF if out of bounds
        """
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF
    
    def advance(self) -> Token:
        """
        Consume and return the current token.
        
        Returns:
            The current token before advancing
        """
        token = self.peek()
        if token.type != TokenType.EOF:
            self.position += 1
        return token
    
    def expect(self, token_type: TokenType, value: str = None) -> Token:
        """
        Consume a token and verify it matches expected type/value.
        
        Args:
            token_type: Expected token type
            value: Expected token value (optional)
            
        Returns:
            The consumed token
            
        Raises:
            ParseError: If token doesn't match expectations
        """
        token = self.peek()
        
        if token.type != token_type:
            raise ParseError(
                f"Unexpected token '{token.value}' at line {token.line}, column {token.column}. "
                f"Expected {token_type.name}"
            )
        
        if value is not None and token.value != value:
            raise ParseError(
                f"Unexpected token '{token.value}' at line {token.line}, column {token.column}. "
                f"Expected '{value}'"
            )
        
        return self.advance()

    def parse_verb_declaration(self) -> VerbDeclaration:
        """
        Parse a verb declaration: 以V為動
        
        Returns:
            VerbDeclaration AST node
            
        Raises:
            ParseError: If syntax is invalid
        """
        self.expect(TokenType.KEYWORD, '以')
        
        # Get the verb identifier
        verb_token = self.peek()
        if verb_token.type not in (TokenType.IDENTIFIER, TokenType.VARIABLE):
            raise ParseError(
                f"Expected identifier for verb at line {verb_token.line}, column {verb_token.column}"
            )
        verb = self.advance().value
        
        self.expect(TokenType.KEYWORD, '為')
        self.expect(TokenType.KEYWORD, '動')
        
        # Add verb to lexicon
        self.verb_lexicon.add(verb)
        
        return VerbDeclaration(verb=verb)

    def parse_proposition(self) -> Proposition:
        """
        Parse a proposition: 曰P
        
        Returns:
            Proposition AST node
            
        Raises:
            ParseError: If syntax is invalid
        """
        self.expect(TokenType.KEYWORD, '曰')
        
        # Get the proposition identifier
        token = self.peek()
        if token.type == TokenType.VARIABLE:
            identifier = self.advance().value
            is_variable = True
        elif token.type == TokenType.IDENTIFIER:
            identifier = self.advance().value
            is_variable = False
        else:
            raise ParseError(
                f"Expected identifier or variable for proposition at line {token.line}, column {token.column}"
            )
        
        return Proposition(identifier=identifier, is_variable=is_variable)

    def parse_svo_clause(self, first_token: Token) -> SVOClause:
        """
        Parse an SVO clause using verb lexicon.
        
        Args:
            first_token: The first identifier/variable token of the clause
            
        Returns:
            SVOClause AST node
            
        Raises:
            ParseError: If no verb found or multiple verbs found
        """
        # Collect all identifiers/variables in the clause
        identifiers = []
        
        # Add the first token
        identifiers.append(first_token)
        
        # Collect remaining identifiers until we hit a statement boundary
        while True:
            token = self.peek()
            
            # Stop at statement boundaries
            if token.type in (TokenType.NEWLINE, TokenType.EOF, TokenType.KEYWORD):
                break
            
            # Collect identifiers and variables
            if token.type in (TokenType.IDENTIFIER, TokenType.VARIABLE):
                identifiers.append(self.advance())
            else:
                # Skip other tokens (like INDENT)
                self.advance()
        
        # If we have a single token, try to split it by finding verb within the string
        if len(identifiers) == 1:
            token = identifiers[0]
            text = token.value
            
            # Search for verb within the text
            verb_found = None
            verb_pos = -1
            for verb in self.verb_lexicon:
                pos = text.find(verb)
                if pos != -1:
                    if verb_found is not None:
                        raise ParseError(
                            f"Multiple verbs found in SVO clause '{text}' at line {first_token.line}"
                        )
                    verb_found = verb
                    verb_pos = pos
            
            if verb_found is None:
                raise ParseError(
                    f"Undeclared verb in SVO clause '{text}' at line {first_token.line}. "
                    f"Use 以V為動 to declare it."
                )
            
            if verb_pos == 0:
                raise ParseError(
                    f"SVO clause must have a subject before the verb at line {first_token.line}"
                )
            
            if verb_pos + len(verb_found) >= len(text):
                raise ParseError(
                    f"SVO clause must have an object after the verb at line {first_token.line}"
                )
            
            # Split the text
            subject = text[:verb_pos]
            object_val = text[verb_pos + len(verb_found):]
            
            # Detect variables in the split portions
            subject_is_var = subject.startswith('其')
            object_is_var = object_val.startswith('其')
            
            return SVOClause(
                subject=subject,
                subject_is_var=subject_is_var,
                verb=verb_found,
                verb_is_var=False,  # Verb can't be variable in this case
                object=object_val,
                object_is_var=object_is_var
            )
        
        # Multiple tokens case - search for verb token
        verb_positions = []
        for i, token in enumerate(identifiers):
            if token.value in self.verb_lexicon:
                verb_positions.append(i)
        
        # Check verb count
        if len(verb_positions) == 0:
            clause_text = ' '.join(t.value for t in identifiers)
            raise ParseError(
                f"Undeclared verb in SVO clause '{clause_text}' at line {first_token.line}. "
                f"Use 以V為動 to declare it."
            )
        
        if len(verb_positions) > 1:
            clause_text = ' '.join(t.value for t in identifiers)
            raise ParseError(
                f"Multiple verbs found in SVO clause '{clause_text}' at line {first_token.line}"
            )
        
        # Split into subject, verb, object based on verb position
        verb_pos = verb_positions[0]
        
        if verb_pos == 0:
            raise ParseError(
                f"SVO clause must have a subject before the verb at line {first_token.line}"
            )
        
        if verb_pos == len(identifiers) - 1:
            raise ParseError(
                f"SVO clause must have an object after the verb at line {first_token.line}"
            )
        
        # Extract subject (all tokens before verb)
        subject_tokens = identifiers[:verb_pos]
        subject = ''.join(t.value for t in subject_tokens)
        subject_is_var = any(t.type == TokenType.VARIABLE for t in subject_tokens)
        
        # Extract verb
        verb_token = identifiers[verb_pos]
        verb = verb_token.value
        verb_is_var = verb_token.type == TokenType.VARIABLE
        
        # Extract object (all tokens after verb)
        object_tokens = identifiers[verb_pos + 1:]
        object_val = ''.join(t.value for t in object_tokens)
        object_is_var = any(t.type == TokenType.VARIABLE for t in object_tokens)
        
        return SVOClause(
            subject=subject,
            subject_is_var=subject_is_var,
            verb=verb,
            verb_is_var=verb_is_var,
            object=object_val,
            object_is_var=object_is_var
        )

    def parse_classification_edge(self, first_token: Token) -> ClassificationEdge:
        """
        Parse a classification edge: X者Y也
        
        Args:
            first_token: The first identifier/variable token (subtype)
            
        Returns:
            ClassificationEdge AST node
            
        Raises:
            ParseError: If syntax is invalid
        """
        # Subtype is the first token
        subtype = first_token.value
        subtype_is_var = first_token.type == TokenType.VARIABLE
        
        # Expect 者
        self.expect(TokenType.KEYWORD, '者')
        
        # Collect supertype - may be multiple tokens if keywords break it up
        supertype_parts = []
        supertype_is_var = False
        
        while True:
            token = self.peek()
            
            # Stop at 也
            if token.type == TokenType.KEYWORD and token.value == '也':
                break
            
            # Collect identifiers, variables, and even some keywords that might be part of names
            if token.type == TokenType.IDENTIFIER:
                supertype_parts.append(self.advance().value)
            elif token.type == TokenType.VARIABLE:
                supertype_parts.append(self.advance().value)
                supertype_is_var = True
            elif token.type == TokenType.KEYWORD:
                # Some keywords like 動 might be part of identifier names
                supertype_parts.append(self.advance().value)
            else:
                break
        
        if not supertype_parts:
            token = self.peek()
            raise ParseError(
                f"Expected identifier or variable for supertype at line {token.line}, "
                f"column {token.column}"
            )
        
        supertype = ''.join(supertype_parts)
        
        # Expect 也
        self.expect(TokenType.KEYWORD, '也')
        
        return ClassificationEdge(
            subtype=subtype,
            subtype_is_var=subtype_is_var,
            supertype=supertype,
            supertype_is_var=supertype_is_var
        )

    def parse_expression(self):
        """
        Parse an expression (proposition, SVO clause, or classification edge).
        
        Returns:
            Proposition, SVOClause, or ClassificationEdge AST node
            
        Raises:
            ParseError: If syntax is invalid
        """
        token = self.peek()
        
        # Check for proposition (曰P)
        if token.type == TokenType.KEYWORD and token.value == '曰':
            return self.parse_proposition()
        
        # Otherwise, it's either an SVO clause or classification edge
        # We need to look ahead to determine which
        if token.type not in (TokenType.IDENTIFIER, TokenType.VARIABLE):
            raise ParseError(
                f"Expected identifier or variable at line {token.line}, column {token.column}"
            )
        
        first_token = self.advance()
        
        # Look ahead to see what follows
        next_token = self.peek()
        
        # If followed by 者, it's a classification edge
        if next_token.type == TokenType.KEYWORD and next_token.value == '者':
            return self.parse_classification_edge(first_token)
        
        # Check if the identifier contains a declared verb - if so, parse as SVO
        contains_verb = any(verb in first_token.value for verb in self.verb_lexicon)
        
        # If followed by statement boundary and doesn't contain a verb, treat as simple proposition
        if not contains_verb:
            if next_token.type in (TokenType.NEWLINE, TokenType.EOF):
                return Proposition(identifier=first_token.value, is_variable=first_token.type == TokenType.VARIABLE)
            
            if next_token.type == TokenType.KEYWORD and next_token.value in ('乎', '則', '且'):
                return Proposition(identifier=first_token.value, is_variable=first_token.type == TokenType.VARIABLE)
        
        # Otherwise, try to parse as SVO clause
        return self.parse_svo_clause(first_token)
    
    def parse_rule(self) -> Rule:
        """
        Parse a rule: 若...則... with optional 且 for multiple premises
        
        Returns:
            Rule AST node
            
        Raises:
            ParseError: If syntax is invalid
        """
        self.expect(TokenType.KEYWORD, '若')
        
        # Parse premises
        premises = []
        
        # Parse first premise
        premises.append(self.parse_expression())
        
        # Parse additional premises with 且
        while True:
            token = self.peek()
            if token.type == TokenType.KEYWORD and token.value == '且':
                self.advance()  # consume 且
                premises.append(self.parse_expression())
            else:
                break
        
        # Expect 則
        self.expect(TokenType.KEYWORD, '則')
        
        # Parse conclusion
        conclusion = self.parse_expression()
        
        return Rule(premises=premises, conclusion=conclusion)

    def parse_query(self) -> Query:
        """
        Parse a query: 問E乎
        
        Returns:
            Query AST node
            
        Raises:
            ParseError: If syntax is invalid
        """
        self.expect(TokenType.KEYWORD, '問')
        
        # Parse the expression
        expression = self.parse_expression()
        
        # Expect 乎
        self.expect(TokenType.KEYWORD, '乎')
        
        return Query(expression=expression)

    def parse_statement(self):
        """
        Parse a single statement.
        
        Returns:
            AST node for the statement
            
        Raises:
            ParseError: If syntax is invalid
        """
        # Skip INDENT and NEWLINE tokens
        while self.peek().type in (TokenType.INDENT, TokenType.NEWLINE):
            self.advance()
        
        token = self.peek()
        
        # Check for EOF
        if token.type == TokenType.EOF:
            return None
        
        # Dispatch based on first keyword
        if token.type == TokenType.KEYWORD:
            if token.value == '以':
                return self.parse_verb_declaration()
            elif token.value == '曰':
                return self.parse_proposition()
            elif token.value == '若':
                return self.parse_rule()
            elif token.value == '問':
                return self.parse_query()
            else:
                raise ParseError(
                    f"Unexpected keyword '{token.value}' at line {token.line}, column {token.column}"
                )
        
        # If it starts with identifier/variable, it's either SVO or classification
        elif token.type in (TokenType.IDENTIFIER, TokenType.VARIABLE):
            first_token = self.advance()
            
            # Look ahead to determine type
            next_token = self.peek()
            if next_token.type == TokenType.KEYWORD and next_token.value == '者':
                return self.parse_classification_edge(first_token)
            else:
                return self.parse_svo_clause(first_token)
        
        else:
            raise ParseError(
                f"Unexpected token '{token.value}' at line {token.line}, column {token.column}"
            )
    
    def parse_program_internal(self) -> list:
        """
        Parse a complete program.
        
        Returns:
            List of AST nodes
        """
        statements = []
        
        while True:
            statement = self.parse_statement()
            if statement is None:
                break
            statements.append(statement)
            
            # Skip trailing newlines
            while self.peek().type == TokenType.NEWLINE:
                self.advance()
        
        return statements


def parse_program(source: str) -> list:
    """
    Parse an Ink program into an AST.
    
    Args:
        source: The source code string
        
    Returns:
        List of AST nodes representing statements
        
    Raises:
        ParseError: If syntax is invalid
    """
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse_program_internal()
