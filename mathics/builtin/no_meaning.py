# -*- coding: utf-8 -*-
"""
Operators without Built-in Meanings

Not all operators recognized by the Mathics3 are associated with functions that have built‐in meanings.
You can use these operators as a way to build up your own notation within Mathics3.
"""

# WARNING: This module uses fancy MetaProgramming to create the Mathics3 Builtin classes for the
# operators in that have no pre-defined meaning. This is tricky and probably fragile code.
# We use the type() function to create the class, and setattr, to include this class inside
# this module.

from sys import modules

import mathics.core.parser.operators
from mathics.core.attributes import A_NO_ATTRIBUTES
from mathics.core.builtin import (
    InfixOperator,
    NoMeaningInfixOperator,
    NoMeaningPostfixOperator,
    NoMeaningPrefixOperator,
)
from mathics.core.parser.operators import OPERATOR_DATA

# This tells documentation how to sort this module
sort_order = "mathics.builtin.operators-without-built-in-meanings"


def init():
    # Generate no-meaning Mathics3 Builtin class from the operator name,
    # affix, and Operator Unicode values found in OPERATOR_DATA.  This
    # data ultimately comes from a YAML file in the MathicsScanner project
    # which is processed into a JSON file.
    for affix, format_fn, operator_base_class in (
        ("infix", "Infix", NoMeaningInfixOperator),
        ("postfix", "Postfix", NoMeaningPostfixOperator),
        ("prefix", "Prefix", NoMeaningPrefixOperator),
    ):
        for operator_name, operator_tuple in OPERATOR_DATA[
            f"no-meaning-{affix}-operators"
        ].items():
            # Create the Mathics3 Builtin class...
            operator_string = operator_tuple[0]
            generated_operator_class = type(
                operator_name,
                (operator_base_class,),
                {
                    "__doc__": operator_base_class.__doc_pattern__.format(
                        operator_name=operator_name, operator_string=operator_string
                    ),
                    "operator": operator_string,
                    "summary_text": f"""{operator_name} {affix} operator "{operator_string}" (no pre-set meaning attached)""",
                    "formats": {
                        (
                            ("InputForm", "OutputForm", "StandardForm"),
                            f"{operator_name}[args__]",
                        ): (('%s[{args}, "%s"]' % (format_fn, operator_string)))
                    },
                },
            )
            if affix == "infix":
                # FIXME get precedence from JSON. Value 100 is a hack for now.
                mathics.core.parser.operators.flat_binary_ops[operator_name] = 100

            # Put the newly-created Builtin class inside this module.
            setattr(modules[__name__], operator_name, generated_operator_class)


init()


class DirectedEdge(InfixOperator):
    # This will be used to create a docstring
    r"""
    <url>
    :WML link:
    https://reference.wolfram.com/language/ref/DirectedEdge.html</url>

    <dl>
      <dt>'DirectedEdge[$x$, $y$, ...]'
      <dd>displays $x$ → $y$ → ...
    </dl>

    >> DirectedEdge[x, y, z]
     = x → y → z

    >> a \[DirectedEdge] b
     = a → b

    """
    formats = {
        (("InputForm", "OutputForm", "StandardForm"), "DirectedEdge[args__]"): (
            'Infix[{args}, "→"]'
        ),
    }

    attributes = A_NO_ATTRIBUTES
    default_formats = False  # Don't use any default format rules. Instead, see belo.

    operator = "→"
    summary_text = 'DirectedEdge infix operator "→"'


class UndirectedEdge(InfixOperator):
    # This will be used to create a docstring
    r"""
    <url>
    :WML link:
    https://reference.wolfram.com/language/ref/UndirectedEdge.html</url>

    <dl>
      <dt>'UndrectedEdge[$x$, $y$, ...]'
      <dd>displays $x$ ↔ $y$ ↔ ...
    </dl>

    >> UndirectedEdge[x, y, z]
     = x ↔ y ↔ z

    >> a \[UndirectedEdge] b
     = a ↔ b

    """
    formats = {
        (("InputForm", "OutputForm", "StandardForm"), "UndirectedEdge[args__]"): (
            'Infix[{args}, "↔"]'
        ),
    }

    attributes = A_NO_ATTRIBUTES
    default_formats = False  # Don't use any default format rules. Instead, see belo.

    operator = "↔"
    summary_text = 'UndirectedEdge infix operator "↔"'
