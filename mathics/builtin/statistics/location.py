"""
Location Statistics
"""

from mathics.algorithm.introselect import introselect
from mathics.builtin.base import Builtin
from mathics.builtin.statistics.base import NotRectangularException, Rectangular
from mathics.core.atoms import Integer2
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import SymbolDivide, SymbolPlus
from mathics.core.systemsymbols import SymbolMedian


class Mean(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Mean.html</url>

    <dl>
    <dt>'Mean[$list$]'
      <dd>returns the statistical mean of $list$.
    </dl>

    >> Mean[{26, 64, 36}]
     = 42

    >> Mean[{1, 1, 2, 3, 5, 8}]
     = 10 / 3

    >> Mean[{a, b}]
     = (a + b) / 2
    """

    summary_text = "mean of a list"
    rules = {
        "Mean[list_]": "Total[list] / Length[list]",
    }


class Median(Rectangular):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Median.html</url>

    <dl>
      <dt>'Median[$list$]'
      <dd>returns the median of $list$.
    </dl>

    >> Median[{26, 64, 36}]
     = 36

    For lists with an even number of elements, Median returns the mean of the two middle values:
    >> Median[{-11, 38, 501, 1183}]
     = 539 / 2

    Passing a matrix returns the medians of the respective columns:
    >> Median[{{100, 1, 10, 50}, {-1, 1, -2, 2}}]
     = {99 / 2, 1, 4, 26}
    """

    messages = {"rectn": "Expected a rectangular array of numbers at position 1 in ``."}
    summary_text = "central value of a dataset"

    def eval(self, data, evaluation: Evaluation):
        "Median[data_List]"
        if not data.elements:
            return
        if all(element.get_head_name() == "System`List" for element in data.elements):
            try:
                return self.rect(data)
            except NotRectangularException:
                evaluation.message("Median", "rectn", Expression(SymbolMedian, data))
        elif all(element.is_numeric(evaluation) for element in data.elements):
            v = data.get_mutable_elements()  # copy needed for introselect
            n = len(v)
            if n % 2 == 0:  # even number of elements?
                i = n // 2
                a = introselect(v, i)
                b = introselect(v, i - 1)
                return Expression(SymbolDivide, Expression(SymbolPlus, a, b), Integer2)
            else:
                i = n // 2
                return introselect(v, i)
        else:
            evaluation.message("Median", "rectn", Expression(SymbolMedian, data))


# TODO: Commonest, TrimmedMean WindsorizedMean, BiweightLocation, SpatialMedian, CentralFeature,
#       HarmonicMean, GeometricMean, ContraharmonicMean
