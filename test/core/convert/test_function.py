"""
Conversion from expressions to functions
"""

from test.helper import session

from mathics.core.convert.function import evaluate_without_side_effects


def test_evaluate_without_side_effects():
    session.reset()
    session.evaluate(
        """
    F[x_]:=G[x];
    G[x_]:=(a=2^2*x;Do[a=x+2^2,{3}];a); 
    Q[x_]:=(a=2^2*x);
    """
    )
    expr = session.parse("F[x]")
    # Notice that since `CompoundExpression` has the attribute "HoldAll",
    # subelements are not evaluated (`2^2`->`2^2`)
    expect = session.parse("(a=2^2*x; Do[a=x+2^2,{3}];a)")
    result = evaluate_without_side_effects(expr, session.evaluation)
    assert result.sameQ(expect)

    expr = session.parse("Q[x]")
    # If the head of the expression does not have the attribute "HoldAll",
    # subelements are evaluated (`2^2`->`4`)
    expect = session.parse("a=4*x")
    result = evaluate_without_side_effects(expr, session.evaluation)

    assert result.sameQ(expect)
