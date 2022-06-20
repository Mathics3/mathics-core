# -*- coding: utf-8 -*-

"""
SparseArray Functions
"""


from mathics.algorithm.parts import walk_parts

from mathics.builtin.base import Builtin


from mathics.core.atoms import Integer, Integer0
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, Symbol
from mathics.core.systemsymbols import SymbolAutomatic, SymbolRule, SymbolTable

SymbolSparseArray = Symbol("SparseArray")


class SparseArray(Builtin):
    """
    <dl>
    <dt>'SparseArray[$rules$]'
        <dd>Builds a sparse array acording to the list of $rules$.
    <dt>'SparseArray[$rules$, $dims$]'
        <dd>Builds a sparse array of dimensions $dims$ acording to the $rules$.
    <dt>'SparseArray[$list$]'
        <dd>Builds a sparse representation of $list$.
    </dl>

    >> SparseArray[{{1, 2} -> 1, {2, 1} -> 1}]
     = SparseArray[Automatic, {2, 2}, 0, {{1, 2} -> 1, {2, 1} -> 1}]
    >> SparseArray[{{1, 2} -> 1, {2, 1} -> 1}, {3, 3}]
     = SparseArray[Automatic, {3, 3}, 0, {{1, 2} -> 1, {2, 1} -> 1}]
    >> M=SparseArray[{{0, a}, {b, 0}}]
     = SparseArray[Automatic, {2, 2}, 0, {{1, 2} -> a, {2, 1} -> b}]
    >> M //Normal
     = {{0, a}, {b, 0}}

    """

    messages = {
        "list": "List expected at position 1 in SparseArray[``1``]",
        "rect": "Rectangular array or list of rules is expected at position 1 in SparseArray[``1``]",
        "exdims": "The dimensions cannot be determined from the positions `1`",
    }
    summary_text = "an array by the values of the non-zero elements"

    def list_to_sparse(self, array, evaluation):
        # TODO: Simplify and modularize this method.

        elements = []
        dims = None
        if not array.has_form("List", None):
            return array
        if len(array.elements) == 0:
            return
        # The first element determines the dimensions
        dims = None
        element = array.elements[0]
        if element.has_form("List", None):
            element = self.list_to_sparse(element, evaluation)
            if element is None:
                return None
        if element.has_form("SparseArray", None):
            dims = element.elements[1]
        if dims:
            elements = [element]
            for i, element in enumerate(array.elements):
                if i == 0:
                    continue
                newelement = self.list_to_sparse(element, evaluation)
                if newelement is None:
                    return
                if not newelement.has_form("SparseArray", None):
                    return
                if not dims == newelement.elements[1]:
                    return
                elements.append(newelement)
        else:
            for i, element in enumerate(array.elements):
                if element.has_form("SparseArray", None) or element.has_form(
                    "List", None
                ):
                    return
                if element.is_numeric(evaluation) and element.is_zero:
                    continue
                elements.append(
                    Expression(SymbolRule, ListExpression(Integer(i + 1)), element)
                )

            dims = ListExpression(Integer(len(array.elements)))
            return Expression(
                SymbolSparseArray,
                SymbolAutomatic,
                dims,
                Integer0,
                ListExpression(*elements),
            )
        # Now, reformat the list of sparse arrays as a single sparse array
        dims = ListExpression(Integer(len(array.elements)), *(dims.elements))
        rules = []
        for i, element in enumerate(elements):
            for rule in element.elements[3].elements:
                pat, val = rule.elements
                pat = ListExpression(Integer(i + 1), *(pat.elements))
                rules.append(Expression(SymbolRule, pat, val))
        return Expression(
            SymbolSparseArray,
            SymbolAutomatic,
            dims,
            Integer0,
            ListExpression(*rules),
        )

    def apply_dimensions(self, dims, default, data, evaluation):
        """System`Dimensions[System`SparseArray[System`Automatic, dims_List, default_, data_List]]"""
        return dims

    def apply_normal(self, dims, default, data, evaluation):
        """System`Normal[System`SparseArray[System`Automatic, dims_List, default_, data_List]]"""
        its = [ListExpression(n) for n in dims.elements]
        table = Expression(SymbolTable, default, *its)
        table = table.evaluate(evaluation)
        # Now, apply the rules...
        for item in data.elements:
            pos, val = item.elements
            if pos.has_form("List", None):
                walk_parts([table], pos.elements, evaluation, val)
        return table

    def find_dimensions(self, rules, evaluation):
        dims = None
        for rule in rules:
            pos = rule.elements[0]
            if pos.has_form("List", None):
                if dims is None:
                    dims = [0] * len(pos.elements)
                for i, idx in enumerate(pos.elements):
                    if isinstance(idx, Integer):
                        j = idx.get_int_value()
                        if dims[i] < j:
                            dims[i] = j
        if any(d == 0 for d in dims):
            return
        return ListExpression(*[Integer(d) for d in dims])

    def apply_1(self, rules, evaluation):
        """SparseArray[rules_List]"""
        if not (rules.has_form("List", None) and len(rules.elements) > 0):
            if rules is Symbol("Automatic"):
                return
            print(rules.has_form("List", (1,)))
            evaluation.message("SparseArray", "list", rules)
            return

        if not isinstance(rules.elements[0], Atom) and rules.elements[
            0
        ].get_head_name() in (
            "System`Rule",
            "System`DelayedRule",
        ):
            dims = self.find_dimensions(rules.elements, evaluation)
            if dims is None:
                return
            return self.apply_3(rules, dims, Integer0, evaluation)
        return self.list_to_sparse(rules, evaluation)

    def apply_2(self, rules, dims, evaluation):
        """SparseArray[rules_List, dims_List]"""
        return self.apply_3(rules, dims, Integer0, evaluation)

    def apply_3(self, rules, dims, default, evaluation):
        """SparseArray[rules_List, dims_List, default_]"""
        return Expression(SymbolSparseArray, SymbolAutomatic, dims, default, rules)
