# -*- coding: utf-8 -*-
"""
Unit tests for mathics.eval.tensors
"""
import unittest

from mathics.core.atoms import Integer
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, Symbol, SymbolList, SymbolPlus, SymbolTimes
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
            # get elements from Expression, for iteratable objects (tuple, list, etc.) it's just identity
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
            Symbol("System`Tuples"), ListExpression(list4, list5, list6)
        ).evaluate(evaluation)

        def cond_next_list(item, level) -> bool:
            return isinstance(item, Atom) or not item.head.sameQ(SymbolList)

        etc_4 = (
            cond_next_list,
            (lambda item: item.elements),
            (lambda elements: elements),  # apply_head
            (lambda current: ListExpression(*current)),  # apply_f
            (lambda current, item: current + (item,)),
            True,
            evaluation,
        )

        assert (
            ListExpression(*construct_outer([list4, list5, list6], (), etc_4))
            == expected_result_3
        )


if __name__ == "__main__":
    unittest.main()
