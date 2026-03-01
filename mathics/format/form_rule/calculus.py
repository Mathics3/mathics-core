from mathics.core.atoms import (
    Integer,
    Integer0,
    Integer1,
    Integer310,
    IntegerM1,
    Rational,
    String,
)
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.systemsymbols import (
    SymbolDivide,
    SymbolHoldForm,
    SymbolInfix,
    SymbolLeft,
    SymbolO,
    SymbolPlus,
)


def format_series(x, x0, data, nmin, nmax, den, evaluation):
    if den.value != 1:
        powers = [Rational(i, den) for i in range(nmin.value, nmax.value + 1)]
    else:
        powers = [Integer(i) for i in range(nmin.value, nmax.value + 1)]

    terms = []
    base = x
    if not x0.is_zero:
        base = base + (-x0).evaluate(evaluation)

    factors = data.elements
    if len(factors) >= len(powers):
        factors = factors[: len(powers)]

    for idx, prefactor in enumerate(factors):
        if prefactor is Integer0:
            continue
        power = powers[idx]
        if power is Integer0:
            terms.append(prefactor)
            continue
        if power is Integer1:
            term = base
        else:
            term = base**power

        if prefactor is Integer1:
            terms.append(term)
            continue
        if isinstance(prefactor, Rational):
            num_value, den_value = prefactor.value.as_numer_denom()
            negative = False
            if num_value < 0:
                num_value, negative = -num_value, True
            if num_value == 1:
                term = Expression(SymbolDivide, term, Integer(den_value))
            else:
                term = Expression(
                    SymbolDivide, Integer(num_value) * term, Integer(den_value)
                )
            if negative:
                term = IntegerM1 * term
        else:
            term = prefactor * term
        terms.append(term)

    regular = Expression(SymbolHoldForm, Expression(SymbolPlus, *terms))
    last = Expression(SymbolHoldForm, Expression(SymbolO, base) ** (powers[-1]))
    return Expression(
        SymbolInfix,
        ListExpression(regular, last),
        String("+"),
        Integer310,
        SymbolLeft,
    )
