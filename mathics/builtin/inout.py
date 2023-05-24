"""
Input and Output
"""

import re

from mathics.builtin.base import Builtin, Predefined
from mathics.core.attributes import A_NO_ATTRIBUTES
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolNull
from mathics.core.systemsymbols import SymbolRow

MULTI_NEWLINE_RE = re.compile(r"\n{2,}")

SymbolNumberForm = Symbol("System`NumberForm")
SymbolSuperscriptBox = Symbol("System`SuperscriptBox")
SymbolTableDepth = Symbol("TableDepth")


class Echo_(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Echo_.html</url>

    <dl>
      <dt>'$Echo'
      <dd>gives a list of files and pipes to which all input is echoed.

    </dl>
    """

    attributes = A_NO_ATTRIBUTES
    name = "$Echo"
    rules = {"$Echo": "{}"}
    summary_text = "files and pipes that echoes the input"


class Print(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Print.html</url>

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

    def eval(self, expr, evaluation: Evaluation):
        "Print[expr__]"

        expr = expr.get_sequence()
        expr = Expression(SymbolRow, ListExpression(*expr))
        evaluation.print_out(expr)
        return SymbolNull
