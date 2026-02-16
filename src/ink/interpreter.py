from ink.ast_nodes import Proposition, SVOClause, ClassificationEdge


from dataclasses import dataclass
from ink.ast_nodes import Proposition, SVOClause, ClassificationEdge, Rule
@dataclass
class Context:
    """
    Evaluation context for the Ink interpreter.

    Attributes:
        facts: Set of all known facts (propositions, SVO clauses, classification edges)
        classification_edges: Subset of facts that are classification edges
        rules: List of rules to apply during fixpoint computation
        verb_lexicon: Set of declared verbs
    """
    facts: set
    classification_edges: set
    rules: list
    verb_lexicon: set
def apply_substitution(node, subst: dict[str, str]):
    """
    Apply variable substitutions to an AST node.
    
    Args:
        node: AST node with possible variables (Proposition, SVOClause, or ClassificationEdge)
        subst: Variable substitutions mapping variable names to concrete identifiers
        
    Returns:
        New AST node with variables replaced by their bindings
    """
    if isinstance(node, Proposition):
        if node.is_variable and node.identifier in subst:
            # Replace variable with its binding (now concrete)
            return Proposition(subst[node.identifier], False)
        return node
    
    elif isinstance(node, SVOClause):
        # Apply substitution to each component
        subject = subst[node.subject] if node.subject_is_var and node.subject in subst else node.subject
        subject_is_var = node.subject_is_var and node.subject not in subst
        
        verb = subst[node.verb] if node.verb_is_var and node.verb in subst else node.verb
        verb_is_var = node.verb_is_var and node.verb not in subst
        
        obj = subst[node.object] if node.object_is_var and node.object in subst else node.object
        object_is_var = node.object_is_var and node.object not in subst
        
        return SVOClause(subject, subject_is_var, verb, verb_is_var, obj, object_is_var)
    
    elif isinstance(node, ClassificationEdge):
        # Apply substitution to subtype and supertype
        subtype = subst[node.subtype] if node.subtype_is_var and node.subtype in subst else node.subtype
        subtype_is_var = node.subtype_is_var and node.subtype not in subst
        
        supertype = subst[node.supertype] if node.supertype_is_var and node.supertype in subst else node.supertype
        supertype_is_var = node.supertype_is_var and node.supertype not in subst
        
        return ClassificationEdge(subtype, subtype_is_var, supertype, supertype_is_var)
    
    else:
        raise TypeError(f"Unsupported node type for substitution: {type(node)}")



def unify(pattern, fact, subst: dict[str, str]) -> dict[str, str] | None:
    """
    Unify a pattern (possibly with variables) against a fact.
    
    Args:
        pattern: AST node with possible variables
        fact: Concrete AST node from context
        subst: Existing variable substitutions
        
    Returns:
        Updated substitution dict if unification succeeds, None otherwise
    """
    # Apply existing substitutions to both pattern and fact before unifying
    pattern = apply_substitution(pattern, subst)
    fact = apply_substitution(fact, subst)
    
    # Type mismatch - cannot unify
    if type(pattern) != type(fact):
        return None
    
    if isinstance(pattern, Proposition):
        return _unify_proposition(pattern, fact, subst)
    elif isinstance(pattern, SVOClause):
        return _unify_svo_clause(pattern, fact, subst)
    elif isinstance(pattern, ClassificationEdge):
        return _unify_classification_edge(pattern, fact, subst)
    else:
        raise TypeError(f"Unsupported node type for unification: {type(pattern)}")


def _unify_proposition(pattern: Proposition, fact: Proposition, subst: dict[str, str]) -> dict[str, str] | None:
    """
    Unify two propositions.
    
    Args:
        pattern: Proposition pattern (may contain variables)
        fact: Concrete proposition
        subst: Existing substitutions
        
    Returns:
        Updated substitution or None if unification fails
    """
    # If pattern is a variable, bind it to the fact's identifier
    if pattern.is_variable:
        # Check if variable is already bound
        if pattern.identifier in subst:
            # Variable already bound - check consistency
            if subst[pattern.identifier] == fact.identifier:
                return subst
            else:
                return None
        else:
            # Bind the variable
            new_subst = subst.copy()
            new_subst[pattern.identifier] = fact.identifier
            return new_subst
    
    # If fact is a variable (shouldn't happen in normal usage, but handle it)
    if fact.is_variable:
        if fact.identifier in subst:
            if subst[fact.identifier] == pattern.identifier:
                return subst
            else:
                return None
        else:
            new_subst = subst.copy()
            new_subst[fact.identifier] = pattern.identifier
            return new_subst
    
    # Both are concrete - check if they match
    if pattern.identifier == fact.identifier:
        return subst  # Empty substitution (no new bindings)
    else:
        return None  # Mismatch



def _unify_svo_clause(pattern: SVOClause, fact: SVOClause, subst: dict[str, str]) -> dict[str, str] | None:
    """
    Unify two SVO clauses by unifying subject, verb, and object independently.
    
    Args:
        pattern: SVO clause pattern (may contain variables)
        fact: Concrete SVO clause
        subst: Existing substitutions
        
    Returns:
        Combined substitution or None if any component fails to unify
    """
    # Unify subject
    subject_pattern = Proposition(pattern.subject, pattern.subject_is_var)
    subject_fact = Proposition(fact.subject, fact.subject_is_var)
    subst = _unify_proposition(subject_pattern, subject_fact, subst)
    if subst is None:
        return None
    
    # Unify verb (thread substitution from subject)
    verb_pattern = Proposition(pattern.verb, pattern.verb_is_var)
    verb_fact = Proposition(fact.verb, fact.verb_is_var)
    subst = _unify_proposition(verb_pattern, verb_fact, subst)
    if subst is None:
        return None
    
    # Unify object (thread substitution from subject and verb)
    object_pattern = Proposition(pattern.object, pattern.object_is_var)
    object_fact = Proposition(fact.object, fact.object_is_var)
    subst = _unify_proposition(object_pattern, object_fact, subst)
    if subst is None:
        return None
    
    return subst



def _unify_classification_edge(pattern: ClassificationEdge, fact: ClassificationEdge, subst: dict[str, str]) -> dict[str, str] | None:
    """
    Unify two classification edges by unifying subtype and supertype independently.
    
    Args:
        pattern: Classification edge pattern (may contain variables)
        fact: Concrete classification edge
        subst: Existing substitutions
        
    Returns:
        Combined substitution or None if any component fails to unify
    """
    # Unify subtype
    subtype_pattern = Proposition(pattern.subtype, pattern.subtype_is_var)
    subtype_fact = Proposition(fact.subtype, fact.subtype_is_var)
    subst = _unify_proposition(subtype_pattern, subtype_fact, subst)
    if subst is None:
        return None
    
    # Unify supertype (thread substitution from subtype)
    supertype_pattern = Proposition(pattern.supertype, pattern.supertype_is_var)
    supertype_fact = Proposition(fact.supertype, fact.supertype_is_var)
    subst = _unify_proposition(supertype_pattern, supertype_fact, subst)
    if subst is None:
        return None
    
    return subst


def compute_classification_closure(edges: set[ClassificationEdge]) -> set[ClassificationEdge]:
    """
    Compute transitive closure of classification edges.
    
    This function iteratively adds transitive edges until no new edges can be derived.
    For example, if A⊑B and B⊑C exist, it will add A⊑C.
    
    Args:
        edges: Set of classification edges
        
    Returns:
        Set including original edges and derived transitive edges
    """
    # Start with all input edges
    closure = set(edges)
    
    # Keep adding transitive edges until no new edges are found
    changed = True
    while changed:
        changed = False
        new_edges = set()
        
        # For each pair of edges, check if we can derive a transitive edge
        for edge1 in closure:
            for edge2 in closure:
                # If edge1 is A⊑B and edge2 is B⊑C (where B matches)
                # Then we can derive A⊑C
                # Only works with concrete (non-variable) edges
                if (not edge1.supertype_is_var and 
                    not edge2.subtype_is_var and 
                    edge1.supertype == edge2.subtype):
                    
                    # Create the transitive edge A⊑C
                    new_edge = ClassificationEdge(
                        edge1.subtype,
                        edge1.subtype_is_var,
                        edge2.supertype,
                        edge2.supertype_is_var
                    )
                    
                    # Add it if it's not already in the closure
                    if new_edge not in closure:
                        new_edges.add(new_edge)
                        changed = True
        
        # Add all new edges to the closure
        closure.update(new_edges)
    
    return closure


def apply_rule(rule: Rule, context: Context) -> set:
    """
    Apply a rule to derive new facts.
    
    This function tries to unify all premises of the rule with facts in the context.
    For each successful unification (substitution), it applies the substitution to
    the conclusion to derive a new fact.
    
    Args:
        rule: Rule to apply
        context: Current evaluation context with facts
        
    Returns:
        Set of newly derived facts (may be empty if rule doesn't fire)
    """
    from itertools import product
    
    # Collect all facts that could match each premise
    # For each premise, find all facts that could unify with it
    premise_matches = []
    for premise in rule.premises:
        matches = []
        for fact in context.facts:
            # Try to unify premise with fact
            subst = unify(premise, fact, {})
            if subst is not None:
                matches.append((fact, subst))
        premise_matches.append(matches)
    
    # If any premise has no matches, the rule cannot fire
    if any(len(matches) == 0 for matches in premise_matches):
        return set()
    
    # Generate all combinations of fact matches across premises
    # Each combination represents a potential way to satisfy all premises
    derived_facts = set()
    
    for combination in product(*premise_matches):
        # Try to combine substitutions from all premises
        combined_subst = {}
        valid = True
        
        for fact, subst in combination:
            # Try to merge this substitution with the combined one
            for var, value in subst.items():
                if var in combined_subst:
                    # Variable already bound - check consistency
                    if combined_subst[var] != value:
                        valid = False
                        break
                else:
                    combined_subst[var] = value
            
            if not valid:
                break
        
        # If we have a valid combined substitution, apply it to the conclusion
        if valid:
            derived_fact = apply_substitution(rule.conclusion, combined_subst)
            # Only add if it's not already in the context (deduplication)
            if derived_fact not in context.facts:
                derived_facts.add(derived_fact)
    
    return derived_facts


def fixpoint(context: Context) -> Context:
    """
    Compute least fixpoint by iteratively applying rules.
    
    This function repeatedly:
    1. Computes the classification closure
    2. Applies all rules to derive new facts
    3. Adds new facts to the context
    
    The process terminates when no new facts can be derived (fixpoint reached).
    
    Args:
        context: Initial context with asserted facts and rules
        
    Returns:
        Final context with all derivable facts
    """
    # Iteratively apply rules until no new facts are derived
    while True:
        # Compute classification closure before applying rules
        # This ensures derived classification edges are available for rule matching
        closed_edges = compute_classification_closure(context.classification_edges)
        
        # Update context with closed classification edges
        # Remove old classification edges and add closed ones
        non_classification_facts = {f for f in context.facts if not isinstance(f, ClassificationEdge)}
        context.facts = non_classification_facts | closed_edges
        context.classification_edges = closed_edges
        
        # Apply all rules and collect newly derived facts
        new_facts = set()
        for rule in context.rules:
            derived = apply_rule(rule, context)
            new_facts.update(derived)
        
        # If no new facts were derived, we've reached fixpoint
        if len(new_facts) == 0:
            break
        
        # Add new facts to context
        context.facts.update(new_facts)
        
        # Update classification_edges if any new facts are classification edges
        for fact in new_facts:
            if isinstance(fact, ClassificationEdge):
                context.classification_edges.add(fact)
    
    return context


def evaluate_query(query, context: Context) -> str:
    """
    Evaluate a query against the final context.
    
    Tries to unify the query expression with each fact in the context.
    Returns ⊤ if any unification succeeds, ? otherwise.
    
    Args:
        query: Query AST node with expression to evaluate
        context: Final context after fixpoint computation
        
    Returns:
        "⊤" if query succeeds (expression unifies with any fact)
        "?" if query fails (expression doesn't unify with any fact)
    """
    from ink.ast_nodes import Query
    
    # Extract the expression from the query
    if isinstance(query, Query):
        expression = query.expression
    else:
        expression = query
    
    # Try to unify the query expression with each fact in the context
    for fact in context.facts:
        # Try unification with empty initial substitution
        result = unify(expression, fact, {})
        if result is not None:
            # Unification succeeded - query is derivable
            return "⊤"
    
    # No fact unified with the query - query is not derivable
    return "?"


def eval_program(ast: list) -> None:
    """
    Evaluate an Ink program and output query results.

    This function orchestrates the entire evaluation process:
    1. Separates statements into verb declarations, assertions, rules, and queries
    2. Processes verb declarations first
    3. Initializes context with assertions and rules
    4. Computes fixpoint to derive all facts
    5. Evaluates queries and prints results

    Args:
        ast: List of AST nodes from parser

    Side Effects:
        Prints query results to stdout

    Raises:
        RuntimeError: If a runtime error occurs during evaluation
    """
    from ink.ast_nodes import VerbDeclaration, Query, Rule

    try:
        # Separate statements by type
        verb_declarations = []
        assertions = []  # Propositions, SVOClauses, ClassificationEdges
        rules = []
        queries = []

        for node in ast:
            if isinstance(node, VerbDeclaration):
                verb_declarations.append(node)
            elif isinstance(node, Query):
                queries.append(node)
            elif isinstance(node, Rule):
                rules.append(node)
            else:
                # Proposition, SVOClause, or ClassificationEdge
                assertions.append(node)

        # Process verb declarations first (build verb lexicon)
        verb_lexicon = set()
        for verb_decl in verb_declarations:
            verb_lexicon.add(verb_decl.verb)

        # Initialize context with assertions and rules
        facts = set(assertions)
        classification_edges = {f for f in facts if isinstance(f, ClassificationEdge)}

        context = Context(
            facts=facts,
            classification_edges=classification_edges,
            rules=rules,
            verb_lexicon=verb_lexicon
        )

        # Compute fixpoint to derive all facts
        final_context = fixpoint(context)

        # Evaluate queries and print results
        for query in queries:
            result = evaluate_query(query, final_context)
            print(result)

    except Exception as e:
        # Catch and re-raise as RuntimeError with context
        raise RuntimeError(f"Runtime error during program evaluation: {e}") from e

