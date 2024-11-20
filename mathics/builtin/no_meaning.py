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

from mathics.core.builtin import (
    OPERATOR_DATA,
    NoMeaningInfixOperator,
    NoMeaningPostfixOperator,
    NoMeaningPrefixOperator,
)

# Generate no-meaning Mathics3 Builtin class from the operator name,
# affix, and Operator Unicode values found read from the JSON operators
# file.
for affix, format_fn, operator_base_class in (
    ("infix", "Infix", NoMeaningInfixOperator),
    ("postfix", "Postfix", NoMeaningPostfixOperator),
    ("prefix", "Prefix", NoMeaningPrefixOperator),
):
    for operator_name, operator_string in OPERATOR_DATA[
        f"no-meaning-{affix}-operators"
    ].items():
        # Create the Mathics3 Builtin class...
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

        # Put the newly-created Builtin class inside this module.
        setattr(modules[__name__], operator_name, generated_operator_class)
