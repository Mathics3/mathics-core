# -*- coding: utf-8 -*-
"""
Regular Expressions
"""


from mathics.core.builtin import Builtin


# eval.strings.to_regex seems to have the implementation.
class RegularExpression(Builtin):
    r"""
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/RegularExpression.html</url>

    <dl>
    <dt>'RegularExpression["regex"]'
      <dd>represents the regex specified by the string "$regex$".
    </dl>

    >> StringSplit["1.23, 4.56  7.89", RegularExpression["(\\s|,)+"]]
     = {1.23, 4.56, 7.89}

    'RegularExpression' just wraps a string to be interpreted as \
    a regular expression, but are not evaluated as stand alone \
    expressions:
    >> RegularExpression["[abc]"]
     = RegularExpression[[abc]]

    """

    summary_text = "string to regular expression."
