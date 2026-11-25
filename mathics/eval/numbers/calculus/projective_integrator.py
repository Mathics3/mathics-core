# -*- coding: utf-8 -*-
"""
Projective Calculus Engine over Q(i, sqrt(d-1)) and Riemann Sphere P^1(C) for Mathics3.

Implements:
  1. Ostrowski-Hermite rational reduction + Lagrange-Rothstein-Trager conjugate pole pairing
     over Q(i, sqrt(d-1)).
  2. Fractional trigonometric rationalization t = tan(a*x + b)^(1/q) and Weierstrass
     stereographic rationalization on P^1 for trigonometric rational integrands.
  3. Exact Pade approximants [m/n] (`eval_pade_approximant`) via Toeplitz linear systems.
  4. Complex Cauchy-Lagrange residues on the Riemann sphere P^1(C) (`eval_residue`),
     including the point at infinity z_0 = oo = [1 : 0].
  5. Closed contour integration (`eval_contour_integrate`) on P^1(C) around circles |z - z_0| = r.
  6. Projective trigonometric identity reduction (`eval_trig_reduce`) on P^1.
"""

from __future__ import annotations

from typing import Optional, Tuple
import sympy as sp


def hermite_reduce_sympy(
    num: sp.Expr, den: sp.Expr, var: sp.Symbol
) -> Tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr, sp.Expr]:
    """Perform exact Ostrowski-Hermite reduction on P(var)/Q(var) purely via polynomial GCD.

    Returns (poly_part, poly_antideriv, hermite_rat, rem_num, sqfree_den) such that:
        int (P(var)/Q(var)) d(var) = poly_antideriv + hermite_rat + int (rem_num / sqfree_den) d(var).
    """
    num_p = sp.Poly(sp.expand(num), var)
    den_p = sp.Poly(sp.expand(den), var)
    sqf_coeff, sqf_factors = sp.sqf_list(den_p.as_expr(), var)
    num_expr = sp.simplify(num_p.as_expr() / sqf_coeff)
    den_expr = sp.Integer(1)
    for fac, mult in sqf_factors:
        den_expr = sp.expand(den_expr * (fac**mult))

    q_poly, r_poly = sp.div(sp.Poly(num_expr, var), sp.Poly(den_expr, var), var)
    poly_part = q_poly.as_expr()
    poly_antideriv = sp.integrate(poly_part, var)
    if r_poly.is_zero:
        return poly_part, poly_antideriv, sp.Integer(0), sp.Integer(0), sp.Integer(1)

    mult_map: dict[int, sp.Expr] = {}
    max_m = 1
    for fac, mult in sqf_factors:
        mult_map[mult] = sp.expand(mult_map.get(mult, sp.Integer(1)) * fac)
        if mult > max_m:
            max_m = mult

    a_cur = r_poly.as_expr()
    hermite_acc = sp.Integer(0)

    while max_m > 1:
        v_m = mult_map.pop(max_m)
        u_other = sp.Integer(1)
        for k_mult, k_fac in mult_map.items():
            u_other = sp.expand(u_other * (k_fac**k_mult))

        v_m_diff = sp.diff(v_m, var)
        w_poly = sp.expand(u_other * v_m_diff)
        scaled_a = sp.expand(a_cur / sp.Rational(1 - max_m))
        s_bez, _, g_bez = sp.gcdex(sp.Poly(w_poly, var), sp.Poly(v_m, var))
        g_expr = g_bez.as_expr()
        b_full = sp.Poly(sp.expand(s_bez.as_expr() * scaled_a / g_expr), var)
        _, b_rem = sp.div(b_full, sp.Poly(v_m, var), var)
        b_expr = b_rem.as_expr()

        c_quo, _ = sp.div(
            sp.Poly(sp.expand(scaled_a - b_expr * w_poly), var),
            sp.Poly(v_m, var),
            var,
        )
        c_expr = c_quo.as_expr()

        hermite_acc = sp.together(hermite_acc + b_expr / (v_m ** (max_m - 1)))
        a_cur = sp.expand((1 - max_m) * c_expr - u_other * sp.diff(b_expr, var))
        mult_map[max_m - 1] = sp.expand(
            mult_map.get(max_m - 1, sp.Integer(1)) * v_m
        )
        max_m -= 1
        while max_m > 1 and max_m not in mult_map:
            max_m -= 1

    sqfree_den = sp.expand(mult_map.get(1, sp.Integer(1)))
    return (
        poly_part,
        poly_antideriv,
        sp.cancel(hermite_acc),
        sp.expand(a_cur),
        sqfree_den,
    )


def _exact_biquadratic_roots(fac: sp.Expr, var: sp.Symbol) -> Optional[list[sp.Expr]]:
    """Extract exact roots over Q(i, sqrt(d-1)) for degree <= 2, binomials a*t^4 + b,
    and biquadratic polynomials a*t^4 + b*t^2 + c.
    """
    poly = sp.Poly(fac, var)
    deg = poly.degree()
    if deg == 0:
        return []
    if deg == 1:
        a1, a0 = poly.all_coeffs()
        return [sp.simplify(-a0 / a1)]
    if deg == 2:
        a2, a1, a0 = poly.all_coeffs()
        disc = sp.simplify(a1 * a1 - 4 * a2 * a0)
        sd = sp.sqrt(disc)
        return [
            sp.simplify((-a1 + sd) / (2 * a2)),
            sp.simplify((-a1 - sd) / (2 * a2)),
        ]
    if deg == 4:
        c4, c3, c2, c1, c0 = poly.all_coeffs()
        if c3 == 0 and c1 == 0:
            if c2 == 0:
                rhs = sp.simplify(-c0 / c4)
                if rhs.is_negative:
                    r4 = sp.simplify((-rhs) ** sp.Rational(1, 4))
                    s2 = sp.sqrt(2) / 2
                    return [
                        sp.simplify(r4 * s2 * (1 + sp.I)),
                        sp.simplify(r4 * s2 * (-1 + sp.I)),
                        sp.simplify(r4 * s2 * (-1 - sp.I)),
                        sp.simplify(r4 * s2 * (1 - sp.I)),
                    ]
                if rhs.is_positive:
                    r4 = sp.simplify(rhs ** sp.Rational(1, 4))
                    return [r4, -r4, sp.I * r4, -sp.I * r4]
            disc2 = sp.simplify(c2 * c2 - 4 * c4 * c0)
            if disc2.is_number and disc2.is_real:
                if disc2 >= 0:
                    u1 = sp.simplify((-c2 + sp.sqrt(disc2)) / (2 * c4))
                    u2 = sp.simplify((-c2 - sp.sqrt(disc2)) / (2 * c4))
                    out: list[sp.Expr] = []
                    for u_val in (u1, u2):
                        su = sp.sqrt(u_val)
                        out.append(sp.simplify(su))
                        out.append(sp.simplify(-su))
                    return out
                if c4 > 0 and c0 > 0:
                    # Explicit real-imaginary decomposition of the 4 roots +/- u_re +/- I * u_im:
                    r_mod = sp.sqrt(sp.simplify(c0 / c4))
                    half_b = sp.simplify(c2 / (2 * c4))
                    u_re = sp.sqrt(sp.simplify((r_mod - half_b) / 2))
                    u_im = sp.sqrt(sp.simplify((r_mod + half_b) / 2))
                    return [
                        u_re + sp.I * u_im,
                        -u_re + sp.I * u_im,
                        -u_re - sp.I * u_im,
                        u_re - sp.I * u_im,
                    ]
    return None


def integrate_rational_projective(expr: sp.Expr, var: sp.Symbol) -> Optional[sp.Expr]:
    """Integrate a rational function P(var)/Q(var) over Q(i, sqrt(d-1)) into elementary real
    Log and ArcTan functions without RootSum.
    """
    if not expr.is_rational_function(var):
        return None
    cancelled = sp.cancel(expr)
    num, den = sp.fraction(cancelled)
    if not num.is_polynomial(var) or not den.is_polynomial(var):
        return None
    if sp.Poly(den, var).degree() <= 0:
        return sp.integrate(cancelled, var)

    _, poly_antideriv, hermite_rat, rem_num, sqfree_den = hermite_reduce_sympy(
        num, den, var
    )
    poles_residues: list[Tuple[sp.Expr, sp.Expr]] = []
    if rem_num != 0 and sqfree_den != 1:
        den_diff = sp.diff(sqfree_den, var)
        _, fac_list = sp.factor_list(sqfree_den, var)
        for fac, _ in fac_list:
            roots = _exact_biquadratic_roots(fac, var)
            if roots is None:
                return None
            for r_sym in roots:
                res_sym = sp.simplify(
                    rem_num.subs(var, r_sym) / den_diff.subs(var, r_sym)
                )
                poles_residues.append((r_sym, res_sym))

    log_atan_expr = sp.Integer(0)
    used = [False] * len(poles_residues)
    for i, (p_i, c_i) in enumerate(poles_residues):
        if used[i]:
            continue
        p_re, p_im = sp.expand(p_i).as_real_imag()
        c_re, c_im = sp.expand(c_i).as_real_imag()
        if p_im == 0:
            used[i] = True
            log_atan_expr += sp.simplify(c_re) * sp.log(var - p_re)
            continue

        partner = None
        for j in range(i + 1, len(poles_residues)):
            if used[j]:
                continue
            q_re, q_im = sp.expand(poles_residues[j][0]).as_real_imag()
            if sp.simplify(p_re - q_re) == 0 and sp.simplify(p_im + q_im) == 0:
                partner = j
                break

        if partner is not None and p_im.is_positive:
            used[i] = True
            used[partner] = True
            d_re, d_im = sp.expand(poles_residues[partner][1]).as_real_imag()
            if sp.simplify(c_re - d_re) == 0 and sp.simplify(c_im + d_im) == 0:
                quad_arg = sp.expand((var - p_re) ** 2 + p_im**2)
                atan_arg = sp.simplify((var - p_re) / p_im)
                if c_re != 0:
                    log_atan_expr += sp.simplify(c_re) * sp.log(quad_arg)
                if c_im != 0:
                    log_atan_expr -= sp.simplify(2 * c_im) * sp.atan(atan_arg)
                continue
        return None

    primitive = poly_antideriv + hermite_rat + log_atan_expr
    return primitive


def integrate_fractional_trig_projective(
    expression: sp.Expr, variable: sp.Symbol
) -> Optional[sp.Expr]:
    """Integrate fractional powers of tan(a*x+b) or cot(a*x+b) via projective substitution
    t = trig(a*x+b)^(1/q) on P^1(Q(i, sqrt(2))).
    """
    if not isinstance(variable, sp.Symbol) or expression.free_symbols - {variable}:
        return None
    trigs = [
        term
        for term in expression.atoms(sp.tan, sp.cot)
        if term.has(variable)
    ]
    if len(trigs) != 1:
        return None
    trig = trigs[0]
    argument = trig.args[0]
    slope = sp.diff(argument, variable)
    offset = sp.simplify(argument - slope * variable)
    if (
        slope.has(variable)
        or offset.has(variable)
        or not slope.is_number
        or slope.is_zero
    ):
        return None
    frac_pows = [
        p
        for p in expression.atoms(sp.Pow)
        if p.base in (trig, -trig) and p.exp.is_Rational and p.exp.q > 1
    ]
    if not frac_pows:
        return None
    root_signs = {1 if p.base == trig else -1 for p in frac_pows}
    if len(root_signs) != 1:
        return None
    root_sign = root_signs.pop()
    root_base = root_sign * trig
    denoms = [int(p.exp.q) for p in frac_pows]
    if any(d_val > 4 for d_val in denoms):
        return None
    q = int(sp.ilcm(1, *denoms))
    if not (2 <= q <= 4):
        return None

    t = sp.Dummy("t_proj", positive=True)
    transformed = expression.subs(trig, root_sign * (t**q))
    if transformed.has(variable) or not transformed.is_rational_function(t):
        return None
    sign = 1 if trig.func == sp.tan else -1
    rat_integrand = sp.cancel(
        root_sign * sign * q * (t ** (q - 1)) * transformed / (slope * (1 + t ** (2 * q)))
    )
    prim_t = integrate_rational_projective(rat_integrand, t)
    if prim_t is None:
        prim_t = sp.integrate(rat_integrand, t)
    if prim_t is None or prim_t.has(sp.Integral, sp.RootSum):
        return None
    if sp.cancel(sp.diff(prim_t, t) - rat_integrand) != 0:
        return None
    return prim_t.subs(t, root_base ** sp.Rational(1, q))


def integrate_weierstrass_projective(
    expression: sp.Expr, variable: sp.Symbol
) -> Optional[sp.Expr]:
    """Integrate rational functions of sin(x), cos(x), tan(x) via stereographic lift
    t = tan(x/2) onto P^1(Q(i, sqrt(d-1))) when degree in t is <= 4.
    """
    if not isinstance(variable, sp.Symbol) or expression.free_symbols - {variable}:
        return None
    if not expression.has(sp.sin, sp.cos, sp.tan, sp.cot, sp.sec, sp.csc):
        return None
    # Check if expression is a function of sin(x)^2, cos(x)^2, tan(x) -> substitute u = tan(x), dx = du/(1+u^2)
    u = sp.Dummy("u_tan", real=True)
    # Try double-angle rational substitution u = tan(x): sin(x)^2 = u^2/(1+u^2), cos(x)^2 = 1/(1+u^2), sin(2x) = 2u/(1+u^2), cos(2x) = (1-u^2)/(1+u^2)
    expr_tan = expression.subs(
        {
            sp.sin(variable) ** 2: u**2 / (1 + u**2),
            sp.sin(variable) ** 4: (u**4) / ((1 + u**2) ** 2),
            sp.cos(variable) ** 2: 1 / (1 + u**2),
            sp.cos(variable) ** 4: 1 / ((1 + u**2) ** 2),
            sp.tan(variable): u,
            sp.cot(variable): 1 / u,
            sp.sin(2 * variable): 2 * u / (1 + u**2),
            sp.cos(2 * variable): (1 - u**2) / (1 + u**2),
        }
    )
    if not expr_tan.has(variable) and expr_tan.is_rational_function(u):
        rat_u = sp.cancel(expr_tan / (1 + u**2))
        prim_u = integrate_rational_projective(rat_u, u)
        if prim_u is not None and not prim_u.has(sp.Integral, sp.RootSum):
            return prim_u.subs(u, sp.tan(variable))

    # General Weierstrass substitution t = tan(x/2)
    t = sp.Dummy("t_weier", real=True)
    expr_w = expression.subs(
        {
            sp.sin(variable): 2 * t / (1 + t**2),
            sp.cos(variable): (1 - t**2) / (1 + t**2),
            sp.tan(variable): 2 * t / (1 - t**2),
            sp.cot(variable): (1 - t**2) / (2 * t),
            sp.sec(variable): (1 + t**2) / (1 - t**2),
            sp.csc(variable): (1 + t**2) / (2 * t),
        }
    )
    if not expr_w.has(variable) and expr_w.is_rational_function(t):
        rat_t = sp.cancel(expr_w * 2 / (1 + t**2))
        _, den_t = sp.fraction(rat_t)
        if sp.Poly(den_t, t).degree() <= 4:
            prim_t = integrate_rational_projective(rat_t, t)
            if prim_t is not None and not prim_t.has(sp.Integral, sp.RootSum):
                return prim_t.subs(t, sp.tan(variable / 2))
    return None


def eval_projective_integrate(f_sympy: sp.Expr, vars_spec: list) -> Optional[sp.Expr]:
    """Pre-SymPy projective integration fast-path for Mathics3 `Integrate`.

    Intercepts:
      1. Fractional trigonometric integrals `Integrate[Sqrt[Tan[x]], x]` where SymPy fails.
      2. Quartic/even trigonometric integrals `Integrate[1/(1 + Sin[x]^4), x]` where SymPy Risch hangs.
    """
    if len(vars_spec) != 1:
        return None
    spec = vars_spec[0]
    if isinstance(spec, sp.Symbol):
        res = integrate_fractional_trig_projective(f_sympy, spec)
        if res is not None:
            return res
        if any(
            p.base in (sp.sin(spec), sp.cos(spec))
            and p.exp.is_Integer
            and int(p.exp) >= 4
            for p in f_sympy.atoms(sp.Pow)
        ):
            res = integrate_weierstrass_projective(f_sympy, spec)
            if res is not None:
                return res
    return None


def eval_pade_approximant(
    f_sympy: sp.Expr, var: sp.Symbol, x0: sp.Expr, m: int, n: int
) -> Optional[sp.Expr]:
    """Compute exact Pade approximant [m / n] of `f_sympy` around `var = x0`."""
    if m < 0 or n < 0:
        return None
    dx = sp.Dummy("dx_pade")
    shifted = f_sympy.subs(var, x0 + dx)
    order = m + n
    try:
        ser = sp.series(shifted, dx, 0, order + 1).removeO()
    except Exception:
        return None

    c = [sp.simplify(ser.coeff(dx, k)) for k in range(order + 1)]
    c[0] = sp.simplify(ser.subs(dx, 0))

    if n == 0:
        return sp.expand(sum(c[k] * ((var - x0) ** k) for k in range(m + 1)))

    mat_rows = []
    rhs_rows = []
    for k in range(m + 1, m + n + 1):
        row = []
        for j in range(1, n + 1):
            idx = k - j
            row.append(c[idx] if idx >= 0 else sp.Integer(0))
        mat_rows.append(row)
        rhs_rows.append(-c[k])

    try:
        mat = sp.Matrix(mat_rows)
        rhs = sp.Matrix(rhs_rows)
        b_sol = mat.LUsolve(rhs)
    except Exception:
        return None

    b_coeffs = [sp.Integer(1)] + [sp.simplify(b_sol[j]) for j in range(n)]
    a_coeffs = []
    for k in range(m + 1):
        ak = sp.Integer(0)
        for j in range(min(k, n) + 1):
            ak += b_coeffs[j] * c[k - j]
        a_coeffs.append(sp.simplify(ak))

    u_var = var - x0
    num_expr = sum(a_coeffs[k] * (u_var**k) for k in range(m + 1))
    den_expr = sum(b_coeffs[j] * (u_var**j) for j in range(n + 1))
    return sp.cancel(num_expr / den_expr)


def eval_residue_projective(
    f_sympy: sp.Expr, var: sp.Symbol, z0: sp.Expr
) -> Optional[sp.Expr]:
    """Compute complex Cauchy-Lagrange residue Res_{var = z0} f(var) on the Riemann sphere P^1(C),
    including the projective point at infinity z0 = oo = [1 : 0].
    """
    try:
        if z0 is sp.oo or z0 is -sp.oo or z0 is sp.zoo:
            w = sp.Dummy("w_inf")
            inv_expr = (-1 / (w**2)) * f_sympy.subs(var, 1 / w)
            return sp.simplify(sp.residue(inv_expr, w, 0))
        return sp.simplify(sp.residue(f_sympy, var, z0))
    except Exception:
        return None


def eval_contour_integrate_projective(
    f_sympy: sp.Expr, var: sp.Symbol, center: sp.Expr, radius: sp.Expr
) -> Optional[sp.Expr]:
    """Compute closed contour integral oint_{|var - center| = radius} f(var) d(var) on P^1(C)
    via Ostrowski-Hermite reduction (eliminating zero-residue repeated-pole derivatives)
    and Lagrange-Rothstein-Trager residues over Q(i, sqrt(d-1)).
    """
    if not f_sympy.is_rational_function(var):
        return None
    r_val = sp.N(radius)
    if not r_val.is_real or float(r_val) <= 0:
        return None
    r_float = float(r_val)
    c_complex = complex(sp.N(center))

    cancelled = sp.cancel(f_sympy)
    num, den = sp.fraction(cancelled)
    _, _, _, rem_num, sqfree_den = hermite_reduce_sympy(num, den, var)
    if rem_num == 0 or sqfree_den == 1:
        return sp.Integer(0)

    den_diff = sp.diff(sqfree_den, var)
    _, fac_list = sp.factor_list(sqfree_den, var)

    res_sum = sp.Integer(0)
    for fac, _ in fac_list:
        roots = _exact_biquadratic_roots(fac, var)
        if roots is None:
            r_dict = sp.roots(sp.Poly(fac, var))
            if sum(r_dict.values()) != sp.Poly(fac, var).degree():
                return None
            roots = []
            for r_k, mult in r_dict.items():
                roots.extend([r_k] * mult)
        for r_sym in roots:
            dist = abs(complex(sp.N(r_sym)) - c_complex)
            if abs(dist - r_float) < 1e-9:
                # Pole lies on contour
                return None
            if dist < r_float:
                res_k = sp.simplify(
                    rem_num.subs(var, r_sym) / den_diff.subs(var, r_sym)
                )
                res_sum += res_k

    return sp.simplify(2 * sp.pi * sp.I * res_sum)


def eval_trig_reduce_projective(f_sympy: sp.Expr) -> Optional[sp.Expr]:
    """Projective trigonometric and hyperbolic reduction on P^1.

    Expands multiple-angle harmonies and reduces products/powers via TR8.
    """
    from sympy.simplify.fu import TR8

    try:
        expanded_angles = sp.expand_trig(f_sympy)
        reduced = sp.expand(TR8(expanded_angles))
        return sp.Integer(0) if sp.simplify(reduced) == 0 else reduced
    except Exception:
        return None


def eval_trig_expand_projective(f_sympy: sp.Expr) -> Optional[sp.Expr]:
    """Expand trigonometric functions of sums and multiple angles via Chebyshev-Cayley expansion."""
    try:
        return sp.expand(sp.expand_trig(f_sympy))
    except Exception:
        return None


def eval_trig_factor_projective(f_sympy: sp.Expr) -> Optional[sp.Expr]:
    """Factor trigonometric sums/polynomials via projective Weierstrass lift and Fu sum-to-product rules."""
    from sympy.simplify.fu import TR10i, fu

    try:
        # First try sum-to-product and Fu factorization
        res = sp.factor(TR10i(sp.expand_trig(f_sympy)))
        cand = fu(f_sympy)
        if cand.is_Mul and not res.is_Mul:
            return cand
        return res
    except Exception:
        return None


def eval_trig_to_exp_projective(f_sympy: sp.Expr) -> Optional[sp.Expr]:
    """Convert trigonometric and hyperbolic functions to complex exponentials on P^1(Q(i))."""
    try:
        return sp.expand(f_sympy.rewrite(sp.exp))
    except Exception:
        return None


def eval_exp_to_trig_projective(f_sympy: sp.Expr) -> Optional[sp.Expr]:
    """Convert complex exponentials exp(i*z) to trigonometric functions (Cos, Sin, Cosh, Sinh)."""
    try:
        return sp.simplify(f_sympy.rewrite(sp.cos))
    except Exception:
        return None


def eval_dyadic_pi_cos_sin(p_num: int, two_pow_q: int) -> Optional[Tuple[sp.Expr, sp.Expr]]:
    """Compute exact nested-radical values (Cos[p*Pi / 2^k], Sin[p*Pi / 2^k]) for any dyadic denominator 2^k >= 8
    via the projective half-angle recursion over Q(sqrt(2)):
        cos(theta / 2) = sqrt((1 + cos(theta)) / 2),
        sin(theta / 2) = sqrt((1 - cos(theta)) / 2).
    """
    if two_pow_q <= 0 or (two_pow_q & (two_pow_q - 1)) != 0:
        return None

    # Reduce angle modulo 2*pi -> p_mod in [0, 2 * two_pow_q)
    period = 2 * two_pow_q
    p_mod = p_num % period
    sign_c = 1
    sign_s = 1

    # Reduce from [0, 2*pi) to [0, pi]
    if p_mod > two_pow_q:
        p_mod = period - p_mod
        sign_s = -sign_s
    # Reduce from [0, pi] to [0, pi/2]
    half_q = two_pow_q // 2
    if p_mod > half_q:
        p_mod = two_pow_q - p_mod
        sign_c = -sign_c
    # Reduce from [0, pi/2] to [0, pi/4] using swap(cos, sin)
    quarter_q = two_pow_q // 4
    swapped = False
    if p_mod > quarter_q:
        p_mod = half_q - p_mod
        swapped = True

    # Recursive half-angle solver on [0, pi/2] for dyadic fraction m / 2^k:
    def _dyadic_first_quad(m_val: int, q_val: int) -> Tuple[sp.Expr, sp.Expr]:
        if m_val == 0:
            return sp.Integer(1), sp.Integer(0)
        while m_val % 2 == 0 and q_val % 2 == 0:
            m_val //= 2
            q_val //= 2
        if q_val == 1:
            # m_val == 1 -> pi
            return sp.Integer(-1), sp.Integer(0)
        if q_val == 2:
            # pi / 2
            return sp.Integer(0), sp.Integer(1)
        if q_val == 4:
            # pi / 4
            s2 = sp.sqrt(2) / 2
            return s2, s2
        # General q_val = 2^k >= 8 with odd m_val < q_val / 2:
        # Angle is (m_val * pi / (q_val / 2)) / 2.
        # Compute c_double = cos(m_val * pi / (q_val // 2)) in [0, pi]:
        half_denom = q_val // 2
        if m_val <= half_denom // 2:
            c_dbl, _ = _dyadic_first_quad(m_val, half_denom)
        else:
            c_supp, _ = _dyadic_first_quad(half_denom - m_val, half_denom)
            c_dbl = -c_supp
        c_half = sp.sqrt((1 + c_dbl) / sp.Integer(2))
        s_half = sp.sqrt((1 - c_dbl) / sp.Integer(2))
        return c_half, s_half

    c_base, s_base = _dyadic_first_quad(p_mod, two_pow_q)
    if swapped:
        c_base, s_base = s_base, c_base
    return sign_c * c_base, sign_s * s_base


def eval_laplace_transform_projective(
    f_sympy: sp.Expr, t_var: sp.Symbol, s_var: sp.Symbol
) -> Optional[sp.Expr]:
    """Compute LaplaceTransform[f(t), t, s] = int_0^oo f(t) exp(-s*t) dt."""
    try:
        res = sp.laplace_transform(f_sympy, t_var, s_var, noconds=True)
        if res is not None and not res.has(sp.LaplaceTransform):
            return sp.cancel(res) if res.is_rational_function(s_var) else res
        return None
    except Exception:
        return None


def eval_inverse_laplace_transform_projective(
    F_sympy: sp.Expr, s_var: sp.Symbol, t_var: sp.Symbol
) -> Optional[sp.Expr]:
    """Compute InverseLaplaceTransform[F(s), s, t] = (1/(2*pi*i)) oint_gamma F(s) exp(s*t) ds
    via Riesz-Dunford-Lagrange pole decomposition over Q(i, sqrt(d-1)) for proper rational resolvents,
    with fallback to SymPy inverse_laplace_transform.
    """
    if F_sympy.is_rational_function(s_var):
        cancelled = sp.cancel(F_sympy)
        num, den = sp.fraction(cancelled)
        if num.is_polynomial(s_var) and den.is_polynomial(s_var):
            deg_n = sp.Poly(num, s_var).degree() if num != 0 else 0
            deg_d = sp.Poly(den, s_var).degree()
            if 0 < deg_d and deg_n < deg_d:
                _, sqf_facs = sp.sqf_list(den, s_var)
                # Fast exact Lagrange residue path for simple poles over Q(i, sqrt(d-1)):
                if all(mult == 1 for _, mult in sqf_facs):
                    den_diff = sp.diff(den, s_var)
                    _, fac_list = sp.factor_list(den, s_var)
                    poles_res: list[Tuple[sp.Expr, sp.Expr]] = []
                    ok_exact = True
                    for fac, _ in fac_list:
                        roots = _exact_biquadratic_roots(fac, s_var)
                        if roots is None:
                            ok_exact = False
                            break
                        for r_sym in roots:
                            c_sym = sp.simplify(
                                num.subs(s_var, r_sym) / den_diff.subs(s_var, r_sym)
                            )
                            poles_res.append((r_sym, c_sym))
                    if ok_exact:
                        time_evol = sp.Integer(0)
                        used = [False] * len(poles_res)
                        for i, (p_i, c_i) in enumerate(poles_res):
                            if used[i]:
                                continue
                            p_re, p_im = sp.expand(p_i).as_real_imag()
                            c_re, c_im = sp.expand(c_i).as_real_imag()
                            if p_im == 0:
                                used[i] = True
                                time_evol += sp.simplify(c_re) * sp.exp(p_re * t_var)
                                continue
                            partner = None
                            for j in range(i + 1, len(poles_res)):
                                if used[j]:
                                    continue
                                q_re, q_im = sp.expand(poles_res[j][0]).as_real_imag()
                                if (
                                    sp.simplify(p_re - q_re) == 0
                                    and sp.simplify(p_im + q_im) == 0
                                ):
                                    partner = j
                                    break
                            if partner is not None and p_im.is_positive:
                                used[i] = True
                                used[partner] = True
                                d_re, d_im = sp.expand(
                                    poles_res[partner][1]
                                ).as_real_imag()
                                if (
                                    sp.simplify(c_re - d_re) == 0
                                    and sp.simplify(c_im + d_im) == 0
                                ):
                                    # c * exp((p_re + i*p_im)*t) + conj(c) * exp((p_re - i*p_im)*t)
                                    # = exp(p_re * t) * (2*c_re*cos(p_im*t) - 2*c_im*sin(p_im*t))
                                    env = sp.exp(p_re * t_var)
                                    osc = sp.Integer(0)
                                    if c_re != 0:
                                        osc += sp.simplify(2 * c_re) * sp.cos(
                                            p_im * t_var
                                        )
                                    if c_im != 0:
                                        osc -= sp.simplify(2 * c_im) * sp.sin(
                                            p_im * t_var
                                        )
                                    time_evol += env * osc
                                    continue
                            ok_exact = False
                            break
                        if ok_exact:
                            return sp.expand(time_evol)

    try:
        res = sp.inverse_laplace_transform(F_sympy, s_var, t_var)
        if res is not None and not res.has(sp.InverseLaplaceTransform):
            return sp.simplify(res.subs(sp.Heaviside(t_var), 1))
        return None
    except Exception:
        return None


def eval_stieltjes_pade_resolvent(
    moments_sympy: list[sp.Expr], z_var: sp.Symbol
) -> Optional[sp.Expr]:
    """Construct the exact [N-1 / N] Stieltjes-Pade projective resolvent G_N(z) = P_{N-1}(z) / Q_N(z)
    on P^1(C) from 2N power moments [mu_0, mu_1, ..., mu_{2N-1}] of a Hilbert-space operator L.
    """
    if len(moments_sympy) < 2 or len(moments_sympy) % 2 != 0:
        return None
    n_order = len(moments_sympy) // 2
    hankel_rows = []
    rhs_rows = []
    for i in range(n_order):
        row = [moments_sympy[i + j] for j in range(n_order)]
        hankel_rows.append(row)
        rhs_rows.append(-moments_sympy[i + n_order])
    try:
        h_mat = sp.Matrix(hankel_rows)
        rhs_vec = sp.Matrix(rhs_rows)
        c_sol = h_mat.LUsolve(rhs_vec)
    except Exception:
        return None

    q_coeffs = [sp.simplify(c_sol[j]) for j in range(n_order)] + [sp.Integer(1)]
    den_poly = sum(q_coeffs[j] * (z_var**j) for j in range(n_order + 1))

    num_poly = sp.Integer(0)
    for m_deg in range(n_order):
        pm = sp.Integer(0)
        for k in range(n_order - m_deg):
            pm += q_coeffs[m_deg + 1 + k] * moments_sympy[k]
        num_poly += sp.simplify(pm) * (z_var**m_deg)

    return sp.cancel(num_poly / den_poly)


