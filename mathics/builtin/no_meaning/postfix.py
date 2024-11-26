"""
Postfix Operators without Built-in Meanings
"""

from sys import modules

import mathics.core.parser.operators
from mathics.core.builtin import NoMeaningPostfixOperator
from mathics.core.parser.operators import OPERATOR_DATA


def add_no_meaning_builtins(
    affix: str, format_function_name: str, operator_base_class, builtin_module
):
    operator_key = f"no-meaning-{affix}-operators"
    for operator_name, operator_tuple in OPERATOR_DATA[operator_key].items():
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
                    ): (('%s[{args}, "%s"]' % (format_function_name, operator_string)))
                },
            },
        )

        # FIXME: Right now, precedence for infix operators is listed in
        # JSON only for infix operators. Extend table generation in the same way
        # for prefix and postfix, and then extend the code below to
        # assign operator precedences for prefix and postfix operators.
        if affix == "infix":
            mathics.core.parser.operators.flat_binary_ops[
                operator_name
            ] = operator_tuple[1]

        # Put the newly-created Builtin class inside this module.
        setattr(builtin_module, operator_name, generated_operator_class)


def add_no_meaning_postfix_operators():
    add_no_meaning_builtins(
        "postfix", "Postfix", NoMeaningPostfixOperator, modules[__name__]
    )


add_no_meaning_postfix_operators()
