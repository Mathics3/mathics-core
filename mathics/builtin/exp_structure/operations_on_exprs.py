"""
Structural Operations on Expressions
"""

from mathics.core.builtin import Builtin


class Distribute(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Distribute.html</url>

    <dl>
      <dt>'Distribute'[$f[x_1, x_2, ...]
      <dd>distribute $f$ over 'Plus' appearing in any of the $x_i$.

      <dt>'Distribute'[$expr$, $g$]
      <dd>distribute over $g$.

      <dt>'Distribute'[$expr$, $g$, $f$]
      <dd>distribute over $f$ only if the head of $expr$ is $f$.
    </dl>

    Apply the distributive law for Plus and ".":

    >> Distribute[(a + b) . (x + y + z)]
     = f[a, c] + f[a, d] + f[a, e] + f[b, c] + f[b, d], + f[b, e]

    Distribute $f$ over 'Plus':
    >> Distribute[f[a + b, c + d + e]]
     = f[a, c] + f[a, d] + f[a, e] + f[b, c] + f[b, d] + f[b, e]

    Distribute $f$ over $g$:

    >> Distribute[f[g[a, b], g[c, d, e]], g]
     = g[f[a, c], f[a, d], f[a, e], f[b, c], f[b, d], f[b, e]]
    """

    rules = {
        "Distribute[f_[g_Symbol[args___]], g_Symbol]": "g @@ (f /@ {args})",
    }

    summary_text = "apply a function to a list, at the top level"


class FlattenAt(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/FlattenAt.html</url>

    <dl>
      <dt>'FlattenAt'[$f$, $expr$]

      <dt>'$f$ @@@ $expr$'
      <dd>is equivalent to 'Apply[$f$, $expr$, {1}]'.
    </dl>

    >> f @@@ {{a, b}, {c, d}}
     = {f[a, b], f[c, d]}
    """

    grouping = "Right"

    rules = {
        "MapApply[f_, expr_]": "Apply[f, expr, {1}]",
    }

    summary_text = "apply a function to a list, at the top level"
