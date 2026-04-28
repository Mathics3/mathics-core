# -*- coding: utf-8 -*-

"""
Converts expressions from SymPy to Mathics3 expressions.
Conversion to SymPy is handled directly in BaseElement descendants.
"""
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple, Union, cast

import sympy
from sympy import (
    Dummy as Sympy_Dummy,
    Symbol as Sympy_Symbol,
    false as SympyFalse,
    true as SympyTrue,
)
from sympy.calculus.accumulationbounds import AccumulationBounds
from sympy.core.singleton import S

from mathics.core.atoms import (
    MATHICS3_COMPLEX_I,
    Complex,
    Integer,
    Integer0,
    Integer1,
    IntegerM1,
    MachineReal,
    Rational,
    RationalOneHalf,
    Real,
    String,
)
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.matrix import matrix_data
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.expression_predefined import (
    MATHICS3_COMPLEX_INFINITY,
    MATHICS3_INFINITY,
    MATHICS3_NEG_INFINITY,
)
from mathics.core.list import ListExpression
from mathics.core.number import FP_MANTISA_BINARY_DIGITS
from mathics.core.symbols import (
    SYMPY_SLOT_PREFIX,
    SYMPY_SYMBOL_PREFIX,
    Symbol,
    SymbolFalse,
    SymbolNull,
    SymbolPlus,
    SymbolPower,
    SymbolTimes,
    SymbolTrue,
    sympy_name,
)
from mathics.core.systemsymbols import (
    SymbolC,
    SymbolCatalan,
    SymbolE,
    SymbolEqual,
    SymbolEulerGamma,
    SymbolFunction,
    SymbolGoldenRatio,
    SymbolGreater,
    SymbolGreaterEqual,
    SymbolIndeterminate,
    SymbolLess,
    SymbolLessEqual,
    SymbolMatrixPower,
    SymbolO,
    SymbolPi,
    SymbolPiecewise,
    SymbolSlot,
    SymbolUnequal,
)

if TYPE_CHECKING:
    from mathics.core.builtin import SympyObject

BasicSympy = sympy.Expr


SymbolPrime = Symbol("Prime")
SymbolRoot = Symbol("Root")
SymbolRootSum = Symbol("RootSum")


mathics_to_sympy: Dict[str, "SympyObject"] = {}  # here we have: name -> sympy object
sympy_to_mathics: Dict[str, "SympyObject"] = {}


sympy_singleton_to_mathics = {
    None: SymbolNull,
    S.Catalan: SymbolCatalan,
    S.ComplexInfinity: MATHICS3_COMPLEX_INFINITY,
    S.EulerGamma: SymbolEulerGamma,
    S.Exp1: SymbolE,
    S.GoldenRatio: SymbolGoldenRatio,
    S.Half: RationalOneHalf,
    S.ImaginaryUnit: MATHICS3_COMPLEX_I,
    S.Infinity: MATHICS3_INFINITY,
    S.NaN: SymbolIndeterminate,
    S.NegativeInfinity: MATHICS3_NEG_INFINITY,
    S.NegativeOne: IntegerM1,
    S.One: Integer1,
    S.Pi: SymbolPi,
    S.Zero: Integer0,
    SympyFalse: SymbolFalse,
    SympyTrue: SymbolTrue,
}


mathics_to_sympy_singleton = {
    key: val for val, key in sympy_singleton_to_mathics.items()
}


def sympy_decode_mathics_symbol_name(name: str) -> str:
    """
    Remove the Prefix for Mathics3 symbols
    and restore the context separator character.
    """
    if name.startswith(SYMPY_SYMBOL_PREFIX):
        return name[len(SYMPY_SYMBOL_PREFIX) :].replace("_", "`")
    return name


def is_Cn_expr(name: str) -> bool:
    """Check if name is of the form {prefix}Cnnn"""
    if name.startswith(SYMPY_SYMBOL_PREFIX) or name.startswith(SYMPY_SLOT_PREFIX):
        return False
    if not name.startswith("C"):
        return False
    number = name[1:]
    return number != "" and number.isdigit()


def to_sympy_matrix(data, **__) -> Optional[sympy.MutableDenseMatrix]:
    """Convert a Mathics3 matrix to one that can be used by Sympy.
    None is returned if we can't convert to a Sympy matrix.
    """
    if not isinstance(data, list):
        data = matrix_data(data)
    try:
        return sympy.Matrix(data)
    except (TypeError, AssertionError, ValueError):
        return None


class SympyExpression(sympy.Expr):
    """A Sympy expression with an associated Mathics3 expression"""

    is_Function = True
    nargs = None
    expr: Expression

    def __new__(cls, *exprs, **kwargs):
        # sympy simplify may also recreate the object if simplification occurred
        # in the elements

        if all(isinstance(expr, BasicSympy) for expr in exprs):
            # called with SymPy arguments
            obj = super().__new__(cls, *exprs)
            obj.expr = None
        elif len(exprs) == 1 and isinstance(exprs[0], Expression):
            # called with Mathics3 argument
            expr = exprs[0]
            sympy_head = expr.head.to_sympy()
            if kwargs.get("convert_functions_for_polynomialq", False):
                sympy_elements = []
            else:
                sympy_elements = [
                    element.to_sympy(**kwargs) for element in expr.elements
                ]
            if sympy_head is None or None in sympy_elements:
                return None
            obj = super().__new__(cls, sympy_head, *sympy_elements)
            obj.expr = expr
        else:
            raise TypeError
        return obj

    @property
    def func(self):
        class SympyExpressionFunc:
            """A class to mimic the behavior of sympy.Function"""

            def __new__(cls, *_):
                return SympyExpression(self.expr)
                # return SympyExpression(expression.Expression(self.expr.head,
                # *(from_sympy(arg) for arg in args[1:])))

        return SympyExpressionFunc

    def has_any_symbols(self, *syms) -> bool:
        """Check if any of the symbols in syms appears in the expression."""
        result = any(
            arg.has_any_symbols(*syms)
            for arg in self.args
            if isinstance(arg, SympyExpression)
        )
        return result

    def _eval_subs(self, old, new):
        """Replace occurencies of old by new in self."""
        if self == old:
            return new
        old, new = from_sympy(old), from_sympy(new)
        old_name = old.get_name()
        if old_name:
            new_expr = self.expr.replace_vars({old_name: new})
            return SympyExpression(new_expr)
        return self

    def _eval_rewrite(self, rule, args, **hints):
        return self

    @property
    def is_commutative(self) -> Optional[bool]:
        """Check if the arguments are commutative."""
        return all(getattr(t, "is_commutative", False) for t in self.args)

    @is_commutative.setter
    def is_commutative(self, value: bool) -> None:
        return

    def __str__(self) -> str:
        return f"{super().__str__()}[{self.expr}])"


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
        return None


def expression_to_sympy(expr: Expression, **kwargs):
    """
    Convert `expr` to its sympy form.
    """
    if len(expr.elements) > 0:
        head_name = expr.get_head_name()
        if head_name.startswith("Global`"):
            if kwargs.get("convert_all_global_functions", False):
                if expr.get_head_name().startswith("Global`"):
                    return expr._as_sympy_function(**kwargs)

        functions = kwargs.get("converted_functions", [])
        if head_name in functions:
            return expr._as_sympy_function(**kwargs)

    lookup_name = expr.get_lookup_name()
    builtin = mathics_to_sympy.get(lookup_name)

    if builtin is not None:
        sympy_expr = builtin.to_sympy(expr, **kwargs)
        if sympy_expr is not None:
            return sympy_expr
    elif exc := kwargs.get("raise_on_error", None):
        raise exc(f"{lookup_name} not registered in mathics_to_sympy")
    return SympyExpression(expr, **kwargs)


def symbol_to_sympy(symbol: Symbol, **kwargs) -> Sympy_Symbol:
    """
    Convert `symbol` to its sympy form.
    """

    result = mathics_to_sympy_singleton.get(symbol, None)
    if result is not None:
        return result

    builtin = mathics_to_sympy.get(symbol.name)
    if builtin is None or not builtin.sympy_name or not builtin.is_constant():  # nopep8
        if symbol in kwargs.get("dummies", {}):
            return Sympy_Dummy(sympy_name(symbol))
        return Sympy_Symbol(sympy_name(symbol))
    return builtin.to_sympy(symbol, **kwargs)


def to_numeric_sympy_args(mathics_args: BaseElement, evaluation) -> list:
    """
    Convert Mathics3 arguments, such as the arguments in an evaluation
    method a Python list that is sutiable for feeding as arguments
    into SymPy.

    We make use of fast conversions for literals.
    """
    from mathics.eval.numerify import numerify

    if mathics_args.is_literal:
        assert hasattr(mathics_args, "value")
        sympy_args = [mathics_args.value]
    else:
        args = numerify(mathics_args, evaluation).get_sequence()
        sympy_args = [a.to_sympy() for a in args]

    return sympy_args


def from_sympy_matrix(
    expr: Union[sympy.Matrix, sympy.ImmutableMatrix, sympy.Array],
) -> ListExpression:
    """
    Convert `expr` of the type sympy.Matrix or sympy.ImmutableMatrix to
    a Mathics3 list.
    """
    if len(expr.shape) == 2 and (expr.shape[1] == 1):
        # This is a vector (only one column)
        # Transpose and select first row to get result equivalent to Mathematica
        return to_mathics_list(*expr.T.tolist()[0], elements_conversion_fn=from_sympy)

    return to_mathics_list(*expr.tolist(), elements_conversion_fn=from_sympy)


"""
sympy_conversion_by_type = {
    complex: lambda expr: Complex(Real(expr.real), Real(expr.imag)),
    int: lambda x: Integer(x),
    float: lambda x: Real(x),
    tuple: lambda expr: to_mathics_list(*expr, elements_conversion_fn=from_sympy),
    list: lambda expr: to_mathics_list(*expr, elements_conversion_fn=from_sympy),
    str: lambda x: String(x),
    sympy.Matrix :from_sympy_matrix,
    sympy.ImmutableMatrix :from_sympy_matrix,
    sympy.MatPow: lambda expr: Expression(
            SymbolMatrixPower, from_sympy(expr.base), from_sympy(expr.exp)
        ),
    SympyExpression: lambda expr: expr.expr,
    SympyPrime: lambda expr: Expression(SymbolPrime, from_sympy(expr.args[0])),
    sympy.RootSum: lambda expr: Expression(SymbolRootSum, from_sympy(expr.poly), from_sympy(expr.fun)),
    sympy.Tuple: lambda expr: to_mathics_list(*expr, elements_conversion_fn=from_sympy),
}

"""

# def new_from_sympy(expr)->BaseElement:
#    """
#    converts a SymPy object to a Mathics3 element.
#    """
#    try:
#        return sympy_singleton_to_mathics[expr]
#    except (KeyError, TypeError):
#        pass
#
#    return sympy_conversion_by_type.get(type(expr), old_from_sympy)(expr)


def from_sympy(sympy_expr) -> BaseElement:
    """
    converts a SymPy object to a Mathics3 element.
    """
    if isinstance(sympy_expr, (tuple, list)):
        return to_mathics_list(*sympy_expr, elements_conversion_fn=from_sympy)
    if isinstance(sympy_expr, int):
        return Integer(sympy_expr)
    if isinstance(sympy_expr, float):
        return Real(sympy_expr)
    if isinstance(sympy_expr, complex):
        return Complex(Real(sympy_expr.real), Real(sympy_expr.imag))
    if isinstance(sympy_expr, str):
        return String(sympy_expr)
    if sympy_expr is None:
        return SymbolNull
    if isinstance(sympy_expr, sympy.Matrix) or isinstance(
        sympy_expr, sympy.ImmutableMatrix
    ):
        return from_sympy_matrix(sympy_expr)
    if isinstance(sympy_expr, sympy.MatPow):
        return Expression(
            SymbolMatrixPower, from_sympy(sympy_expr.base), from_sympy(sympy_expr.exp)
        )
    if sympy_expr.is_Atom:
        name = None
        if sympy_expr.is_Symbol:
            name = str(sympy_expr)
            if isinstance(sympy_expr, sympy.Dummy):
                name = name[1:]
                if "_" not in name:
                    name = f"sympy`dummy`Dummy${sympy_expr.dummy_index}"  # type: ignore[attr-defined]
                else:
                    name = sympy_decode_mathics_symbol_name(name)
                # Probably, this should be the value attribute
                return Symbol(name)
            if is_Cn_expr(name):
                return Expression(SymbolC, Integer(int(name[1:])))
            name = sympy_decode_mathics_symbol_name(name)
            if name.startswith(SYMPY_SLOT_PREFIX):
                index = int(name[len(SYMPY_SLOT_PREFIX) :])
                return Expression(SymbolSlot, Integer(index))
        elif sympy_expr.is_NumberSymbol:
            name = str(sympy_expr)
        if name is not None:
            builtin = sympy_to_mathics.get(name)
            if builtin is not None:
                name = builtin.get_name()
            return Symbol(name)
        if isinstance(sympy_expr, sympy.core.numbers.Infinity):
            return MATHICS3_INFINITY
        if isinstance(sympy_expr, sympy.core.numbers.ComplexInfinity):
            return MATHICS3_COMPLEX_INFINITY
        if isinstance(sympy_expr, sympy.core.numbers.NegativeInfinity):
            return MATHICS3_NEG_INFINITY
        if isinstance(sympy_expr, sympy.core.numbers.ImaginaryUnit):
            return MATHICS3_COMPLEX_I
        if isinstance(sympy_expr, sympy.Integer):
            return Integer(int(sympy_expr))
        if isinstance(sympy_expr, sympy.Rational):
            numerator, denominator = map(int, sympy_expr.as_numer_denom())
            if denominator == 0:
                if numerator > 0:
                    return MATHICS3_INFINITY
                elif numerator < 0:
                    return MATHICS3_NEG_INFINITY
                else:
                    assert numerator == 0
                    return SymbolIndeterminate
            return Rational(numerator, denominator)
        if isinstance(sympy_expr, sympy.Float):
            if sympy_expr._prec == FP_MANTISA_BINARY_DIGITS:
                return MachineReal(float(sympy_expr))
            return Real(sympy_expr)
        if isinstance(sympy_expr, sympy.core.numbers.NaN):
            return SymbolIndeterminate
        if isinstance(sympy_expr, sympy.core.function.FunctionClass):
            name = str(sympy_expr).replace("_", "`")
            return Symbol(name)
        if sympy_expr is sympy.true:
            return SymbolTrue
        if sympy_expr is sympy.false:
            return SymbolFalse

    if sympy_expr.is_number and all(x.is_Number for x in sympy_expr.as_real_imag()):
        # Hack to convert <Integer> * I to Complex[0, <Integer>]
        try:
            return Complex(*[from_sympy(arg) for arg in sympy_expr.as_real_imag()])
        except ValueError:
            # The exception happens if one of the components is infinity
            pass
    if sympy_expr.is_Add:
        return to_expression(
            SymbolPlus, *sorted([from_sympy(arg) for arg in sympy_expr.args])
        )
    if sympy_expr.is_Mul:
        return to_expression(
            SymbolTimes, *sorted([from_sympy(arg) for arg in sympy_expr.args])
        )
    if sympy_expr.is_Pow:
        return to_expression(SymbolPower, *[from_sympy(arg) for arg in sympy_expr.args])
    if sympy_expr.is_Equality:
        return to_expression(SymbolEqual, *[from_sympy(arg) for arg in sympy_expr.args])

    if isinstance(sympy_expr, SympyExpression):
        return sympy_expr.expr

    if isinstance(sympy_expr, sympy.Piecewise):
        return Expression(
            SymbolPiecewise,
            ListExpression(
                *[
                    to_mathics_list(from_sympy(case), from_sympy(cond))
                    for case, cond in cast(
                        Sequence[Tuple[sympy.Basic, sympy.Basic]], sympy_expr.args
                    )
                ]
            ),
        )

    if isinstance(sympy_expr, SympyPrime):
        return Expression(SymbolPrime, from_sympy(sympy_expr.args[0]))
    if isinstance(sympy_expr, sympy.RootSum):
        return Expression(SymbolRootSum, from_sympy(sympy_expr.poly), from_sympy(sympy_expr.fun))  # type: ignore[attr-defined]
    if isinstance(sympy_expr, sympy.PurePoly):
        coeffs = sympy_expr.coeffs()
        monoms = sympy_expr.monoms()
        result: List[BaseElement] = []
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
                if len(factors) == 1:
                    result.append(factors[0])
                else:
                    result.append(Expression(SymbolTimes, *factors))
            else:
                result.append(Integer1)
        return Expression(SymbolFunction, Expression(SymbolPlus, *sorted(result)))
    if isinstance(sympy_expr, sympy.CRootOf):
        try:
            e_root, indx = sympy_expr.args
        except ValueError:
            return SymbolNull

        try:
            e_root = sympy.PurePoly(e_root)
        except Exception:
            pass

        return Expression(SymbolRoot, from_sympy(e_root), Integer(indx + 1))
    if isinstance(sympy_expr, sympy.Lambda):
        variables = [
            sympy.Symbol(f"{SYMPY_SLOT_PREFIX}{index + 1}")
            for index in range(len(sympy_expr.variables))
        ]
        return Expression(SymbolFunction, from_sympy(sympy_expr(*variables)))

    if sympy_expr.is_Function or isinstance(
        sympy_expr,
        (
            sympy.Derivative,
            sympy.Integral,
            sympy.Product,
            sympy.Sum,
        ),
    ):
        if isinstance(sympy_expr, sympy.Integral):
            name = "Integral"
        elif isinstance(sympy_expr, sympy.Derivative):
            name = "Derivative"
            margs = []
            for arg in sympy_expr.args:
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
            assert builtin is not None
            return builtin.from_sympy(tuple(margs))

        elif isinstance(sympy_expr, sympy.sign):
            name = "Sign"
        else:
            name = sympy_expr.func.__name__
            assert name is not None
            if is_Cn_expr(name):
                return Expression(
                    Expression(Symbol("C"), Integer(int(name[1:]))),
                    *[from_sympy(arg) for arg in sympy_expr.args],
                )
            name = sympy_decode_mathics_symbol_name(name)
        args = [from_sympy(arg) for arg in sympy_expr.args]
        builtin = sympy_to_mathics.get(name)
        if builtin is not None:
            return builtin.from_sympy(tuple(args))
        return Expression(Symbol(name), *args)

    if isinstance(sympy_expr, sympy.Tuple):
        return to_mathics_list(*sympy_expr.args, elements_conversion_fn=from_sympy)

    # elif isinstance(sympy_expr, sympy.Sum):
    #    return Expression('Sum', )

    if isinstance(sympy_expr, sympy.LessThan):
        return to_expression(
            SymbolLessEqual, *sympy_expr.args, elements_conversion_fn=from_sympy
        )
    if isinstance(sympy_expr, sympy.StrictLessThan):
        return to_expression(
            SymbolLess, *sympy_expr.args, elements_conversion_fn=from_sympy
        )
    if isinstance(sympy_expr, sympy.GreaterThan):
        return to_expression(
            SymbolGreaterEqual, *sympy_expr.args, elements_conversion_fn=from_sympy
        )
    if isinstance(sympy_expr, sympy.StrictGreaterThan):
        return to_expression(
            SymbolGreater, *sympy_expr.args, elements_conversion_fn=from_sympy
        )
    if isinstance(sympy_expr, sympy.Unequality):
        return to_expression(
            SymbolUnequal, *sympy_expr.args, elements_conversion_fn=from_sympy
        )
    if isinstance(sympy_expr, sympy.Equality):
        return to_expression(
            SymbolEqual, *sympy_expr.args, elements_conversion_fn=from_sympy
        )

    if isinstance(sympy_expr, sympy.O):
        if sympy_expr.args[0].func == sympy.core.power.Pow:
            [var, power] = [from_sympy(arg) for arg in sympy_expr.args[0].args]
            o_expr = Expression(SymbolO, var)
            return Expression(SymbolPower, o_expr, power)
        else:
            return Expression(SymbolO, from_sympy(sympy_expr.args[0]))

    # FIXME: this should be an Interval, but we currently do
    # not have intervals. The primary place this appears is in
    # Limit, so check that as well for adjusting.
    if isinstance(sympy_expr, AccumulationBounds):
        return SymbolIndeterminate

    raise ValueError(
        "Unknown SymPy expression: {} (instance of {})".format(
            sympy_expr, str(sympy_expr.__class__)
        )
    )
