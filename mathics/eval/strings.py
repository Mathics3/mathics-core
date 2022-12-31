from mathics.core.atoms import String
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.symbols import Symbol
from mathics.eval.makeboxes import format_element


def eval_ToString(
    expr: BaseElement, form: Symbol, encoding: String, evaluation: Evaluation
) -> String:
    boxes = format_element(expr, evaluation, form, encoding=encoding)
    text = boxes.boxes_to_text(evaluation=evaluation)
    return String(text)
