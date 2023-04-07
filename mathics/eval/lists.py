from mathics.builtin.box.layout import RowBox
from mathics.core.atoms import String
from mathics.core.convert.expression import to_expression
from mathics.core.exceptions import PartDepthError, PartRangeError
from mathics.core.expression import Expression
from mathics.core.symbols import Atom
from mathics.core.systemsymbols import SymbolMakeBoxes, SymbolSequence


def delete_one(expr, pos):
    if isinstance(expr, Atom):
        raise PartDepthError(pos)
    elements = expr.elements
    if pos == 0:
        return Expression(SymbolSequence, *elements)
    s = len(elements)
    truepos = pos
    if truepos < 0:
        truepos = s + truepos
    else:
        truepos = truepos - 1
    if truepos < 0 or truepos >= s:
        raise PartRangeError
    elements = (
        elements[:truepos]
        + (to_expression("System`Sequence"),)
        + elements[truepos + 1 :]
    )
    return to_expression(expr.get_head(), *elements)


def delete_rec(expr, pos):
    if len(pos) == 1:
        return delete_one(expr, pos[0])
    truepos = pos[0]
    if truepos == 0 or isinstance(expr, Atom):
        raise PartDepthError(pos[0])
    elements = expr.elements
    s = len(elements)
    if truepos < 0:
        truepos = truepos + s
        if truepos < 0:
            raise PartRangeError
        newelement = delete_rec(elements[truepos], pos[1:])
        elements = elements[:truepos] + (newelement,) + elements[truepos + 1 :]
    else:
        if truepos > s:
            raise PartRangeError
        newelement = delete_rec(elements[truepos - 1], pos[1:])
        elements = elements[: truepos - 1] + (newelement,) + elements[truepos:]
    return Expression(expr.get_head(), *elements)


def get_tuples(items):
    if not items:
        yield []
    else:
        for item in items[0]:
            for rest in get_tuples(items[1:]):
                yield [item] + rest


def list_boxes(items, f, evaluation, open=None, close=None):
    result = [
        Expression(SymbolMakeBoxes, item, f).evaluate(evaluation) for item in items
    ]
    if f.get_name() in ("System`OutputForm", "System`InputForm"):
        sep = ", "
    else:
        sep = ","
    result = riffle(result, String(sep))
    if len(items) > 1:
        result = RowBox(*result)
    elif items:
        result = result[0]
    if result:
        result = [result]
    else:
        result = []
    if open is not None and close is not None:
        return [String(open)] + result + [String(close)]
    else:
        return result


def riffle(items, sep):
    result = items[:1]
    for item in items[1:]:
        result.append(sep)
        result.append(item)
    return result
