from typing import Optional, Union

from sympy.combinatorics import Permutation
from sympy.tensor.array.expressions import PermuteDims
from sympy.utilities.iterables import permutations

from mathics.core.atoms import Integer, Integer0, Integer1, String
from mathics.core.convert.matrix import to_sympy_array
from mathics.core.convert.python import from_python
from mathics.core.convert.sympy import from_sympy_matrix
from mathics.core.evaluation import Evaluation
from mathics.core.expression import BaseElement, Expression
from mathics.core.list import ListExpression
from mathics.core.number import is_numeric
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolFalse,
    SymbolList,
    SymbolTimes,
    SymbolTrue,
)
from mathics.core.systemsymbols import (
    SymbolAutomatic,
    SymbolDirectedInfinity,
    SymbolInner,
    SymbolNormal,
    SymbolOuter,
    SymbolRule,
    SymbolSparseArray,
    SymbolSquaredEuclideanDistance,
)
from mathics.eval.parts import get_part


def get_default_distance(p):
    if all(is_numeric(q) for q in p):
        return SymbolSquaredEuclideanDistance
    elif all(q.get_head_name() == "System`List" for q in p):
        dimensions = [get_dimensions(q) for q in p]
        if len(dimensions) < 1:
            return None
        d0 = dimensions[0]
        if not all(d == d0 for d in dimensions[1:]):
            return None
        if len(dimensions[0]) == 1:  # vectors?

            def is_boolean(x):
                return x.get_head_name() == "System`Symbol" and x in (
                    SymbolTrue,
                    SymbolFalse,
                )

            if all(all(is_boolean(e) for e in q.elements) for q in p):
                return Symbol("JaccardDissimilarity")
        return Symbol("SquaredEuclideanDistance")
    elif all(isinstance(q, String) for q in p):
        return Symbol("EditDistance")
    else:
        from mathics.builtin.colors.color_directives import expression_to_color

        if all(expression_to_color(q) is not None for q in p):
            return Symbol("ColorDistance")

        return None


def get_dimensions(expr, head=None):
    if isinstance(expr, Atom):
        return []
    else:
        if head is not None and not expr.head.sameQ(head):
            return []
        # The dimensions below this level are those that all elements
        # share: the longest common prefix of their dimensions. For
        # {{a, b}, {{c, d}, {e, f}}} the elements have dimensions {2} and
        # {2, 2}, so the whole has dimensions {2, 2}.
        sub = None
        for element in expr.elements:
            element_dims = get_dimensions(element, expr.head)
            if sub is None:
                sub = element_dims
            else:
                common = 0
                for d1, d2 in zip(sub, element_dims):
                    if d1 != d2:
                        break
                    common += 1
                sub = sub[:common]
            if not sub:
                break
        return [len(expr.elements)] + (sub or [])


def to_std_sparse_array(sparse_array, evaluation: Evaluation):
    "Get a SparseArray equivalent to input with default value 0."

    if sparse_array.elements[2] == Integer0:
        return sparse_array
    else:
        return Expression(
            SymbolSparseArray, Expression(SymbolNormal, sparse_array)
        ).evaluate(evaluation)


def construct_outer(
    lists, current, const_etc: tuple, levels: Optional[list] = None
) -> Union[list, BaseElement]:
    """
    Recursively unpacks lists to construct outer product.
    ------------------------------------

    Unlike direct products, outer (tensor) products require traversing the
    lowest level of each list, hence we recursively unpacking lists until
    the lowest level is reached.

    Parameters:

    ``item``: the current item to be unpacked (if not at lowest level),
    or joined to current (if at lowest level)

    ``rest_lists``: the rest of lists to be unpacked

    ``current``: the current lowest level elements

    ``level``: the current level

    ``levels``: None, or for each list the deepest level at which it is
    taken apart (None: all the way down), as in ``Outer[f, lists, n1, n2, ...]``

    ``const_etc``: a tuple of functions used in unpacking, remains constant
    throughout the recursion.

    Format of ``const_etc``:

    ```
    (
        cond_next_list,  # return True/False to unpack the next list/this list at next level
        get_elements,  # get elements of list, tuple, ListExpression, etc.
        apply_head,  # e.g. lambda elements: Expression(head, *elements)
        apply_f,  # e.g. lambda current: Expression(f, *current)
        join_elem,  # join current lowest level elements (i.e. current) with a new one
        if_flattened,  # True for result as flattened list, False for result as nested list
        evaluation,  # evaluation: Evaluation
    )
    ```

    For those unfamiliar with ``construct_outer``, ``ConstructOuterTest``
    in ``test/eval/test_tensors.py`` provides a detailed introduction and
    several good examples.
    """
    (
        cond_next_list,  # return True when the next list should be unpacked
        get_elements,  # get elements of list, tuple, ListExpression, etc.
        apply_head,  # e.g. lambda elements: Expression(head, *elements)
        apply_f,  # e.g. lambda current: Expression(f, *current)
        join_elem,  # join current lowest level elements (i.e. current) with a new one
        if_flatten,  # True for result as flattened list ({a,b,c,d}), False for result as nested list ({{a,b},{c,d}})
        evaluation,  # evaluation: Evaluation
    ) = const_etc

    _apply_f = (lambda current: (apply_f(current),)) if if_flatten else apply_f

    # Recursive step of unpacking
    def _unpack_outer(
        item, rest_lists, current, level: int
    ) -> Union[list, BaseElement]:
        evaluation.check_stopped()
        max_level = levels[len(lists) - len(rest_lists) - 1] if levels else None
        if (max_level is not None and level > max_level) or cond_next_list(
            item, level
        ):  # unpack next list
            if rest_lists:
                return _unpack_outer(
                    rest_lists[0], rest_lists[1:], join_elem(current, item), 1
                )  # unpacking of a list always start from level 1
            else:
                return _apply_f(join_elem(current, item))
        else:  # unpack this list at next level
            elements = []
            action = elements.extend if if_flatten else elements.append
            # elements.extend flattens the result as list instead of as ListExpression
            for element in get_elements(item):
                action(_unpack_outer(element, rest_lists, current, level + 1))
            return apply_head(elements)

    return _unpack_outer(lists[0], lists[1:], current, 1)


def eval_Inner(f, list1, list2, g, evaluation: Evaluation):
    "Evaluates recursively the inner product of list1 and list2"

    m = get_dimensions(list1)
    n = get_dimensions(list2)

    if not m or not n:
        evaluation.message(
            "Inner", "normal", Integer1, Expression(SymbolInner, list1, list2)
        )
        return
    if list1.get_head() != list2.get_head():
        evaluation.message("Inner", "heads", list1.get_head(), list2.get_head())
        return
    if m[-1] != n[0]:
        evaluation.message("Inner", "incom", m[-1], len(m), list1, n[0], list2)
        return

    head = list1.get_head()
    inner_dim = n[0]

    def rec(i_cur, j_cur, i_rest, j_rest):
        evaluation.check_stopped()
        if i_rest:
            elements = []
            for i in range(1, i_rest[0] + 1):
                elements.append(rec(i_cur + [i], j_cur, i_rest[1:], j_rest))
            return Expression(head, *elements)
        elif j_rest:
            elements = []
            for j in range(1, j_rest[0] + 1):
                elements.append(rec(i_cur, j_cur + [j], i_rest, j_rest[1:]))
            return Expression(head, *elements)
        else:

            def summand(i):
                part1 = get_part(list1, i_cur + [i])
                part2 = get_part(list2, [i] + j_cur)
                return Expression(f, part1, part2)

            part = Expression(g, *[summand(i) for i in range(1, inner_dim + 1)])
            # cur_expr.elements.append(part)
            return part

    return rec([], [], m[:-1], n[1:])


OUTER_INFINITY = Expression(SymbolDirectedInfinity, Integer1)


def outer_levels(args: tuple) -> tuple:
    """
    The levels given after the lists in Outer[f, list1, ..., n1, n2, ...]:
    a positive integer, or Infinity (None here), each.

    Returns (levels, None), or (None, i) when args[i] is not a level.
    """
    levels = []
    for i, arg in enumerate(args):
        if isinstance(arg, Integer) and arg.value > 0:
            levels.append(arg.value)
        elif arg.sameQ(OUTER_INFINITY):
            levels.append(None)
        else:
            return None, i
    return levels, None


def eval_Outer(f, lists, evaluation: Evaluation):
    "Evaluates recursively the outer product of lists"

    args = lists.get_sequence()
    # Outer[f, list1, list2, ..., n1, n2, ...]: everything from the first
    # atom (or Infinity) on gives the levels at which each list is taken apart.
    nlists = next(
        (
            i
            for i, arg in enumerate(args)
            if isinstance(arg, Atom) or arg.sameQ(OUTER_INFINITY)
        ),
        len(args),
    )
    if nlists == 0:
        evaluation.message(
            "Outer", "normal", Integer(2), Expression(SymbolOuter, f, *args)
        )
        return
    lists = args[:nlists]
    levels, bad = outer_levels(args[nlists:])
    if levels is None:
        evaluation.message(
            "Outer",
            "ipnfm",
            Integer(nlists + bad + 2),
            Expression(SymbolOuter, f, *args),
        )
        return
    # A single level applies to every list; with several, a list without
    # one is taken apart completely.
    if len(levels) == 1:
        levels = levels * nlists
    levels = (levels + [None] * nlists)[:nlists]
    if all(level is None for level in levels):
        levels = None

    # If f=!=Times, or lists contain both SparseArray and List, or levels
    # are given, then convert all SparseArrays to Lists
    head = None
    sparse_to_list = f != SymbolTimes or levels is not None
    contain_sparse = False
    contain_list = False
    new_lists = []
    for _list in lists:
        if _list.head.sameQ(SymbolSparseArray):
            contain_sparse = True
        if _list.head.sameQ(SymbolList):
            contain_list = True
        sparse_to_list = sparse_to_list or (contain_sparse and contain_list)
        if sparse_to_list:
            break
    for _list in lists:
        if sparse_to_list:
            if _list.head.sameQ(SymbolSparseArray):
                _list = Expression(SymbolNormal, _list).evaluate(evaluation)
            new_lists.append(_list)
        if head is None:
            head = _list.head
        elif not _list.head.sameQ(head):
            evaluation.message("Outer", "heads", head, _list.head)
            return

    if sparse_to_list:
        lists = new_lists

    # head != SparseArray
    if not head.sameQ(SymbolSparseArray):

        def cond_next_list(item, level) -> bool:
            return isinstance(item, Atom) or not item.head.sameQ(head)

        etc = (
            cond_next_list,
            (lambda item: item.elements),  # get_elements
            (lambda elements: Expression(head, *elements)),  # apply_head
            (lambda current: Expression(f, *current)),  # apply_f
            (lambda current, item: current + (item,)),  # join_elem
            False,  # if_flatten
            evaluation,
        )
        return construct_outer(lists, (), etc, levels)

    # head == SparseArray
    dims = []
    val = Integer1
    for _list in lists:
        _dims, _val = _list.elements[1:3]
        dims.extend(_dims)
        val *= _val
    dims = ListExpression(*dims)

    def sparse_cond_next_list(item, level) -> bool:
        return isinstance(item, Atom) or not item.head.sameQ(head)

    def sparse_apply_Rule(current) -> Expression:
        return Expression(SymbolRule, ListExpression(*current[0]), current[1])

    def sparse_join_elem(current, item) -> tuple:
        return (current[0] + item.elements[0].elements, current[1] * item.elements[1])

    etc = (
        sparse_cond_next_list,
        (lambda item: to_std_sparse_array(item, evaluation).elements[3].elements),
        (lambda elements: elements),  # apply_head
        sparse_apply_Rule,  # apply_f
        sparse_join_elem,  # join_elem
        True,  # if_flatten
        evaluation,
    )
    return Expression(
        SymbolSparseArray,
        SymbolAutomatic,
        dims,
        val,
        ListExpression(*construct_outer(lists, ((), Integer1), etc)),
    )


def eval_LeviCivitaTensor(d, type):
    "Evaluates Levi-Civita tensor of rank d"

    if isinstance(d, Integer) and type == SymbolSparseArray:
        d = d.int_value
        perms = list(permutations(list(range(1, d + 1))))
        rules = [
            Expression(
                SymbolRule,
                from_python(p),
                from_python(Permutation.from_sequence(p).signature()),
            )
            for p in perms
        ]
        return Expression(SymbolSparseArray, from_python(rules), from_python([d] * d))


def eval_Transpose(m, dimensions: int) -> Optional[Expression]:
    """Transpose a two- or three-dimensional matrix"""

    if dimensions == 3:
        sympy_m = to_sympy_array(m)
        # The below seems to be the default permuatation WMA uses
        # for 3D matrices.
        p = PermuteDims(sympy_m, (1, 0, 2))
        return from_sympy_matrix(p.as_explicit())

    assert dimensions == 2, "eval_Transpose only applies to 2- and 3-dimensional array."
    # Rearrange the elements directly. Going through a SymPy matrix
    # would turn a result with a single column, such as the transpose
    # of {{1, 2, 3}}, into a vector.
    rows = [row.elements for row in m.elements]
    return ListExpression(*(ListExpression(*column) for column in zip(*rows)))
