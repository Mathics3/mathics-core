from test.helper import evaluate, session

from mathics.builtin.base import Predefined
from mathics.builtin.box.expression import BoxExpression
from mathics.builtin.graphics import GRAPHICS_OPTIONS
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED, A_READ_PROTECTED
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol

SymbolCustomGraphicsBox = Symbol("CustomGraphicsBox")


class CustomBoxExpression(BoxExpression):
    def __init__(self, evaluation):
        super().__init__(evaluation=evaluation)
        self._elements = [1, 2, 3]

    def boxes_to_text(self, elements=None, **options):
        if not elements:
            elements = self.elements
        return "CustomBoxExpression<<" + self.elements.__str__() + ">>"

    def boxes_to_mathml(self, elements=None, **options):
        if not elements:
            elements = self.elements
        return "CustomBoxExpression<<" + self.elements.__str__() + ">>"

    def boxes_to_tex(self, elements=None, **options):
        if not elements:
            elements = self.elements
        return "CustomBoxExpression<<" + int(self.elements) + ">>"


class CustomAtom(Predefined):
    """
    just a test
    """

    context = "System`"
    rules = {
        "N[System`CustomAtom]": "37",
    }

    def eval_to_boxes(self, evaluation):
        "System`MakeBoxes[System`CustomAtom, StandardForm|TraditionalForm|OutputForm|InputForm]"
        return CustomBoxExpression(evaluation=evaluation)


class CustomGraphicsBox(BoxExpression):
    """"""

    options = GRAPHICS_OPTIONS
    attributes = A_HOLD_ALL | A_PROTECTED | A_READ_PROTECTED

    def init(self, *elems, **options):
        self._elements = elems
        self.evaluation = options.pop("evaluation", None)
        self.box_options = options.copy()

    def to_expression(self):
        return Expression(SymbolCustomGraphicsBox, *self.elements)

    def eval_box(self, expr, evaluation: Evaluation, options: dict):
        """System`MakeBoxes[System`Graphics[System`expr_, System`OptionsPattern[System`Graphics]],
        System`StandardForm|System`TraditionalForm|System`OutputForm]"""
        instance = CustomGraphicsBox(*(expr.elements), evaluation=evaluation)
        return instance

    def boxes_to_text(self, elements=None, **options):
        if elements:
            self._elements = elements
        return (
            "--custom graphics--: I should plot " + self.elements.__str__() + " items"
        )

    def boxes_to_tex(self, elements=None, **options):
        return (
            "--custom graphics--: I should plot " + self.elements.__str__() + " items"
        )

    def boxes_to_mathml(self, elements=None, **options):
        return (
            "--custom graphics--: I should plot " + self.elements.__str__() + " items"
        )

    def boxes_to_svg(self, evaluation):
        return (
            "--custom graphics--: I should plot " + self.elements.__str__() + " items"
        )

    @property
    def elements(self):
        return self._elements


def test_custom_boxconstruct():
    defs = session.evaluation.definitions
    instance_custom_atom = CustomAtom(expression=False)
    instance_custom_atom.contribute(defs, is_pymodule=True)
    evaluate("MakeBoxes[CustomAtom, InputForm]")
    formatted = session.format_result().boxes_to_mathml()
    assert formatted == "CustomBoxExpression<<[1, 2, 3]>>"


def test_custom_graphicsbox_constructor():
    defs = session.evaluation.definitions
    instance_customgb_atom = CustomGraphicsBox(
        expression=False, evaluation=session.evaluation
    )
    instance_customgb_atom.contribute(defs, is_pymodule=True)
    evaluate("MakeBoxes[Graphics[{Circle[{0,0},1]}], OutputForm]")
    formatted = session.format_result().boxes_to_mathml()
    assert (
        formatted
        == "--custom graphics--: I should plot (<Expression: System`Circle[<ListExpression: (<Integer: 0>, <Integer: 0>)>, 1]>,) items"
    )
