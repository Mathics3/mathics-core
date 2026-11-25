# -*- coding: utf-8 -*-
"""
Unit tests for Projective Calculus over Q(i, sqrt(d-1)) and Riemann Sphere P^1(C)
in Mathics3:
  - Integrate (fractional trig rationalization & Weierstrass stereographic lift)
  - PadeApproximant ([m/n] and diagonal [n/n])
  - Residue (finite poles in Q(i, sqrt(2)) and projective infinity [1 : 0])
  - ContourIntegrate (closed circular contours on P^1(C))
  - TrigReduce (projective P^1 trigonometric reduction)
"""

from test.helper import check_evaluation
import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg"),
    [
        # 1. PadeApproximant [m/n] and diagonal [n/n]
        (
            "PadeApproximant[Exp[x], {x, 0, {2, 2}}]",
            "(12 + 6 x + x ^ 2) / (12 - 6 x + x ^ 2)",
            "Pade [2/2] of Exp[x]",
        ),
        (
            "PadeApproximant[Exp[x], {x, 0, 2}]",
            "(12 + 6 x + x ^ 2) / (12 - 6 x + x ^ 2)",
            "Diagonal Pade [2/2] of Exp[x]",
        ),
        (
            "PadeApproximant[ArcTan[x], {x, 0, {3, 3}}]",
            "(15 x + 4 x ^ 3) / (15 + 9 x ^ 2)",
            "Pade [3/3] of ArcTan[x]",
        ),
        (
            "PadeApproximant[Log[1 + x], {x, 0, {2, 2}}]",
            "(6 x + 3 x ^ 2) / (6 + 6 x + x ^ 2)",
            "Pade [2/2] of Log[1 + x]",
        ),
        # 2. Residue on P^1(C) including projective infinity
        (
            "Residue[1 / (z^2 + 1), {z, I}]",
            "-I / 2",
            "Residue at simple pole z = I",
        ),
        (
            "Residue[1 / (1 + z^4), {z, (1 + I) / Sqrt[2]}]",
            "(-1 / 8 - I / 8) Sqrt[2]",
            "Residue at biquadratic pole in Q(i, sqrt(2))",
        ),
        (
            "Residue[1 / z, {z, Infinity}]",
            "-1",
            "Residue at projective infinity [1 : 0] on P^1(C)",
        ),
        (
            "Residue[z^2 / (1 + z^3), {z, Infinity}]",
            "-1",
            "Residue of rational function at projective infinity",
        ),
        # 3. ContourIntegrate on the Riemann sphere P^1(C)
        (
            "ContourIntegrate[1 / (1 + z^4), {z, Circle[{0, 1}, 1]}]",
            "Sqrt[2] Pi / 2",
            "Contour integral enclosing two upper-half-plane poles of 1/(1+z^4)",
        ),
        (
            "ContourIntegrate[1 / (1 + z^4), {z, 0, 2}]",
            "0",
            "Contour integral enclosing all four poles of 1/(1+z^4) vanishes by P^1 residue sum",
        ),
        (
            "ContourIntegrate[1 / (1 + z^2), {z, I, 1}]",
            "Pi",
            "Contour integral around z = I",
        ),
        (
            "ContourIntegrate[1 / (z - 1)^3, {z, Circle[{1, 0}, 2]}]",
            "0",
            "Ostrowski-Hermite exact derivative has zero contour residue",
        ),
        # 4. TrigReduce on P^1
        (
            "TrigReduce[Sin[3 x] - (3 Sin[x] - 4 Sin[x]^3)]",
            "0",
            "Triple-angle sine identity via TrigReduce",
        ),
        (
            "TrigReduce[Cos[4 x] - (8 Cos[x]^4 - 8 Cos[x]^2 + 1)]",
            "0",
            "Quadruple-angle cosine identity via TrigReduce",
        ),
        (
            "TrigReduce[2 Sin[x] Cos[x]]",
            "Sin[2 x]",
            "Double-angle product reduction",
        ),
        # 5. Projective Integrate extensions over Q(i, sqrt(2))
        (
            "TrigReduce[D[Integrate[Sqrt[Tan[x]], x], x] - Sqrt[Tan[x]]]",
            "0",
            "Derivative of projective primitive for Sqrt[Tan[x]] equals integrand",
        ),
        (
            "TrigReduce[D[Integrate[Sqrt[Cot[x]], x], x] - Sqrt[Cot[x]]]",
            "0",
            "Derivative of projective primitive for Sqrt[Cot[x]] equals integrand",
        ),
        (
            "FreeQ[Integrate[1 / (1 + Sin[x]^4), x], Integrate]",
            "True",
            "Projective Weierstrass primitive for 1/(1 + Sin[x]^4) evaluates in closed form",
        ),
        # 6. Dyadic half-angle tower Cos[p*Pi/2^k], Sin[p*Pi/2^k] over Q(sqrt(2))
        (
            "Cos[Pi / 16]",
            "Sqrt[1 / 2 + Sqrt[1 / 2 + Sqrt[2] / 4] / 2]",
            "Exact nested-radical Cos[Pi/16] via projective half-angle tower",
        ),
        (
            "Sin[Pi / 16]",
            "Sqrt[1 / 2 - Sqrt[1 / 2 + Sqrt[2] / 4] / 2]",
            "Exact nested-radical Sin[Pi/16] via projective half-angle tower",
        ),
        (
            "Simplify[Cos[Pi / 16]^2 + Sin[Pi / 16]^2]",
            "1",
            "Unitary circle invariant Cos[Pi/16]^2 + Sin[Pi/16]^2 == 1",
        ),
        (
            "Simplify[Cos[Pi / 32]^2 + Sin[Pi / 32]^2]",
            "1",
            "Unitary circle invariant Cos[Pi/32]^2 + Sin[Pi/32]^2 == 1",
        ),
        # 7. TrigExpand, TrigFactor, TrigToExp, ExpToTrig
        (
            "TrigExpand[Sin[2 x]]",
            "2 Cos[x] Sin[x]",
            "TrigExpand of double-angle sine",
        ),
        (
            "TrigFactor[Sin[x]^2 - Cos[x]^2]",
            "(-Cos[x] + Sin[x]) (Cos[x] + Sin[x])",
            "TrigFactor of difference of squares",
        ),
        (
            "TrigToExp[Cos[x]]",
            "E ^ (-I x) / 2 + E ^ (I x) / 2",
            "TrigToExp of Cos[x]",
        ),
        (
            "ExpToTrig[Exp[I x] + Exp[-I x]]",
            "2 Cos[x]",
            "ExpToTrig of conjugate exponential pair",
        ),
        # 8. LaplaceTransform, InverseLaplaceTransform, and infinite-dimensional StieltjesPadeResolvent
        (
            "LaplaceTransform[Sin[t], t, s]",
            "1 / (1 + s ^ 2)",
            "LaplaceTransform of Sin[t]",
        ),
        (
            "InverseLaplaceTransform[1 / (1 + s^2), s, t]",
            "Sin[t]",
            "InverseLaplaceTransform of 1/(1 + s^2)",
        ),
        (
            "StieltjesPadeResolvent[{1, 3, 11, 43}, s]",
            "(-2 + s) / (4 - 5 s + s ^ 2)",
            "Stieltjes-Pade [1/2] operator resolvent from moments {1, 3, 11, 43}",
        ),
        (
            "InverseLaplaceTransform[StieltjesPadeResolvent[{1, 3, 11, 43}, s], s, t]",
            "E ^ t / 3 + 2 E ^ (4 t) / 3",
            "Riesz-Dunford time-evolution operator from Stieltjes-Pade resolvent",
        ),
        # 9. Non-circular pure-rational ProjectiveConstant for Pi, E, Log2, GoldenRatio, Lemniscate, Gamma14, Catalan, Apery, EulerGamma
        (
            'Abs[ProjectiveConstant["Pi", 30] - 314159265358979323846264338328 / 10^29] < 10^-25',
            "True",
            "Non-circular projective Pi via Gaussian (5+i)^4(239-i) and Cayley-Pade (5,5)",
        ),
        (
            'Abs[ProjectiveConstant["E", 30] - 271828182845904523536028747135 / 10^29] < 10^-25',
            "True",
            "Non-circular projective E via dyadic halving and Cayley-Pade (5,5)",
        ),
        (
            'Abs[ProjectiveConstant["Log2", 30] - 693147180559945309417232121458 / 10^30] < 10^-25',
            "True",
            "Non-circular projective ln(2) via Heron descent and Cayley-Pade (5,5)",
        ),
        (
            'Abs[ProjectiveConstant["GoldenRatio", 30] - 161803398874989484820458683437 / 10^29] < 10^-25',
            "True",
            "Non-circular projective GoldenRatio via Heron iteration",
        ),
        (
            'Abs[ProjectiveConstant["Lemniscate", 30] - 262205755429211981046483958989 / 10^29] < 10^-25',
            "True",
            "Non-circular projective Gauss lemniscate constant varpi via AGM(1, sqrt(2))",
        ),
        (
            'Abs[ProjectiveConstant["Gamma14", 30] - 362560990822190831193068515587 / 10^29] < 10^-25',
            "True",
            "Non-circular projective Gamma(1/4) via Gauss AGM(1, sqrt(2))",
        ),
        (
            'Abs[ProjectiveConstant["Catalan", 30] - 915965594177219015054603514932 / 10^30] < 10^-25',
            "True",
            "Non-circular projective Catalan G via Ramanujan Log_P(2 + sqrt(3)) over Q(sqrt(3))",
        ),
        (
            'Abs[ProjectiveConstant["Apery", 30] - 120205690315959428539973816151 / 10^29] < 10^-25',
            "True",
            "Non-circular projective Apery zeta(3) via Amdeberhan-Zeilberger rational acceleration",
        ),
        (
            'Abs[ProjectiveConstant["EulerGamma", 30] - 577215664901532860606512090082 / 10^30] < 10^-25',
            "True",
            "Non-circular projective Euler-Mascheroni gamma via Brent-McMillan + Log_P(n)",
        ),
    ],
)
def test_projective_calculus_builtins(
    str_expr: str, str_expected: str, fail_msg: str
) -> None:
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
    )
