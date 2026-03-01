"""
Mathics3-specific Forms

Mathics3 provides a few forms that do not appear in WMA.

These provide conversion to Python or Python using Python-based libraries. This is facilited \
by Mathics3's implementation in Python.

"""

from typing import Optional

from mathics.builtin.forms.base import FormBaseClass
from mathics.core.atoms import StringFromPython
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol


class PythonForm(FormBaseClass):
    """
    <dl>
      <dt>'PythonForm'[$expr$]
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
    = (1, 2, 3)
    """

    in_outputforms = True
    in_printforms = True
    summary_text = "translate expressions as Python source code"
    # >> PythonForm[HoldForm[Sqrt[a^3]]]
    #  = sympy.sqrt{a**3} # or something like this

    def eval_python(self, expr, evaluation) -> Expression:
        "MakeBoxes[expr_, PythonForm]"

        def build_python_form(expr):
            if isinstance(expr, Symbol):
                return expr.to_sympy()
            return expr.to_python()

        try:
            python_equivalent = build_python_form(expr)
        except Exception:
            return
        return StringFromPython(python_equivalent)

    def eval(self, expr, evaluation) -> Expression:
        "PythonForm[expr_]"
        return self.eval_python(expr, evaluation)


class SympyForm(FormBaseClass):
    """
    <dl>
      <dt>'SympyForm'[$expr$]
      <dd>returns an Sympy $expr$ in Python. Sympy is used internally
      to implement a number of Mathics functions, like Simplify.
    </dl>

    >> SympyForm[Pi^2]
    = pi**2
    >> E^2 + 3E // SympyForm
    = exp(2) + 3*E
    """

    in_outputforms = True
    in_printforms = True
    summary_text = "translate expressions to SymPy"

    def eval_sympy(self, expr, evaluation) -> Optional[Expression]:
        "MakeBoxes[expr_, SympyForm]"

        try:
            sympy_equivalent = expr.to_sympy()
        except Exception:
            return
        return StringFromPython(sympy_equivalent)

    def eval(self, expr, evaluation) -> Expression:
        "SympyForm[expr_]"
        return self.eval_sympy(expr, evaluation)
