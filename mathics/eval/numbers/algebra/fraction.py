from typing import Optional

from sympy import (  # Poly,; fraction,
    FunctionClass,
    cos,
    cosh,
    cot,
    coth,
    csc,
    csch,
    sec,
    sin,
    sinh,
    tan,
    tanh,
)

from mathics.core.atoms import Integer, Integer1, Real
from mathics.core.convert.sympy import from_sympy
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolPower


def identify_trig(sympy_expr) -> Optional[FunctionClass]:
    """
    Figure out what the right rewrite function is appropriate for a sympy_expr
    """
    match sympy_expr.func:
        case func if func in (tan, cot):
            return cos
        case func if func in (sec, csc):
            return sin
        case func if func in (cosh, csch, coth):
            return sinh
        case func if func in (tanh,):
            return cosh
        case _:
            return None


def get_fractional_parts(expr, evaluation, algebraic_options, want_numerator):

    # We need to first evaluate expr which may alter the form
    # of the expression.
    evaluated_expr = expr.evaluate(evaluation)
    if isinstance(evaluated_expr, Integer):
        return evaluated_expr if want_numerator else Integer1

    # If the evaluated value is a number, we use that value
    # in Numerator/Denominator calculation
    if isinstance(evaluated_expr, Real):
        return None

    sympy_expr = evaluated_expr.to_sympy()

    if sympy_expr is None:
        return None

    # if (modulus := algebraic_options.modulus) and modulus is not None:
    #     breakpoint()
    #     try:
    #         # Convert to a SymPy Rational Function (cancel common factors)
    #         # We specify the domain as GF(n)
    #         domain_str = f'GF({modulus})'

    #         # Poly can represent the numerator/denominator structure
    #         # when handled as a fraction of polynomials
    #         num, den = fraction(sympy_expr)

    #         # Reduce both numerator and denominator in the finite field
    #         p_num = Poly(num, domain=domain_str)
    #         p_den = Poly(den, domain=domain_str)

    #         # Perform the "cancel" operation in the finite field
    #         # SymPy's cancel() or gcd() logic respects the domain
    #         common_gcd = p_num.gcd(p_den)
    #         reduced_den = p_den // common_gcd

    #         sympy_expr = reduced_den.as_expr()

    #     except Exception:
    #         # Fallback for non-polynomial expressions:
    #         # Reduce the raw denominator modulo n
    #         pass

    if algebraic_options.trig:
        if (
            hasattr(evaluated_expr, "head")
            and evaluated_expr.head is SymbolPower
            and isinstance(power_exponent := evaluated_expr.elements[1], Integer)
            and power_exponent.value > 0
        ):
            # We have a special case for expr^positive_Integer.
            # Isolate expr, and compute the denominator/numerator
            # Finally, fold back in the Power function.
            trig_fn_expr = evaluated_expr.elements[0]
            if (sympy_expr := trig_fn_expr.to_sympy()) is None:
                return

            if (trig_fn := identify_trig(sympy_expr)) is None:
                return None

            sympy_expr = sympy_expr.rewrite(trig_fn)
            if sympy_expr is None:
                return None
            numerator, denominator = sympy_expr.as_numer_denom()
            part = numerator if want_numerator else denominator
            return Expression(SymbolPower, from_sympy(part), power_exponent)

        if (trig_fn := identify_trig(sympy_expr)) is not None:
            sympy_expr = sympy_expr.rewrite(trig_fn)
    numerator, denominator = sympy_expr.as_numer_denom()
    part = numerator if want_numerator else denominator
    return from_sympy(part)


def eval_Denominator(expr, evaluation, algebraic_options):
    return get_fractional_parts(
        expr, evaluation, algebraic_options, want_numerator=False
    )


def eval_Numerator(expr, evaluation, algebraic_options):
    return get_fractional_parts(
        expr, evaluation, algebraic_options, want_numerator=True
    )
