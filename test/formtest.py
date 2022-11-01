"""
Example to show how new Format-directed Boxing might work.

This is a minimal example so we can discuss feasiblity.
"""
from mathics.builtin.forms.base import box
from mathics.core.atoms import IntegerM1, Integer1, Integer2, Rational
from mathics.core.expression import Expression
from mathics.core.parser import parse, MathicsSingleLineFeeder
from mathics.core.symbols import SymbolDivide
from mathics.core.systemsymbols import (
    SymbolFractionBox,
    SymbolMakeBoxes,
    SymbolPower,
    SymbolSqrt,
    SymbolStandardForm,
)
from mathics.session import MathicsSession

session = MathicsSession(character_encoding="ASCII")


# Hacky pseudo boxing rules.
# Currently in MakeBox rule rewriting occurs via MakeBox rewrite rules
# which are attached to various Builtin classes.

# The rewrite is performed as a part of rewriting portion of Expression evaluation.
# We probably want to segregate these rules from other kinds of rules.
#
# The below hacky code is to simulate the rule behavior for
# just a few kinds of things so we don't have to hook into the
# complex rewrite mechanism in use in general evaluation. The implementation we use
# is just good enough for the new kinds of things we need.
# It is not intended to be used in a final implementation.


def fractionbox_fn(expr):
    # To be continued...
    return Expression(SymbolFractionBox, *expr.elements)


def sqrtbox_fn(expr):
    return Expression(SymbolSqrt, expr.elements[0])


def powerbox_fn(expr):
    new_expr = expr.elements[0]
    if new_expr.elements[-1] == IntegerM1:
        return Expression(SymbolDivide, Integer1, new_expr.elements[0])
    elif new_expr.elements[-1] in (Rational(1, 2), Integer1 * (Integer2**IntegerM1)):
        return Expression(SymbolSqrt, new_expr.elements[0])
    return new_expr


boxform_rules = {
    # SymbolTimes: fractionbox_fn,
    SymbolPower: powerbox_fn,
    SymbolSqrt: sqrtbox_fn,
}


def apply_formatvalues_rules(expr, evaluation):
    """
    Hacky replacement for rules() found in Expression rewrite_apply_eval().
    Note, we need to add builtin FormatValues() and the internals that go with that.
    """
    if expr.elements[-1] not in (SymbolStandardForm,):  # Or more generally $BoxForms
        # For other forms, there might be other transformations too, and this should
        # be discussed.
        # For simplicity, we will just handle a small number of $BoxForms rules
        return expr

    # Remove the Form from expression "expr"
    unboxed_expr = expr.elements[0]

    if unboxed_expr.head in boxform_rules:
        new_expr = boxform_rules[unboxed_expr.head](expr)
        return new_expr
    return unboxed_expr


# Begin demo code.

for expr_str in (
    # FIXME;
    # "1 / x",  # Show off "Division" boxing
    "a ^ b",  # Show off "Power" boxing
    "Sqrt[a]",  # "Square-root boxing"
    "a ^ (1/2)",  # "Square-root boxing"
):
    print("expression:        ", expr_str)

    # Parse, but don't evaluate expression.
    expr = parse(session.definitions, MathicsSingleLineFeeder(expr_str))
    print("Parsed expression: ", expr)

    # Here is how Mathics currently evaluates MakeBoxes
    boxed_expr = Expression(SymbolMakeBoxes, expr, SymbolStandardForm)
    print("Mathics MakeBoxes: ", boxed_expr)

    # Evaluate to get final printed/rendered form
    print("Eval'd Makeboxes:  ", boxed_expr.evaluate(session.evaluation))

    # Here is how Mathics might better box an expression.
    # First we apply MakeBox boxing transformation rules.
    # This handles expression rewriting.
    transformed_boxed_expr = apply_formatvalues_rules(boxed_expr, session.evaluation)

    boxed_expr2 = box(transformed_boxed_expr, session.evaluation, SymbolStandardForm)
    print("New    MakeBoxes:  ", boxed_expr2)
    print("-" * 30)
    print("")
