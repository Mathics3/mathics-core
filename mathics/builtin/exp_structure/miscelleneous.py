"""
Miscellaneous Structural Operations on Expressions
"""

from mathics.core.attributes import A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolIdentity
from mathics.eval.exp_structure import eval_Distribute
from mathics.eval.tensors import eval_Outer


class Distribute(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Distribute.html</url>

    <dl>
      <dt>'Distribute'[$expr$]
      <dd>distributes $expr$ over 'Plus' (addition).
      <dt>'Distribute'[$expr$, $operator$]
      <dd>distributes $expr$ over the specified $operator$.
      <dt>'Distribute'[$expr$, $operator$, $f$]
      <dd>applies $f$ to each component of the result.

      ## <dt>'Distribute'[$expr$, $operator$, $f$, $gp$, $fp$]
      ## <dd>distributes $expr$ over $operator$, replacing outer function with $gp$ and inner function with $fp$.
    </dl>

    Distribute multiplication over addition:
    >> Distribute[a(b + c)]
     = a b + a c

    >> Distribute[(a + b)(c + d)]
     = a c + a d + b c + b d

    Using a custom target head:
    >> Distribute[f[a + b, c], Plus]
     = f[a, c] + f[b, c]

    Distribute can also work with lists:
    >> Distribute[{a(b + c), d(e + f)}]
     = {a b + a c, d e + d f}

    >> Distribute[Table[{1, 2}, {2}], List]
     = {{1, 1}, {1, 2}, {2, 1}, {2, 2}}

    ## Applying a function to results:
    ## >> Distribute[a(b + c), Plus, Square]
    ##  = Square[a b] + Square[a c]

    Special forms:
    >> Distribute[f[g[a + b]]]
     = f[g[a]] + f[g[b]]

    Distribute $f$ over $g$:
    >> Distribute[f[g[a, b], g[c, d, e]], g]
     = g[f[a, c], f[a, d], f[a, e], f[b, c], f[b, d], f[b, e]]

    ## Using a custom operator and functions:
    ## >> Distribute[f[g[a, b], g[c, d, e]], g, f, gp, fp]
    ##  = gp[fp[a, c], fp[a, d], fp[a, e], fp[b, c], fp[b, d], fp[b, e]]
    """

    attributes = A_PROTECTED

    eval_error = Builtin.generic_argument_error
    expected_args = range(1, 6)

    rules = {
        "Distribute[expr_]": "Distribute[expr, Plus]",
        "Distribute[expr_, operator_]": "Distribute[expr, operator, Identity]",
    }

    summary_text = "distribute functions over a head"

    def eval(self, expr, operator, filt, evaluation: Evaluation):
        "Distribute[expr_, operator_, filt_]"

        # Handle Identity filter
        if filt is SymbolIdentity:
            filt = None

        result = eval_Distribute(expr, operator, evaluation)

        if result is None:
            return expr

        if filt:
            return Expression(filt, result)

        return result

    # def eval_with_function_replacement(
    #         self, expr, operator, f, g, gp, fp, evaluation: Evaluation
    # ):
    #     "Distribute[expr_, f_, g_, gp_, fp_]"

    #     result = eval_Distribute_with_replacement(expr, f, g, gp, fp, evaluation)

    #     if result is None:
    #         return expr

    #     return result


class Outer(Builtin):
    """
    <url>:Outer product:https://en.wikipedia.org/wiki/Outer_product</url> \
    (<url>:WMA link: https://reference.wolfram.com/language/ref/Outer.html</url>)

    <dl>
      <dt>'Outer'[$f$, $x$, $y$]
      <dd>computes a generalised outer product of $x$ and $y$, using the function $f$ in place of multiplication.
    </dl>

    >> Outer[f, {a, b}, {1, 2, 3}]
     = {{f[a, 1], f[a, 2], f[a, 3]}, {f[b, 1], f[b, 2], f[b, 3]}}

    Outer product of two matrices:
    >> Outer[Times, {{a, b}, {c, d}}, {{1, 2}, {3, 4}}]
     = {{{{a, 2 a}, {3 a, 4 a}}, {{b, 2 b}, {3 b, 4 b}}}, {{{c, 2 c}, {3 c, 4 c}}, {{d, 2 d}, {3 d, 4 d}}}}

    Outer product of two sparse arrays:
    >> Outer[Times, SparseArray[{{1, 2} -> a, {2, 1} -> b}], SparseArray[{{1, 2} -> c, {2, 1} -> d}]]
     = SparseArray[Automatic, {2, 2, 2, 2}, 0, {{1, 2, 1, 2} ⇾ a c, {1, 2, 2, 1} ⇾ a d, {2, 1, 1, 2} ⇾ b c, {2, 1, 2, 1} ⇾ b d}]

    'Outer' of multiple lists:
    >> Outer[f, {a, b}, {x, y, z}, {1, 2}]
     = {{{f[a, x, 1], f[a, x, 2]}, {f[a, y, 1], f[a, y, 2]}, {f[a, z, 1], f[a, z, 2]}}, {{f[b, x, 1], f[b, x, 2]}, {f[b, y, 1], f[b, y, 2]}, {f[b, z, 1], f[b, z, 2]}}}

    'Outer' converts input sparse arrays to lists if f=!=Times, or if the input is a mixture of sparse arrays and lists:
    >> Outer[f, SparseArray[{{1, 2} -> a, {2, 1} -> b}], SparseArray[{{1, 2} -> c, {2, 1} -> d}]]
     = {{{{f[0, 0], f[0, c]}, {f[0, d], f[0, 0]}}, {{f[a, 0], f[a, c]}, {f[a, d], f[a, 0]}}}, {{{f[b, 0], f[b, c]}, {f[b, d], f[b, 0]}}, {{f[0, 0], f[0, c]}, {f[0, d], f[0, 0]}}}}

    >> Outer[Times, SparseArray[{{1, 2} -> a, {2, 1} -> b}], {c, d}]
     = {{{0, 0}, {a c, a d}}, {{b c, b d}, {0, 0}}}

    Arrays can be ragged:
    >> Outer[Times, {{1, 2}}, {{a, b}, {c, d, e}}]
     = {{{{a, b}, {c, d, e}}, {{2 a, 2 b}, {2 c, 2 d, 2 e}}}}

    Word combinations:
    >> Outer[StringJoin, {"", "re", "un"}, {"cover", "draw", "wind"}, {"", "ing", "s"}] // InputForm
     = {{{"cover", "covering", "covers"}, {"draw", "drawing", "draws"}, {"wind", "winding", "winds"}}, {{"recover", "recovering", "recovers"}, {"redraw", "redrawing", "redraws"}, {"rewind", "rewinding", "rewinds"}}, {{"uncover", "uncovering", "uncovers"}, {"undraw", "undrawing", "undraws"}, {"unwind", "unwinding", "unwinds"}}}

    Compositions of trigonometric functions:
    >> trigs = Outer[Composition, {Sin, Cos, Tan}, {ArcSin, ArcCos, ArcTan}]
     = {{Composition[Sin, ArcSin], Composition[Sin, ArcCos], Composition[Sin, ArcTan]}, {Composition[Cos, ArcSin], Composition[Cos, ArcCos], Composition[Cos, ArcTan]}, {Composition[Tan, ArcSin], Composition[Tan, ArcCos], Composition[Tan, ArcTan]}}
    Evaluate at 0:
    >> Map[#[0] &, trigs, {2}]
     = {{0, 1, 0}, {1, 0, 1}, {0, ComplexInfinity, 0}}
    """

    summary_text = "generalized outer product"

    def eval(self, f, lists, evaluation: Evaluation):
        "Outer[f_, lists__]"

        return eval_Outer(f, lists, evaluation)
