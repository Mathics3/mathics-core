# -*- coding: utf-8 -*-

"""
Shape Statistics
"""

from mathics.builtin.base import Builtin


class Kurtosis(Builtin):
    """
    <url>:Kurtosis: https://en.wikipedia.org/wiki/Kurtosis</url> (<url>:WMA: https://reference.wolfram.com/language/ref/Kurtosis.html</url>)
    <dl>
      <dt>'Kurtosis[$list$]'
      <dd>gives the Pearson measure of kurtosis for $list$ (a measure of existing outliers).
    </dl>

    >> Kurtosis[{1.1, 1.2, 1.4, 2.1, 2.4}]
     = 1.42098
    """

    rules = {
        "Kurtosis[list_List]": "CentralMoment[list, 4] / (CentralMoment[list, 2] ^ 2)",
    }
    summary_text = "kurtosis coefficient"


class Skewness(Builtin):
    """
    <url>:Skewness: https://en.wikipedia.org/wiki/Skewness</url> (<url>:WMA: https://reference.wolfram.com/language/ref/Skewness.html</url>)

    <dl>
      <dt>'Skewness[$list$]'
      <dd>gives Pearson's moment coefficient of skewness for $list$ (a measure for estimating the symmetry of a distribution).
    </dl>

    >> Skewness[{1.1, 1.2, 1.4, 2.1, 2.4}]
     = 0.407041
    """

    rules = {
        "Skewness[list_List]": "CentralMoment[list, 3] / (CentralMoment[list, 2] ^ (3 / 2))",
    }
    summary_text = "skewness coefficient"


# TODO: QuartileSkewness, Entropy, EstimatedDistribution
