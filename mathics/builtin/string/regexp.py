# -*- coding: utf-8 -*-
"""
Regular Expressions
"""


from mathics.builtin.base import Builtin


# builtin.strings.atomic.to_regex seems to have the implementation.
class RegularExpression(Builtin):
    r"""
    <dl>
    <dt>'RegularExpression["regex"]'
      <dd>represents the regex specified by the string $"regex"$.
    </dl>

    >> StringSplit["1.23, 4.56  7.89", RegularExpression["(\\s|,)+"]]
     = {1.23, 4.56, 7.89}

    #> RegularExpression["[abc]"]
     = RegularExpression[[abc]]

    ## Mathematica doesn't seem to verify the correctness of regex
    #> StringSplit["ab23c", RegularExpression["[0-9]++"]]
     : Element RegularExpression[[0-9]++] is not a valid string or pattern element in RegularExpression[[0-9]++].
     = StringSplit[ab23c, RegularExpression[[0-9]++]]

    #> StringSplit["ab23c", RegularExpression[2]]
     : Element RegularExpression[2] is not a valid string or pattern element in RegularExpression[2].
     = StringSplit[ab23c, RegularExpression[2]]
    """
    summary_text = "string to regular expression."
