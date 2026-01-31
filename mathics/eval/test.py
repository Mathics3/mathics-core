# -*- coding: utf-8 -*-
"""
This module contains basic low-level functions that implement
test evaluations over ``Expression``s.
"""


from mathics.core.pattern import StopGenerator
from mathics.core.symbols import Atom


class _StopGeneratorBaseElementIsFree(StopGenerator):
    pass


def item_is_free(item, form, evaluation):
    # for vars, rest in form.match(self, {}, evaluation, fully=False):
    def yield_match(vars, rest):
        raise _StopGeneratorBaseElementIsFree(False)
        # return False

    try:
        form.match(
            item,
            pattern_context={
                "yield_func": yield_match,
                "vars_dict": {},
                "evaluation": evaluation,
                "fully": False,
            },
        )
    except _StopGeneratorBaseElementIsFree as exc:
        return exc.value

    if isinstance(item, Atom):
        return True
    else:
        return item_is_free(item.head, form, evaluation) and all(
            item_is_free(element, form, evaluation) for element in item.elements
        )
