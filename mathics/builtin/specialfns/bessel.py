"""
Bessel and Related Functions
"""

import mpmath


from mathics.builtin.arithmetic import _MPMathFunction
from mathics.builtin.base import Builtin
from mathics.core.atoms import Integer
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.number import machine_precision, get_precision, PrecisionValueError
from mathics.core.number import prec as _prec

from mathics.core.attributes import (
    listable as LISTABLE,
    n_hold_first as N_HOLD_FIRST,
    numeric_function as NUMERIC_FUNCTION,
    protected as PROTECTED,
    read_protected as READ_PROTECTED,
)


class _Bessel(_MPMathFunction):

    attributes = LISTABLE | NUMERIC_FUNCTION | PROTECTED | READ_PROTECTED

    nargs = {2}


class AiryAi(_MPMathFunction):
    """
    <url>:Airy function of the first kind: https://en.wikipedia.org/wiki/Airy_function</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.bessel.airyai</url>, <url>:WMA: https://reference.wolfram.com/language/ref/AiryAi.html</url>)
    <dl>
      <dt>'AiryAi[$x$]'
      <dd>returns the Airy function Ai($x$).
    </dl>

    Exact values:
    >> AiryAi[0]
     = 3 ^ (1 / 3) / (3 Gamma[2 / 3])

    'AiryAi' can be evaluated numerically:
    >> AiryAi[0.5]
     = 0.231694
    >> AiryAi[0.5 + I]
     = 0.157118 - 0.24104 I

    >> Plot[AiryAi[x], {x, -10, 10}]
     = -Graphics-
    """

    rules = {
        "Derivative[1][AiryAi]": "AiryAiPrime",
    }

    mpmath_name = "airyai"
    summary_text = "Airy's function Ai"
    sympy_name = "airyai"


class AiryAiPrime(_MPMathFunction):
    """
    Derivative of Airy function (<url>:Sympy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.bessel.airyaiprime</url>, <url>:WMA:https://reference.wolfram.com/language/ref/AiryAiPrime.html</url>)
    <dl>
      <dt>'AiryAiPrime[$x$]'
      <dd>returns the derivative of the Airy function 'AiryAi[$x$]'.
    </dl>

    Exact values:
    >> AiryAiPrime[0]
     = -3 ^ (2 / 3) / (3 Gamma[1 / 3])

    Numeric evaluation:
    >> AiryAiPrime[0.5]
     = -0.224911
    """

    mpmath_name = ""

    rules = {
        "Derivative[1][AiryAiPrime]": "(#1 AiryAi[#1])&",
    }

    summary_text = "derivative of the Airy's function Ai"
    sympy_name = "airyaiprime"

    def get_mpmath_function(self, args):
        return lambda x: mpmath.airyai(x, derivative=1)


class AiryAiZero(Builtin):
    """
    <dl>
      <dt>'AiryAiZero[$k$]'
      <dd>returns the $k$th zero of the Airy function Ai($z$).
    </dl>

    >> N[AiryAiZero[1]]
     = -2.33811

    #> AiryAiZero[1]
     = AiryAiZero[1]

    #> AiryAiZero[1.]
     = AiryAiZero[1.]

    #> AiryAi[AiryAiZero[1]]
     = 0

    #> N[AiryAiZero[2], 100]
     = -4.087949444130970616636988701457391060224764699108529754984160876025121946836047394331169160758270562
    """

    # TODO: 'AiryAiZero[$k$, $x0$]' - $k$th zero less than x0

    attributes = LISTABLE | N_HOLD_FIRST | NUMERIC_FUNCTION | PROTECTED | READ_PROTECTED

    rules = {
        "AiryAi[AiryAiZero[k_]]": "0",
    }

    summary_text = "kth zero of the Airy's function Ai"

    def apply_N(self, k, precision, evaluation):
        "N[AiryAiZero[k_Integer], precision_]"

        try:
            d = get_precision(precision, evaluation)
        except PrecisionValueError:
            return

        if d is None:
            p = machine_precision
        else:
            p = _prec(d)

        k_int = k.value

        with mpmath.workprec(p):
            result = mpmath.airyaizero(k_int)
            return from_mpmath(result, d)


class AiryBi(_MPMathFunction):
    """
    <dl>
    <dt>'AiryBi[$x$]'
      <dd>returns the Airy function of the second kind Bi($x$).
    </dl>

    Exact values:
    >> AiryBi[0]
     = 3 ^ (5 / 6) / (3 Gamma[2 / 3])

    Numeric evaluation:
    >> AiryBi[0.5]
     = 0.854277
    >> AiryBi[0.5 + I]
     = 0.688145 + 0.370815 I

    >> Plot[AiryBi[x], {x, -10, 2}]
     = -Graphics-
    """

    mpmath_name = "airybi"

    rules = {
        "Derivative[1][AiryBi]": "AiryBiPrime",
    }

    summary_text = "Airy's function Bi"
    sympy_name = "airybi"


class AiryBiPrime(_MPMathFunction):
    """
    <dl>
    <dt>'AiryBiPrime[$x$]'
        <dd>returns the derivative of the Airy function of the second
        kind 'AiryBi[$x$]'.
    </dl>

    Exact values:
    >> AiryBiPrime[0]
     = 3 ^ (1 / 6) / Gamma[1 / 3]

    Numeric evaluation:
    >> AiryBiPrime[0.5]
     = 0.544573
    """

    mpmath_name = ""
    sympy_name = "airybiprime"

    rules = {
        "Derivative[1][AiryBiPrime]": "(#1 AiryBi[#1])&",
    }

    summary_text = "derivative of the Airy's function Bi"

    def get_mpmath_function(self, args):
        return lambda x: mpmath.airybi(x, derivative=1)


class AiryBiZero(Builtin):
    """
    <dl>
    <dt>'AiryBiZero[$k$]'
      <dd>returns the $k$th zero of the Airy function Bi($z$).
    </dl>

    >> N[AiryBiZero[1]]
     = -1.17371

    #> AiryBiZero[1]
     = AiryBiZero[1]

    #> AiryBiZero[1.]
     = AiryBiZero[1.]

    #> AiryBi[AiryBiZero[1]]
     = 0

    #> N[AiryBiZero[2], 100]
     = -3.271093302836352715680228240166413806300935969100284801485032396261130864238742879252000673830055014
    """

    # TODO: 'AiryBiZero[$k$, $x0$]' - $k$th zero less than x0

    attributes = LISTABLE | N_HOLD_FIRST | NUMERIC_FUNCTION | PROTECTED | READ_PROTECTED

    rules = {
        "AiryBi[AiryBiZero[z_]]": "0",
    }

    summary_text = "kth zero of the Airy's function Bi"

    def apply_N(self, k: Integer, precision, evaluation):
        "N[AiryBiZero[k_Integer], precision_]"

        try:
            d = get_precision(precision, evaluation)
        except PrecisionValueError:
            return

        if d is None:
            p = machine_precision
        else:
            p = _prec(d)

        k_int = k.value

        with mpmath.workprec(p):
            result = mpmath.airybizero(k_int)
            return from_mpmath(result, d)


class AngerJ(_Bessel):
    """
    <url>:Anger function: https://en.wikipedia.org/wiki/Anger_function</url> (<url>:mpmath: https://mpmath.org/doc/current/functions/bessel.html#mpmath.angerj</url>, <url>:WMA: https://reference.wolfram.com/language/ref/AngerJ.html</url>)
    <dl>
      <dt>'AngerJ[$n$, $z$]'
      <dd>returns the Anger function J_$n$($z$).
    </dl>

    >> AngerJ[1.5, 3.5]
     = 0.294479

    >> Plot[AngerJ[1, x], {x, -10, 10}]
     = -Graphics-
    """

    # TODO: Associated Anger function AngerJ[v, u, z]

    mpmath_name = "angerj"
    summary_text = "Anger's function J"
    sympy_name = ""


# Bessel Functions


class BesselI(_Bessel):
    """

    <url>:Modified Bessel function of the first kind: https://en.wikipedia.org/wiki/Bessel_function#Bessel_functions_of_the_first_kind:_J%CE%B1</url> (<url>:Sympy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.bessel.besseli</url>, <url>:WMA: https://reference.wolfram.com/language/ref/BesselI.html</url>)

    <dl>
    <dt>'BesselI[$n$, $z$]'
      <dd>returns the modified Bessel function of the first kind I_$n$($z$).
    </dl>

    >> BesselI[1.5, 4]
     = 8.17263

    >> Plot[BesselI[0, x], {x, 0, 5}]
     = -Graphics-
    """

    rules = {
        "Derivative[0, 1][BesselI]": "((BesselI[-1 + #1, #2] + BesselI[1 + #1, #2])/2)&",
    }

    mpmath_name = "besseli"
    sympy_name = "besseli"
    summary_text = "Bessel's function of the second kind"


class BesselJ(_Bessel):
    """
    <url>:Bessel function of the first kind: https://en.wikipedia.org/wiki/Bessel_function#Bessel_functions_of_the_first_kind:_J%CE%B1</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.bessel.besselj</url>, <url>:WMA: https://reference.wolfram.com/language/ref/BesselJ.html</url>)

    <dl>
    <dt>'BesselJ[$n$, $z$]'
      <dd>returns the Bessel function of the first kind J_$n$($z$).
    </dl>

    >> BesselJ[0, 5.2]
     = -0.11029

    #> BesselJ[2.5, 1]
     = 0.0494968

    >> D[BesselJ[n, z], z]
     = -BesselJ[1 + n, z] / 2 + BesselJ[-1 + n, z] / 2

    #> BesselJ[0., 0.]
     = 1.

    >> Plot[BesselJ[0, x], {x, 0, 10}]
     = -Graphics-
    """

    # TODO: Sympy Backend is not as powerful as Mathematica
    """
    >> BesselJ[1/2, x]
     = Sqrt[2 / Pi] Sin[x] / Sqrt[x]
    """

    mpmath_name = "besselj"
    rules = {
        "Derivative[0,1][BesselJ]": "(BesselJ[#1- 1, #2] / 2 - BesselJ[#1 + 1, #2] / 2)&",
    }

    summary_text = "Bessel's function of the first kind"
    sympy_name = "besselj"


class BesselK(_Bessel):
    """
    <url>:Modified Bessel function of the second kind: https://en.wikipedia.org/wiki/Bessel_function#Modified_Bessel_functions:_I%CE%B1,_K%CE%B1</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.bessel.besselk</url>, <url>:WMA:https://reference.wolfram.com/language/ref/BesselJ.html</url>)

    <dl>
      <dt>'BesselK[$n$, $z$]'
      <dd>returns the modified Bessel function of the second kind K_$n$($z$).
    </dl>

    >> BesselK[1.5, 4]
     = 0.014347

    >> Plot[BesselK[0, x], {x, 0, 5}]
     = -Graphics-
    """

    mpmath_name = "besselk"

    rules = {
        "Derivative[0, 1][BesselK]": "((-BesselK[-1 + #1, #2] - BesselK[1 + #1, #2])/2)&",
    }

    summary_text = "modified Bessel's function of the second kind"
    sympy_name = "besselk"


class BesselY(_Bessel):
    """
    <dl>
      <dt>'BesselY[$n$, $z$]'
      <dd>returns the Bessel function of the second kind Y_$n$($z$).
    </dl>

    >> BesselY[1.5, 4]
     = 0.367112

    ## Returns ComplexInfinity instead
    ## #> BesselY[0., 0.]
    ##  = -Infinity

    >> Plot[BesselY[0, x], {x, 0, 10}]
     = -Graphics-
    """

    # TODO: Special Values
    """
    >> BesselY[0, 0]
     = -Infinity
    """
    rules = {
        "Derivative[0,1][BesselY]": "(BesselY[-1 + #1, #2] / 2 - BesselY[1 + #1, #2] / 2)&",
    }

    mpmath_name = "bessely"
    summary_text = "Bessel's function of the second kind"
    sympy_name = "bessely"


class BesselJZero(_Bessel):
    """
    <dl>
      <dt>'BesselJZero[$n$, $k$]'
      <dd>returns the $k$th zero of the Bessel function of the first kind J_$n$($z$).
    </dl>

    >> N[BesselJZero[0, 1]]
     = 2.40483

    >> N[BesselJZero[0, 1], 10]
     = 2.404825558
    """

    mpmath_name = "besseljzero"
    summary_text = "kth zero of the Bessel's function of the first kind"
    sympy_name = ""


class BesselYZero(_Bessel):
    """
    <dl>
      <dt>'BesselYZero[$n$, $k$]'
      <dd>returns the $k$th zero of the Bessel function of the second kind Y_$n$($z$).
    </dl>

    >> N[BesselYZero[0, 1]]
     = 0.893577

    >> N[BesselYZero[0, 1], 10]
     = 0.8935769663
    """

    mpmath_name = "besselyzero"
    summary_text = "kth zero of the Bessel's function of the second kind"
    sympy_name = ""


# Hankel Functions


class HankelH1(_Bessel):
    """
    <dl>
      <dt>'HankelH1[$n$, $z$]'
      <dd>returns the Hankel function of the first kind H_$n$^1 ($z$).
    </dl>

    >> HankelH1[1.5, 4]
     = 0.185286 + 0.367112 I
    """

    mpmath_name = "hankel1"

    rules = {
        "Derivative[0, 1][HankelH1]": "((HankelH1[-1 + #1, #2] - HankelH1[1 + #1, #2])/2)&",
    }
    summary_text = "Hankel's function of the first kind"
    sympy_name = "hankel1"


class HankelH2(_Bessel):
    """
    <dl>
      <dt>'HankelH2[$n$, $z$]'
      <dd>returns the Hankel function of the second kind H_$n$^2 ($z$).
    </dl>

    >> HankelH2[1.5, 4]
     = 0.185286 - 0.367112 I
    """

    mpmath_name = "hankel2"
    rules = {
        "Derivative[0, 1][HankelH2]": "((HankelH2[-1 + #1, #2] - HankelH2[1 + #1, #2])/2)&",
    }

    summary_text = "Hankel's function of the second kind"
    sympy_name = "hankel2"


# Kelvin Functions


class KelvinBei(_Bessel):
    """
    <url>:Kelvin function bei: https://en.wikipedia.org/wiki/Kelvin_functions#bei(x)</url> (<url>:mpmath: https://mpmath.org/doc/current/functions/bessel.html#bei</url>, <url>:WMA: https://reference.wolfram.com/language/ref/KelvinBei.html</url>)

    <dl>
      <dt>'KelvinBei[$z$]'
      <dd>returns the Kelvin function bei($z$).

      <dt>'KelvinBei[$n$, $z$]'
      <dd>returns the Kelvin function bei_$n$($z$).
    </dl>

    >> KelvinBei[0.5]
     = 0.0624932

    >> KelvinBei[1.5 + I]
     = 0.326323 + 0.755606 I

    >> KelvinBei[0.5, 0.25]
     = 0.370153

    >> Plot[KelvinBei[x], {x, 0, 10}]
     = -Graphics-
    """

    mpmath_name = "bei"
    rules = {
        "KelvinBei[z_]": "KelvinBei[0, z]",
        "Derivative[1][KelvinBei]": "((2*KelvinBei[1, #1] - 2*KelvinBer[1, #1])/(2*Sqrt[2]))&",
    }

    summary_text = "Kelvin's function bei"
    sympy_name = ""


class KelvinBer(_Bessel):
    """
    <url>:Kelvin function ber: https://en.wikipedia.org/wiki/Kelvin_functions#ber(x)</url> (<url>:mpmath: https://mpmath.org/doc/current/functions/bessel.html#ber</url>, <url>:WMA: https://reference.wolfram.com/language/ref/KelvinBer.html</url>)
    <dl>
      <dt>'KelvinBer[$z$]'
      <dd>returns the Kelvin function ber($z$).

      <dt>'KelvinBer[$n$, $z$]'
      <dd>returns the Kelvin function ber_$n$($z$).
    </dl>

    >> KelvinBer[0.5]
     = 0.999023

    >> KelvinBer[1.5 + I]
     = 1.1162 - 0.117944 I

    >> KelvinBer[0.5, 0.25]
     = 0.148824

    >> Plot[KelvinBer[x], {x, 0, 10}]
     = -Graphics-
    """

    mpmath_name = "ber"
    rules = {
        "KelvinBer[z_]": "KelvinBer[0, z]",
        "Derivative[1][KelvinBer]": "((2*KelvinBei[1, #1] + 2*KelvinBer[1, #1])/(2*Sqrt[2]))&",
    }

    summary_text = "Kelvin's function ber"
    sympy_name = ""


class KelvinKei(_Bessel):
    """
    <url>:Kelvin function kei: https://en.wikipedia.org/wiki/Kelvin_functions#kei(x)</url> (<url>:mpmath: https://mpmath.org/doc/current/functions/bessel.html#kei</url>, <url>:WMA: https://reference.wolfram.com/language/ref/KelvinKei.html</url>)

    <dl>
      <dt>'KelvinKei[$z$]'
      <dd>returns the Kelvin function kei($z$).

      <dt>'KelvinKei[$n$, $z$]'
      <dd>returns the Kelvin function kei_$n$($z$).
    </dl>

    >> KelvinKei[0.5]
     = -0.671582

    >> KelvinKei[1.5 + I]
     = -0.248994 + 0.303326 I

    >> KelvinKei[0.5, 0.25]
     = -2.0517

    >> Plot[KelvinKei[x], {x, 0, 10}]
     = -Graphics-
    """

    mpmath_name = "kei"

    rules = {
        "KelvinKei[z_]": "KelvinKei[0, z]",
    }

    summary_text = "Kelvin's function kei"
    sympy_name = ""


class KelvinKer(_Bessel):
    """
    <url>:Kelvin function ker: https://en.wikipedia.org/wiki/Kelvin_functions#ker(x)</url> (<url>:mpmath: https://mpmath.org/doc/current/functions/bessel.html#ker</url>, <url>:WMA: https://reference.wolfram.com/language/ref/KelvinKer.html</url>)

    <dl>
      <dt>'KelvinKer[$z$]'
      <dd>returns the Kelvin function ker($z$).
    <dt>'KelvinKer[$n$, $z$]'
      <dd>returns the Kelvin function ker_$n$($z$).
    </dl>

    >> KelvinKer[0.5]
     = 0.855906

    >> KelvinKer[1.5 + I]
     = -0.167162 - 0.184404 I

    >> KelvinKer[0.5, 0.25]
     = 0.450023

    >> Plot[KelvinKer[x], {x, 0, 10}]
     = -Graphics-
    """

    mpmath_name = "ker"
    rules = {
        "KelvinKer[z_]": "KelvinKer[0, z]",
    }
    summary_text = "Kelvin's function ker"
    sympy_name = ""


class SphericalBesselJ(_Bessel):
    """

    <url>:Spherical Bessel function of the first kind: https://en.wikipedia.org/wiki/Bessel_function#Spherical_Bessel_functions</url> (<url>:Sympy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.bessel.jn</url>, <url>:WMA: https://reference.wolfram.com/language/ref/SphericalBesselJ.html</url>)

    <dl>
      <dt>'SphericalBesselJ[$n$, $z$]'
      <dd>returns the spherical Bessel function of the first kind Y_$n$($z$).
    </dl>

    >> SphericalBesselJ[1, 5.2]
     = -0.122771

    ## FIXME: should be able to tolerate Plotting at 0.
    >> Plot[SphericalBesselJ[1, x], {x, 0.1, 10}]
     = -Graphics-
    """

    rules = {"SphericalBesselJ[n_, z_]": "Sqrt[Pi / 2] / Sqrt[z] BesselJ[n + 0.5, z]"}

    summary_text = "spherical Bessel's function of the first kind"
    sympy_name = "jn"


class SphericalBesselY(_Bessel):
    """
    <url>:Spherical Bessel function of the first kind: https://en.wikipedia.org/wiki/Bessel_function#Spherical_Bessel_functions</url> (<url>:Sympy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.bessel.yn</url>, <url>:WMA: https://reference.wolfram.com/language/ref/SphericalBesselY.html</url>)

    <dl>
      <dt>'SphericalBesselY[$n$, $z$]'
      <dd>returns the spherical Bessel function of the second kind Y_$n$($z$).
    </dl>

    >> SphericalBesselY[1, 5.5]
     = 0.104853

    >> Plot[SphericalBesselY[1, x], {x, 0, 10}]
     = -Graphics-
    """

    rules = {"SphericalBesselY[n_, z_]": "Sqrt[Pi / 2] / Sqrt[z] BesselY[n + 0.5, z]"}

    summary_text = "spherical Bessel's function of the second kind"
    sympy_name = "yn"


class SphericalHankelH1(_Bessel):
    """

    <url>:Spherical Bessel function of the first kind: https://en.wikipedia.org/wiki/Bessel_function#Spherical_Bessel_functions</url>

    <dl>
      <dt>'SphericalHankelH1[$n$, $z$]'
      <dd>returns the spherical Hankel function of the first kind h_$n$^(1)($z$).
    </dl>

    >> SphericalHankelH1[3, 1.5]
     = 0.0283246 - 3.78927 I
    """

    rules = {"SphericalHankelH1[n_, z_]": "Sqrt[Pi / 2] / Sqrt[z] HankelH1[n + 0.5, z]"}

    summary_text = "spherical Hankel's function of the first kind"
    sympy_name = "hankel1"


class SphericalHankelH2(_Bessel):
    """

    <url>:Spherical Bessel function of the second kind: https://en.wikipedia.org/wiki/Bessel_function#Spherical_Bessel_functions</url>

    <dl>
      <dt>'SphericalHankelH1[$n$, $z$]'
      <dd>returns the spherical Hankel function of the second kind h_$n$^(2)($z$).
    </dl>

    >> SphericalHankelH2[3, 1.5]
     = 0.0283246 + 3.78927 I
    """

    rules = {"SphericalHankelH2[n_, z_]": "Sqrt[Pi / 2] / Sqrt[z] HankelH2[n + 0.5, z]"}

    summary_text = "spherical Hankel's function of the second kind"
    sympy_name = "hankel2"


class StruveH(_Bessel):
    """
    <url>:Struve functions H: https://en.wikipedia.org/wiki/Struve_function</url>
    <dl>
      <dt>'StruveH[$n$, $z$]'
      <dd>returns the Struve function H_$n$($z$).
    </dl>

    >> StruveH[1.5, 3.5]
     = 1.13192

    >> Plot[StruveH[0, x], {x, 0, 10}]
     = -Graphics-
    """

    mpmath_name = "struveh"
    summary_text = "Struvel's function H"
    sympy_name = ""


class StruveL(_Bessel):
    """
    <url>:Modified Struve functions L: https://en.wikipedia.org/wiki/Struve_function</url>
    <dl>
      <dt>'StruveL[$n$, $z$]'
      <dd>returns the modified Struve function L_$n$($z$).
    </dl>

    >> StruveL[1.5, 3.5]
     = 4.41126

    >> Plot[StruveL[0, x], {x, 0, 5}]
     = -Graphics-
    """

    mpmath_name = "struvel"
    summary_text = "Struvel's function L"
    sympy_name = ""


class WeberE(_Bessel):
    """
    <dl>
      <dt>'WeberE[$n$, $z$]'
      <dd>returns the Weber function E_$n$($z$).
    </dl>

    >> WeberE[1.5, 3.5]
     = -0.397256

    >> Plot[WeberE[1, x], {x, -10, 10}]
     = -Graphics-
    """

    # TODO: Associated Weber function WeberE[v, u, z]

    mpmath_name = "webere"
    summary_text = "Weber's function E"
    sympy_name = ""
