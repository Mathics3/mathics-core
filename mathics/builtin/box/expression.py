from typing import Optional, Sequence, Union

from mathics.core.attributes import A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import BuiltinElement
from mathics.core.element import BoxElementMixin
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolHoldForm, ensure_context

# This is never intended to go in Mathics3 docs
no_doc = True


def split_name(name: str) -> str:
    """
    insert spaces in front of upper case letters
    and numbers. For instance,
    ``split_name("BezierCurve3D")`` results in
    ``"bezier curve 3D"``

    """
    if name == "":
        return ""
    result = name[0]
    for i in range(1, len(name)):
        if name[i].isupper():
            if not name[i - 1].isdigit():
                result = result + " "
        elif name[i].isdigit():
            if not name[i - 1].isdigit():
                result = result + " "
        result = result + name[i]
    return result.lower()


# TODO: Review this
class BoxExpression(BuiltinElement, BoxElementMixin):
    """
    This is the base class for Boxed (compound) Expressions.

    Boxing of a BoxExpression generally does not need a general M-Expression kind
    of evaluation, although it can happen.

    For example:
       InputForm[ToBoxes[a+b]]

    should be evaluated to ``Expression(SymbolRowBox, '"a"', '"+"', '"b"')``.
    """

    attributes = A_PROTECTED | A_READ_PROTECTED

    def __new__(cls, *elements, **kwargs):
        instance = super().__new__(cls, *elements, **kwargs)
        # This should not be here.
        article = (
            "an "
            if instance.get_name()[0].lower() in ("a", "e", "i", "o", "u")
            else "a "
        )

        instance.summary_text = (
            "box representation for "
            + article
            + split_name(cls.get_name(short=True)[:-3])
        )
        if not instance.__doc__:
            instance.__doc__ = rf"""
            <dl>
              <dt>'{instance.get_name()}'
              <dd> box structure.
            </dl>
            """

        # the __new__ method from BuiltinElement
        # calls self.init. It is expected that it set
        # self._elements. However, if it didn't happen,
        # we set it with a default value.
        # There should be a better way to implement this
        # behaviour...
        if not hasattr(instance, "_elements"):
            instance._elements = None
        return instance

    def do_format(self, evaluation, format):
        return self

    @property
    def elements(self):
        if self._elements is None:
            self._elements = tuple()
        return self._elements

    @elements.setter
    def elements(self, value):
        self._elements = value
        return self._elements

    def format(self, evaluation, fmt):
        expr = Expression(SymbolHoldForm, self.to_expression())
        fexpr = expr.format(evaluation, fmt)
        return fexpr

    # Deprecated: remove eventually
    def get_elements(self):
        return self._elements

    def get_head(self):
        return Symbol(self.get_name())

    def get_head_name(self):
        return self.get_name()

    def get_lookup_name(self):
        return self.get_name()

    @property
    def element_order(self) -> tuple:
        """Return a tuple value that is used in ordering elements of
        an expression. The tuple is ultimately compared
        lexicographically.

        """
        return self.to_expression().element_order

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        return self.to_expression().pattern_precedence

    def get_string_value(self):
        return "-@" + self.get_head_name() + "@-"

    @property
    def head(self):
        return self.get_head()

    @head.setter
    def head(self, value):
        raise ValueError("BoxExpression.head is write protected.")

    def has_form(
        self, heads: Union[Sequence[str], str], *element_counts: Optional[int]
    ) -> bool:
        """
        element_counts:
            (,):        no elements allowed
            (None,):    no constraint on number of elements
            (n, None):  element count >= n
            (n1, n2, ...):    element count in {n1, n2, ...}
        """

        head_name = self.get_name()

        if isinstance(heads, (tuple, list, set)):
            if head_name not in [ensure_context(h) for h in heads]:
                return False
        elif isinstance(heads, str):
            if head_name != ensure_context(heads):
                return False
        else:
            raise TypeError(
                f"Heads must be a string or a sequence of strings, not {type(heads)}"
            )
        if not element_counts:
            return False
        if element_counts and element_counts[0] is not None:
            count = len(self.elements)
            if count not in element_counts:
                if (
                    len(element_counts) == 2
                    and element_counts[1] is None  # noqa
                    and count >= element_counts[0]
                ):
                    return True
                else:
                    return False
        return True

    @property
    def is_literal(self) -> bool:
        """
        True if the value can't change, i.e. a value is set and it does not
        depend on definition bindings. That is why, in contrast to
        `is_uncertain_final_definitions()` we don't need a `definitions`
        parameter.
        """
        return False

    def replace_vars(self, vars, options=None, in_scoping=True, in_function=True):
        expr = self.to_expression()
        result = expr.replace_vars(vars, options, in_scoping, in_function)
        return result

    def sameQ(self, expr) -> bool:
        """Mathics SameQ"""
        return expr.sameQ(self.to_expression())

    def tex_block(self, tex, only_subsup=False):
        if len(tex) == 1:
            return tex
        else:
            if not only_subsup or "_" in tex or "^" in tex:
                return "{%s}" % tex
            else:
                return tex

    def to_expression(self) -> Expression:
        return Expression(Symbol(self.get_name()), *self.elements)

    def flatten_pattern_sequence(self, evaluation) -> "BoxExpression":
        return self

    def flatten_with_respect_to_head(self, symbol):
        return self.to_expression().flatten_with_respect_to_head(symbol)

    def get_option_values(self, elements, **options):
        evaluation = options.get("evaluation", None)
        if evaluation:
            default = evaluation.definitions.get_options(self.get_name()).copy()
        else:
            # If evaluation is not available, load the default values
            # for the options directly from the class. This requires
            # to parse the rules.
            from mathics.core.parser import parse_builtin_rule

            default = {}
            for option, value in self.options.items():
                option = ensure_context(option)
                default[option] = parse_builtin_rule(value)

        # Now, update the default options with the options explicitly
        # included in the elements
        options = ListExpression(*elements).get_option_values(evaluation)
        default.update(options)
        return default


DOES_NOT_ADD_BUILTIN_DEFINITION = [BoxExpression]
