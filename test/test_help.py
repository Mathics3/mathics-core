# -*- coding: utf-8 -*-
from mathics.builtin.base import Builtin

from .helper import check_evaluation


class Builtin1(Builtin):
    summary_text = "short description"


class Builtin2(Builtin):
    "long description"


def test_short_description():
    check_evaluation("?Builtin1", "Null", "short description")


def test_long_description():
    check_evaluation("??Builtin2", "Null", "long description")
