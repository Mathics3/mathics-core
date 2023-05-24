# -*- coding: utf-8 -*-
import pytest
from mathics_scanner.errors import IncompleteSyntaxError

from .helper import check_evaluation, reset_session

str_test_context_1 = """
BeginPackage["FeynCalc`"];

AppendTo[$ContextPath, "FeynCalc`Package`"];

Begin["`Package`"];(*Symbols to be shared between subpackages*)
sharedSymbol;
End[];


foo::usage = "";
bar::usage = "";(*-----------------------------------------*)

Begin["`MySubpackageA`Private`"];
intVarA::usage = "";
foo[x_] := (
   Print["I can access sharedSymbol directly, since it is in ",
    Context[sharedSymbol], " and not in ",
    Context[intVarA]];
   sharedSymbol = x;
   x
   );
End[];(*-----------------------------------------*)

Begin["`MySubpackageB`Private`"];
intVarB::usage = "";
bar[] := (
   Print["I can access sharedSymbol directly, since it is in ",
    Context[sharedSymbol], " and not in ",
    Context[intVarB]];
   sharedSymbol
   );
End[];

EndPackage[];
"""


def test_context1():
    expr = ""
    for line in str_test_context_1.split("\n"):
        if line in ("", "\n"):
            continue
        expr = expr + line
        try:
            print("expr=", expr)
            check_evaluation(
                expr, "Null", to_string_expr=False, to_string_expected=False
            )
            expr = ""
            print("  OK")
        except IncompleteSyntaxError:
            continue
    check_evaluation("foo[42]", "42", to_string_expr=False, to_string_expected=False)
    check_evaluation("bar[]", "42", to_string_expr=False, to_string_expected=False)


@pytest.mark.parametrize(
    ("expr", "expected", "lst_messages", "msg"),
    [
        (
            """globalvarY = 37;""",
            None,
            None,
            "set the value of a global symbol",
        ),
        (
            """globalvarZ = 37;""",
            None,
            None,
            "set the value of a global symbol",
        ),
        (
            """BeginPackage["apackage`"];""",
            None,
            None,
            "Start a context. Add it to the context path",
        ),
        (
            """Minus::usage=" usage string setted in the package for Minus";""",
            None,
            None,
            "set the usage string for a protected symbol ->no error",
        ),
        (
            """Minus::mymessage=" custom message string for Minus";""",
            None,
            None,
            "set a custom message for a protected symbol ->no error",
        ),
        (
            """Minus = pq;""",
            None,
            tuple(
                [
                    "Symbol Minus is Protected.",
                ]
            ),
            "try to set a value for a protected symbol ->error",
        ),
        (
            """X::usage = "package variable";""",
            None,
            None,
            "set the usage string for a package variable",
        ),
        (
            """globalvarZ::usage = "a global variable";""",
            None,
            None,
            "set the usage string for a global symbol",
        ),
        (
            """globalvarZ = 57;""",
            None,
            None,
            "reset the value of a global symbol",
        ),
        ("""B = 6;""", None, None, "Set a symbol value in the package context"),
        (
            """Begin["`implementation`"];""",
            None,
            None,
            "Start a context. Do not add it to the context path",
        ),
        (
            """{Context[A], Context[B], Context[X], Context[globalvarY], Context[globalvarZ]}""",
            """{"apackage`implementation`", "apackage`", "apackage`", "apackage`implementation`", "apackage`"}""",
            None,
            None,  # "context of the variables"
        ),
        (
            """globalvarY::usage = "a global variable";""",
            None,
            None,
            "set the usage string for a global symbol",
        ),
        (
            """globalvarY = 97;""",
            None,
            None,
            "reset the value of a global symbol",
        ),
        (
            """Plus = PP;""",
            None,
            tuple(
                [
                    "Symbol Plus is Protected.",
                ]
            ),
            "try to set a value for a protected symbol ->error",
        ),
        (
            """Plus::usage=" usage string setted in the package for Plus";""",
            None,
            None,
            "set the usage string for a protected symbol ->no error",
        ),
        (
            """Plus::mymessage=" custom message string for Plus";""",
            None,
            None,
            "set a custom message for a protected symbol ->no error",
        ),
        ("""A = 7;""", None, None, "Set a symbol value in the context"),
        ("""X = 9;""", None, None, "set the value of the package variable"),
        ("""End[];""", None, None, "go back to the previous context"),
        (
            """{Context[A], Context[B], Context[X], Context[globalvarY], Context[globalvarZ]}""",
            """{"apackage`", "apackage`", "apackage`", "apackage`", "apackage`"}""",
            None,
            None,  # "context of the variables in the package"
        ),
        (
            """EndPackage[];""",
            None,
            None,
            "go back to the previous context. Keep the context in the contextpath",
        ),
        (
            """{Context[A], Context[B], Context[X], Context[globalvarY], Context[globalvarZ]}""",
            """{"apackage`", "apackage`", "apackage`", "apackage`", "apackage`"}""",
            None,
            None,  # "context of the variables at global level"
        ),
        ("""A""", "A", None, "A is not in any context of the context path. "),
        ("""B""", "6", None, "B is in a context of the context path"),
        ("""Global`globalvarY""", "37", None, ""),
        (
            """Global`globalvarY::usage""",
            "Global`globalvarY::usage",
            None,
            "In WMA, the value would be set in the package",
        ),
        ("""Global`globalvarZ""", "37", None, "the value set inside the package"),
        (
            """Global`globalvarZ::usage""",
            "Global`globalvarZ::usage",
            None,
            "not affected by the package",
        ),
        ("""globalvarY""", "apackage`globalvarY", None, ""),
        (
            """globalvarY::usage""",
            "apackage`globalvarY::usage",
            None,
            "In WMA, the value would be set in the package",
        ),
        ("""globalvarZ""", "57", None, "the value set inside the package"),
        (
            """globalvarZ::usage""",
            '"a global variable"',
            None,
            "not affected by the package",
        ),
        ("""X""", "9", None, "X is in a context of the context path"),
        (
            """X::usage""",
            '"package variable"',
            None,
            "X is in a context of the context path",
        ),
        (
            """apackage`implementation`A""",
            "7",
            None,
            "get A using its fully qualified name",
        ),
        ("""apackage`B""", "6", None, "get B using its fully qualified name"),
        (
            """Plus::usage""",
            ' " usage string setted in the package for Plus" ',
            None,
            "custom usage for Plus",
        ),
        (
            """Minus::usage""",
            '" usage string setted in the package for Minus"',
            None,
            "custom usage for Minus",
        ),
        (
            """Plus::mymessage""",
            '" custom message string for Plus"',
            None,
            "custom message for Plus",
        ),
        (
            """Minus::mymessage""",
            '" custom message string for Minus"',
            None,
            "custom message for Minus",
        ),
        (None, None, None, None),
    ],
)
def test_context2(expr, expected, lst_messages, msg):
    if expr is not None and expected is None:
        expected = "System`Null"

    if lst_messages is None:
        lst_messages = tuple([])
    check_evaluation(
        expr,
        expected,
        failure_message=msg,
        to_string_expr=False,
        to_string_expected=False,
        expected_messages=lst_messages,
        hold_expected=True,
    )
