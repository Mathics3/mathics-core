# -*- coding: utf-8 -*-
from .helper import check_evaluation
from mathics_scanner.errors import IncompleteSyntaxError


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


def test_context2():
    nomessage = tuple([])
    for expr, expected, lst_messages, msg in [
        (
            """BeginPackage["apackage`"];""",
            None,
            nomessage,
            "Start a context. Add it to the context path",
        ),
        (
            """Minus::usage=" usage string setted in the package for Minus";""",
            None,
            nomessage,
            "set the usage string for a protected symbol ->no error",
        ),
        (
            """Minus::mymessage=" custom message string for Minus";""",
            None,
            nomessage,
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
            nomessage,
            "set the usage string for a package variable",
        ),
        ("""B = 6;""", None, nomessage, "Set a symbol value in the package context"),
        (
            """Begin["`implementation`"];""",
            None,
            nomessage,
            "Start a context. Do not add it to the context path",
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
            nomessage,
            "set the usage string for a protected symbol ->no error",
        ),
        (
            """Plus::mymessage=" custom message string for Plus";""",
            None,
            nomessage,
            "set a custom message for a protected symbol ->no error",
        ),
        ("""A = 7;""", None, nomessage, "Set a symbol value in the context"),
        ("""X = 9;""", None, nomessage, "set the value of the package variable"),
        ("""End[];""", None, nomessage, "go back to the previous context"),
        (
            """EndPackage[];""",
            None,
            nomessage,
            "go back to the previous context. Keep the context in the contextpath",
        ),
        ("""A""", "A", nomessage, "A is not in any context of the context path. "),
        ("""B""", "6", nomessage, "B is in a context of the context path"),
        ("""X""", "9", nomessage, "X is in a context of the context path"),
        (
            """X::usage""",
            '"package variable"',
            nomessage,
            "X is in a context of the context path",
        ),
        (
            """apackage`implementation`A""",
            "7",
            nomessage,
            "get A using its fully qualified name",
        ),
        ("""apackage`B""", "6", nomessage, "get B using its fully qualified name"),
        (
            """Plus::usage""",
            ' " usage string setted in the package for Plus" ',
            nomessage,
            "custom usage for Plus",
        ),
        (
            """Minus::usage""",
            '" usage string setted in the package for Minus"',
            nomessage,
            "custom usage for Minus",
        ),
        (
            """Plus::mymessage""",
            '" custom message string for Plus"',
            nomessage,
            "custom message for Plus",
        ),
        (
            """Minus::mymessage""",
            '" custom message string for Minus"',
            nomessage,
            "custom message for Minus",
        ),
    ]:

        if expected is None:
            expected = "System`Null"
        check_evaluation(
            expr,
            expected,
            failure_message=msg,
            to_string_expr=False,
            to_string_expected=False,
            expected_messages=lst_messages,
            hold_expected=True,
        )
