# -*- coding: utf-8 -*-
from mathics.core.builtin import Builtin

from .helper import check_evaluation, session

# TODO: These builtins should be loaded in Definitions
# to have any effect...


class Builtin1(Builtin):
    summary_text = "short description"


class Builtin2(Builtin):
    """
    <url>fake:http://fake</url>
    long description

    <dl>
      <dt>'Builtin2'
      <dd>a description of what this symbol does.
    </dl>

    """


def test_short_description():
    check_evaluation(
        "?Builtin1", "Global`Builtin1\n", "short description", hold_expected=True
    )
    check_evaluation(
        "?Builtin2", "Global`Builtin2\n", "short description", hold_expected=True
    )


def test_long_description():
    check_evaluation(
        "??Builtin1", "Global`Builtin1\n", "long description", hold_expected=True
    )
    check_evaluation(
        "??Builtin2", "Global`Builtin2\n", "long description", hold_expected=True
    )
