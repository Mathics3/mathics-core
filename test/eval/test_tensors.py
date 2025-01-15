# -*- coding: utf-8 -*-
"""
Unit tests for mathics.eval.tensors
"""
import unittest

from mathics.core.atoms import Integer
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.expression import BaseElement, Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, Symbol, SymbolList
from mathics.eval.scoping import dynamic_scoping
from mathics.eval.tensors import construct_outer

definitions = Definitions(add_builtin=True)
evaluation = Evaluation(definitions, catch_interrupt=False)


class ConstructOuterTest(unittest.TestCase):
    """
    Test construct_outer, and introduce some of its potential applications.
    """

    def testCartesianProduct(self):
        """
        Cartesian Product (Tuples) can be implemented by construct_outer.
        """
        list1 = [1, 2, 3]
        list2 = [4, 5]
        list3 = [6, 7, 8]

        expected_result_1 = [
            [[(1, 4, 6), (1, 4, 7), (1, 4, 8)], [(1, 5, 6), (1, 5, 7), (1, 5, 8)]],
            [[(2, 4, 6), (2, 4, 7), (2, 4, 8)], [(2, 5, 6), (2, 5, 7), (2, 5, 8)]],
            [[(3, 4, 6), (3, 4, 7), (3, 4, 8)], [(3, 5, 6), (3, 5, 7), (3, 5, 8)]],
        ]  # Cartesian Product list1 × list2 × list3, nested

        etc_1 = (
            (lambda item, level: level > 1),
            # True to unpack the next list, False to unpack the current list at the next level
            (lambda item: item),
            # get elements from Expression, for iterable objects (tuple, list, etc.) it's just identity
            list,
            # apply_head: each level of result would be in form of apply_head(...)
            tuple,
            # apply_f: lowest level of result would be apply_f(joined lowest level elements of each list)
            (lambda current, item: current + [item]),
            # join current lowest level elements (i.e. current) with a new one, in most cases it's just "Append"
            False,
            # True for result as flattened list like {a,b,c,d}, False for result as nested list like {{a,b},{c,d}}
            evaluation,  # evaluation
        )

        etc_2 = (
            (lambda item, level: not isinstance(item, list)),
            # list1~list3 all have depth 1, so level > 1 equals to not isinstance(item, list)
            (lambda item: item),
            (lambda elements: elements),
            # internal level structure used in construct_outer is exactly list, so list equals to identity
            (lambda current: current),
            # now join_elem is in form of tuple, so we no longer need to convert it to tuple
            (lambda current, item: current + (item,)),
            False,
            evaluation,
        )

        # Here initial current is empty, but in some cases we expect non-empty ones like ((), Integer1)
        assert construct_outer([list1, list2, list3], [], etc_1) == expected_result_1
        assert construct_outer([list1, list2, list3], (), etc_2) == expected_result_1

        # Now let's try something different

        expected_result_2 = (
            [2, 5, 7],
            [2, 5, 8],
            [2, 5, 9],
            [2, 6, 7],
            [2, 6, 8],
            [2, 6, 9],
            [3, 5, 7],
            [3, 5, 8],
            [3, 5, 9],
            [3, 6, 7],
            [3, 6, 8],
            [3, 6, 9],
            [4, 5, 7],
            [4, 5, 8],
            [4, 5, 9],
            [4, 6, 7],
            [4, 6, 8],
            [4, 6, 9],
        )  # add 1 to each element of Tuples[{list1, list2, list3}], flattened.

        etc_3 = (
            (lambda item, level: level > 1),
            (lambda item: item),
            tuple,  # use tuple instead of list
            list,  # use list instead of tuple
            (lambda current, item: current + [item + 1]),  # add 1 to each element
            True,
            evaluation,
        )

        assert construct_outer([list1, list2, list3], [], etc_3) == expected_result_2

        # M-Expression

        list4 = ListExpression(Integer(1), Integer(2), Integer(3))
        list5 = ListExpression(Integer(4), Integer(5))
        list6 = ListExpression(Integer(6), Integer(7), Integer(8))

        expected_result_3 = Expression(
            Symbol("System`Outer"), SymbolList, list4, list5, list6
        ).evaluate(evaluation)

        expected_result_4 = Expression(
            Symbol("System`Tuples"), ListExpression(list4, list5, list6)
        ).evaluate(evaluation)

        def cond_next_list(item, level) -> bool:
            return isinstance(item, Atom) or not item.head.sameQ(SymbolList)

        etc_4 = (
            cond_next_list,  # equals to (lambda item, level: level > 1)
            (lambda item: item.elements),
            (lambda elements: ListExpression(*elements)),  # apply_head
            (lambda current: ListExpression(*current)),  # apply_f
            (lambda current, item: current + (item,)),
            False,
            evaluation,
        )

        etc_5 = (
            cond_next_list,
            (lambda item: item.elements),
            (lambda elements: elements),  # apply_head
            (lambda current: ListExpression(*current)),  # apply_f
            (lambda current, item: current + (item,)),
            True,
            evaluation,
        )

        assert construct_outer([list4, list5, list6], (), etc_4) == expected_result_3
        assert (
            ListExpression(*construct_outer([list4, list5, list6], (), etc_5))
            == expected_result_4
        )

    def testTable(self):
        """
        Table can be implemented by construct_outer.
        """
        iter1 = [2]  # {i, 2}
        iter2 = [3, 4]  # {j, 3, 4}
        iter3 = [5, 1, -2]  # {k, 5, 1, -2}

        list1 = [1, 2]  # {i, {1, 2}}
        list2 = [3, 4]  # {j, {3, 4}}
        list3 = [5, 3, 1]  # {k, {5, 3, 1}}

        def get_range_1(_iter: list) -> range:
            if len(_iter) == 1:
                return range(1, _iter[0] + 1)
            elif len(_iter) == 2:
                return range(_iter[0], _iter[1] + 1)
            elif len(_iter) == 3:
                pm = 1 if _iter[2] >= 0 else -1
                return range(_iter[0], _iter[1] + pm, _iter[2])
            else:
                raise ValueError("Invalid iterator")

        expected_result_1 = [
            [[18, 2, -6], [11, -5, -13]],
            [[20, 4, -4], [13, -3, -11]],
        ]  # Table[2*i - j^2 + k^2, {i, 2}, {j, 3, 4}, {k, 5, 1, -2}]
        # Table[2*i - j^2 + k^2, {{i, {1, 2}}, {j, {3, 4}}, {k, {5, 3, 1}}]

        etc_1 = (
            (lambda item, level: level > 1),  # range always has depth 1
            get_range_1,
            (lambda elements: elements),
            (lambda current: 2 * current[0] - current[1] ** 2 + current[2] ** 2),
            (lambda current, item: current + (item,)),
            False,
            evaluation,
        )

        etc_2 = (
            (lambda item, level: level > 1),
            (lambda item: item),
            (lambda elements: elements),
            (lambda current: 2 * current[0] - current[1] ** 2 + current[2] ** 2),
            (lambda current, item: current + (item,)),
            False,
            evaluation,
        )

        assert construct_outer([iter1, iter2, iter3], (), etc_1) == expected_result_1
        assert construct_outer([list1, list2, list3], (), etc_2) == expected_result_1

        # Flattened result

        etc_3 = (
            (lambda item, level: level > 1),
            (lambda item: item),
            (lambda elements: elements),
            (lambda current: 2 * current[0] - current[1] ** 2 + current[2] ** 2),
            (lambda current, item: current + (item,)),
            True,
            evaluation,
        )

        expected_result_2 = [18, 2, -6, 11, -5, -13, 20, 4, -4, 13, -3, -11]

        assert construct_outer([list1, list2, list3], (), etc_3) == expected_result_2

        # M-Expression

        iter4 = ListExpression(Symbol("i"), Integer(2))
        iter5 = ListExpression(Symbol("j"), Integer(3), Integer(4))
        iter6 = ListExpression(Symbol("k"), Integer(5), Integer(1), Integer(-2))

        list4 = ListExpression(Symbol("i"), ListExpression(Integer(1), Integer(2)))
        list5 = ListExpression(Symbol("j"), ListExpression(Integer(3), Integer(4)))
        list6 = ListExpression(
            Symbol("k"), ListExpression(Integer(5), Integer(3), Integer(1))
        )

        expr_to_evaluate = (
            Integer(2) * Symbol("i")
            - Symbol("j") ** Integer(2)
            + Symbol("k") ** Integer(2)
        )  # 2*i - j^2 + k^2

        expected_result_3 = Expression(
            Symbol("System`Table"),
            expr_to_evaluate,
            iter4,
            iter5,
            iter6,
        ).evaluate(evaluation)
        # Table[2*i - j^2 + k^2, {i, 2}, {j, 3, 4}, {k, 5, 1, -2}]

        def get_range_2(_iter: BaseElement) -> BaseElement:
            if isinstance(_iter.elements[1], Atom):  # {i, 2}, etc.
                _list = (
                    Expression(Symbol("System`Range"), *_iter.elements[1:])
                    .evaluate(evaluation)
                    .elements
                )
            else:  # {i, {1, 2}}, etc.
                _list = _iter.elements[1].elements
            return ({_iter.elements[0].name: item} for item in _list)

        def evaluate_current(current: dict) -> BaseElement:
            return dynamic_scoping(expr_to_evaluate.evaluate, current, evaluation)

        etc_4 = (
            (lambda item, level: level > 1),
            get_range_2,
            (lambda elements: ListExpression(*elements)),  # apply_head
            evaluate_current,
            (lambda current, item: {**current, **item}),
            False,
            evaluation,
        )

        assert construct_outer([iter4, iter5, iter6], {}, etc_4) == expected_result_3
        assert construct_outer([list4, list5, list6], {}, etc_4) == expected_result_3

    def testTensorProduct(self):
        """
        Tensor Product can be implemented by construct_outer.
        """
        list1 = [[4, 5], [8, 10], [12, 15]]
        list2 = [6, 7, 8]

        expected_result_1 = [
            [[24, 28, 32], [30, 35, 40]],
            [[48, 56, 64], [60, 70, 80]],
            [[72, 84, 96], [90, 105, 120]],
        ]

        def product_of_list(_list):
            result = 1
            for item in _list:
                result *= item
            return result

        etc_1 = (
            (lambda item, level: not isinstance(item, list)),
            (lambda item: item),
            (lambda elements: elements),
            product_of_list,
            (lambda current, item: current + (item,)),
            False,
            evaluation,
        )

        etc_2 = (
            (lambda item, level: not isinstance(item, list)),
            (lambda item: item),
            (lambda elements: elements),
            (lambda current: current),
            (lambda current, item: current * item),
            False,
            evaluation,
        )

        assert construct_outer([list1, list2], (), etc_1) == expected_result_1
        assert construct_outer([list1, list2], 1, etc_2) == expected_result_1

        # M-Expression

        list3 = ListExpression(
            ListExpression(Integer(4), Integer(5)),
            ListExpression(Integer(8), Integer(10)),
            ListExpression(Integer(12), Integer(15)),
        )
        list4 = ListExpression(Integer(6), Integer(7), Integer(8))

        expected_result_2 = Expression(
            Symbol("System`Outer"), Symbol("System`Times"), list3, list4
        ).evaluate(evaluation)

        def cond_next_list(item, level) -> bool:
            return isinstance(item, Atom) or not item.head.sameQ(SymbolList)

        etc_3 = (
            cond_next_list,
            (lambda item: item.elements),
            (lambda elements: ListExpression(*elements)),
            (lambda current: Expression(Symbol("System`Times"), *current)),
            (lambda current, item: current + (item,)),
            False,
            evaluation,
        )

        etc_4 = (
            cond_next_list,
            (lambda item: item.elements),
            (lambda elements: ListExpression(*elements)),
            (lambda current: current),
            (lambda current, item: current * item),
            False,
            evaluation,
        )

        assert (
            construct_outer([list3, list4], (), etc_3).evaluate(evaluation)
            == expected_result_2
        )
        assert (
            construct_outer([list3, list4], Integer(1), etc_4).evaluate(evaluation)
            == expected_result_2
        )

    def testOthers(self):
        """
        construct_outer can be used in other cases.
        """
        list1 = [[4, 5], [8, [10, 12]], 15]  # ragged
        list2 = [6, 7, 8]
        list3 = []  # empty

        expected_result_1 = [
            [[24, 28, 32], [30, 35, 40]],
            [[48, 56, 64], [[60, 70, 80], [72, 84, 96]]],
            [90, 105, 120],
        ]

        expected_result_2 = [
            [[(4, 6), (4, 7), (4, 8)], [(5, 6), (5, 7), (5, 8)]],
            [[(8, 6), (8, 7), (8, 8)], [([10, 12], 6), ([10, 12], 7), ([10, 12], 8)]],
            [(15, 6), (15, 7), (15, 8)],
        ]

        expected_result_3 = [
            [[[], [], []], [[], [], []]],
            [[[], [], []], [[], [], []]],
            [[], [], []],
        ]

        etc_1 = (
            (lambda item, level: not isinstance(item, list)),
            (lambda item: item),
            (lambda elements: elements),
            (lambda current: current),
            (lambda current, item: current * item),
            False,
            evaluation,
        )

        etc_2 = (
            (lambda item, level: not isinstance(item, list) or level > 2),
            (lambda item: item),
            (lambda elements: elements),
            (lambda current: current),
            (lambda current, item: current + (item,)),
            False,
            evaluation,
        )

        assert construct_outer([list1, list2], 1, etc_1) == expected_result_1
        assert construct_outer([list1, list2], (), etc_2) == expected_result_2
        assert construct_outer([list1, list2, list3], (), etc_2) == expected_result_3
        assert construct_outer([list3, list1, list2], (), etc_2) == []


if __name__ == "__main__":
    unittest.main()
