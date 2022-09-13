# -*- coding: utf-8 -*-

"""
Converts expressions from SymPy to Mathics expressions.
Conversion to SymPy is handled directly in BaseElement descendants.
"""

import sympy

from typing import Optional

BasicSympy = sympy.Expr


from mathics.core.symbols import (
    Symbol,
    SymbolFalse,
    SymbolPlus,
    SymbolPower,
    SymbolTimes,
    SymbolTrue,
    sympy_symbol_prefix,
    sympy_slot_prefix,
)
from mathics.core.systemsymbols import (
    SymbolC,
    SymbolEqual,
    SymbolFunction,
    SymbolGreater,
    SymbolGreaterEqual,
    SymbolIndeterminate,
    SymbolInfinity,
    SymbolLess,
    SymbolLessEqual,
    SymbolMatrixPower,
    SymbolO,
    SymbolPiecewise,
    SymbolSlot,
    SymbolUnequal,
)

from mathics.core.convert.matrix import matrix_data

SymbolPrime = Symbol("Prime")
SymbolRoot = Symbol("Root")
SymbolRootSum = Symbol("RootSum")


def is_Cn_expr(name) -> bool:
    if name.startswith(sympy_symbol_prefix) or name.startswith(sympy_slot_prefix):
        return False
    if not name.startswith("C"):
        return False
    n = name[1:]
    if n and n.isdigit():
        return True
    return False


def to_sympy_matrix(data, **kwargs) -> Optional[sympy.MutableDenseMatrix]:
    """Convert a Mathics matrix to one that can be used by Sympy.
    None is returned if we can't convert to a Sympy matrix.
    """
    if not isinstance(data, list):
        data = matrix_data(data)
    try:
        return sympy.Matrix(data)
    except (TypeError, AssertionError, ValueError):
        return None


class SympyExpression(BasicSympy):
    is_Function = True
    nargs = None

    def __new__(cls, *exprs):
        # sympy simplify may also recreate the object if simplification occurred
        # in the elements
        from mathics.core.expression import Expression

        if all(isinstance(expr, BasicSympy) for expr in exprs):
            # called with SymPy arguments
            obj = BasicSympy.__new__(cls, *exprs)
        elif len(exprs) == 1 and isinstance(exprs[0], Expression):
            # called with Mathics argument
            expr = exprs[0]
            sympy_head = expr.head.to_sympy()
            sympy_elements = [element.to_sympy() for element in expr.elements]
            if sympy_head is None or None in sympy_elements:
                return None
            obj = BasicSympy.__new__(cls, sympy_head, *sympy_elements)
            obj.expr = expr
        else:
            raise TypeError
        return obj

    """def new(self, *args):
        from mathics.core import expression

        expr = expression.Expression(from_sympy(args[0]),
            *(from_sympy(arg) for arg in args[1:]))
        return SympyExpression(expr)"""

    @property
    def func(self):
        class SympyExpressionFunc:
            def __new__(cls, *args):
                return SympyExpression(self.expr)
                # return SympyExpression(expression.Expression(self.expr.head,
                # *(from_sympy(arg) for arg in args[1:])))

        return SympyExpressionFunc

    def has_any_symbols(self, *syms) -> bool:
        result = any(arg.has_any_symbols(*syms) for arg in self.args)
        return result

    def _eval_subs(self, old, new):
        if self == old:
            return new
        old, new = from_sympy(old), from_sympy(new)
        old_name = old.get_name()
        if old_name:
            new_expr = self.expr.replace_vars({old_name: new})
            return SympyExpression(new_expr)
        return self

    def _eval_rewrite(self, pattern, rule, **hints):
        return self

    @property
    def is_commutative(self) -> bool:
        if all(getattr(t, "is_commutative", False) for t in self.args):
            return True
        else:
            return False

    def __str__(self) -> str:
        return "%s[%s]" % (super(SympyExpression, self).__str__(), self.expr)


class SympyPrime(sympy.Function):
    """
    A safe wrapper for sympy.prime
    """

    @classmethod
    def eval(cls, n):
        if n.is_Integer and n > 0:
            try:
                return sympy.prime(n)
            except Exception:
                # n is too big, SymPy doesn't know the n-th prime
                pass


def from_sympy(expr):
    from mathics.builtin import sympy_to_mathics
    from mathics.core.atoms import (
        Integer,
        Integer0,
        Integer1,
        Rational,
        Real,
        Complex,
        String,
        MachineReal,
    )
    from mathics.core.convert.expression import to_expression, to_mathics_list
    from mathics.core.expression import Expression
    from mathics.core.list import ListExpression
    from mathics.core.symbols import (
        Symbol,
        SymbolNull,
    )
    from mathics.core.number import machine_precision

    if isinstance(expr, (tuple, list)):
        return to_mathics_list(*expr, elements_conversion_fn=from_sympy)
    if isinstance(expr, int):
        return Integer(expr)
    if isinstance(expr, float):
        return Real(expr)
    if isinstance(expr, complex):
        return Complex(Real(expr.real), Real(expr.imag))
    if isinstance(expr, str):
        return String(expr)
    if expr is None:
        return SymbolNull
    if isinstance(expr, sympy.Matrix) or isinstance(expr, sympy.ImmutableMatrix):
        if len(expr.shape) == 2 and (expr.shape[1] == 1):
            # This is a vector (only one column)
            # Transpose and select first row to get result equivalent to Mathematica
            return to_mathics_list(
                *expr.T.tolist()[0], elements_conversion_fn=from_sympy
            )
        else:
            return to_mathics_list(*expr.tolist(), elements_conversion_fn=from_sympy)
    if isinstance(expr, sympy.MatPow):
        return Expression(
            SymbolMatrixPower, from_sympy(expr.base), from_sympy(expr.exp)
        )
    if expr.is_Atom:
        name = None
        if expr.is_Symbol:
            name = str(expr)
            if isinstance(expr, sympy.Dummy):
                name = name + ("__Dummy_%d" % expr.dummy_index)
                # Probably, this should be the value attribute
                return Symbol(name, sympy_dummy=expr)
            if is_Cn_expr(name):
                return Expression(SymbolC, Integer(int(name[1:])))
            if name.startswith(sympy_symbol_prefix):
                name = name[len(sympy_symbol_prefix) :]
            if name.startswith(sympy_slot_prefix):
                index = name[len(sympy_slot_prefix) :]
                return Expression(SymbolSlot, Integer(int(index)))
        elif expr.is_NumberSymbol:
            name = str(expr)
        if name is not None:
            builtin = sympy_to_mathics.get(name)
            if builtin is not None:
                name = builtin.get_name()
            return Symbol(name)
        elif isinstance(
            expr, (sympy.core.numbers.Infinity, sympy.core.numbers.ComplexInfinity)
        ):
            return Symbol(expr.__class__.__name__)
        elif isinstance(expr, sympy.core.numbers.NegativeInfinity):
            return Expression(SymbolTimes, Integer(-1), SymbolInfinity)
        elif isinstance(expr, sympy.core.numbers.ImaginaryUnit):
            return Complex(Integer0, Integer1)
        elif isinstance(expr, sympy.Integer):
            return Integer(int(expr))
        elif isinstance(expr, sympy.Rational):
            numerator, denominator = map(int, expr.as_numer_denom())
            if denominator == 0:
                if numerator > 0:
                    return SymbolInfinity
                elif numerator < 0:
                    return Expression(SymbolTimes, Integer(-1), SymbolInfinity)
                else:
                    assert numerator == 0
                    return SymbolIndeterminate
            return Rational(numerator, denominator)
        elif isinstance(expr, sympy.Float):
            if expr._prec == machine_precision:
                return MachineReal(float(expr))
            return Real(expr)
        elif isinstance(expr, sympy.core.numbers.NaN):
            return SymbolIndeterminate
        elif isinstance(expr, sympy.core.function.FunctionClass):
            return Symbol(str(expr))
        elif expr is sympy.true:
            return SymbolTrue
        elif expr is sympy.false:
            return SymbolFalse

    elif expr.is_number and all([x.is_Number for x in expr.as_real_imag()]):
        # Hack to convert 3 * I to Complex[0, 3]
        return Complex(*[from_sympy(arg) for arg in expr.as_real_imag()])
    elif expr.is_Add:
        return to_expression(
            SymbolPlus, *sorted([from_sympy(arg) for arg in expr.args])
        )
    elif expr.is_Mul:
        return to_expression(
            SymbolTimes, *sorted([from_sympy(arg) for arg in expr.args])
        )
    elif expr.is_Pow:
        return to_expression(SymbolPower, *[from_sympy(arg) for arg in expr.args])
    elif expr.is_Equality:
        return to_expression(SymbolEqual, *[from_sympy(arg) for arg in expr.args])

    elif isinstance(expr, SympyExpression):
        return expr.expr

    elif isinstance(expr, sympy.Piecewise):
        args = expr.args
        return Expression(
            SymbolPiecewise,
            ListExpression(
                *[
                    to_mathics_list(from_sympy(case), from_sympy(cond))
                    for case, cond in args
                ]
            ),
        )

    elif isinstance(expr, SympyPrime):
        return Expression(SymbolPrime, from_sympy(expr.args[0]))
    elif isinstance(expr, sympy.RootSum):
        return Expression(SymbolRootSum, from_sympy(expr.poly), from_sympy(expr.fun))
    elif isinstance(expr, sympy.PurePoly):
        coeffs = expr.coeffs()
        monoms = expr.monoms()
        result = []
        for coeff, monom in zip(coeffs, monoms):
            factors = []
            if coeff != 1:
                factors.append(from_sympy(coeff))
            for index, exp in enumerate(monom):
                if exp != 0:
                    slot = Expression(SymbolSlot, Integer(index + 1))
                    if exp == 1:
                        factors.append(slot)
                    else:
                        factors.append(Expression(SymbolPower, slot, from_sympy(exp)))
            if factors:
                result.append(Expression(SymbolTimes, *factors))
            else:
                result.append(Integer1)
        return Expression(SymbolFunction, Expression(SymbolPlus, *result))
    elif isinstance(expr, sympy.CRootOf):
        try:
            e, i = expr.args
        except ValueError:
            return SymbolNull

        try:
            e = sympy.PurePoly(e)
        except Exception:
            pass

        return Expression(SymbolRoot, from_sympy(e), Integer(i + 1))
    elif isinstance(expr, sympy.Lambda):
        vars = [
            sympy.Symbol("%s%d" % (sympy_slot_prefix, index + 1))
            for index in range(len(expr.variables))
        ]
        return Expression(SymbolFunction, from_sympy(expr(*vars)))

    elif expr.is_Function or isinstance(
        expr, (sympy.Integral, sympy.Derivative, sympy.Sum, sympy.Product)
    ):
        if isinstance(expr, sympy.Integral):
            name = "Integral"
        elif isinstance(expr, sympy.Derivative):
            name = "Derivative"
            margs = []
            for arg in expr.args:
                # parse (x, 1) ==> just x for test_conversion
                # IMHO this should be removed in future versions
                if isinstance(arg, sympy.Tuple):
                    if arg[1] == 1:
                        margs.append(from_sympy(arg[0]))
                    else:
                        margs.append(from_sympy(arg))
                else:
                    margs.append(from_sympy(arg))
            builtin = sympy_to_mathics.get(name)
            return builtin.from_sympy(name, margs)

        elif isinstance(expr, sympy.sign):
            name = "Sign"
        else:
            name = expr.func.__name__
            if is_Cn_expr(name):
                return Expression(
                    Expression(Symbol("C"), Integer(int(name[1:]))),
                    *[from_sympy(arg) for arg in expr.args]
                )
            if name.startswith(sympy_symbol_prefix):
                name = name[len(sympy_symbol_prefix) :]
        args = [from_sympy(arg) for arg in expr.args]
        builtin = sympy_to_mathics.get(name)
        if builtin is not None:
            return builtin.from_sympy(name, args)
        return Expression(Symbol(name), *args)

    elif isinstance(expr, sympy.Tuple):
        return to_mathics_list(*expr.args, elements_conversion_fn=from_sympy)

    # elif isinstance(expr, sympy.Sum):
    #    return Expression('Sum', )

    elif isinstance(expr, sympy.LessThan):
        return to_expression(
            SymbolLessEqual, *expr.args, elements_conversion_fn=from_sympy
        )
    elif isinstance(expr, sympy.StrictLessThan):
        return to_expression(SymbolLess, *expr.args, elements_conversion_fn=from_sympy)
    elif isinstance(expr, sympy.GreaterThan):
        return to_expression(
            SymbolGreaterEqual, *expr.args, elements_conversion_fn=from_sympy
        )
    elif isinstance(expr, sympy.StrictGreaterThan):
        return to_expression(
            SymbolGreater, *expr.args, elements_conversion_fn=from_sympy
        )
    elif isinstance(expr, sympy.Unequality):
        return to_expression(
            SymbolUnequal, *expr.args, elements_conversion_fn=from_sympy
        )
    elif isinstance(expr, sympy.Equality):
        return to_expression(SymbolEqual, *expr.args, elements_conversion_fn=from_sympy)

    elif isinstance(expr, sympy.O):
        if expr.args[0].func == sympy.core.power.Pow:
            [var, power] = [from_sympy(arg) for arg in expr.args[0].args]
            o = Expression(SymbolO, var)
            return Expression(SymbolPower, o, power)
        else:
            return Expression(SymbolO, from_sympy(expr.args[0]))
    else:
        raise ValueError(
            "Unknown SymPy expression: {} (instance of {})".format(
                expr, str(expr.__class__)
            )
        )
