# -*- coding: utf-8 -*-
"""
Basic tests for the MathicsSession class.

"""


from mathics.core.atoms import Integer1, Integer2, IntegerM1
from mathics.core.evaluation import Result
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolNull
from mathics.core.systemsymbols import SymbolDirectedInfinity, SymbolPower, SymbolTimes
from mathics.session import MathicsSession

session = MathicsSession()


def test_session_evaluation():
    """Some basic tests"""
    session.reset()
    assert session.evaluate("(**)") is SymbolNull
    assert session.evaluate("1/0").sameQ(Expression(SymbolDirectedInfinity))
    out = session.evaluation.out
    assert (
        len(session.evaluation.out) == 1
        and out[0].text == "Infinite expression 1 / 0 encountered."
    )
    assert session.evaluate("F[x]").sameQ(
        Expression(Symbol("Global`F"), Symbol("Global`x"))
    )
    assert len(session.evaluation.out) == 0
    assert session.evaluate("$Line") is Symbol("$Line")


def test_session_evaluation_as_in_cli():
    # `evaluation_as_in_cli` returns a `Result` object
    session.reset()
    assert session.evaluate("$Line") is Symbol("$Line")
    result = session.evaluate_as_in_cli('Print["Hola"]')
    assert isinstance(result, Result)
    assert len(result.out) == 1 and result.out[0].text == "Hola"
    # Use session.evaluate(...) does not modify the `$Line` or
    # `Out` definitions, while `evaluate_as_in_cli` does:
    assert session.evaluate("$Line") is Integer1
    assert session.evaluate_as_in_cli("$Line", form="unformatted").result == Integer2
    assert session.evaluate("Out[1]") is SymbolNull
    assert session.evaluate_as_in_cli("Out[1]").result is None
    session.reset()
    assert session.evaluate("$Line") is Symbol("$Line")


def test_session_format_evaluation():
    result = session.evaluate("a/b")
    assert session.format_result(form="unformatted").sameQ(result)
    assert session.format_result(form="text") == "a / b"
    assert session.format_result(form="latex") == "\\frac{a}{b}"
    assert session.format_result(form="xml") == (
        '<math display="block"><mfrac>' "<mi>a</mi> <mi>b</mi>" "</mfrac></math>"
    )


def test_session_parse():
    parsed = session.parse("a/b")
    expected = Expression(
        SymbolTimes,
        Symbol("Global`a"),
        Expression(SymbolPower, Symbol("Global`b"), IntegerM1),
    )
    print("parsed:", parsed)
    print("expected:", expected)
    assert parsed.sameQ(expected)


if __name__ == "__main__":
    test_session_evaluation()
    test_session_evaluation_as_in_cli()
    test_session_format_evaluation()
    test_session_parse()
