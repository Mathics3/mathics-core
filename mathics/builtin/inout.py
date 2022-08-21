"""
Input and Output
"""

import re

from typing import Optional


from mathics.builtin.base import (
    Builtin,
    Predefined,
)
from mathics.builtin.box.layout import GridBox, RowBox, to_boxes
from mathics.builtin.comparison import expr_min
from mathics.builtin.makeboxes import MakeBoxes
from mathics.builtin.tensors import get_dimensions

from mathics.core.atoms import Integer, String, StringFromPython

from mathics.core.element import EvalMixin
from mathics.core.expression import Expression, BoxError
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Symbol,
    SymbolFullForm,
    SymbolList,
    SymbolNull,
)

from mathics.core.systemsymbols import (
    SymbolMakeBoxes,
    SymbolRow,
    SymbolRowBox,
    SymbolRule,
)

MULTI_NEWLINE_RE = re.compile(r"\n{2,}")

SymbolNumberForm = Symbol("System`NumberForm")
SymbolSuperscriptBox = Symbol("System`SuperscriptBox")
SymbolTableDepth = Symbol("TableDepth")


class TableForm(Builtin):
    """
    <dl>
      <dt>'TableForm[$expr$]'
      <dd>displays $expr$ as a table.
    </dl>

    >> TableForm[Array[a, {3,2}],TableDepth->1]
     = {a[1, 1], a[1, 2]}
     .
     . {a[2, 1], a[2, 2]}
     .
     . {a[3, 1], a[3, 2]}

    A table of Graphics:
    >> Table[Style[Graphics[{EdgeForm[{Black}], RGBColor[r,g,b], Rectangle[]}], ImageSizeMultipliers->{0.2, 1}], {r,0,1,1/2}, {g,0,1,1/2}, {b,0,1,1/2}] // TableForm
     = -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-

    #> TableForm[{}]
     = #<--#
    """

    options = {"TableDepth": "Infinity"}
    summary_text = "format as a table"

    def apply_makeboxes(self, table, f, evaluation, options):
        """MakeBoxes[%(name)s[table_, OptionsPattern[%(name)s]],
        f:StandardForm|TraditionalForm|OutputForm]"""

        dims = len(get_dimensions(table, head=SymbolList))
        depth = self.get_option(options, "TableDepth", evaluation)
        depth = expr_min((Integer(dims), depth))
        depth = depth.value
        if depth is None:
            evaluation.message(self.get_name(), "int")
            return

        if depth <= 0:
            return Expression(SymbolMakeBoxes, table, f)
        elif depth == 1:
            return GridBox(
                ListExpression(
                    *(
                        ListExpression(Expression(SymbolMakeBoxes, item, f))
                        for item in table.elements
                    ),
                )
            )
            # return Expression(
            #    'GridBox', Expression('List', *(
            #        Expression('List', Expression('MakeBoxes', item, f))
            #        for item in table.elements)))
        else:
            new_depth = Expression(SymbolRule, SymbolTableDepth, Integer(depth - 2))

            def transform_item(item):
                if depth > 2:
                    return Expression(Symbol(self.get_name()), item, new_depth)
                else:
                    return item

            return GridBox(
                ListExpression(
                    *(
                        ListExpression(
                            *(
                                Expression(SymbolMakeBoxes, transform_item(item), f)
                                for item in row.elements
                            ),
                        )
                        for row in table.elements
                    ),
                )
            )


class MatrixForm(TableForm):
    """
    <dl>
      <dt>'MatrixForm[$m$]'
      <dd>displays a matrix $m$, hiding the underlying list
        structure.
    </dl>

    >> Array[a,{4,3}]//MatrixForm
     = a[1, 1]   a[1, 2]   a[1, 3]
     .
     . a[2, 1]   a[2, 2]   a[2, 3]
     .
     . a[3, 1]   a[3, 2]   a[3, 3]
     .
     . a[4, 1]   a[4, 2]   a[4, 3]

    ## Issue #182
    #> {{2*a, 0},{0,0}}//MatrixForm
     = 2 a   0
     .
     . 0     0
    """

    summary_text = "format as a matrix"

    def apply_makeboxes_matrix(self, table, f, evaluation, options):
        """MakeBoxes[%(name)s[table_, OptionsPattern[%(name)s]],
        f:StandardForm|TraditionalForm]"""

        result = super(MatrixForm, self).apply_makeboxes(table, f, evaluation, options)
        if result.get_head_name() == "System`GridBox":
            return Expression(
                SymbolRowBox, ListExpression(String("("), result, String(")"))
            )
        return result


class StringForm(Builtin):
    """
    <dl>
      <dt>'StringForm[$str$, $expr1$, $expr2$, ...]'
      <dd>displays the string $str$, replacing placeholders in $str$
        with the corresponding expressions.
    </dl>

    >> StringForm["`1` bla `2` blub `` bla `2`", a, b, c]
     = a bla b blub c bla b
    """

    summary_text = "make an string from a template and a list of parameters"

    def apply_makeboxes(self, s, args, f, evaluation):
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


class Echo_(Predefined):
    """
    <dl>
      <dt>'$Echo'
      <dd>gives a list of files and pipes to which all input is echoed.

    </dl>
    """

    attributes = 0
    name = "$Echo"
    rules = {"$Echo": "{}"}
    summary_text = "files and pipes that echoes the input"


class Print(Builtin):
    """
    <dl>
      <dt>'Print[$expr$, ...]'
      <dd>prints each $expr$ in string form.
    </dl>

    >> Print["Hello world!"]
     | Hello world!
    >> Print["The answer is ", 7 * 6, "."]
     | The answer is 42.

    #> Print["-Hola\\n-Qué tal?"]
     | -Hola
     . -Qué tal?
    """

    summary_text = "print strings and formatted text"

    def apply(self, expr, evaluation):
        "Print[expr__]"

        expr = expr.get_sequence()
        expr = Expression(SymbolRow, ListExpression(*expr))
        evaluation.print_out(expr)
        return SymbolNull


class FullForm(Builtin):
    """
    <dl>
      <dt>'FullForm[$expr$]'
      <dd>displays the underlying form of $expr$.
    </dl>

    >> FullForm[a + b * c]
     = Plus[a, Times[b, c]]
    >> FullForm[2/3]
     = Rational[2, 3]
    >> FullForm["A string"]
     = "A string"
    """

    summary_text = "underlying M-Expression representation"


class StandardForm(Builtin):
    """
    <dl>
      <dt>'StandardForm[$expr$]'
      <dd>displays $expr$ in the default form.
    </dl>

    >> StandardForm[a + b * c]
     = a + b c
    >> StandardForm["A string"]
     = A string
    'StandardForm' is used by default:
    >> "A string"
     = A string
    >> f'[x]
     = f'[x]
    """

    summary_text = "default output format"


class TraditionalForm(Builtin):
    """
    <dl>
      <dt>'TraditionalForm[$expr$]'
      <dd>displays $expr$ in a format similar to the traditional mathematical notation, where
           function evaluations are represented by brackets instead of square brackets.
    </dl>

    ## To pass this test, we need to improve the implementation of Element.format
    ## >> TraditionalForm[g[x]]
    ## = g(x)
    """

    summary_text = "traditional output format"


class InputForm(Builtin):
    r"""
    <dl>
      <dt>'InputForm[$expr$]'
      <dd>displays $expr$ in an unambiguous form suitable for input.
    </dl>

    >> InputForm[a + b * c]
     = a + b*c
    >> InputForm["A string"]
     = "A string"
    >> InputForm[f'[x]]
     = Derivative[1][f][x]
    >> InputForm[Derivative[1, 0][f][x]]
     = Derivative[1, 0][f][x]
    #> InputForm[2 x ^ 2 + 4z!]
     = 2*x^2 + 4*z!
    #> InputForm["\$"]
     = "\\$"
    """
    summary_text = "plain-text input format"


class OutputForm(Builtin):
    """
    <dl>
      <dt>'OutputForm[$expr$]'
      <dd>displays $expr$ in a plain-text form.
    </dl>

    >> OutputForm[f'[x]]
     = f'[x]
    >> OutputForm[Derivative[1, 0][f][x]]
     = Derivative[1, 0][f][x]
    >> OutputForm["A string"]
     = A string
    >> OutputForm[Graphics[Rectangle[]]]
     = -Graphics-
    """

    summary_text = "plain-text output format"


class MathMLForm(Builtin):
    """
    <dl>
      <dt>'MathMLForm[$expr$]'
      <dd>displays $expr$ as a MathML expression.
    </dl>

    >> MathMLForm[HoldForm[Sqrt[a^3]]]
     = ...

    ## Test cases for Unicode - redo please as a real test
    >> MathMLForm[\\[Mu]]
    = ...

    # This can causes the TeX to fail
    # >> MathMLForm[Graphics[Text["\u03bc"]]]
    #  = ...

    ## The <mo> should contain U+2062 INVISIBLE TIMES
    ## MathMLForm[MatrixForm[{{2*a, 0},{0,0}}]]
    = ...
    """

    summary_text = "formatted expression as MathML commands"

    def apply_mathml(self, expr, evaluation) -> Expression:
        "MakeBoxes[expr_, MathMLForm]"

        boxes = MakeBoxes(expr).evaluate(evaluation)
        try:
            mathml = boxes.boxes_to_mathml(evaluation=evaluation)
        except BoxError:
            evaluation.message(
                "General",
                "notboxes",
                Expression(SymbolFullForm, boxes).evaluate(evaluation),
            )
            mathml = ""
        is_a_picture = mathml[:6] == "<mtext"

        # mathml = '<math><mstyle displaystyle="true">%s</mstyle></math>' % mathml
        # #convert_box(boxes)
        query = evaluation.parse("Settings`$UseSansSerif")
        usesansserif = query.evaluate(evaluation).to_python()
        if not is_a_picture:
            if isinstance(usesansserif, bool) and usesansserif:
                mathml = '<mstyle mathvariant="sans-serif">%s</mstyle>' % mathml

        mathml = '<math display="block">%s</math>' % mathml  # convert_box(boxes)
        return Expression(SymbolRowBox, ListExpression(String(mathml)))


class PythonForm(Builtin):
    """
    <dl>
      <dt>'PythonForm[$expr$]'
      <dd>returns an approximate equivalent of $expr$ in Python, when that is possible. We assume
      that Python has SymPy imported. No explicit import will be include in the result.
    </dl>

    >> PythonForm[Infinity]
    = math.inf
    >> PythonForm[Pi]
    = sympy.pi
    >> E // PythonForm
    = sympy.E
    >> {1, 2, 3} // PythonForm
    = [1, 2, 3]
    """

    summary_text = "translate expressions as Python source code"
    # >> PythonForm[HoldForm[Sqrt[a^3]]]
    #  = sympy.sqrt{a**3} # or something like this

    def apply_python(self, expr, evaluation) -> Expression:
        "MakeBoxes[expr_, PythonForm]"

        try:
            # from trepan.api import debug; debug()
            python_equivalent = expr.to_python(python_form=True)
        except Exception:
            return
        return StringFromPython(python_equivalent)

    def apply(self, expr, evaluation) -> Expression:
        "PythonForm[expr_]"
        return self.apply_python(expr, evaluation)


class SympyForm(Builtin):
    """
    <dl>
      <dt>'SympyForm[$expr$]'
      <dd>returns an Sympy $expr$ in Python. Sympy is used internally
      to implement a number of Mathics functions, like Simplify.
    </dl>

    >> SympyForm[Pi^2]
    = pi**2
    >> E^2 + 3E // SympyForm
    = exp(2) + 3*E
    """

    summary_text = "translate expressions to SymPy"

    def apply_sympy(self, expr, evaluation) -> Optional[Expression]:
        "MakeBoxes[expr_, SympyForm]"

        try:
            sympy_equivalent = expr.to_sympy()
        except Exception:
            return
        return StringFromPython(sympy_equivalent)

    def apply(self, expr, evaluation) -> Expression:
        "SympyForm[expr_]"
        return self.apply_sympy(expr, evaluation)


class TeXForm(Builtin):
    r"""
    <dl>
      <dt>'TeXForm[$expr$]'
      <dd>displays $expr$ using TeX math mode commands.
    </dl>

    >> TeXForm[HoldForm[Sqrt[a^3]]]
     = \sqrt{a^3}

    #> {"hi","you"} //InputForm //TeXForm
     = \left\{\text{``hi''}, \text{``you''}\right\}

    #> TeXForm[a+b*c]
     = a+b c
    #> TeXForm[InputForm[a+b*c]]
     = a\text{ + }b*c
    """
    summary_text = "formatted expression as TeX commands"

    def apply_tex(self, expr, evaluation) -> Expression:
        "MakeBoxes[expr_, TeXForm]"
        boxes = MakeBoxes(expr).evaluate(evaluation)
        try:
            # Here we set ``show_string_characters`` to False, to reproduce
            # the standard behaviour in WMA. Remove this parameter to recover the
            # quotes in InputForm and FullForm
            tex = boxes.boxes_to_tex(
                show_string_characters=False, evaluation=evaluation
            )

            # Replace multiple newlines by a single one e.g. between asy-blocks
            tex = MULTI_NEWLINE_RE.sub("\n", tex)

            tex = tex.replace(" \uF74c", " \\, d")  # tmp hack for Integrate
        except BoxError:
            evaluation.message(
                "General",
                "notboxes",
                Expression(SymbolFullForm, boxes).evaluate(evaluation),
            )
            tex = ""
        return Expression(SymbolRowBox, ListExpression(String(tex)))
