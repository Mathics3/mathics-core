# -*- coding: utf-8 -*-

"""
Solving Recurrence Equations
"""

# This tells documentation how to sort this module
# Here we are also hiding "moments" since this erroneously appears at the top level.
sort_order = "mathics.builtin.solving-recurrence-equations"


import sympy

from mathics.builtin.base import Builtin

from mathics.core.atoms import IntegerM1
from mathics.core.attributes import constant
from mathics.core.convert.sympy import sympy_symbol_prefix, from_sympy
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, Symbol, SymbolPlus, SymbolTimes
from mathics.core.systemsymbols import SymbolFunction, SymbolRule


class RSolve(Builtin):
    """
    <dl>
    <dt>'RSolve[$eqn$, $a$[$n$], $n$]'
        <dd>solves a recurrence equation for the function '$a$[$n$]'.
    </dl>

    Solve a difference equation:
    >> RSolve[a[n] == a[n+1], a[n], n]
     = {{a[n] -> C[0]}}

    No boundary conditions gives two general paramaters:
    >> RSolve[{a[n + 2] == a[n]}, a, n]
     = {{a -> (Function[{n}, C[0] + C[1] (-1) ^ n])}}

    Include one boundary condition:
    >> RSolve[{a[n + 2] == a[n], a[0] == 1}, a, n]
     = ...
    ## Order of terms depends on intepreter:
    ## PyPy:    {{a -> (Function[{n}, 1 - C[1] + C[1] -1 ^ n])}}
    ## CPython: {{a -> (Function[{n}, 1 + C[1] -1 ^ n - C[1]])}

    Geta "pure function" solution for a with two boundary conditions:
    >> RSolve[{a[n + 2] == a[n], a[0] == 1, a[1] == 4}, a, n]
     = {{a -> (Function[{n}, 5 / 2 - 3 (-1) ^ n / 2])}}
    """

    messages = {
        "deqn": (
            "Equation or list of equations expected instead of `1` "
            "in the first argument `1`."
        ),
        "deqx": (
            "Supplied equations are not difference equations of the " "given functions."
        ),
        "dsfun": "`1` cannot be used as a function.",
        "dsvar": "`1` cannot be used as a variable.",
    }
    summary_text = "recurrence equations solver"

    def apply(self, eqns, a, n, evaluation):
        "RSolve[eqns_, a_, n_]"

        # TODO: Do this with rules?
        if not eqns.has_form("List", None):
            eqns = ListExpression(eqns)

        if len(eqns.elements) == 0:
            return

        for eqn in eqns.elements:
            if eqn.get_head_name() != "System`Equal":
                evaluation.message("RSolve", "deqn", eqn)
                return

        if (
            (isinstance(n, Atom) and not isinstance(n, Symbol))
            or n.get_head_name() in ("System`Plus", "System`Times", "System`Power")
            or constant & n.get_attributes(evaluation.definitions)
        ):
            # TODO: Factor out this check for dsvar into a separate
            # function. DSolve uses this too.
            evaluation.message("RSolve", "dsvar")
            return

        try:
            a.elements
            function_form = None
            func = a
        except AttributeError:
            func = Expression(a, n)
            function_form = ListExpression(n)

        if isinstance(func, Atom) or len(func.elements) != 1:
            evaluation.message("RSolve", "dsfun", a)

        if n not in func.elements:
            evaluation.message("DSolve", "deqx")

        # Seperate relations from conditions
        conditions = {}

        def is_relation(eqn):
            left, right = eqn.elements
            for le, ri in [(left, right), (right, left)]:
                if (
                    left.get_head_name() == func.get_head_name()
                    and len(left.elements) == 1  # noqa
                    and isinstance(le.elements[0].to_python(), int)
                    and ri.is_numeric(evaluation)
                ):

                    r_sympy = ri.to_sympy()
                    if r_sympy is None:
                        raise ValueError
                    conditions[le.elements[0].to_python()] = r_sympy
                    return False
            return True

        # evaluate is_relation on all elements to store conditions
        try:
            relations = [element for element in eqns.elements if is_relation(element)]
        except ValueError:
            return
        relation = relations[0]

        left, right = relation.elements
        relation = Expression(
            SymbolPlus, left, Expression(SymbolTimes, IntegerM1, right)
        ).evaluate(evaluation)

        sym_eq = relation.to_sympy(converted_functions={func.get_head_name()})
        if sym_eq is None:
            return
        sym_n = sympy.core.symbols(str(sympy_symbol_prefix + n.name))
        sym_func = sympy.Function(str(sympy_symbol_prefix + func.get_head_name()))(
            sym_n
        )

        sym_conds = {}
        for cond in conditions:
            sym_conds[
                sympy.Function(str(sympy_symbol_prefix + func.get_head_name()))(cond)
            ] = conditions[cond]

        try:
            # Sympy raises error when given empty conditions. Fixed in
            # upcomming sympy release.
            if sym_conds != {}:
                sym_result = sympy.rsolve(sym_eq, sym_func, sym_conds)
            else:
                sym_result = sympy.rsolve(sym_eq, sym_func)

            if not isinstance(sym_result, list):
                sym_result = [sym_result]
        except ValueError:
            return

        if function_form is None:
            return ListExpression(
                *[
                    ListExpression(Expression(SymbolRule, a, from_sympy(soln)))
                    for soln in sym_result
                ]
            )
        else:
            return ListExpression(
                *[
                    ListExpression(
                        Expression(
                            SymbolRule,
                            a,
                            Expression(SymbolFunction, function_form, from_sympy(soln)),
                        ),
                    )
                    for soln in sym_result
                ]
            )
