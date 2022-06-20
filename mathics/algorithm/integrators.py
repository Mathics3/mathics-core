# -*- coding: utf-8 -*-

import numpy as np

from mathics.core.number import machine_epsilon
from mathics.core.expression import Expression
from mathics.core.atoms import (
    Integer,
    Integer0,
    Number,
)

from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolPlus, SymbolSequence, SymbolTimes


from mathics.core.systemsymbols import (
    SymbolBlank,
    SymbolComplex,
    SymbolD,
    SymbolNIntegrate,
    SymbolRule,
)


def decompose_domain(interval, evaluation):
    if interval.has_form("System`Sequence", 1, None):
        intervals = []
        for element in interval.elements:
            inner_interval = decompose_domain(element, evaluation)
            if inner_interval:
                intervals.append(inner_interval)
            else:
                evaluation.message("ilim", element)
                return None
        return intervals

    if interval.has_form("System`List", 3, None):
        intervals = []
        intvar = interval.elements[0]
        if not isinstance(intvar, Symbol):
            evaluation.message("ilim", interval)
            return None
        boundaries = interval.elements[1:]  # Rest[interval]
        if any([b.get_head_name() == "System`Complex" for b in boundaries]):
            intvar = ListExpression(intvar, Expression(SymbolBlank, SymbolComplex))
        for i in range(len(boundaries) - 1):
            intervals.append((boundaries[i], boundaries[i + 1]))
        if len(intervals) > 0:
            return (intvar, intervals)

    evaluation.message("ilim", interval)
    return None


def _internal_adaptative_simpsons_rule(f, a, b, **opts):
    """
    1D adaptative Simpson's rule integrator
    Adapted from https://en.wikipedia.org/wiki/Adaptive_Simpson%27s_method
       by @mmatera

    TODO: handle weak divergences
    """
    wsr = 1.0 / 6.0

    tol = opts.get("tol")
    if not tol:
        tol = 1.0e-10

    maxrec = opts.get("maxrec")
    if not maxrec:
        maxrec = 150

    def _quad_simpsons_mem(f, a, fa, b, fb):
        """Evaluates the Simpson's Rule, also returning m and f(m) to reuse"""
        m = 0.5 * (a + b)
        try:
            fm = f(m)
        except ZeroDivisionError:
            fm = None

        if fm is None or np.isinf(fm):
            m = m + 1e-10
            fm = f(m)
        return (m, fm, wsr * abs(b - a) * (fa + 4.0 * fm + fb))

    def _quad_asr(f, a, fa, b, fb, eps, whole, m, fm, maxrec):
        """
        Efficient recursive implementation of adaptive Simpson's rule.
        Function values at the start, middle, end of the intervals
        are retained.
        """
        maxrec = maxrec - 1
        try:
            left = _quad_simpsons_mem(f, a, fa, m, fm)
            lm, flm, left = left
            right = _quad_simpsons_mem(f, m, fm, b, fb)
            rm, frm, right = right

            delta = left + right - whole
            err = abs(delta)
            if err <= 15 * eps or maxrec == 0:
                return (left + right + delta / 15, err)
            left = _quad_asr(f, a, fa, m, fm, 0.5 * eps, left, lm, flm, maxrec)
            right = _quad_asr(f, m, fm, b, fb, 0.5 * eps, right, rm, frm, maxrec)
            return (left[0] + right[0], left[1] + right[1])
        except Exception:
            raise

    def ensure_evaluation(f, x):
        try:
            val = f(x)
        except ZeroDivisionError:
            return None
        try:
            if np.isinf(val):
                return None
        except TypeError:
            return None
        return val

    invert_interval = False
    if a > b:
        b, a, invert_interval = a, b, True

    fa, fb = ensure_evaluation(f, a), ensure_evaluation(f, b)
    if fa is None:
        x = 10.0 * machine_epsilon if a == 0 else a * (1.0 + 10.0 * machine_epsilon)
        fa = ensure_evaluation(f, x)
        if fa is None:
            raise Exception(f"Function undefined around {a}. Cannot integrate")
    if fb is None:
        x = -10.0 * machine_epsilon if b == 0 else b * (1.0 - 10.0 * machine_epsilon)
        fb = ensure_evaluation(f, x)
        if fb is None:
            raise Exception(f"Function undefined around {b}. Cannot integrate")

    m, fm, whole = _quad_simpsons_mem(f, a, fa, b, fb)
    if invert_interval:
        return -_quad_asr(f, a, fa, b, fb, tol, whole, m, fm, maxrec)
    else:
        return _quad_asr(f, a, fa, b, fb, tol, whole, m, fm, maxrec)


def _fubini(func, ranges, **opts):
    if not ranges:
        return 0.0
    a, b = ranges[0]
    integrator = opts["integrator"]
    tol = opts.get("tol")
    if tol is None:
        opts["tol"] = 1.0e-10
        tol = 1.0e-10

    if len(ranges) > 1:

        def subintegral(*u):
            def ff(*z):
                return func(*(u + z))

            val = _fubini(ff, ranges[1:], **opts)[0]
            return val

        opts["tol"] = 4.0 * tol
        val = integrator(subintegral, a, b, **opts)
        return val
    else:
        val = integrator(func, a, b, **opts)
        return val


def apply_D_to_Integral(func, domain, var, evaluation, options, head):
    """Implements D[%(name)s[func_, domain__, OptionsPattern[%(name)s]], var_Symbol]"""
    if head is SymbolNIntegrate:
        options = tuple(
            Expression(SymbolRule, Symbol(key), options[key]) for key in options
        )
    else:
        # It would be better to set those options that are not default...
        options = tuple()
    # if the integration is along several variables, take the integration of the inner
    # variables as func.
    if domain._head is SymbolSequence:
        func = Expression(head, func, *(domain._elements[:-1]), *options)
        domain = domain._elements[-1]

    terms = []
    # Evaluates the derivative regarding the integrand:
    integrand = Expression(SymbolD, func, var).evaluate(evaluation)
    if integrand:
        term = Expression(head, integrand, domain, *options)
        terms = [term]

    # Run over the intervals, and evaluate the derivative
    # regarding the integration limits.
    list_domain = decompose_domain(domain, evaluation)
    if not list_domain:
        return

    ivar, limits = list_domain
    for limit in limits:
        for k, lim in enumerate(limit):
            jac = Expression(SymbolD, lim, var)
            ev_jac = jac.evaluate(evaluation)
            if ev_jac:
                jac = ev_jac
            if isinstance(jac, Number) and jac.is_zero:
                continue
            f = func.replace_vars({ivar.get_name(): lim})
            if k == 1:
                f = Expression(SymbolTimes, f, jac)
            else:
                f = Expression(SymbolTimes, Integer(-1), f, jac)
            eval_f = f.evaluate(evaluation)
            if eval_f:
                f = eval_f
            if isinstance(f, Number) and f.is_zero:
                continue
            terms.append(f)

    if len(terms) == 0:
        return Integer0
    if len(terms) == 1:
        return terms[0]
    return Expression(SymbolPlus, *terms)


integrator_methods = {
    "Internal": (_internal_adaptative_simpsons_rule, False),
}
integrator_methods["Simpson"] = integrator_methods["Internal"]
integrator_methods["Automatic"] = integrator_methods["Internal"]

integrator_messages = {}
