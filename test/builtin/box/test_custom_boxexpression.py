from test.helper import session

from mathics.builtin.box.expression import BoxExpression
from mathics.builtin.graphics import GRAPHICS_OPTIONS
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Predefined
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.rules import BaseRule, FunctionApplyRule, Rule
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
        return "CustomBoxExpression<<" + str(int(self.elements)) + ">>"


class CustomAtom(Predefined):
    """
    just a test
    """

    context = "System`"
    rules = {
        "N[System`CustomAtom]": "37",
    }

    # Since this is a Mathics3 Module which is loaded after
    # the core symbols are loaded, it is safe to assume that `MakeBoxes`
    # definition was already loaded. We can add then rules to it.
    # This modified `contribute` method do that, adding specific
    # makeboxes rules for this kind of atoms.
    def contribute(self, definitions, is_pymodule=True):
        super().contribute(definitions, is_pymodule)
        # Add specific MakeBoxes rules
        name = self.get_name()

        for pattern, function in self.get_functions("makeboxes_"):
            mb_rule = FunctionApplyRule(
                name, pattern, function, None, attributes=None, system=True
            )
            definitions.add_format("System`MakeBoxes", mb_rule, "_MakeBoxes")

    def makeboxes_general(self, evaluation):
        "System`MakeBoxes[System`CustomAtom, StandardForm|TraditionalForm]"
        return CustomBoxExpression(evaluation=evaluation)

    def makeboxes_inputform(self, evaluation):
        "System`MakeBoxes[InputForm[System`CustomAtom], StandardForm|TraditionalForm]"
        return CustomBoxExpression(evaluation=evaluation)


class CustomGraphicsBox(BoxExpression):
    """"""

    options = GRAPHICS_OPTIONS
    attributes = A_HOLD_ALL | A_PROTECTED | A_READ_PROTECTED

    # Since this is a Mathics3 Module which is loaded after
    # the core symbols are loaded, it is safe to assume that `MakeBoxes`
    # definition was already loaded. We can add then rules to it.
    # This modified `contribute` method do that, adding specific
    # makeboxes rules for this kind of BoxExpression.
    def contribute(self, definitions, is_pymodule=True):
        super().contribute(definitions, is_pymodule)
        # Add specific MakeBoxes rules
        name = self.get_name()

        for pattern, function in self.get_functions("makeboxes_"):
            mb_rule = FunctionApplyRule(
                name, pattern, function, None, attributes=None, system=True
            )
            definitions.add_format("System`MakeBoxes", mb_rule, "_MakeBoxes")

    def init(self, *elems, **options):
        self._elements = elems
        self.evaluation = options.pop("evaluation", None)
        self.box_options = options.copy()

    def to_expression(self):
        return Expression(SymbolCustomGraphicsBox, *self.elements)

    def makeboxes_graphics(self, expr, evaluation: Evaluation, options: dict):
        """System`MakeBoxes[System`Graphics[System`expr_, System`OptionsPattern[System`Graphics]],
        System`StandardForm|System`TraditionalForm]"""
        instance = CustomGraphicsBox(*(expr.elements), evaluation=evaluation)
        return instance

    def makeboxes_outputForm(self, expr, evaluation: Evaluation, options: dict):
        """System`MakeBoxes[System`OutputForm[System`Graphics[System`expr_, System`OptionsPattern[System`Graphics]]],
        System`StandardForm|System`TraditionalForm]"""
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
    formatted = session.evaluate("MakeBoxes[InputForm[CustomAtom]]").boxes_to_mathml()
    assert formatted == "CustomBoxExpression<<[1, 2, 3]>>"


def test_custom_graphicsbox_constructor():
    defs = session.evaluation.definitions
    instance_customgb_atom = CustomGraphicsBox(
        expression=False, evaluation=session.evaluation
    )
    instance_customgb_atom.contribute(defs, is_pymodule=True)
    result = session.evaluate("MakeBoxes[OutputForm[Graphics[{Circle[{0,0},1]}]]]")
    formatted = result.boxes_to_mathml()
    assert (
        formatted
        == "--custom graphics--: I should plot (<Expression: <Symbol: System`Circle>[<ListExpression: (<Integer: 0>, <Integer: 0>)>, <Integer: 1>]>,) items"
    )
