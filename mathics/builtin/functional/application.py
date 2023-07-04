# -*- coding: utf-8 -*-

"""
Function Application
"""

# This tells documentation how to sort this module
sort_order = "mathics.builtin.function-application"


from itertools import chain

from mathics.builtin.base import Builtin, PostfixOperator
from mathics.core.attributes import A_HOLD_ALL, A_N_HOLD_ALL, A_PROTECTED
from mathics.core.convert.sympy import SymbolFunction
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol


class Function(PostfixOperator):
    """
    <dl>
      <dt>'Function[$body$]'
      <dt>'$body$ &'
      <dd>represents a pure function with parameters '#1', '#2', etc.

      <dt>'Function[{$x1$, $x2$, ...}, $body$]'
      <dd>represents a pure function with parameters $x1$, $x2$, etc.

      <dt>'Function[{$x1$, $x2$, ...}, $body$, $attr$]'
      <dd>assume that the function has the attributes $attr$.
    </dl>

    >> f := # ^ 2 &
    X> f[3]
     = 9
    X> #^3& /@ {1, 2, 3}
     = {1, 8, 27}
    X> #1+#2&[4, 5]
     = 9

    You can use 'Function' with named parameters:
    >> Function[{x, y}, x * y][2, 3]
     = 6

    Parameters are renamed, when necessary, to avoid confusion:
    >> Function[{x}, Function[{y}, f[x, y]]][y]
     = Function[{y$}, f[y, y$]]
    >> Function[{y}, f[x, y]] /. x->y
     = Function[{y}, f[y, y]]
    >> Function[y, Function[x, y^x]][x][y]
     = x ^ y
    >> Function[x, Function[y, x^y]][x][y]
     = x ^ y

    Slots in inner functions are not affected by outer function application:
    >> g[#] & [h[#]] & [5]
     = g[h[5]]

    #> g[x_,y_] := x+y
    #> g[Sequence@@Slot/@Range[2]]&[1,2]
     = #1 + #2
    #> Evaluate[g[Sequence@@Slot/@Range[2]]]&[1,2]
     = 3


    In the evaluation process, the attributes associated with an Expression are \
    determined by its Head.  If the Head is also a non-atomic Expression, in general,\
    no Attribute is assumed. In particular, it is what happens when the head \
    of the expression has the form:

    ``Function[$body$]``
    or:
    ``Function[$vars$, $body$]``

    >> h := Function[{x}, Hold[1+x]]
    >> h[1 + 1]
     = Hold[1 + 2]

    Notice that $Hold$ in the body prevents the evaluation of $1+x$, but not \
    the evaluation of $1+1$. To avoid that evaluation, of its arguments, the Head \
    should have the attribute 'HoldAll'. This behavior can be obtained by using the \
    three arguments form version of this expression:

    >> h:= Function[{x}, Hold[1+x], HoldAll]
    >> h[1+1]
     = Hold[1 + (1 + 1)]

    In this case, the attribute 'HoldAll' is assumed, \
    preventing the evaluation of the argument $1+1$ before passing it \
    to the function body.
    """

    operator = "&"
    precedence = 90
    attributes = A_HOLD_ALL | A_PROTECTED

    messages = {
        "slot": "`1` should contain a positive integer.",
        "slotn": "Slot number `1` cannot be filled.",
        "fpct": "Too many parameters to be filled.",
        "iassoc": "Invalid association item `1`",
    }
    summary_text = "define an anonymous (pure) function"

    def eval_slots(self, body, args, evaluation: Evaluation):
        "Function[body_][args___]"

        args = list(chain([Expression(SymbolFunction, body)], args.get_sequence()))
        return body.replace_slots(args, evaluation)

    def eval_named(self, vars, body, args, evaluation: Evaluation):
        "Function[vars_, body_][args___]"

        if vars.has_form("List", None):
            vars = vars.elements
        else:
            vars = [vars]

        # print([v.get_head_name()=="System`Pattern" or isinstance(v, Symbol) for v in vars])
        args = args.get_sequence()
        if len(vars) > len(args):
            evaluation.message("Function", "fpct")
        else:
            # Allows to use both symbols or Blank patterns (z_Complex) to state the symbol.
            # this is not included in WL, and here does not have any impact, but it is needed for
            # translating the function to a compiled version.
            var_names = (
                var.get_name()
                if isinstance(var, Symbol)
                else var.elements[0].get_name()
                for var in vars
            )
            vars = dict(list(zip(var_names, args[: len(vars)])))
            try:
                return body.replace_vars(vars)
            except Exception:
                return

    # Not sure if DRY is possible here...
    def eval_named_attr(self, vars, body, attr, args, evaluation: Evaluation):
        "Function[vars_, body_, attr_][args___]"
        if vars.has_form("List", None):
            vars = vars.elements
        else:
            vars = [vars]

        args = args.get_sequence()
        if len(vars) > len(args):
            evaluation.message("Function", "fpct")
        else:
            vars = dict(list(zip((var.get_name() for var in vars), args[: len(vars)])))
            try:
                return body.replace_vars(vars)
            except Exception:
                return


class Slot(Builtin):
    """
    <dl>
      <dt>'#$n$'
      <dd>represents the $n$th argument to a pure function.

      <dt>'#'
      <dd>is short-hand for '#1'.

      <dt>'#0'
      <dd>represents the pure function itself.
    </dl>

    X> #
     = #1

    Unused arguments are simply ignored:
    >> {#1, #2, #3}&[1, 2, 3, 4, 5]
     = {1, 2, 3}

    Recursive pure functions can be written using '#0':
    >> If[#1<=1, 1, #1 #0[#1-1]]& [10]
     = 3628800

    #> # // InputForm
     = #1

    #> #0 // InputForm
     = #0
    """

    attributes = A_N_HOLD_ALL | A_PROTECTED
    rules = {
        "Slot[]": "Slot[1]",
        "MakeBoxes[Slot[n_Integer?NonNegative],"
        "  f:StandardForm|TraditionalForm|InputForm|OutputForm]": (
            '"#" <> ToString[n]'
        ),
    }
    summary_text = "one argument of a pure function"


class SlotSequence(Builtin):
    """
    <dl>
      <dt>'##'
      <dd>is the sequence of arguments supplied to a pure function.

      <dt>'##$n$'
      <dd>starts with the $n$th argument.
    </dl>

    >> Plus[##]& [1, 2, 3]
     = 6
    >> Plus[##2]& [1, 2, 3]
     = 5

    >> FullForm[##]
     = SlotSequence[1]

    #> ## // InputForm
     = ##1
    """

    attributes = A_N_HOLD_ALL | A_PROTECTED

    rules = {
        "SlotSequence[]": "SlotSequence[1]",
        "MakeBoxes[SlotSequence[n_Integer?Positive],"
        "f:StandardForm|TraditionalForm|InputForm|OutputForm]": ('"##" <> ToString[n]'),
    }
    summary_text = "the full sequence of arguments of a pure function"
