# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.assignments.assignment

Tests here check the compatibility of
the  default behavior of the different assignment operators
with WMA.
"""
# TODO: consider splitting this module into sub-modules.

from test.helper import check_arg_counts, check_evaluation, session

import pytest
from mathics_scanner.errors import IncompleteSyntaxError

STR_TEST_SET_WITH_ONE_IDENTITY = """
SetAttributes[SUNIndex, {OneIdentity}];
SetAttributes[SUNFIndex, {OneIdentity}];

SUNIndex[SUNFIndex[___]]:=
	(Print["This error shouldn't be triggered here!"];
	Abort[]);

SUNFIndex[SUNIndex[___]]:=
	(Print["This error shouldn't be triggered here!"];
	Abort[]);

SUNIndex /: MakeBoxes[SUNIndex[p_], TraditionalForm]:=ToBoxes[p, TraditionalForm];

SUNFIndex /: MakeBoxes[SUNFIndex[p_], TraditionalForm]:=ToBoxes[p, TraditionalForm];
"""


def test_setdelayed_oneidentity():
    """
    This test checks the behavior of DelayedSet over
    symbols with the attribute OneIdentity.
    """
    expr = ""
    for line in STR_TEST_SET_WITH_ONE_IDENTITY.split("\n"):
        if line in ("", "\n"):
            continue
        expr = expr + line
        try:
            check_evaluation(
                expr, "Null", to_string_expr=False, to_string_expected=False
            )
            expr = ""
        except IncompleteSyntaxError:
            continue
