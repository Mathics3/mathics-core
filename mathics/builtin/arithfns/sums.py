# -*- coding: utf-8 -*-
"""
Sums, Simple Statistics

These functions perform a simple arithmetic computation over a list.
"""


from mathics.builtin.base import Builtin


class Accumulate(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Accumulate.html</url>

    <dl>
      <dt>'Accumulate[$list$]'
      <dd>accumulates the values of $list$, returning a new list.
    </dl>

    >> Accumulate[{1, 2, 3}]
     = {1, 3, 6}
    """

    summary_text = "cumulative sums in a list"
    rules = {"Accumulate[head_]": "FoldList[Plus, head]"}


class Total(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Total.html</url>

    <dl>
      <dt>'Total[$list$]'
      <dd>adds all values in $list$.

      <dt>'Total[$list$, $n$]'
      <dd>adds all values up to level $n$.

      <dt>'Total[$list$, {$n$}]'
      <dd>totals only the values at level {$n$}.

      <dt>'Total[$list$, {$n_1$, $n_2$}]'
      <dd>totals at levels {$n_1$, $n_2$}.
    </dl>

    >> Total[{1, 2, 3}]
     = 6
    >> Total[{{1, 2, 3}, {4, 5, 6}, {7, 8 ,9}}]
     = {12, 15, 18}

    Total over rows and columns
    >> Total[{{1, 2, 3}, {4, 5, 6}, {7, 8 ,9}}, 2]
     = 45

    Total over rows instead of columns
    >> Total[{{1, 2, 3}, {4, 5, 6}, {7, 8 ,9}}, {2}]
     = {6, 15, 24}
    """

    summary_text = "total of the elements in a list"
    rules = {
        "Total[head_]": "Apply[Plus, head]",
        "Total[head_, n_]": "Apply[Plus, Flatten[head, n]]",
    }
