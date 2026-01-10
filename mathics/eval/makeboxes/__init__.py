"""
Functions related to the evaluation of MakeBoxes.
"""

from mathics.eval.makeboxes.formatvalues import StringLParen, StringRParen, do_format
from mathics.eval.makeboxes.makeboxes import (
    _boxed_string,
    eval_generic_makeboxes,
    eval_makeboxes,
    eval_makeboxes_fullform,
    eval_makeboxes_outputform,
    format_element,
    int_to_string_shorter_repr,
    to_boxes,
)
from mathics.eval.makeboxes.numberform import NumberForm_to_String, eval_baseform
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
    "NumberForm_to_String",
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
    "eval_makeboxes_outputform",
    "eval_mathmlform",
    "eval_postprefix",
    "eval_tableform",
    "eval_texform",
    "format_element",
    "int_to_string_shorter_repr",
    "parenthesize",
    "render_input_form",
    "to_boxes",
]
