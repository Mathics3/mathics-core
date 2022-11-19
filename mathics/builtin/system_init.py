"""
One-time system setup to read in built-ins module.
"""

# Signals to Mathics doc processing not to include this module in its documentation.
no_doc = True

# Set this to True to print all the builtins that do not have
# a summary_text. In the future, we can set this to True
# and raise an error if a new builtin is added without
# this property or if it does not fulfill some other conditions.
RUN_SANITY_TEST = False


def sanity_check(cls, module):
    if not RUN_SANITY_TEST:
        return True

    if not hasattr(cls, "summary_text"):
        print(
            "In ",
            module.__name__,
            cls.__name__,
            " does not have a summary_text.",
        )
        return False
    return True
