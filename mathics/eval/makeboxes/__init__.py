"""
Functions related to the evaluation of MakeBoxes.
"""

from mathics.eval.makeboxes.formatvalues import StringLParen, StringRParen, do_format
from mathics.eval.makeboxes.makeboxes import (
    _boxed_string,
    eval_generic_makeboxes,
    eval_makeboxes,
    eval_makeboxes_fullform,
    format_element,
    int_to_string_shorter_repr,
    to_boxes,
)
from mathics.eval.makeboxes.numberform import (
    eval_baseform,
    get_numberform_parameters,
    numberform_to_boxes,
)
from mathics.eval.makeboxes.operators import eval_infix, eval_postprefix
from mathics.eval.makeboxes.outputforms import (
    eval_mathmlform,
    eval_tableform,
    eval_texform,
)
from mathics.eval.makeboxes.precedence import (
    builtins_precedence,
    compare_precedence,
    parenthesize,
)

__all__ = [
    "numberform_to_boxes",
    "StringLParen",
    "StringRParen",
    "_boxed_string",
    "builtins_precedence",
    "compare_precedence",
    "do_format",
    "eval_baseform",
    "eval_generic_makeboxes",
    "eval_infix",
    "eval_makeboxes",
    "eval_makeboxes_fullform",
    "eval_mathmlform",
    "eval_postprefix",
    "eval_tableform",
    "eval_texform",
    "format_element",
    "get_numberform_parameters",
    "int_to_string_shorter_repr",
    "parenthesize",
    "render_input_form",
    "to_boxes",
]
