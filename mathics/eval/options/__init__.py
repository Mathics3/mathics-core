"""
Evaluation routines and associated code for Built-in functions found under module
mathics.builtins.options.
"""

from mathics.eval.options.functions import filter_from_iterable, options_to_rules
from mathics.eval.options.options import eval_Options
from mathics.eval.options.values import filter_non_default_values

__all__ = [
    "eval_Options",
    "filter_from_iterable",
    "filter_non_default_values",
    "options_to_rules",
]
