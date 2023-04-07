"""
Cluster Analysis
"""

import heapq

from mathics.algorithm.clusters import (
    AutomaticMergeCriterion,
    AutomaticSplitCriterion,
    LazyDistances,
    PrecomputedDistances,
    agglomerate,
    kmeans,
    optimize,
)
from mathics.builtin.base import Builtin
from mathics.builtin.options import options_to_rules
from mathics.core.atoms import FP_MANTISA_BINARY_DIGITS, Integer, Real, String, min_prec
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, strip_context
from mathics.core.systemsymbols import (
    SymbolClusteringComponents,
    SymbolFailed,
    SymbolFindClusters,
    SymbolRule,
)
from mathics.eval.distance import (
    IllegalDataPoint,
    IllegalDistance,
    dist_repr,
    to_real_distance,
)
from mathics.eval.nevaluator import eval_N
from mathics.eval.parts import walk_levels


class _LazyDistances(LazyDistances):
    # computes single distances only as needed, caches already computed distances.

    def __init__(self, df, p, evaluation):
        super(_LazyDistances, self).__init__()
        self._df = df
        self._p = p
        self._evaluation = evaluation

    def _compute_distance(self, i, j):
        p = self._p
        d = eval_N(self._df(p[i], p[j]), self._evaluation)
        return to_real_distance(d)


class _PrecomputedDistances(PrecomputedDistances):
    # computes all n^2 distances for n points with one big evaluation in the beginning.

    def __init__(self, df, p, evaluation):
        distances_form = [df(p[i], p[j]) for i in range(len(p)) for j in range(i)]
        distances = eval_N(ListExpression(*distances_form), evaluation)
        mpmath_distances = [to_real_distance(d) for d in distances.elements]
        super(_PrecomputedDistances, self).__init__(mpmath_distances)


class _Cluster(Builtin):
    options = {
        "Method": "Optimize",
        "DistanceFunction": "Automatic",
        "RandomSeed": "Automatic",
    }

    messages = {
        "amtd": "`1` failed to pick a suitable distance function for `2`.",
        "bdmtd": 'Method in `` must be either "Optimize", "Agglomerate" or "KMeans".',
        "intpm": "Positive integer expected at position 2 in ``.",
        "list": "Expected a list or a rule with equally sized lists at position 1 in ``.",
        "nclst": "Cannot find more clusters than there are elements: `1` is larger than `2`.",
        "xnum": "The distance function returned ``, which is not a non-negative real value.",
        "rseed": "The random seed specified through `` must be an integer or Automatic.",
        "kmsud": "KMeans only supports SquaredEuclideanDistance as distance measure.",
    }

    _criteria = {
        "Optimize": AutomaticSplitCriterion,
        "Agglomerate": AutomaticMergeCriterion,
        "KMeans": None,
    }

    def _cluster(self, p, k, mode, evaluation, options, expr):
        method_string, method = self.get_option_string(options, "Method", evaluation)
        if method_string not in ("Optimize", "Agglomerate", "KMeans"):
            evaluation.message(
                self.get_name(), "bdmtd", Expression(SymbolRule, "Method", method)
            )
            return

        dist_p, repr_p = dist_repr(p)

        if dist_p is None or len(dist_p) != len(repr_p):
            evaluation.message(self.get_name(), "list", expr)
            return

        if not dist_p:
            return ListExpression()

        if k is not None:  # the number of clusters k is specified as an integer.
            if not isinstance(k, Integer):
                evaluation.message(self.get_name(), "intpm", expr)
                return
            py_k = k.get_int_value()
            if py_k < 1:
                evaluation.message(self.get_name(), "intpm", expr)
                return
            if py_k > len(dist_p):
                evaluation.message(self.get_name(), "nclst", py_k, len(dist_p))
                return
            elif py_k == 1:
                return ListExpression(*repr_p)
            elif py_k == len(dist_p):
                return ListExpression(*[ListExpression(q) for q in repr_p])
        else:  # automatic detection of k. choose a suitable method here.
            if len(dist_p) <= 2:
                return ListExpression(*repr_p)
            constructor = self._criteria.get(method_string)
            py_k = (constructor, {}) if constructor else None

        seed_string, seed = self.get_option_string(options, "RandomSeed", evaluation)
        if seed_string == "Automatic":
            py_seed = 12345
        elif isinstance(seed, Integer):
            py_seed = seed.get_int_value()
        else:
            evaluation.message(
                self.get_name(), "rseed", Expression(SymbolRule, "RandomSeed", seed)
            )
            return

        distance_function_string, distance_function = self.get_option_string(
            options, "DistanceFunction", evaluation
        )
        if distance_function_string == "Automatic":
            from mathics.builtin.tensors import get_default_distance

            distance_function = get_default_distance(dist_p)
            if distance_function is None:
                name_of_builtin = strip_context(self.get_name())
                evaluation.message(
                    self.get_name(),
                    "amtd",
                    name_of_builtin,
                    ListExpression(*dist_p),
                )
                return
        if method_string == "KMeans" and distance_function is not Symbol(
            "SquaredEuclideanDistance"
        ):
            evaluation.message(self.get_name(), "kmsud")
            return

        def df(i, j) -> Expression:
            return Expression(distance_function, i, j)

        try:
            if method_string == "Agglomerate":
                clusters = self._agglomerate(mode, repr_p, dist_p, py_k, df, evaluation)
            elif method_string == "Optimize":
                clusters = optimize(
                    repr_p, py_k, _LazyDistances(df, dist_p, evaluation), mode, py_seed
                )
            elif method_string == "KMeans":
                clusters = self._kmeans(mode, repr_p, dist_p, py_k, py_seed, evaluation)
        except IllegalDistance as e:
            evaluation.message(self.get_name(), "xnum", e.distance)
            return
        except IllegalDataPoint:
            name_of_builtin = strip_context(self.get_name())
            evaluation.message(
                self.get_name(),
                "amtd",
                name_of_builtin,
                ListExpression(*dist_p),
            )
            return

        if mode == "clusters":
            return ListExpression(*[ListExpression(*c) for c in clusters])
        elif mode == "components":
            return to_mathics_list(*clusters)
        else:
            raise ValueError("illegal mode %s" % mode)

    def _agglomerate(self, mode, repr_p, dist_p, py_k, df, evaluation):
        if mode == "clusters":
            clusters = agglomerate(
                repr_p, py_k, _PrecomputedDistances(df, dist_p, evaluation), mode
            )
        elif mode == "components":
            clusters = agglomerate(
                repr_p, py_k, _PrecomputedDistances(df, dist_p, evaluation), mode
            )

        return clusters

    def _kmeans(self, mode, repr_p, dist_p, py_k, py_seed, evaluation):
        items = []

        def convert_scalars(p):
            for q in p:
                if not isinstance(q, (Real, Integer)):
                    raise IllegalDataPoint
                mpq = q.to_mpmath()
                if mpq is None:
                    raise IllegalDataPoint
                items.append(q)
                yield mpq

        def convert_vectors(p):
            d = None
            for q in p:
                if q.get_head_name() != "System`List":
                    raise IllegalDataPoint
                v = list(convert_scalars(q.elements))
                if d is None:
                    d = len(v)
                elif len(v) != d:
                    raise IllegalDataPoint
                yield v

        if dist_p[0].is_numeric(evaluation):
            numeric_p = [[x] for x in convert_scalars(dist_p)]
        else:
            numeric_p = list(convert_vectors(dist_p))

        # compute epsilon similar to Real.__eq__, such that "numbers that differ in their last seven binary digits
        # are considered equal"

        prec = min_prec(*items) or FP_MANTISA_BINARY_DIGITS
        eps = 0.5 ** (prec - 7)

        return kmeans(numeric_p, repr_p, py_k, mode, py_seed, eps)


class ClusteringComponents(_Cluster):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ClusteringComponents.html</url>

    <dl>
      <dt>'ClusteringComponents[$list$]'
      <dd>forms clusters from $list$ and returns a list of cluster indices, in which each
        element shows the index of the cluster in which the corresponding element in $list$
        ended up.
      <dt>'ClusteringComponents[$list$, $k$]'
      <dd>forms $k$ clusters from $list$ and returns a list of cluster indices, in which
        each element shows the index of the cluster in which the corresponding element in
        $list$ ended up.
    </dl>

    For more detailed documentation regarding options and behavior, see FindClusters[].

    >> ClusteringComponents[{1, 2, 3, 1, 2, 10, 100}]
     = {1, 1, 1, 1, 1, 1, 2}

    >> ClusteringComponents[{10, 100, 20}, Method -> "KMeans"]
     = {1, 0, 1}
    """

    summary_text = "label data with the index of the cluster it is in"

    def eval(self, p, evaluation: Evaluation, options: dict):
        "ClusteringComponents[p_, OptionsPattern[%(name)s]]"
        return self._cluster(
            p,
            None,
            "components",
            evaluation,
            options,
            Expression(SymbolClusteringComponents, p, *options_to_rules(options)),
        )

    def eval_manual_k(self, p, k: Integer, evaluation: Evaluation, options: dict):
        "ClusteringComponents[p_, k_Integer, OptionsPattern[%(name)s]]"
        return self._cluster(
            p,
            k,
            "components",
            evaluation,
            options,
            Expression(SymbolClusteringComponents, p, k, *options_to_rules(options)),
        )


class FindClusters(_Cluster):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/FindClusters.html</url>

    <dl>
      <dt>'FindClusters[$list$]'
      <dd>returns a list of clusters formed from the elements of $list$. The number of cluster is determined
        automatically.
      <dt>'FindClusters[$list$, $k$]'
      <dd>returns a list of $k$ clusters formed from the elements of $list$.
    </dl>

    >> FindClusters[{1, 2, 20, 10, 11, 40, 19, 42}]
     = {{1, 2, 20, 10, 11, 19}, {40, 42}}

    >> FindClusters[{25, 100, 17, 20}]
     = {{25, 17, 20}, {100}}

    >> FindClusters[{3, 6, 1, 100, 20, 5, 25, 17, -10, 2}]
     = {{3, 6, 1, 5, -10, 2}, {100}, {20, 25, 17}}

    >> FindClusters[{1, 2, 10, 11, 20, 21}]
     = {{1, 2}, {10, 11}, {20, 21}}

    >> FindClusters[{1, 2, 10, 11, 20, 21}, 2]
     = {{1, 2, 10, 11}, {20, 21}}

    >> FindClusters[{1 -> a, 2 -> b, 10 -> c}]
     = {{a, b}, {c}}

    >> FindClusters[{1, 2, 5} -> {a, b, c}]
     = {{a, b}, {c}}

    >> FindClusters[{1, 2, 3, 1, 2, 10, 100}, Method -> "Agglomerate"]
     = {{1, 2, 3, 1, 2, 10}, {100}}

    >> FindClusters[{1, 2, 3, 10, 17, 18}, Method -> "Agglomerate"]
     = {{1, 2, 3}, {10}, {17, 18}}

    >> FindClusters[{{1}, {5, 6}, {7}, {2, 4}}, DistanceFunction -> (Abs[Length[#1] - Length[#2]]&)]
     = {{{1}, {7}}, {{5, 6}, {2, 4}}}

    >> FindClusters[{"meep", "heap", "deep", "weep", "sheep", "leap", "keep"}, 3]
     = {{meep, deep, weep, keep}, {heap, leap}, {sheep}}

    FindClusters' automatic distance function detection supports scalars, numeric tensors, boolean vectors and
    strings.

    The Method option must be either "Agglomerate" or "Optimize". If not specified, it defaults to "Optimize".
    Note that the Agglomerate and Optimize methods usually produce different clusterings.

    The runtime of the Agglomerate method is quadratic in the number of clustered points n, builds the clustering
    from the bottom up, and is exact (no element of randomness). The Optimize method's runtime is linear in n,
    Optimize builds the clustering from top down, and uses random sampling.
    """

    summary_text = "divide data into lists of similar elements"

    def eval(self, p, evaluation: Evaluation, options: dict):
        "FindClusters[p_, OptionsPattern[%(name)s]]"
        return self._cluster(
            p,
            None,
            "clusters",
            evaluation,
            options,
            Expression(SymbolFindClusters, p, *options_to_rules(options)),
        )

    def eval_manual_k(self, p, k: Integer, evaluation: Evaluation, options: dict):
        "FindClusters[p_, k_Integer, OptionsPattern[%(name)s]]"
        return self._cluster(
            p,
            k,
            "clusters",
            evaluation,
            options,
            Expression(SymbolFindClusters, p, k, *options_to_rules(options)),
        )


class Nearest(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Nearest.html</url>

    <dl>
      <dt>'Nearest[$list$, $x$]'
      <dd>returns the one item in $list$ that is nearest to $x$.

      <dt>'Nearest[$list$, $x$, $n$]'
      <dd>returns the $n$ nearest items.

      <dt>'Nearest[$list$, $x$, {$n$, $r$}]'
      <dd>returns up to $n$ nearest items that are not farther from $x$ than $r$.

      <dt>'Nearest[{$p1$ -> $q1$, $p2$ -> $q2$, ...}, $x$]'
      <dd>returns $q1$, $q2$, ... but measures the distances using $p1$, $p2$, ...

      <dt>'Nearest[{$p1$, $p2$, ...} -> {$q1$, $q2$, ...}, $x$]'
      <dd>returns $q1$, $q2$, ... but measures the distances using $p1$, $p2$, ...
    </dl>

    >> Nearest[{5, 2.5, 10, 11, 15, 8.5, 14}, 12]
     = {11}

    Return all items within a distance of 5:

    >> Nearest[{5, 2.5, 10, 11, 15, 8.5, 14}, 12, {All, 5}]
     = {11, 10, 14}

    >> Nearest[{Blue -> "blue", White -> "white", Red -> "red", Green -> "green"}, {Orange, Gray}]
     = {{red}, {white}}

    >> Nearest[{{0, 1}, {1, 2}, {2, 3}} -> {a, b, c}, {1.1, 2}]
     = {b}
    """

    messages = {
        "amtd": "`1` failed to pick a suitable distance function for `2`.",
        "list": "Expected a list or a rule with equally sized lists at position 1 in ``.",
        "nimp": "Method `1` is not implemented yet.",
    }

    options = {
        "DistanceFunction": "Automatic",
        "Method": '"Scan"',
    }

    rules = {
        "Nearest[list_, pattern_]": "Nearest[list, pattern, 1]",
        "Nearest[pattern_][list_]": "Nearest[list, pattern]",
    }
    summary_text = "the nearest element from a list"

    def eval(
        self, items, pivot, limit, expression, evaluation: Evaluation, options: dict
    ):
        "Nearest[items_, pivot_, limit_, OptionsPattern[%(name)s]]"

        method = self.get_option(options, "Method", evaluation)
        if not isinstance(method, String) or method.get_string_value() != "Scan":
            evaluation("Nearest", "nimp", method)
            return

        dist_p, repr_p = dist_repr(items)

        if dist_p is None or len(dist_p) != len(repr_p):
            evaluation.message(self.get_name(), "list", expression)
            return

        if limit.has_form("List", 2):
            up_to = limit.elements[0]
            py_r = limit.elements[1].to_mpmath()
        else:
            up_to = limit
            py_r = None

        if isinstance(up_to, Integer):
            py_n = up_to.get_int_value()
        elif up_to.get_name() == "System`All":
            py_n = None
        else:
            return

        if not dist_p or (py_n is not None and py_n < 1):
            return ListExpression()

        multiple_x = False

        distance_function_string, distance_function = self.get_option_string(
            options, "DistanceFunction", evaluation
        )
        if distance_function_string == "Automatic":
            from mathics.builtin.tensors import get_default_distance

            distance_function = get_default_distance(dist_p)
            if distance_function is None:
                evaluation.message(
                    self.get_name(), "amtd", "Nearest", ListExpression(*dist_p)
                )
                return

            if pivot.get_head_name() == "System`List":
                _, depth_x = walk_levels(pivot)
                _, depth_items = walk_levels(dist_p[0])

                if depth_x > depth_items:
                    multiple_x = True

        def nearest(x) -> ListExpression:
            calls = [Expression(distance_function, x, y) for y in dist_p]
            distances = ListExpression(*calls).evaluate(evaluation)

            if not distances.has_form("List", len(dist_p)):
                raise ValueError()

            py_distances = [
                (to_real_distance(d), i) for i, d in enumerate(distances.elements)
            ]

            if py_r is not None:
                py_distances = [(d, i) for d, i in py_distances if d <= py_r]

            def pick():
                if py_n is None:
                    candidates = sorted(py_distances)
                else:
                    candidates = heapq.nsmallest(py_n, py_distances)

                for d, i in candidates:
                    yield repr_p[i]

            return ListExpression(*list(pick()))

        try:
            if not multiple_x:
                return nearest(pivot)
            else:
                return ListExpression(*[nearest(t) for t in pivot.elements])
        except IllegalDistance:
            return SymbolFailed
        except ValueError:
            return SymbolFailed
