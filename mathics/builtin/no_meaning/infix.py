"""
Infix Operators without Built-in Meanings
"""

from sys import modules

from mathics.core.builtin import NoMeaningInfixOperator, add_no_meaning_builtin_classes


# Note: this function has to exist inside this module, for the created modules
# to be put under module `mathics.builtin.no_meaning.infix`. This seems to be
# a limitation on the Python class-creation function type().
def create_class_function(
    operator_name: str,
    operator_base_class,
    operator_string: str,
    mathics3_format_function_name: str,
) -> type:
    """
    Returns a Mathics3 Builtin function associated with this module
    (mathics.builtin.no_meaning.infix) that implements a Mathics infix operator
    with no pre-existing meaning.
    """
    return type(
        operator_name,
        (operator_base_class,),
        {
            "__doc__": operator_base_class.__doc_pattern__.format(
                operator_name=operator_name, operator_string=operator_string
            ),
            "operator": operator_string,
            "summary_text": f"""{operator_name} infix operator "{operator_string}" (no pre-set meaning attached)""",
            "formats": {
                (
                    ("InputForm", "OutputForm", "StandardForm"),
                    f"{operator_name}[args__]",
                ): (
                    (
                        '%s[{args}, "%s"]'
                        % (mathics3_format_function_name, operator_string)
                    )
                )
            },
        },
    )


add_no_meaning_builtin_classes(
    create_class_function, "infix", "Infix", NoMeaningInfixOperator, modules[__name__]
)
