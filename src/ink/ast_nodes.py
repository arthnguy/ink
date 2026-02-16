from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Proposition:
    """Represents an atomic proposition: 曰P"""
    identifier: str
    is_variable: bool


@dataclass(frozen=True)
class SVOClause:
    """Represents a Subject-Verb-Object clause"""
    subject: str
    subject_is_var: bool
    verb: str
    verb_is_var: bool
    object: str
    object_is_var: bool


@dataclass(frozen=True)
class ClassificationEdge:
    """Represents a classification edge: X者Y也 (X is-a Y)"""
    subtype: str
    subtype_is_var: bool
    supertype: str
    supertype_is_var: bool


@dataclass(frozen=True)
class Rule:
    """Represents an inference rule: 若...則..."""
    premises: list[Union[Proposition, SVOClause, ClassificationEdge]]
    conclusion: Union[Proposition, SVOClause, ClassificationEdge]
    
    def __hash__(self):
        """Custom hash to handle mutable list of premises"""
        return hash((tuple(self.premises), self.conclusion))


@dataclass(frozen=True)
class Query:
    """Represents a query: 問E乎"""
    expression: Union[Proposition, SVOClause, ClassificationEdge]


@dataclass(frozen=True)
class VerbDeclaration:
    """Represents a verb declaration: 以V為動"""
    verb: str
