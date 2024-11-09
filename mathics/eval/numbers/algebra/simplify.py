# -*- coding: utf-8 -*-

"""
Algorithms for simplifying expressions and evaluate complexity.
"""

from sympy import simplify

from mathics.core.atoms import Number
from mathics.core.convert.sympy import from_sympy
from mathics.core.expression import Expression
from mathics.core.symbols import Atom, Symbol, SymbolFalse, SymbolList, SymbolTrue
from mathics.core.systemsymbols import SymbolAutomatic
from mathics.eval.inference import evaluate_predicate


def default_complexity_function(expr: Expression) -> int:
    """
    Evaluates the complexity of an expression. Each atom
    counts 1, except for numbers that counts 1 each 5 characters
    in its decimal expansion.
    """
    # TODO: write this in an iterative form instead a recursive one.
    if isinstance(expr, Number):
        # This can be improved in several ways...
        return int(len(str(expr).strip())) + 1
    elif isinstance(expr, Expression):
        return default_complexity_function(expr.get_head()) + +sum(
            default_complexity_function(e) for e in expr.elements
        )
    else:
        return 1


def eval_Simplify(symbol_name: Symbol, expr, evaluation, options: dict):
    # Check first if we are dealing with a logic expression...
    if expr in (SymbolTrue, SymbolFalse, SymbolList):
        return expr

    # ``evaluate_predicate`` tries to reduce expr taking into account
    # the assumptions established in ``$Assumptions``.
    expr = evaluate_predicate(expr, evaluation)

    # If we get an atom, return it.
    if isinstance(expr, Atom):
        return expr

    # Now, try to simplify the elements.
    # TODO:  Consider to move this step inside ``evaluate_predicate``.
    # Notice that here we want to pass through the full evaluation process
    # to use all the defined rules...
    elements = [
        Expression(symbol_name, element).evaluate(evaluation)
        for element in expr._elements
    ]
    head = Expression(symbol_name, expr.get_head()).evaluate(evaluation)
    expr = Expression(head, *elements)

    # At this point, we used all the tools available in Mathics.
    # If the expression has a sympy form, try to use it.
    # Now, convert the expression to sympy
    sympy_expr = expr.to_sympy()
    # If the expression cannot be handled by Sympy, just return it.
    if sympy_expr is None:
        return expr
    # Now, try to simplify using sympy
    complexity_function = options.get("System`ComplexityFunction", None)
    if complexity_function is None or complexity_function is SymbolAutomatic:

        def _default_complexity_function(x):
            return default_complexity_function(from_sympy(x))

        complexity_function = _default_complexity_function
    else:
        if isinstance(complexity_function, (Expression, Symbol)):
            _complexity_function = complexity_function
            complexity_function = (
                lambda x: Expression(_complexity_function, from_sympy(x))
                .evaluate(evaluation)
                .to_python()
            )

    try:
        # At this point, ``complexity_function`` is a function that takes a
        # sympy expression and returns an integer.
        sympy_result = simplify(sympy_expr, measure=complexity_function, doit=False)
        sympy_result = sympy_result.doit(roots=False)  # Don't expand RootSum
        # and bring it back
        result = from_sympy(sympy_result).evaluate(evaluation)
    except ValueError:
        return expr
    return result
