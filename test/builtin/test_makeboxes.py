# -*- coding: utf-8 -*-
import os
from test.helper import check_evaluation, session

import pytest
from mathics_scanner.errors import IncompleteSyntaxError

# To check the progress in the improvement of formatting routines, set this variable to 1.
# Otherwise, the tests are going to be skipped.
DEBUGMAKEBOXES = int(os.environ.get("DEBUGMAKEBOXES", "0")) == 1

if DEBUGMAKEBOXES:
    skip_or_fail = pytest.mark.xfail
else:
    skip_or_fail = pytest.mark.skip


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg", "msgs"),
    [
        ('rb=RowBox[{"a", "b"}]; rb[[1]]', "{a, b}", None, []),
        ("rb[[0]]", "RowBox", None, []),
        (
            "rb[[2]]",
            "RowBox[{a, b}][[2]]",
            None,
            ["Part 2 of RowBox[{a, b}] does not exist."],
        ),
        ('fb=FractionBox["1", "2"]; fb[[0]]', "FractionBox", None, []),
        ("fb[[1]]", "1", None, []),
        ('sb=StyleBox["string", "Section"]; sb[[0]]', "StyleBox", None, []),
        ("sb[[1]]", "string", None, []),
        # FIXME: <<RowBox object does not have the attribute "restructure">>
        # ('rb[[All, 1]]', "{a, b}", "\"a\"", []),
        # ('fb[[All]][[1]]','1', None, []),
        # ('sb[[All]][[1]]','string', None, []),
    ],
)
@skip_or_fail
def test_part_boxes(str_expr, str_expected, fail_msg, msgs):
    """
    This unit test checks that certain typical box structures
    work together with `Part`. In the current master,
    these expressions crashes the interpreter.
    """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


# 15 tests
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (r"MakeBoxes[0`3]", r"0", None),
        (r"MakeBoxes[14]", r"14", None),
    ],
)
def test_makeboxes_real(str_expr, str_expected, msg):
    """
    # Constructing boxes from Real
    """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


# 15 tests
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (r"MakeBoxes[1.4]", r"1.4`", None),
        (r"MakeBoxes[1.4`]", r"1.4`", None),
        (r"MakeBoxes[1.5`20]", r"1.5`20.", None),
        (r"MakeBoxes[1.4`20]", r"1.4`20.", None),
        (r"MakeBoxes[1.5``20]", r"1.5`20.1760912591", None),
        (r"MakeBoxes[-1.4]", r"RowBox[{-, 1.4`}]", None),
        (r"MakeBoxes[34.*^3]", r"34000.`", None),
        (r"MakeBoxes[0`]", r"0.`", None),
        (r"MakeBoxes[0``30]", r"0.``30.", None),
        (r"MakeBoxes[0.`]", r"0.`", None),
        (r"MakeBoxes[0.`3]", r"0.`", None),
        (r"MakeBoxes[0.``30]", r"0.``30.", None),
        (r"MakeBoxes[-14]", r"RowBox[{-, 14}]", None),
    ],
)
@skip_or_fail
def test_makeboxes_real_fail(str_expr, str_expected, msg):
    """
    # TODO: Constructing boxes from Real which are currently failing
    """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


# 3 tests
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (r"\(x \/ y + z\)", r"RowBox[{FractionBox[x, y], +, z}]", None),
        (r"\( \@ a + b \)", r"RowBox[{SqrtBox[a], +, b}]", None),
    ],
)
def test_makeboxes_precedence(str_expr, str_expected, msg):
    """Test precedence in string-like boxes"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


# 2 tests
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            r"\(x \/ (y + z)\)",
            r"FractionBox[x, RowBox[{(, RowBox[{y, +, z}], )}]]",
            None,
        ),
    ],
)
@skip_or_fail
def test_makeboxes_precedence_fail(str_expr, str_expected, msg):
    """TODO: fix the parsing for testing precedence in string-like boxes ("""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


# 3 tests
# TODO: Convert operators to appropriate representations e.g. 'Plus' to '+'
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (r"\(a + b\)", r"RowBox[{a, +, b}]", None),
        (r"\(x \/ \(y + z\)\)", r"FractionBox[x, RowBox[{y, +, z}]]", None),
    ],
)
def test_makeboxes_representation(str_expr, str_expected, msg):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


# 3 tests
# TODO: Convert operators to appropriate representations e.g. 'Plus' to '+'
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            r"\(TraditionalForm \` a + b\)",
            r"FormBox[RowBox[{a, +, b}], TraditionalForm]",
            None,
        ),
    ],
)
@skip_or_fail
def test_makeboxes_representation_fail(str_expr, str_expected, msg):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


#  5 tests
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            r"\( a, b \)",
            r"RowBox[{a, ,, b}]",
            "TODO: Parsing of special characters (like commas)",
        ),
    ],
)
def test_makeboxes_others(str_expr, str_expected, msg):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


#  5 tests
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            r"\(c (1 + x)\)",
            r"RowBox[{c, RowBox[{(, RowBox[{1, +, x}], )}]}]",
            r"FIXME: Don't insert spaces with brackets",
        ),
        (r"\!\(x \^ 2\)", r"x ^ 2", "Required MakeExpression"),
        (r"FullForm[%]", r"Power[x, 2]", "Required MakeExpression"),
        (r"MakeBoxes[1 + 1]", r"RowBox[{1, +, 1}]", "TODO: Fix Infix operators"),
    ],
)
@skip_or_fail
def test_makeboxes_others_fail(str_expr, str_expected, msg):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


# Fixme: "2." should be "2.`"
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            r"MakeBoxes[G[F[2.]], StandardForm]",
            r'RowBox[{"G","[",RowBox[{"F","[","2.","]"}],"]"}]',
            "Standard bahaviour",
        ),
        (
            r'MakeBoxes[F[x_], fmt_] := "F[" <> ToString[x] <> "]";MakeBoxes[G[F[3.002]], StandardForm]',
            r'RowBox[{"G","[","F[3.002]","]"}]',
            "Checking the rule over regular (Standard)",
        ),
        (
            r"MakeBoxes[OutputForm[G[F[3.002]]], StandardForm]",
            # We do not use InterpretationBox   = InterpretationBox[PaneBox["\"G[F[3.002]]\""], OutputForm[G[F[3.002`]]], Rule[Editable, False]]
            r'RowBox[{"G","[","F[3.002]","]"}]',
            "Checking the rule over OutputForm",
        ),
        (
            r'Format[F[x_]] := {"Formatted f", {x}, "Standard"};',
            r"System`Null",
            "Adding a generic format",
        ),
        (
            r"MakeBoxes[G[F[3.002]], StandardForm]",
            r'RowBox[{"G","[",RowBox[{"{",RowBox[{"\"Formatted f\"",",", RowBox[{"{","3.002","}"}],"," ,"\"Standard\""}],"}"}],"]"}]',
            "Checking again, with the defined StandardForm format",
        ),
        # InterpretationBox is not used in Mathics  = InterpretationBox[PaneBox["\"G[{Formatted f, {3.002}, Standard}]\""], OutputForm[G[F[3.002`]]], Rule[Editable, False]]
        (
            r"MakeBoxes[OutputForm[G[F[3.002]]], StandardForm]",
            r'RowBox[{"G","[",RowBox[{"{",RowBox[{"\"Formatted f\"",", ", RowBox[{"{","3.002","}"}],", ","\"Standard\""}],"}"}],"]"}]',
            "Checking again, with the defined StandardForm OutputForm",
        ),
        (
            r'Format[F[x_], StandardForm] :=  {"Formatted f", {x}, "Standard"};Format[F[x_], OutputForm] :=  {"Formatted f", {x}, "Output"};',
            r"Null",
            "Defining now specific formats",
        ),
        (
            r"MakeBoxes[G[F[3.002]], StandardForm]",
            r'RowBox[{"G","[",RowBox[{"{",RowBox[{"\"Formatted f\"",",",RowBox[{"{","3.002","}"}],",","\"Standard\""}],"}"}],"]"}]',
            "Test Custom StandardForm",
        ),
        # InterpretationBox is now used here... = InterpretationBox[PaneBox["\"G[{Formatted f, {3.002}, Output}]\""], OutputForm[G[F[3.002`]]], Rule[Editable, False]]
        (
            r"MakeBoxes[OutputForm[G[F[3.002]]], StandardForm]",
            r'RowBox[{"G","[",RowBox[{"{",RowBox[{"\"Formatted f\"",", ",RowBox[{"{","3.002","}"}],", ","\"Standard\""}],"}"}],"]"}]',
            "Test Custom OutputForm",
        ),
        (
            r"ClearAll[F]; MakeBoxes[G[F[2.]], StandardForm]",
            r'RowBox[{"G","[","F[2.]","]"}]',
            "Clear Formats",
        ),
        (
            r"MakeBoxes[F[x_], fmt_]=.; MakeBoxes[G[F[2.]], StandardForm]",
            r'RowBox[{"G","[",RowBox[{"F","[","2.","]"}],"]"}]',
            "Clear MakeBoxes rule",
        ),
    ],
)
@skip_or_fail
def test_makeboxes_custom(str_expr, str_expected, msg):
    """
    These tests checks the behaviour of MakeBoxes.
    Most of them are broken, because our implementation
    is different that the WMA.

    In WMA, MakeBoxes[...] is not evaluated as
    other expressions, but behaves like `Format[]`:
    Format rules (and MakeBoxes) are not taken into
    account in the regular evaluation.
    When a MakeBoxes expression is found, then
    the kernel applies first the format rules,
    and then the MakeBoxes rules

    """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=False,
        to_string_expected=False,
        hold_expected=False,
        to_python_expected=False,
        failure_message=msg,
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            r'MakeBoxes[F[x__], fmt_] :=  RowBox[{"F", "<~", RowBox[MakeBoxes[#1, fmt] & /@ List[x]], "~>"}]',
            "Null",
            "MakeBoxes rule for F",
        ),
        #
        (
            r'MakeBoxes[G[x___], fmt_] := RowBox[{"G", "<", RowBox[MakeBoxes[#1, fmt] & /@ List[x]], ">"}]',
            "Null",
            "MakeBoxes rule for G",
        ),
        #
        (
            r'MakeBoxes[GG[x___], fmt_] := RowBox[{"GG", "<<", RowBox[MakeBoxes[#1, fmt] & /@ List[x]], ">>"}]',
            "Null",
            "MakeBoxes rule for GG",
        ),
        #
        (
            r'Format[F[x_, y_], StandardForm] := {F[x], "Standard"}',
            "Null",
            "Format rule for F, StandardForm",
        ),
        #
        (
            r'Format[G[x___], StandardForm] :=  {"Standard", GG[x]}',
            "Null",
            "Format rule for G, StandardForm",
        ),
        #
        (
            r'ToString[G[F[1., "l"], .2], StandardForm]',
            r"{Standard, GG << {F<~1.`~>, Standard} 0.2` >>}",
            None,
        ),
        #
        (r'ToString[FullForm[G[F[1., "l"], .2]]]', r'G[F[1.`, "l"], 0.2`]', "FullForm"),
        #
        (
            r'ToString[G[F[1., "l"], .2], InputForm]',
            r'"G[F[1.`, \"l\"], 0.2`]"',
            "InputForm - no format defined",
        ),
        #
        (
            r'ToString[G[F[1., "l"], .2], OutputForm]',
            r'"G[F[1.`, l], 0.2`]"',
            "OutputForm - no format defined",
        ),
        #
        (
            r'Format[F[x_, y_], InputForm] := {F[x], "In"}',
            "Null",
            "Format rule for F, InputForm",
        ),
        #
        (
            r'Format[G[x___], InputForm] :=  {"In", GG[x]}',
            "Null",
            "Format rule for G, OutputForm",
        ),
        #
        (
            r'Format[F[x_, y_], OutputForm] := {F[x], "Out"}',
            "Null",
            "Format rule for F, InputForm",
        ),
        #
        (
            r'Format[G[x___], OutputForm] :=  {"Out", GG[x]}',
            "Null",
            "Format rule for G, OutputForm",
        ),
        #
        (
            r'Format[F[x_, y_], FullForm] := {F[x], "full"}',
            "Null",
            "Format for FullForm. (never used)",
        ),
        #
        (
            r'ToString[G[F[1., "l"], .2], StandardForm]',
            r'"{Standard, GG << {F<~1.`~>, Standard} 0.2` >>}"',
            "StandardForm - formats defined",
        ),
        #
        (r'ToString[FullForm[G[F[1., "l"], .2]]]', r'"G[F[1.`, \"l\"], 0.2`]"', None),
        #
        (
            r'ToString[G[F[1., "l"], .2], InputForm]',
            r'"{\"In\", GG[{F[1.], \"In\"}, 0.2]}"',
            "FullForm - formats defined",
        ),
        #
        (
            r'ToString[G[F[1., "l"], .2], OutputForm]',
            r'"{Out, GG[{F[1.], Out}, 0.2]}"',
            None,
        ),
        #
        (
            r'MakeBoxes[G[F[1., "l"], .2], StandardForm]',
            (
                r'RowBox[{"{", RowBox[{"\"Standard\"", ",",'
                r'RowBox[{"GG", "<<", RowBox[{RowBox[{"{",'
                r'RowBox[{RowBox[{"F", "<~", RowBox[{"1.`"}], "~>"}],'
                r'",", "\"Standard\""}], "}"}], "0.2`"}], ">>"}]}], "}"}]'
            ),
            "MakeBoxes, StandardForm",
        ),
        #
        (
            r'MakeBoxes[InputForm[G[F[1., "l"], .2]], StandardForm]',
            (
                r'InterpretationBox[StyleBox["{\"In\", GG[{F[1.], \"In\"}, 0.2]}", '
                r"ShowStringCharacters->True, NumberMarks->True], "
                r'InputForm[G[F[1.`, "l"], 0.2`]], Editable-> True, '
                r"AutoDelete->True]"
            ),
            "MakeBoxes, InputForm",
        ),
        #
        (
            r'MakeBoxes[OutputForm[G[F[1., "l"], .2]], StandardForm]',
            (
                r'InterpretationBox[PaneBox["\"{Out, GG[{F[1.], Out}, 0.2]}\""],'
                r'OutputForm[G[F[1.`, "l"], 0.2`]], Editable->False]'
            ),
            "MakeBoxes, OutputForm",
        ),
        #
        (
            r'ToString[TeXForm[G[F[1., "l"], .2]]]',
            r'"G<F<\sim 1.\text{l}\sim >0.2>"',
            "TeXForm - format defined",
        ),
        #
        (
            r'ToString[TeXForm[InputForm[G[F[1., "l"], .2]]]]',
            r'"\text{$\{$In, GG[$\{$F[1.], In$\}$, 0.2]$\}$}"',
            "TeXForm - InputForm - format defined",
        ),
        #
        (r"ClearAll[F, G, GG]", "Null", "Clear Format rules"),
        #
        (
            r'ToString[G[F[1., "l"], .2], StandardForm]',
            r'"G < F<~1.`l~>0.2` >"',
            "StandardForm - formats clear",
        ),
        #
        (
            r'ToString[FullForm[G[F[1., "l"], .2]]]',
            r'"G[F[1., \"l\"], 0.2`]"',
            "FullForm - formats clear",
        ),
        #
        (
            r'ToString[G[F[1., "l"], .2], InputForm]',
            r'"G[F[1., \"l\"], 0.2]"',
            "InputForm - formats clear",
        ),
        #
        (
            r'ToString[G[F[1., "l"], .2], OutputForm]',
            r'"G[F[1., l], 0.2]"',
            "OutputForm - formats clear",
        ),
        #
        (r"MakeBoxes[F[x__], fmt_]=.", "Null", "Clear MakeBoxes rule for F"),
        #
        (r"MakeBoxes[G[x___], fmt_]=.", "Null", "Clear MakeBoxes rule for G"),
        #
        (r"MakeBoxes[GG[x___], fmt_]=.", "Null", "Clear MakeBoxes rule for GG"),
        #
        (
            r'ToString[G[F[1., "l"], .2], StandardForm]',
            r'"G[F[1.`, l], 0.2`]"',
            "StandardForm - Boxes clear",
        ),
        #
        (
            r'ToString[FullForm[G[F[1., "l"], .2]]]',
            r'"G[F[1.`, \"l\"], 0.2`]"',
            "FullForm - Boxes clear",
        ),
        #
        (
            r'ToString[G[F[1., "l"], .2], InputForm]',
            r'"G[F[1., \"l\"], 0.2]"',
            "InputForm - Boxes clear",
        ),
        #
        (
            r'ToString[G[F[1., "l"], .2], OutputForm]',
            r'"G[F[1., l], 0.2]"',
            "OutputForm - Boxes clear",
        ),
    ],
)
@skip_or_fail
def test_makeboxes_custom2(str_expr, str_expected, msg):
    """
    These tests checks the behaviour of MakeBoxes.
    Most of them are broken, because our implementation
    is different that the WMA.
    """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=False,
        to_string_expected=False,
        hold_expected=False,
        to_python_expected=False,
        failure_message=msg,
    )
