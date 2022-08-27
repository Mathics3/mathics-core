from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolPlus,
    SymbolPower,
    SymbolTimes,
)

from mathics.core.atoms import Integer, Integer0, Rational
from mathics.core.expression import Expression
from mathics.core.convert.expression import to_mathics_list
from mathics.core.list import ListExpression
from mathics.core.rules import Pattern
from mathics.core.systemsymbols import (
    SymbolComplexInfinity,
    SymbolD,
    SymbolDirectedInfinity,
    SymbolFactorial,
    SymbolIndeterminate,
    SymbolInfinity,
)

IntegerMinusOne = Integer(-1)
SymbolSeries = Symbol("Series")
SymbolSeriesData = Symbol("SeriesData")


def same_monomial(expr, x, x0):
    """
    Checks if expr == (x-x0)
    """
    if x0.is_zero and expr.sameQ(x):
        return True
    if expr.get_head() is not SymbolPlus:
        return False
    y, y0 = expr.elements
    if y0.sameQ(x):
        if x0.sameQ(-y) or y.sameQ(-x0):
            return True
    if y.sameQ(x):
        if x.sameQ(-y) or y.sameQ(-x):
            return True
    return False


# def to_series_term(series, term, x, x0):
#     return None, None
#     coeff = None
#     power = None
#     reminder = None
#     if isinstance(term, Atom):
#         if term.sameQ(x):
#             coeff = Integer1
#             power = 1
#             reminder = -x0
#         else:
#             coeff = term
#             power = 0
#             reminder = None
#     else:
#         head, elements = term.head, term.elements
#         if head is SymbolPower:
#             base, exponent = elements
#             head_exponent = exponent.get_head()
#             if head_exponent is SymbolInteger:
#                 power = exponent.to_float()
#             elif head_exponent is SymbolRational:
#                 num, den = exponent.value.as_numer_denom()
#                 if den != 1 and den != series[-1]:
#                     return None, None
#                 power = exponent.to_float()
#             else:
#                 return None, None
#             if x.sameQ(base):
#                 reminder = -term + Expression(SymbolPower, x - x0, exponent)
#                 coeff = 1
#             elif same_monomial(base, x, x0):
#                 coeff = 1
#                 reminder = None
#             else:
#                 return None, None
#         elif head is SymbolTimes:
#             coeffs_free = []
#             coeffs_powers = []
#             coeffs_x = []
#             for element in elements:
#                 if x.sameQ(elemnt):
#                     coeffs_x.append(x)
#                 elif isinstance(element, Atom):
#                     coeffs_free.append(element)
#                 elif element.get_head() is SymbolPower:
#                     coeffs_powers.append(element)
#                 else:
#                     return None, None
#             # All the factors are of the form x^k
#             if all(x.sameQ(element.elements[0]) for element in coeffs_powers):
#                 coeff = Expression(SymbolTimes, *coeffs_free)
#                 power = len(coeffs_x)
#                 exponents = [element.elements[1] for element in coeffs_powers]
#                 if not all(
#                     isinstance(exponent, (Integer, Rational)) for exponent in exponents
#                 ):
#                     return None, None
#                 power = power + sum([exp.to_python() for exp in exponents])
#                 reminder = -term + Expression(
#                     SymbolTimes, coeff, Expression(SymbolPower, x - x0, power)
#                 )
#             # All the factors are of the form (x-x0)^k
#             elif (
#                 all(same_monomial(element.elements[0], x, x0) for element in coeffs_powers)
#                 and len(coeffs_x) == 0
#             ):
#                 coeff = Expression(SymbolTimes, *coeffs_free)
#                 exponents = [element.elements[1] for element in coeffs_powers]
#                 if not all(
#                     isinstance(exponent, (Integer, Rational)) for exponent in exponents
#                 ):
#                     return None, None
#                 power = power + sum([exp.to_python() for exp in exponents])
#                 reminder = None
#             else:
#                 return None, None
#     if coeff:
#         power = power * series[-1]
#         if power > series[-2] or (power - int(power)) != 0:
#             return None, None
#         nmin = series[1]
#         power = int(power) - nmin
#         if power < 0:
#             nmin = nmin + power
#             newdata = [coef] + [Integer0 for i in range(1 - power)] + series[0].elements
#         else:
#             newdata = [
#                 c + coeff if p == power else c for p, c in enumerate(series[0].elements)
#             ]
#         return (
#             ListExpression(*newdata),
#             nmin,
#             series[-2],
#             series[-1],
#         ), reminder
#     return None, None


def series_plus_series(series1, series2):
    """
    Tries to reduce the sum of series1 and series2 on the same variable and neighbourhood
    to a single series. None if it is not possible.
    """
    # First, check that series1 has the smaller power.
    if series1[1] / series1[3] > series2[1] / series2[3]:
        series1, series2 = series2, series1

    data1, nmin1, nmax1, den1 = series1
    data2, nmin2, nmax2, den2 = series2
    data1 = data1.elements
    data2 = data2.elements

    den = den1 * den2
    nmin1_ = nmin1 * int(den1 / den)
    nmin2_ = nmin2 * int(den2 / den)
    nmin = nmin1_
    offset2 = nmin2_ - nmin1
    nmax1_ = nmax1 * int(den1 / den) - nmin
    nmax2_ = nmax2 * int(den2 / den) - nmin
    nmax = min(nmax1_, nmax2_)  # relative to nmin
    len_newdata = nmax
    nmax = nmax + nmin
    data = [Integer0 for x in range(len_newdata)]

    for k, coeff in enumerate(data1):
        p = k * int(den1 / den)
        if p < len_newdata:
            data[p] = coeff

    for k, coeff in enumerate(data2):
        p = k * int(den2 / den) + offset2
        if p < len_newdata:
            if data[p].is_zero:
                data[p] = coeff
            else:
                data[p] = Expression(SymbolPlus, data[p], coeff)

    data = ListExpression(*data)
    result = reduce_series_trailing_zeros((data, nmin, nmax, den))
    return result


def series_times_series(series1, series2):
    """
    Tries to reduce the product of series1 and series2 on the same variable and neighbourhood
    to a single series. None if it is not possible
    """
    data1, nmin1, nmax1, den1 = series1
    data2, nmin2, nmax2, den2 = series2
    data1 = data1.elements
    data2 = data2.elements
    # maybe we should use the MCD
    den = den1 * den2
    offset1 = int(den1 / den)
    offset2 = int(den2 / den)
    nmin = nmin1 * offset1 + nmin2 * offset2
    nmax = min(nmax1 * den2, nmax2 * den1)
    len_newdata = min(len(data1) * len(data2), nmax)
    data = [Integer0 for k in range(len_newdata)]

    for k1, c1 in enumerate(data1):
        for k2, c2 in enumerate(data2):
            pos = k1 * offset1 + k2 * offset2
            if pos >= len_newdata:
                continue
            if data[pos].is_zero:
                data[pos] = Expression(SymbolTimes, c1, c2)
            elif data[pos].get_head() is SymbolPlus:
                data[pos] = Expression(
                    SymbolPlus, Expression(SymbolTimes, c1, c2), *(data[pos].elements)
                )
            else:
                data[pos] = Expression(
                    SymbolPlus, Expression(SymbolTimes, c1, c2), data[pos]
                )

    data = ListExpression(*data)
    return reduce_series_trailing_zeros((data, nmin, nmax, den))


def _series_times_rational_power(series, num_power, den_power):
    """
    Tries to reduce the producto of a series with a power of the basic monomial
    to a single series. None if it is not possible
    """
    data, nmin, nmax, den = series
    data = data.elements
    # TODO: use the MCD
    den_ = den * den_power
    nmin_ = int(nmin * den_ / den + num_power * den_ / den_power)
    nmax_ = int(nmax * den_ / den + num_power * den_ / den_power)
    granularity = int(den_ / den_power)
    data_ = [Integer0 for u in range(len(data) * granularity)]
    for k, val in enumerate(data):
        data_[k * granularity] = val
    return reduce_series_trailing_zeros(
        (ListExpression(*data_), nmin_, nmax_, den * den_power)
    )


def reduce_series_trailing_zeros(series):
    """
    Reduce the series representation to start with a non-zero
    coefficient, and to remove coefficients of order larger that
    nmax
    """
    data, nmin, nmax, den = series
    data = data.elements
    if len(data) == 0:
        return series
    i = 0
    while i < len(data) and data[i].is_zero:
        i = i + 1
    nmin = nmin + i
    data = data[i:]
    useful_len = nmax - nmin
    if len(data) > useful_len:
        data = data[:useful_len]
    if len(data) == 0:
        nmin = nmax
    result = (ListExpression(*data), nmin, nmax, den)
    return result


def reduce_series(series):
    series = reduce_series_trailing_zeros(series)

    def factors(den):
        # TODO: extend the list of primes?
        for factor in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
            if den < factor:
                break
            if den % factor == 0:
                yield (factor)

    def reduce_dataseries(series, factor):
        data, nmin, nmax, den = series
        data = data.elements
        notdone = True
        while notdone:
            if (den % factor == 0) and (nmin % factor == 0) and (nmax % factor == 0):
                if all(
                    q.is_zero for q in data[1 + factor :: 2] for r in range(factor - 1)
                ):
                    data = data[0::factor]
                    nmin, nmax, den = (
                        int(nmin / factor),
                        int(nmax / factor),
                        int(den / factor),
                    )
                    continue
            notdone = False

        if series[-1] == den:
            return series
        return (ListExpression(*data), nmin, nmax, den)

    for factor in factors(series[-1]):
        series = reduce_dataseries(series, factor)

    return series


def reduce_series_plus(series, terms, x, x0):
    """
    Tries to reduce the sum of a Series with elements in expr_list.
    """
    old_series, old_terms = series, terms
    other_terms = []
    if not terms:
        return series, None

    # Loop over terms
    for term in terms:
        if term.is_zero:
            continue
        if isinstance(term, Atom):
            other_terms.append(term)
            continue
        term_head = term.head
        term_elements = term.elements
        if term_head is SymbolSeriesData:
            y, y0, data, nummin, nummax, den = term_elements
            if not x.sameQ(y):
                data = ListExpression(term)
                y = x
                y0 = x0
                nummin = 0
                nummax = series[2]
                den = series[3]
            elif not x0.sameQ(y0):
                other_terms.append(term)
                continue
            new_series = series_plus_series(
                series,
                (
                    data,
                    nummin.get_int_value(),
                    nummax.get_int_value(),
                    den.get_int_value(),
                ),
            )
            if new_series:
                series = new_series
                continue
        # TODO: handle constant terms, and terms of the form x^n, a x^n
        other_terms.append(term)
    if len(other_terms) == 0:
        return series, None

    if series is old_series:
        if len(other_terms) == len(old_terms) and all(
            term.sameQ(old_term) for term, old_term in zip(other_terms, old_terms)
        ):
            return None, None
    series = reduce_series(series)
    return series, other_terms


def build_series(f, x, x0, n, evaluation):
    """
    Builds the series expansion of f on x around x0, upto order n.
    """
    # TODO:
    # - Deal with special cases (monomials, fractional powers, singular cases)
    # - Use definitions of Series for builtin functions
    # - Asymptotic series
    x_name = x.get_name()
    vars = {
        x_name: x0,
    }
    x_pattern = Pattern.create(x)

    if f.is_free(x_pattern, evaluation):
        print(x, " not in ", f)
        return f

    data = [f.replace_vars(vars)]
    df = f
    n = n.get_int_value()
    for i in range(n):
        df = Expression(SymbolD, df, x).evaluate(evaluation)
        newcoeff = df.replace_vars(vars).evaluate(evaluation)
        factorial = Expression(SymbolFactorial, Integer(i + 1))
        newcoeff = Expression(
            SymbolTimes,
            Expression(SymbolPower, factorial, IntegerMinusOne),
            newcoeff,
        ).evaluate(evaluation)
        if newcoeff in (
            SymbolInfinity,
            SymbolComplexInfinity,
            SymbolIndeterminate,
        ) or newcoeff.get_head() in (SymbolDirectedInfinity,):
            return Expression(
                f.get_head(),
                *[
                    build_series(element, x, x0, Integer(n), evaluation)
                    for element in f.elements
                ]
            )
        data.append(newcoeff)
    data = ListExpression(*data).evaluate(evaluation)
    series = reduce_series_trailing_zeros((data, 0, n + 1, 1))
    return Expression(
        SymbolSeriesData,
        x,
        x0,
        series[0],
        Integer(series[1]),
        Integer(series[2]),
        Integer(series[3]),
    )


def series_derivative(series, x, x0, y, evaluation):
    """
    Evaluates the derivative of the series
    """
    data, nmin, nmax, den = series
    coeffs = list(data.elements)
    if all(
        [
            not coeff.has_symbol(y.get_name())
            for coeff in coeffs
            if hasattr(coeff, "has_symbol")
        ]
    ):
        dcoeffs = None
    else:
        dcoeffs = [Expression(SymbolD, coeff, y) for coeff in coeffs]

    prefactor = Expression(SymbolD, x - x0, y).evaluate(evaluation)

    if Integer0.sameQ(prefactor):
        if dcoeffs:
            return reduce_series_trailing_zeros(
                (
                    to_mathics_list(*[coeff.evaluate(evaluation) for coeff in dcoeffs]),
                    nmin,
                    nmax,
                    den,
                )
            )
        else:
            return None
    nmax = nmax - den
    trailings0 = [Integer0 for k in range(den)]
    if nmin != 0:
        if den == 1:
            coeffs2 = [
                (Integer(k + nmin) * prefactor * coeff)
                for k, coeff in enumerate(coeffs)
            ] + trailings0
        else:
            coeffs2 = [
                (Rational(k + nmin, den) * prefactor * coeff)
                for k, coeff in enumerate(coeffs)
            ] + trailings0
        nmin = nmin - den
        if dcoeffs:
            dcoeffs = trailings0 + dcoeffs
    else:
        coeffs = coeffs[1:]
        if den == 1:
            coeffs2 = [
                (Integer(k + 1) * prefactor * coeff) for k, coeff in enumerate(coeffs)
            ] + trailings0
        else:
            coeffs2 = [
                (Rational(k + 1, den) * prefactor * coeff)
                for k, coeff in enumerate(coeffs)
            ] + trailings0

    if dcoeffs:
        new_coeffs = [
            (c1 + c2).evaluate(evaluation) for c1, c2 in zip(dcoeffs, coeffs2)
        ]
    else:
        new_coeffs = [c1.evaluate(evaluation) for c1 in coeffs2]

    result = reduce_series_trailing_zeros(
        (ListExpression(*new_coeffs), nmin, nmax, den)
    )
    return result
