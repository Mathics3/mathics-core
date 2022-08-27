# -*- coding: utf-8 -*-
"""
General Statistics
"""

# from mathics.builtin.base import Builtin, SympyFunction
from mathics.builtin.base import Builtin

# import sympy.stats
# from mathics.core.convert.sympy import from_sympy


class CentralMoment(Builtin):
    """
    <url>:Central moment: https://en.wikipedia.org/wiki/Central_moment</url> (<url>:WMA: https://reference.wolfram.com/language/ref/CentralMoment.html</url>)

    <dl>
      <dt>'CentralMoment[$list$, $r$]'
      <dd>gives the the $r$th central moment (i.e. the $r$th moment about the mean) of $list$.
    </dl>

    >> CentralMoment[{1.1, 1.2, 1.4, 2.1, 2.4}, 4]
     = 0.100845
    """

    rules = {
        "CentralMoment[list_List, r_]": "Total[(list - Mean[list]) ^ r] / Length[list]",
    }
    summary_text = "central moments of distributions and data"


# class Moment(SympyFunction):
#     """
#     <dl>
#       <dt>'Moment[$sample_List$, $r$]'
#       <dd>gives the the $r$th sample moment of the elements of $list$.
#     </dl>

#     >> Moment[{1.1, 1.2, 1.4, 2.1, 2.4}, 4]
#      = 0.100845
#     """

#     summary_text = "moment of distributions and data"
#     sympy_name = "Moment"

#     def apply_sample_r(self, sample, r, evaluation):
#         "%(name)s[sample_List, r_]"
#         sympy_sample = sample.to_sympy()
#         sympy_r = r.to_sympy()
#         return from_sympy(sympy.stats.Moment(sympy_sample, sympy_r))


# TODO FactorialMoment, Cumulant, RootMeanSquare, Expectation, Probability, BinCounts
