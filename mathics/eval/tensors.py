import itertools

from sympy.combinatorics import Permutation
from sympy.utilities.iterables import permutations

from mathics.core.atoms import Integer, Integer0, Integer1, String
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
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
    SymbolNormal,
    SymbolRule,
    SymbolSparseArray,
)
from mathics.eval.parts import get_part


def get_default_distance(p):
    if all(q.is_numeric() for q in p):
        return Symbol("SquaredEuclideanDistance")
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
        sub_dim = None
        sub = []
        for element in expr.elements:
            sub = get_dimensions(element, expr.head)
            if sub_dim is None:
                sub_dim = sub
            else:
                if sub_dim != sub:
                    sub = []
                    break
        return [len(expr.elements)] + sub


def eval_Inner(f, list1, list2, g, evaluation: Evaluation):
    "Evaluates recursively the inner product of list1 and list2"

    m = get_dimensions(list1)
    n = get_dimensions(list2)

    if not m or not n:
        evaluation.message("Inner", "normal")
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


def eval_Outer(f, lists, evaluation: Evaluation):
    "Evaluates recursively the outer product of lists"

    # If f=!=Times, or lists contain both SparseArray and List, then convert all SparseArrays to Lists
    lists = lists.get_sequence()
    head = None
    sparse_to_list = f != SymbolTimes
    contain_sparse = False
    contain_list = False
    for _list in lists:
        if _list.head.sameQ(SymbolSparseArray):
            contain_sparse = True
        if _list.head.sameQ(SymbolList):
            contain_list = True
        sparse_to_list = sparse_to_list or (contain_sparse and contain_list)
        if sparse_to_list:
            break
    if sparse_to_list:
        new_lists = []
    for _list in lists:
        if isinstance(_list, Atom):
            evaluation.message("Outer", "normal")
            return
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

    def rec(item, rest_lists, current):
        evaluation.check_stopped()
        if isinstance(item, Atom) or not item.head.sameQ(head):
            if rest_lists:
                return rec(rest_lists[0], rest_lists[1:], current + [item])
            else:
                return Expression(f, *(current + [item]))
        else:
            elements = []
            for element in item.elements:
                elements.append(rec(element, rest_lists, current))
            return Expression(head, *elements)

    def rec_sparse(item, rest_lists, current):
        evaluation.check_stopped()
        if isinstance(item, tuple):  # (rules)
            elements = []
            for element in item:
                elements.extend(rec_sparse(element, rest_lists, current))
            return tuple(elements)
        else:  # rule
            _pos, _val = item.elements
            if rest_lists:
                return rec_sparse(
                    rest_lists[0],
                    rest_lists[1:],
                    (current[0] + _pos.elements, current[1] * _val),
                )
            else:
                return (
                    Expression(
                        SymbolRule,
                        ListExpression(*(current[0] + _pos.elements)),
                        current[1] * _val,
                    ),
                )

    # head != SparseArray
    if not head.sameQ(SymbolSparseArray):
        return rec(lists[0], lists[1:], [])

    # head == SparseArray
    dims = []
    val = Integer1
    data = []  # data = [(rules), ...]
    for _list in lists:
        _dims, _val, _rules = _list.elements[1:]
        dims.extend(_dims)
        val *= _val
        if _val == Integer0:  # _val==0, append (_rules)
            data.append(_rules.elements)
        else:  # _val!=0, append (_rules, other pos->_val)
            other_pos = []
            for pos in itertools.product(*(range(1, d.value + 1) for d in _dims)):
                other_pos.append(ListExpression(*(Integer(i) for i in pos)))
            rules_pos = set(rule.elements[0] for rule in _rules.elements)
            other_pos = set(other_pos) - rules_pos
            other_rules = []
            for pos in other_pos:
                other_rules.append(Expression(SymbolRule, pos, _val))
            data.append(_rules.elements + tuple(other_rules))
    dims = ListExpression(*dims)
    return Expression(
        SymbolSparseArray,
        SymbolAutomatic,
        dims,
        val,
        ListExpression(*rec_sparse(data[0], data[1:], ((), Integer1))),
    )


def eval_LeviCivitaTensor(d, type):
    "Evaluates Levi-Civita tensor of rank d"

    if isinstance(d, Integer) and type == SymbolSparseArray:
        d = d.get_int_value()
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
