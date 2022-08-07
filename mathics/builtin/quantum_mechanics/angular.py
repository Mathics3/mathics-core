"""
Angular Momentum

<url>:Angular momentum: https://en.wikipedia.org/wiki/Angular_momentum</url> in physics is the rotational analog of linear momentum. It is an important quantity in physics because it is a conserved quantity—the total angular momentum of a closed system remains constant.
"""

from sympy.physics.matrices import msigma
from sympy.physics.quantum.cg import CG
from sympy.physics.wigner import wigner_3j, wigner_6j
from typing import List

from mathics.builtin.base import SympyFunction
from mathics.core.atoms import Integer
from mathics.core.convert.sympy import from_sympy
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol

from mathics.core.attributes import (
    listable as A_LISTABLE,
    # numeric_function as A_NUMERIC_FUNCTION,
    protected as A_PROTECTED,
    read_protected as A_READ_PROTECTED,
)


class ClebschGordan(SympyFunction):
    """
    <url>:Clebsch–Gordan coefficients matrices: https://en.wikipedia.org/wiki/Clebsch%E2%80%93Gordan_coefficients</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/physics/quantum/cg.html</url>, <url>:WMA: https://reference.wolfram.com/language/ref/ClebschGordan</url>)

    <dl>
      <dt>'ClebschGordan[{$j1$, $m1$}, {$j2$, $m2$}, {$j$ $m$}]'
      <dd>returns the Clebsch–Gordan coefficient for the decomposition of in terms of |$j$, $m$> in terms of $j2$, $m2$.
    </dl>

    >> ClebschGordan[{3 / 2, 3 / 2}, {1 / 2, -1 / 2}, {1, 1}]
     = Sqrt[3] / 2

    Compare with WMA example:
    >> ClebschGordan[{5, 0}, {4, 0}, {1, 0}] == Sqrt[5 / 33]
     = True

    """

    attributes = A_PROTECTED | A_READ_PROTECTED
    summary_text = "Clebsch–Gordan coefficient"
    sympy_name = "physics.quantum.cg.CG"

    def apply(
        self,
        j1m1: ListExpression,
        j2m2: ListExpression,
        jm: ListExpression,
        evaluation: Evaluation,
    ):
        "ClebschGordan[j1m1_List, j2m2_List, jm_List]"

        sympy_jms: List[int] = []

        for pair in (j1m1, j2m2, jm):
            if len(pair.elements) != 2:
                return
            sympy_jms += [p.to_sympy() for p in pair.elements]
        return from_sympy(CG(*sympy_jms).doit())


class PauliMatrix(SympyFunction):
    """
    <url>:Pauli matrices: https://en.wikipedia.org/wiki/Pauli_matrices</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/physics/matrices.html#sympy.physics.matrices.msigma</url>, <url>:WMA: https://reference.wolfram.com/language/ref/PauliMatrix.html</url>)

    <dl>
      <dt>'PauliMatrix[$k$]'
      <dd>returns the $k$th Pauli spin matrix).
    </dl>

    >> PauliMatrix[Range[3]]
     = {{{0, 1}, {1, 0}}, {{0, -I}, {I, 0}}, {{1, 0}, {0, -1}}}
    """

    attributes = A_LISTABLE | A_PROTECTED | A_READ_PROTECTED
    messages = {
        "pauli": "PauliMatrix parameter k=`` is not in the range 1..3.",
    }
    summary_text = "Pauli spin matrix"
    sympy_name = "physics.matrices.msigma"

    def apply(self, k: Integer, evaluation: Evaluation):
        "PauliMatrix[k_Integer]"
        py_k = k.value
        if 1 <= py_k <= 3:
            return from_sympy(msigma(py_k))
        else:
            evaluation.message("PauliMatrix", "pauli", k)


class SixJSymbol(SympyFunction):
    """
    <url>:6-j symbol: https://en.wikipedia.org/wiki/6-j_symbol</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/physics/wigner.html#sympy.physics.wigner.wigner_6j</url>, <url>:WMA: https://reference.wolfram.com/language/ref/SixJSymbol.html</url>)

    <dl>
      <dt>'SixJSymbol[{$j1, $j2$, $j3$}, {$j4$, $j5$, $j6$}]'
      <dd>returns the values of the Wigner 6-$j$ symbol.
    </dl>

    >> SixJSymbol[{3,3,3}, {3,3,3}]
     = -1 / 14

    >> SixJSymbol[{5,5,5}, {5,5,5}]
     = 1 / 52

    Compare with WMA example:
    >> SixJSymbol[{1, 2, 3}, {2, 1, 2}] == 1 / (5 Sqrt[21])
     = True

    Result 0 returned for unphysical cases:
    >> SixJSymbol[{1, 2, 3}, {4, 5, 12}]
     = 0
    """

    attributes = A_PROTECTED | A_READ_PROTECTED
    messages = {
        "sixjsymbol": "Parameter `` of `` has value ``; SixJSymbol cannot handle symbols yet.",
    }

    # WMA docs say Ricah 6-j symbol, but Wigner 6-j sees to be more likely, and that is what
    # https://mathworld.wolfram.com/Wigner6j-Symbol.html claims SixJSymbol means.
    # Also, Mathematica 5 refers to (Wigner) 6-j. So the WMA doc is probably wrong.
    summary_text = "values of the Wigner 6-j symbol"
    sympy_name = "physics.wigner.wigner_6j"

    def apply(self, j13: ListExpression, j46: ListExpression, evaluation: Evaluation):
        "SixJSymbol[j13_List, j46_List]"
        sympy_js = []
        i = 0
        for triple in (j13, j46):
            i += 1
            if len(triple.elements) != 3:
                return
            for element in triple.elements:
                if isinstance(element, Symbol):
                    evaluation.message("SixJSymbol", "sixjsymbol", i, triple, element)
                    return
                py_element = element.to_sympy()
                sympy_js.append(py_element)

        return from_sympy(wigner_6j(*sympy_js))


class ThreeJSymbol(SympyFunction):
    """
    <url>:3-j symbol: https://en.wikipedia.org/wiki/3-j_symbol</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/physics/wigner.html#sympy.physics.wigner.wigner_3j</url>, <url>:WMA: https://reference.wolfram.com/language/ref/ThreeJSymbol.html</url>)

    <dl>
      <dt>'ThreeJSymbol[{$j1, $m1}, {$j2$, $m2$}, {$j3$, $m3$}]'
      <dd>returns the values of the Wigner 3‐$j$ symbol. .
    </dl>

    Compare with SymPy examples:
    >> ThreeJSymbol[{2, 0}, {6, 0}, {4, 0}]
     = Sqrt[715] / 143

    >> ThreeJSymbol[{2, 0}, {6, 0}, {4, 1}]
     = 0

    Compare with WMA examples:
    >> ThreeJSymbol[{6, 0}, {4, 0}, {2, 0}] == Sqrt[5 / 143]
     = True

    >> ThreeJSymbol[{2, 1}, {2, 2}, {4, -3}] == -(1 / (3 Sqrt[2]))
     = True

    Result 0 returned for unphysical cases:
    >>ThreeJSymbol[{1, 2, 3}, {4, 5, 12}]
    """

    attributes = A_PROTECTED | A_READ_PROTECTED
    messages = {
        "threejsymbol": "Parameter `` of `` has value ``; ThreeJSymbol cannot handle symbols yet.",
    }
    summary_text = "values of the Wigner 3-j symbol"
    sympy_name = "physics.wigner.wigner_3j"

    def apply(
        self,
        j12: ListExpression,
        j34: ListExpression,
        j56: ListExpression,
        evaluation: Evaluation,
    ):
        "ThreeJSymbol[j12_List, j34_List, j56_List]"
        sympy_js = [None] * 6
        for i, pair in enumerate([j12, j34, j56]):
            if len(pair.elements) != 2:
                return
            for j, element in enumerate(pair.elements):
                if isinstance(element, Symbol):
                    evaluation.message("ThreeJSymbol", "threejsymbol", i, pair, element)
                    return
                py_element = element.to_sympy()
                # SymPy wants all of the j's together first and then all of the m's together
                # rather than pairs if (j, m).
                sympy_js[j * 3 + i] = py_element

        return from_sympy(wigner_3j(*sympy_js))
