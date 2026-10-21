# -*- coding: utf-8 -*-

from mathics_scanner.location import ContainerKind

from mathics.core.parser import MathicsSingleLineFeeder
from mathics.core.parser.convert import convert
from mathics.core.parser.parser import Parser
from mathics.session import MathicsSession

session = MathicsSession(add_builtin=False, catch_interrupt=True)
parser = Parser()


def test_elements_properties():
    """
    Tests that properties regarding elements of a (compound) Expression
    coming out of initial conversion are set accurately.
    """

    for str_expression, full_eval, is_flat, is_ordered in [
        # fmt: off
        # expr          fully evaluated?  flat?  ordered?
        ("Plus[1, 1, 1]",          True,  True,  True),
        ("List[]",                 True,  True,  True),
        ('List["a", "a", "b"]',    True,  True,  True),
        ('List["b", "a", "a"]',    True,  True,  False),

        ('List["a", 2, 3]',        True,  True,  False),
        ("Plus[1, 2, 3]",          True,  True,  True),
        ("Plus[x]",                False, True,  True),
        ("Plus[Plus[x]]",          False, False, True),
        ("Plus[x, y]",             False, True,  True),

        ("Plus[Plus[x], Plus[x]]", False, False, True),

        ("Plus[Plus[y], Plus[x]]", False, False, False),

        # Is sorted is true here since we have the same symbol repeated
        ('List[a, a, a]',          False,  True,  True),

        ('Plus["x", Plus["x"]]',   False, False, True),
    ]:
        # fmt: on
        session.evaluation.out.clear()
        feeder = MathicsSingleLineFeeder(
            str_expression, "<test_elements_properties>", ContainerKind.STRING
        )
        ast = parser.parse(feeder)

        # convert() creates the initial Expression. In that various properties should
        # be set.
        expr = convert(ast, session.definitions)
        expr._build_elements_properties()
        # print("XXX", str_expression, expr)
        assert (
            expr.elements_properties.elements_fully_evaluated == full_eval
        ), str_expression
        assert expr.elements_properties.is_ordered == is_ordered, str_expression
        assert expr.elements_properties.is_flat == is_flat, str_expression


def test_is_uniform_after_conversion():
    """
    is_uniform, as set by the initial conversion, must be False when the
    elements have different lookup names: only the first element of a uniform
    expression is searched for upvalues.
    """
    for str_expression, is_uniform in [
        # fmt: off
        ("F[1, 2]",        True),
        ("F[x, x]",        True),
        ("F[g[1], g[2]]",  True),
        ("F[1, y]",        False),
        ("F[w, z]",        False),
        ("F[A[2], Y[2]]",  False),
        # fmt: on
    ]:
        feeder = MathicsSingleLineFeeder(
            str_expression, "<test_is_uniform>", ContainerKind.STRING
        )
        expr = convert(parser.parse(feeder), session.definitions)
        assert expr.elements_properties.is_uniform == is_uniform, str_expression


def test_evaluation_keeps_unchanged_expression():
    """
    Evaluating an expression that does not change gives back the same object,
    with its cache renewed. A rule kept in a list built by Join is then not
    evaluated again on every use of the list.
    """
    from mathics.core.expression import Expression

    full_session = MathicsSession()
    full_session.evaluate(
        "rules = Join[{}, {g[k_Integer] :> k + 1, h[k_] -> k}]; Table[k, {k, 2}];"
    )
    stored = (
        full_session.definitions.get_definition("Global`rules")
        .get_values_list("ownvalues")[0]
        .replace
    )
    evaluation = full_session.evaluation
    for rule in stored.elements:
        assert isinstance(rule, Expression)
        # `k` changed after the rule was evaluated: the rule must be evaluated again,
        assert rule.is_uncertain_final_definitions(full_session.definitions)
        # and that gives back the very same rule, now known to be evaluated.
        assert rule.evaluate(evaluation) is rule, rule
        assert not rule.is_uncertain_final_definitions(full_session.definitions)


def test_evaluation_with_evaluate_in_held_first_element():
    """
    An expression whose only change is an Evaluate in a held first element
    is not the unchanged expression.
    """
    full_session = MathicsSession()
    result = full_session.evaluate(
        "SetAttributes[hf, HoldFirst]; hf[Evaluate[1 + 1], 5]"
    )
    assert result.sameQ(full_session.evaluate("Hold[hf[2, 5]]").elements[0]), result
