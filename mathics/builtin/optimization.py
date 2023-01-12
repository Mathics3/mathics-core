# -*- coding: utf-8 -*-
"""Mathematical Optimization

Mathematical optimization is the selection of a best element, with regard to \
some criterion, from some set of available alternatives.

Optimization problems of sorts arise in all quantitative disciplines from \
computer science and engineering to operations research and economics, \
and the development of solution methods has been of interest in mathematics \
for centuries.

We intend to provide local and global optimization techniques, both numeric \
and symbolic.
"""

# This tells documentation how to sort this module
sort_order = "mathics.builtin.mathematical-optimization"

import sympy

from mathics.builtin.base import Builtin
from mathics.core.atoms import IntegerM1
from mathics.core.attributes import A_CONSTANT, A_PROTECTED, A_READ_PROTECTED
from mathics.core.convert.python import from_python
from mathics.core.convert.sympy import from_sympy
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, Symbol
from mathics.core.systemsymbols import SymbolRule

SymbolMinimize = Symbol("Minimize")


class Maximize(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Maximize.html</url>

    <dl>
      <dt>'Maximize[$f$, $x$]'
      <dd>compute the maximum of $f$ respect $x$ that change between \
      $a$ and $b$.
    </dl>

    >> Maximize[-2 x^2 - 3 x + 5, x]
     = {{49 / 8, {x -> -3 / 4}}}

    #>> Maximize[1 - (x y - 3)^2, {x, y}]
     = {{1, {x -> 3, y -> 1}}}

    #>> Maximize[{x - 2 y, x^2 + y^2 <= 1}, {x, y}]
     = {{Sqrt[5], {x -> Sqrt[5] / 5, y -> -2 Sqrt[5] / 5}}}
    """

    attributes = A_PROTECTED | A_READ_PROTECTED
    summary_text = "compute the maximum of a function"

    def eval(self, f, vars, evaluation: Evaluation):
        "Maximize[f_?NotListQ, vars_]"

        dual_f = f.to_sympy() * (-1)

        dual_solutions = (
            Expression(SymbolMinimize, from_sympy(dual_f), vars)
            .evaluate(evaluation)
            .elements
        )

        solutions = []
        for dual_solution in dual_solutions:
            solution_elements = dual_solution.elements
            solutions.append([solution_elements[0] * IntegerM1, solution_elements[1]])

        return from_python(solutions)

    def eval_constraints(self, f, vars, evaluation: Evaluation):
        "Maximize[f_List, vars_]"

        constraints = [function for function in f.elements]
        constraints[0] = from_sympy(constraints[0].to_sympy() * IntegerM1)

        dual_solutions = (
            Expression(SymbolMinimize, constraints, vars).evaluate(evaluation).elements
        )

        solutions = []
        for dual_solution in dual_solutions:
            solution_elements = dual_solution.elements
            solutions.append([solution_elements[0] * IntegerM1, solution_elements[1]])

        return from_python(solutions)


class Minimize(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Minimize.html</url>

    <dl>
    <dt>'Minimize[$f$, $x$]'
        <dd>compute the minimum of $f$ respect $x$ that change between \
        $a$ and $b$.
    </dl>

    >> Minimize[2 x^2 - 3 x + 5, x]
     = {{31 / 8, {x -> 3 / 4}}}

    #>> Minimize[(x y - 3)^2 + 1, {x, y}]
     = {{1, {x -> 3, y -> 1}}}

    #>> Minimize[{x - 2 y, x^2 + y^2 <= 1}, {x, y}]
     = {{-Sqrt[5], {x -> -Sqrt[5] / 5, y -> 2 Sqrt[5] / 5}}}
    """

    attributes = A_PROTECTED | A_READ_PROTECTED
    summary_text = "compute the minimum of a function"

    def eval_onevariable(self, f, x, evaluation: Evaluation):
        "Minimize[f_?NotListQ, x_?NotListQ]"

        sympy_x = x.to_sympy()
        sympy_f = f.to_sympy()

        derivative = sympy.diff(sympy_f, sympy_x)
        second_derivative = sympy.diff(derivative, sympy_x)
        candidates = sympy.solve(derivative, sympy_x, real=True, dict=True)

        minimum_list = []

        for candidate in candidates:
            value = second_derivative.subs(candidate)
            if value.is_real and value > 0:

                if candidate is not list:
                    candidate = candidate

                minimum_list.append([candidate[sympy_x], sympy_f.subs(candidate)])

        return ListExpression(
            *(
                ListExpression(
                    from_sympy(minimum[1]),
                    ListExpression((Expression(SymbolRule, x, from_sympy(minimum[0])))),
                )
                for minimum in minimum_list
            )
        )

    def eval_multiplevariable(self, f, vars, evaluation: Evaluation):
        "Minimize[f_?NotListQ, vars_List]"

        head_name = vars.get_head_name()
        vars_or = vars
        vars = vars.elements
        for var in vars:
            if (
                (isinstance(var, Atom) and not isinstance(var, Symbol))
                or head_name in ("System`Plus", "System`Times", "System`Power")  # noqa
                or A_CONSTANT & var.get_attributes(evaluation.definitions)
            ):

                evaluation.message("Minimize", "ivar", vars_or)
                return

        vars_sympy = [var.to_sympy() for var in vars]
        sympy_f = f.to_sympy()

        jacobian = [sympy.diff(sympy_f, x) for x in vars_sympy]
        hessian = sympy.Matrix(
            [[sympy.diff(deriv, x) for x in vars_sympy] for deriv in jacobian]
        )

        candidates_tmp = sympy.solve(jacobian, vars_sympy, dict=True)
        candidates = []

        for candidate in candidates_tmp:
            if len(candidate) != len(vars_sympy):
                for variable in candidate:
                    for i in range(len(candidate), len(vars_sympy)):
                        candidate[variable] = candidate[variable].subs(
                            {vars_sympy[i]: 1}
                        )

                for i in range(len(candidate), len(vars_sympy)):
                    candidate[vars_sympy[i]] = 1

            candidates.append(candidate)

        minimum_list = []

        for candidate in candidates:
            eigenvals = hessian.subs(candidate).eigenvals()

            positives_eigenvalues = 0
            negatives_eigenvalues = 0

            for val in eigenvals:
                if val.is_real:
                    if val < 0:
                        negatives_eigenvalues += 1
                    elif val >= 0:
                        positives_eigenvalues += 1

            if positives_eigenvalues + negatives_eigenvalues != len(eigenvals):
                continue

            if positives_eigenvalues == len(eigenvals):
                minimum_list.append(candidate)

        return ListExpression(
            *(
                ListExpression(
                    from_sympy(sympy_f.subs(minimum).simplify()),
                    [
                        Expression(
                            SymbolRule,
                            from_sympy(list(minimum.keys())[i]),
                            from_sympy(list(minimum.values())[i]),
                        )
                        for i in range(len(vars_sympy))
                    ],
                )
                for minimum in minimum_list
            )
        )

    def eval_constraints(self, f, vars, evaluation: Evaluation):
        "Minimize[f_List, vars_List]"
        head_name = vars.get_head_name()
        vars_or = vars
        vars = vars.elements
        for var in vars:
            if (
                (isinstance(var, Atom) and not isinstance(var, Symbol))
                or head_name in ("System`Plus", "System`Times", "System`Power")  # noqa
                or A_CONSTANT & var.get_attributes(evaluation.definitions)
            ):

                evaluation.message("Minimize", "ivar", vars_or)
                return

        vars_sympy = [var.to_sympy() for var in vars]
        constraints = [function for function in f.elements]
        objective_function = constraints[0].to_sympy()

        constraints = constraints[1:]

        g_functions = []
        h_functions = []

        g_variables = []
        h_variables = []

        for constraint in constraints:
            left, right = constraint.elements
            head_name = constraint.get_head_name()

            left = left.to_sympy()
            right = right.to_sympy()

            if head_name == "System`LessEqual" or head_name == "System`Less":
                eq = left - right
                eq = sympy.together(eq)
                eq = sympy.cancel(eq)

                g_functions.append(eq)
                g_variables.append(sympy.Symbol("kkt_g" + str(len(g_variables))))

            elif head_name == "System`GreaterEqual" or head_name == "System`Greater":
                eq = -1 * (left - right)
                eq = sympy.together(eq)
                eq = sympy.cancel(eq)

                g_functions.append(eq)
                g_variables.append(sympy.Symbol("kkt_g" + str(len(g_variables))))

            elif head_name == "System`Equal":
                eq = left - right
                eq = sympy.together(eq)
                eq = sympy.cancel(eq)

                h_functions.append(eq)
                h_variables.append(sympy.Symbol("kkt_h" + str(len(h_variables))))

        equations = []

        for variable in vars_sympy:
            equation = sympy.diff(objective_function, variable)

            for i in range(len(g_variables)):
                g_variable = g_variables[i]
                g_function = g_functions[i]

                equation = equation + g_variable * sympy.diff(g_function, variable)

            for i in range(len(h_variables)):
                h_variable = h_variables[i]
                h_function = h_functions[i]

                equation = equation + h_variable * sympy.diff(h_function, variable)

            equations.append(equation)

        for i in range(len(g_variables)):
            g_variable = g_variables[i]
            g_function = g_functions[i]

            equations.append(g_variable * g_function)

        for i in range(len(h_variables)):
            h_variable = h_variables[i]
            h_function = h_functions[i]

            equations.append(h_variable * h_function)

        all_variables = vars_sympy + g_variables + h_variables

        candidates_tmp = sympy.solve(equations, all_variables, dict=True)
        candidates = []

        for candidate in candidates_tmp:
            if len(candidate) != len(vars_sympy):
                for variable in candidate:
                    for i in range(len(candidate), len(vars_sympy)):
                        candidate[variable] = candidate[variable].subs(
                            {vars_sympy[i]: 1}
                        )
                for i in range(len(candidate), len(vars_sympy)):
                    candidate[vars_sympy[i]] = 1

            candidates.append(candidate)

        kkt_candidates = []

        for candidate in candidates:
            kkt_ok = True

            sum_constraints = 0

            for i in range(len(g_variables)):
                g_variable = g_variables[i]
                g_function = g_functions[i]

                if candidate[g_variable] < 0:
                    kkt_ok = False

                if candidate[g_variable] * g_function.subs(candidate) != 0:
                    kkt_ok = False

                sum_constraints = sum_constraints + candidate[g_variable]

            for i in range(len(h_variables)):
                h_variable = h_variables[i]
                h_function = h_functions[i]

                sum_constraints = sum_constraints + abs(candidate[h_variable])

            if sum_constraints <= 0:
                kkt_ok = False

            if not kkt_ok:
                continue

            kkt_candidates.append(candidate)

        hessian = sympy.Matrix(
            [[sympy.diff(deriv, x) for x in all_variables] for deriv in equations]
        )

        for i in range(0, len(all_variables) - len(vars_sympy)):
            hessian.col_del(len(all_variables) - i - 1)
            hessian.row_del(len(all_variables) - i - 1)

        minimum_list = []

        for candidate in kkt_candidates:
            eigenvals = hessian.subs(candidate).eigenvals()

            positives_eigenvalues = 0
            negatives_eigenvalues = 0

            for val in eigenvals:
                val = complex(sympy.N(val, chop=True))

                if val.imag == 0:
                    val = val.real
                    if val < 0:
                        negatives_eigenvalues += 1
                    elif val > 0:
                        positives_eigenvalues += 1

            if positives_eigenvalues + negatives_eigenvalues != len(eigenvals):
                continue

            if positives_eigenvalues == len(eigenvals):
                for g_variable in g_variables:
                    del candidate[g_variable]
                for h_variable in h_variables:
                    del candidate[h_variable]

                minimum_list.append(candidate)

        return ListExpression(
            *(
                ListExpression(
                    from_sympy(objective_function.subs(minimum).simplify()),
                    [
                        Expression(
                            SymbolRule,
                            from_sympy(list(minimum.keys())[i]),
                            from_sympy(list(minimum.values())[i]),
                        )
                        for i in range(len(vars_sympy))
                    ],
                )
                for minimum in minimum_list
            )
        )
