r"""
Forms which are not in '\$OutputForms'
"""

import re

from mathics.builtin.box.layout import RowBox, to_boxes
from mathics.builtin.forms.base import FormBaseClass
from mathics.builtin.makeboxes import MakeBoxes
from mathics.core.atoms import String
from mathics.core.element import EvalMixin
from mathics.eval.strings import eval_ToString


class SequenceForm(FormBaseClass):
    r"""
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/SequenceForm.html</url>

    <dl>
      <dt>'SequenceForm[$expr1$, $expr2$, ..]'
      <dd>format the textual concatenation of the printed forms of $expi$.
    </dl>
    'SequenceForm' has been superseded by <url>:Row:
    /doc/reference-of-built-in-symbols/layout/row
    </url> and 'Text' (which is not implemented yet).

    >> SequenceForm["[", "x = ", 56, "]"]
     = [x = 56]
    """

    in_outputforms = False
    in_printforms = False

    options = {
        "CharacterEncoding": '"Unicode"',
    }

    summary_text = "format a string from a template and a list of parameters"

    def eval_makeboxes(self, args, form, evaluation, options: dict):
        """MakeBoxes[SequenceForm[args___, OptionsPattern[SequenceForm]],
        form:StandardForm|TraditionalForm|OutputForm]"""
        encoding = options["System`CharacterEncoding"]
        return RowBox(
            *[
                (
                    arg
                    if isinstance(arg, String)
                    else eval_ToString(arg, form, encoding.value, evaluation)
                )
                for arg in args.get_sequence()
            ]
        )


class StringForm(FormBaseClass):
    r"""
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
    summary_text = "format a string from a template and a list of parameters"

    def eval_makeboxes(self, s, args, form, evaluation):
        """MakeBoxes[StringForm[s_String, args___],
        form:StandardForm|TraditionalForm|OutputForm]"""

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
            last_index = max(index, last_index)
            if start > pos:
                result.append(to_boxes(String(s[pos:start]), evaluation))
            pos = end
            if 1 <= index <= len(args):
                arg = args[index - 1]
                result.append(
                    to_boxes(MakeBoxes(arg, form).evaluate(evaluation), evaluation)
                )
        if pos < len(s):
            result.append(to_boxes(String(s[pos:]), evaluation))
        return RowBox(
            *tuple(
                r.evaluate(evaluation) if isinstance(r, EvalMixin) else r
                for r in result
            )
        )
