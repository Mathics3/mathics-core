# -*- coding: utf-8 -*-
import pytest
from mathics_scanner.errors import IncompleteSyntaxError

from .helper import check_evaluation

DEFAULT_CONTEXT_PATH = '{"System`", "Global`"}'

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
            """Minus::usage=" usage string set in the package for Minus";""",
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
            """Plus::usage=" usage string set in the package for Plus";""",
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
            ' " usage string set in the package for Plus" ',
            None,
            "custom usage for Plus",
        ),
        (
            """Minus::usage""",
            '" usage string set in the package for Minus"',
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


@pytest.mark.parametrize(
    ("expr", "expected", "lst_messages", "msg"),
    [
        (None, None, None, None),
        (
            "$Packages",
            '{"ImportExport`","XML`","Internal`","System`","Global`"}',
            None,
            "initial value of $Packages",
        ),
        ("$ContextPath", DEFAULT_CONTEXT_PATH, None, "Default context path"),
        ('BeginPackage["MyPackage`", {"VectorAnalysis`"}]', '"MyPackage`"', None, None),
        (
            "$Packages",
            '{"MyPackage`","VectorAnalysis`","ImportExport`","XML`","Internal`","System`","Global`"}',
            None,
            "Now, $Package is stored as available.",
        ),
        ("$Context", '"MyPackage`"', None, None),
        (
            "$ContextPath",
            ' {"MyPackage`", "VectorAnalysis`", "System`"}',
            None,
            "Context path now include MyPackage` and it needs...",
        ),
        ('Begin["`Private`"]', '"MyPackage`Private`"', None, None),
        ("$Context", '"MyPackage`Private`"', None, None),
        ("$ContextPath", '{"MyPackage`", "VectorAnalysis`", "System`"}', None, None),
        ("End[]", '"MyPackage`Private`"', None, None),
        ("$Context", '"MyPackage`"', None, None),
        ("$ContextPath", '{"MyPackage`", "VectorAnalysis`", "System`"}', None, None),
        ("EndPackage[]", "System`Null", None, None),
        ("$Context", '"Global`"', None, None),
        (
            "$ContextPath",
            '{"MyPackage`", "VectorAnalysis`", "System`", "Global`"}',
            None,
            None,
        ),
        ("End[]", '"Global`"', ["No previous context defined."], None),
        ("EndPackage[]", "System`Null", ["No previous context defined."], None),
        (
            "$Packages",
            '{"MyPackage`","VectorAnalysis`","ImportExport`","XML`","Internal`","System`","Global`"}',
            None,
            "Now, the package name is stored.",
        ),
        (None, None, None, None),
        (
            "$Packages",
            '{"ImportExport`","XML`","Internal`","System`","Global`"}',
            None,
            "After reset, the package are not there anymore.",
        ),
    ],
)
def test_context_with_need(expr, expected, lst_messages, msg):
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


@pytest.mark.xfail
@pytest.mark.parametrize(
    ("expr", "expected", "lst_messages", "msg"),
    [
        (None, None, None, None),
        # The following two tests fail because we are not producing the message yet.
        (
            "BeginPackage[3]",
            "BeginPackage[3]",
            [
                "Invalid context specified at position 1 in `BeginPackage[3,...]`. A context must consist of valid symbol names separated by and ending with `."
            ],
            "numbers are not context names",
        ),
        (
            "BeginPackage[symb]",
            "BeginPackage[symb]",
            [
                "Invalid context specified at position 1 in `BeginPackage[symb,...]`. A context must consist of valid symbol names separated by and ending with `."
            ],
            "symbols are not context names",
        ),
        (
            'BeginPackage["P"]',
            'BeginPackage["P"]',
            [
                "Invalid context specified at position 1 in `BeginPackage[P,...]`. A context must consist of valid symbol names separated by and ending with `."
            ],
            "invalid name",
        ),
        # This test fails, because Mathics3 implementation does not check for valid context names.
        # TODO: Implement Internal`SymbolNameQ to check if a string is a valid symbol name.
        # ('BeginPackage["a+b`", "nocontext"]', 'BeginPackage["a+b`", {"nocontext"}]', ['Invalid context specified at position 1 in `BeginPackage[a+b`,...]`. A context must consist of valid symbol names separated by and ending with `.'],  "a valid context name should not have operators inside."),
        (
            'BeginPackage["P", "nocontext`"]',
            'BeginPackage["P", "nocontext`"]',
            [
                "Invalid context specified at position 1 in `BeginPackage[P,...]`. A context must consist of valid symbol names separated by and ending with `."
            ],
            "invalid name",
        ),
        (
            'BeginPackage["P`", 3]',
            'BeginPackage["P`", 3]',
            [
                "Context or non-empty list of contexts expected at position 2 in `BeginPackage[P`, 3]`"
            ],
            "numbers are not valid arguments for Needs",
        ),
        (
            'BeginPackage["P`", symb]',
            'BeginPackage["P`", symb]',
            [
                "Context or non-empty list of contexts expected at position 2 in `BeginPackage[P`, symb]`"
            ],
            "numbers are not needs",
        ),
        # The following test fails because with the current implementation, Mathics3 still
        # set the context, even if the needs field is not a valid name
        # ('BeginPackage["P`", "nocontext"]', 'BeginPackage["P`", {"nocontext"}]', ['Context or non-empty list of contexts expected at position 2 in `BeginPackage[P`, nocontext]`'], "not a valid context name in needs."),
        # The following two tests fail because we are not producing the message yet.
        (
            "Begin[3]",
            "Begin[3]",
            [
                "Invalid context specified at position 1 in `Begin[3]`. A context must consist of valid symbol names separated by and ending with `."
            ],
            "numbers are not context names",
        ),
        (
            "Begin[symb]",
            "Begin[symb]",
            [
                "Invalid context specified at position 1 in `Begin[symb,...]`. A context must consist of valid symbol names separated by and ending with `."
            ],
            "symbols are not context names",
        ),
        (
            'Begin["P"]',
            'Begin["P"]',
            [
                "Invalid context specified at position 1 in `Begin[P,...]`. A context must consist of valid symbol names separated by and ending with `."
            ],
            "invalid name",
        ),
        (
            "$Context",
            '"Global`"',
            None,
            "Any of the previous calls change the context.",
        ),
        (
            "$ContextPath",
            DEFAULT_CONTEXT_PATH,
            None,
            "Any of the previous calls change the context.",
        ),
    ],
)
def test_context_messages(expr, expected, lst_messages, msg):
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
