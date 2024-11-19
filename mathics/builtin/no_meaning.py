# -*- coding: utf-8 -*-
# Note: this will be redone soon to pull no-meaning operator information from operators.yml out
# of the MathicsScanner project.
"""
Operators without Built-in Meanings

Not all operators recognized by the Mathics3 are associated with functions that have built‐in meanings.
You can use these operators as a way to build up your own notation within Mathics3.
"""

from inspect import getmembers, isclass
from sys import modules

from mathics.core.builtin import OPERATOR_DATA, NoMeaningInfixOperator

# Note: classes in this file must *only* be "no-meaning"
# builtin operator classes.


class Because(NoMeaningInfixOperator):
    r"""This text is replaced! But it needs to be here for documentation detection."""


class Cap(NoMeaningInfixOperator):
    r"""This text is replaced! But it needs to be here for documentation detection."""


class CenterDot(NoMeaningInfixOperator):
    r"""This text is replaced! But it needs to be here for documentation detection."""


class Star(NoMeaningInfixOperator):
    r"""This text is replaced! But it needs to be here for documentation detection."""


# Generate Builtin No-meaning Builtin Infix operators, using
# the Operator name and Operator Unicode found by reading
# the operators JSON file.
for name, operator_class in getmembers(modules[__name__]):
    if isclass(operator_class):
        operator_name = operator_class.__name__
        operator_string = OPERATOR_DATA["no-meaning-infix-operators"].get(operator_name)
        if operator_string is not None:
            operator_class.operator = operator_string
            operator_class.__doc__ = NoMeaningInfixOperator.__doc_pattern__.format(
                operator_name=operator_name, operator_string=operator_string
            )
        operator_class.summary_text = f"""{operator_name} infix operator "{operator_string}" (no pre-set meaning attached)"""
        operator_class.formats = {
            (("InputForm", "OutputForm", "StandardForm"), f"{operator_name}[args__]"): (
                ('Infix[{args}, "%s"]' % operator_string)
            )
        }
