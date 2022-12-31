"""
Forms which are not in '$OutputForms'
"""

import re

from mathics.builtin.box.layout import RowBox, to_boxes
from mathics.builtin.forms.base import FormBaseClass
from mathics.builtin.makeboxes import MakeBoxes
from mathics.core.atoms import String
from mathics.core.element import EvalMixin


class StringForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/StringForm.html</url>

    <dl>
      <dt>'StringForm[$str$, $expr1$, $expr2$, ...]'
      <dd>displays the string $str$, replacing placeholders in $str$
        with the corresponding expressions.
    </dl>

    >> StringForm["`1` bla `2` blub `` bla `2`", a, b, c]
     = a bla b blub c bla b
    """

    in_outputforms = False
    in_printforms = False
    summary_text = "make an string from a template and a list of parameters"

    def eval_makeboxes(self, s, args, f, evaluation):
        """MakeBoxes[StringForm[s_String, args___],
        f:StandardForm|TraditionalForm|OutputForm]"""

        s = s.value
        args = args.get_sequence()
        result = []
        pos = 0
        last_index = 0
        for match in re.finditer(r"(\`(\d*)\`)", s):
            start, end = match.span(1)
            if match.group(2):
                index = int(match.group(2))
            else:
                index = last_index + 1
            if index > last_index:
                last_index = index
            if start > pos:
                result.append(to_boxes(String(s[pos:start]), evaluation))
            pos = end
            if 1 <= index <= len(args):
                arg = args[index - 1]
                result.append(
                    to_boxes(MakeBoxes(arg, f).evaluate(evaluation), evaluation)
                )
        if pos < len(s):
            result.append(to_boxes(String(s[pos:]), evaluation))
        return RowBox(
            *tuple(
                r.evaluate(evaluation) if isinstance(r, EvalMixin) else r
                for r in result
            )
        )
