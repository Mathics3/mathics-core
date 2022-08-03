# -*- coding: utf-8 -*-
# cython: language_level=3

import re
import sympy
from functools import total_ordering
import importlib
from itertools import chain
from typing import Any, Callable, Dict, Iterable, List, Optional, Union, cast


from mathics.builtin.exceptions import (
    BoxConstructError,
    MessageException,
)

from mathics.core.atoms import (
    Integer,
    MachineReal,
    PrecisionReal,
    String,
)
from mathics.core.attributes import protected, read_protected, no_attributes
from mathics.core.convert.expression import to_expression
from mathics.core.convert.python import from_bool
from mathics.core.convert.sympy import from_sympy
from mathics.core.definitions import Definition
from mathics.core.element import BoxElement
from mathics.core.expression import Expression, SymbolDefault
from mathics.core.list import ListExpression
from mathics.core.number import get_precision, PrecisionValueError
from mathics.core.parser.util import SystemDefinitions, PyMathicsDefinitions
from mathics.core.rules import Rule, BuiltinRule, Pattern
from mathics.core.symbols import (
    BaseElement,
    Symbol,
    SymbolHoldForm,
    ensure_context,
    strip_context,
)
from mathics.core.systemsymbols import SymbolMessageName, SymbolRule


def check_requires_list(requires: list) -> bool:
    """
    Check if module names in ``requires`` can be imported and return True if they can or False if not.
    """
    for package in requires:
        lib_is_installed = True
        try:
            lib_is_installed = importlib.util.find_spec(package) is not None
        except ImportError:
            lib_is_installed = False
        if not lib_is_installed:
            return False
    return True


def get_option(options, name, evaluation, pop=False, evaluate=True):
    # we do not care whether an option X is given as System`X,
    # Global`X, or with any prefix from $ContextPath for that
    # matter. Also, the quoted string form "X" is ok. all these
    # variants name the same option. this matches Wolfram Language
    # behaviour.
    name = strip_context(name)
    contexts = (s + "%s" for s in evaluation.definitions.get_context_path())

    for variant in chain(contexts, ('"%s"',)):
        resolved_name = variant % name
        if pop:
            value = options.pop(resolved_name, None)
        else:
            value = options.get(resolved_name)
        if value is not None:
            return value.evaluate(evaluation) if evaluate else value
    return None


def has_option(options, name, evaluation):
    return get_option(options, name, evaluation, evaluate=False) is not None


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


mathics_to_python = {}


class Builtin:
    """
    A base class for a Built-in function symbols, like List, or variables, like $SystemID,
    and Built-in Objects, like DateTimeObject.

    Some of the class variables of the Builtin object are used to
    create a definition object for that built-in symbol.  In particular,
    there are (transformation) rules, attributes, (error) messages,
    options, and other things.

    Function application pattern matching
    -------------------------------------

    Method names of a builtin-class that start with the word ``apply`` are evaluation methods that
    will get called when the docstring of that method matches the expression to be evaluated.

    For example:

    ```
        def apply(x, evaluation):
             "F[x_Real]"
             return Expression(Symbol("G"), x*2)
    ```

    adds a ``BuiltinRule`` to the symbol's definition object that implements ``F[x_]->G[x*2]``.

    As shown in the example above, leading argument names of the
    function are the arguments mentioned in the names given up to the
    first underscore ``_``.  So the single parameter in the above is
    ``x``. The method must also have an evaluation parameter, and may
    have an optional `options` parameter.

    If the ``apply*`` method returns ``None``, the replacement fails, and the expression keeps its original form.

    For rules including ``OptionsPattern``
    ```
        def apply_with_options(x, evaluation, options):
             '''F[x_Real, OptionsPattern[]]'''
             ...
    ```
    the options are stored as a dictionary in the last parameter. For example, if the rule is applied to ``F[x, Method->Automatic]``
    the expression is replaced by the output of ``apply_with_options(x, evaluation, {"System`Method": Symbol("Automatic")})

    The method ``contribute`` stores the definition of the  ``Builtin`` ` `Symbol`` into a set of ``Definitions``. For example,

    ```
    definitions = Definitions(add_builtin=False)
    List(expression=False).contribute(definitions)
    ```
    produces a ``Definitions`` object with just one definition, for the ``Symbol`` ``System`List``.

    Notice that for creating a Builtin, we must pass to the constructor the option ``expression=False``. Otherwise,
    an Expression object is created, with the ``Symbol`` associated to the definition as the ``Head``.
    For example,

    ```
    builtinlist = List(expression=False)
    ```
    creates the  ``Builtin``  ``List``, associated to the symbol ``System`List``, but

    ```
    expr_list = List(Integer(1), Integer(2), Integer(3))
    ```
    is equivalent to:
    ```
    expr_list = ListExpression(Integer(1), Integer(2), Integer(3))
    ```
    """

    name: Optional[str] = None
    context: str = ""
    abstract: bool = False
    attributes: int = protected
    is_numeric: bool = False
    rules: Dict[str, Any] = {}
    formats: Dict[str, Any] = {}
    messages: Dict[str, Any] = {}
    options: Dict[str, Any] = {}
    defaults = {}

    def __new__(cls, *args, **kwargs):
        # comment @mmatera:
        # The goal of this method is to allow to build expressions
        # like ``ListExpression(x,y,z)``
        # in the handy way  ``List(x,y,z)``.
        # This is handy, but can be confusing if this is not very
        # well documented.
        # Notice that this behavior was used extensively in
        # mathics.builtin.inout

        if kwargs.get("expression", None) is not False:
            return to_expression(cls.get_name(), *args)
        else:
            instance = super().__new__(cls)
            if not instance.formats:
                # Reset formats so that not every instance shares the same
                # empty dict {}
                instance.formats = {}
            return instance

    def __init__(self, *args, **kwargs):
        super().__init__()
        if hasattr(self, "python_equivalent"):
            mathics_to_python[self.get_name()] = self.python_equivalent

    def contribute(self, definitions, is_pymodule=False):
        from mathics.core.parser import parse_builtin_rule

        # Set the default context
        if not self.context:
            self.context = "Pymathics`" if is_pymodule else "System`"

        name = self.get_name()
        options = {}
        option_syntax = "Warn"

        for option, value in self.options.items():
            if option == "$OptionSyntax":
                option_syntax = value
                continue
            option = ensure_context(option)
            options[option] = parse_builtin_rule(value)
            if option.startswith("System`"):
                # Create a definition for the option's symbol.
                # Otherwise it'll be created in Global` when it's
                # used, so it won't work.
                if option not in definitions.builtin:
                    definitions.builtin[option] = Definition(name=name)

        # Check if the given options are actually supported by the Builtin.
        # If not, we might issue an optx error and abort. Using '$OptionSyntax'
        # in your Builtin's 'options', you can specify the exact behaviour
        # using one of the following values:

        # - 'Strict': warn and fail with unsupported options
        # - 'Warn': warn about unsupported options, but continue
        # - 'Ignore': allow unsupported options, do not warn

        if option_syntax in ("Strict", "Warn", "System`Strict", "System`Warn"):

            def check_options(options_to_check, evaluation):
                name = self.get_name()
                for key, value in options_to_check.items():
                    short_key = strip_context(key)
                    if not has_option(options, short_key, evaluation):
                        evaluation.message(
                            name,
                            "optx",
                            Expression(SymbolRule, String(short_key), value),
                            strip_context(name),
                        )
                        if option_syntax in ("Strict", "System`Strict"):
                            return False
                return True

        elif option_syntax in ("Ignore", "System`Ignore"):
            check_options = None
        else:
            raise ValueError(
                "illegal option mode %s; check $OptionSyntax." % option_syntax
            )

        rules = []
        definition_class = (
            PyMathicsDefinitions() if is_pymodule else SystemDefinitions()
        )

        for pattern, function in self.get_functions(is_pymodule=is_pymodule):
            rules.append(
                BuiltinRule(name, pattern, function, check_options, system=True)
            )
        for pattern, replace in self.rules.items():
            if not isinstance(pattern, BaseElement):
                pattern = pattern % {"name": name}
                pattern = parse_builtin_rule(pattern, definition_class)
            replace = replace % {"name": name}
            # FIXME: Should system=True be system=not is_pymodule ?
            rules.append(Rule(pattern, parse_builtin_rule(replace), system=True))

        box_rules = []
        if name != "System`MakeBoxes":
            new_rules = []
            for rule in rules:
                if rule.pattern.get_head_name() == "System`MakeBoxes":
                    box_rules.append(rule)
                else:
                    new_rules.append(rule)
            rules = new_rules

        def extract_forms(name, pattern):
            # Handle a tuple of (forms, pattern) as well as a pattern
            # on the left-hand side of a format rule. 'forms' can be
            # an empty string (=> the rule applies to all forms), or a
            # form name (like 'System`TraditionalForm'), or a sequence
            # of form names.
            def contextify_form_name(f):
                # Handle adding 'System`' to a form name, unless it's
                # '' (meaning the rule applies to all forms).
                return "" if f == "" else ensure_context(f)

            if isinstance(pattern, tuple):
                forms, pattern = pattern
                if isinstance(forms, str):
                    forms = [contextify_form_name(forms)]
                else:
                    forms = [contextify_form_name(f) for f in forms]
            else:
                forms = [""]
            return forms, pattern

        formatvalues = {"": []}
        for pattern, function in self.get_functions("format_"):
            forms, pattern = extract_forms(name, pattern)
            for form in forms:
                if form not in formatvalues:
                    formatvalues[form] = []
                formatvalues[form].append(
                    BuiltinRule(name, pattern, function, None, system=True)
                )
        for pattern, replace in self.formats.items():
            forms, pattern = extract_forms(name, pattern)
            for form in forms:
                if form not in formatvalues:
                    formatvalues[form] = []
                if not isinstance(pattern, BaseElement):
                    pattern = pattern % {"name": name}
                    pattern = parse_builtin_rule(pattern)
                replace = replace % {"name": name}
                formatvalues[form].append(
                    Rule(pattern, parse_builtin_rule(replace), system=True)
                )
        for form, formatrules in formatvalues.items():
            formatrules.sort()

        if hasattr(self, "summary_text"):
            self.messages["usage"] = self.summary_text
        messages = [
            Rule(
                Expression(SymbolMessageName, Symbol(name), String(msg)),
                String(value),
                system=True,
            )
            for msg, value in self.messages.items()
        ]

        messages.append(
            Rule(
                Expression(SymbolMessageName, Symbol(name), String("optx")),
                String("`1` is not a supported option for `2`[]."),
                system=True,
            )
        )

        options = {}
        for option, value in self.options.items():
            option = ensure_context(option)
            options[option] = parse_builtin_rule(value)
            if option.startswith("System`"):
                # Create a definition for the option's symbol.
                # Otherwise it'll be created in Global` when it's
                # used, so it won't work.
                if option not in definitions.builtin:
                    definitions.builtin[option] = Definition(name=name)
        defaults = []
        for spec, value in self.defaults.items():
            value = parse_builtin_rule(value)
            pattern = None
            if spec is None:
                pattern = Expression(SymbolDefault, Symbol(name))
            elif isinstance(spec, int):
                pattern = Expression(SymbolDefault, Symbol(name), Integer(spec))
            if pattern is not None:
                defaults.append(Rule(pattern, value, system=True))

        definition = Definition(
            name=name,
            rules=rules,
            formatvalues=formatvalues,
            messages=messages,
            attributes=self.attributes,
            options=options,
            defaultvalues=defaults,
            builtin=self,
            is_numeric=self.is_numeric,
        )
        if is_pymodule:
            definitions.pymathics[name] = definition
        else:
            definitions.builtin[name] = definition

        makeboxes_def = definitions.builtin["System`MakeBoxes"]
        for rule in box_rules:
            makeboxes_def.add_rule(rule)

    @classmethod
    def get_name(cls, short=False) -> str:
        if cls.name is None:
            shortname = cls.__name__
        else:
            shortname = cls.name
        if short:
            return shortname
        return cls.context + shortname

    def get_operator(self) -> Optional[str]:
        return None

    def get_operator_display(self) -> Optional[str]:
        return None

    def get_functions(self, prefix="apply", is_pymodule=False):
        from mathics.core.parser import parse_builtin_rule

        unavailable_function = self._get_unavailable_function()
        for name in dir(self):
            if name.startswith(prefix):
                function = getattr(self, name)
                pattern = function.__doc__
                if pattern is None:  # Fixes PyPy bug
                    continue
                else:
                    m = re.match(r"([\w,]+)\:\s*(.*)", pattern)
                if m is not None:
                    attrs = m.group(1).split(",")
                    pattern = m.group(2)
                else:
                    attrs = []
                # if is_pymodule:
                #    name = ensure_context(self.get_name(short=True), "Pymathics")
                # else:
                name = self.get_name()
                pattern = pattern % {"name": name}
                definition_class = (
                    PyMathicsDefinitions() if is_pymodule else SystemDefinitions()
                )
                pattern = parse_builtin_rule(pattern, definition_class)
                if unavailable_function:
                    function = unavailable_function
                if attrs:
                    yield (attrs, pattern), function
                else:
                    yield (pattern, function)

    @staticmethod
    def get_option(options, name, evaluation, pop=False):
        return get_option(options, name, evaluation, pop)

    def _get_unavailable_function(self) -> Optional[Callable]:
        """
        If some of the required libraries for a symbol are not available,
        returns a default function that override the ``apply_`` methods
        of the class. Otherwise, returns ``None``.
        """

        def apply_unavailable(**kwargs):  # will override apply method
            kwargs["evaluation"].message(
                "General",
                "pyimport",  # see inout.py
                strip_context(self.get_name()),
            )

        requires = getattr(self, "requires", [])
        return None if check_requires_list(requires) else apply_unavailable

    def get_option_string(self, *params):
        s = self.get_option(*params)
        if isinstance(s, String):
            return s.get_string_value(), s
        elif isinstance(s, Symbol):
            for prefix in ("Global`", "System`"):
                if s.get_name().startswith(prefix):
                    return s.get_name()[len(prefix) :], s
        return None, s

    @property
    def is_literal(self) -> bool:
        """
        True if the value can't change, i.e. a value is set and it does not
        depend on definition bindings. That is why, in contrast to
        `is_uncertain_final_definitions()` we don't need a `definitions`
        parameter.

        Each subclass should decide what is right here.
        """
        raise NotImplementedError


class BuiltinElement(Builtin, BaseElement):
    def __new__(cls, *args, **kwargs):
        new_kwargs = kwargs.copy()
        new_kwargs["expression"] = False
        instance = super().__new__(cls, *args, **new_kwargs)
        if not instance.formats:
            # Reset formats so that not every instance shares the same empty
            # dict {}
            instance.formats = {}
        if kwargs.get("expression", None) is not False:
            try:
                instance.init(*args, **kwargs)
            except TypeError:
                # TypeError occurs when unpickling instance, e.g. PatternObject,
                # because parameter expr is not given. This should no be a
                # problem, as pickled objects need their init-method not
                # being called.
                pass
        return instance

    def init(self, *args, **kwargs):
        pass

    def __hash__(self):
        return hash((self.get_name(), id(self)))


class AtomBuiltin(Builtin):
    """
    This class is used to define Atoms other than those ones in core, but also
    have the Builtin function/variable/object properties.
    """

    # allows us to define apply functions, rules, messages, etc. for Atoms
    # which are by default not in the definitions' contribution pipeline.
    # see Image[] for an example of this.

    def get_name(self, short=False) -> str:
        name = super().get_name(short=short)
        return re.sub(r"Atom$", "", name)


class Operator(Builtin):
    operator: Optional[str] = None
    precedence: Optional[int] = None
    precedence_parse = None
    needs_verbatim = False

    default_formats = True

    def get_operator(self) -> Optional[str]:
        return self.operator

    def get_operator_display(self) -> Optional[str]:
        if hasattr(self, "operator_display"):
            return self.operator_display
        else:
            return self.operator


class Predefined(Builtin):
    def get_functions(self, prefix="apply", is_pymodule=False) -> List[Callable]:
        functions = list(super().get_functions(prefix))
        if prefix == "apply" and hasattr(self, "evaluate"):
            functions.append((Symbol(self.get_name()), self.evaluate))
        return functions


class SympyObject(Builtin):
    sympy_name: Optional[str] = None

    mathics_to_sympy = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.sympy_name is None:
            self.sympy_name = strip_context(self.get_name()).lower()
        self.mathics_to_sympy[self.__class__.__name__] = self.sympy_name

    def is_constant(self) -> bool:
        return False

    def get_sympy_names(self) -> List[str]:
        if self.sympy_name:
            return [self.sympy_name]
        return []


class UnaryOperator(Operator):
    def __init__(self, format_function, *args, **kwargs):
        super().__init__(*args, **kwargs)
        name = self.get_name()
        if self.needs_verbatim:
            name = "Verbatim[%s]" % name
        if self.default_formats:
            op_pattern = "%s[item_]" % name
            if op_pattern not in self.formats:
                operator = self.get_operator_display()
                if operator is not None:
                    form = '%s[{HoldForm[item]},"%s",%d]' % (
                        format_function,
                        operator,
                        self.precedence,
                    )
                    self.formats[op_pattern] = form


class PrefixOperator(UnaryOperator):
    def __init__(self, *args, **kwargs):
        super().__init__("Prefix", *args, **kwargs)


class PostfixOperator(UnaryOperator):
    def __init__(self, *args, **kwargs):
        super().__init__("Postfix", *args, **kwargs)


class BinaryOperator(Operator):
    grouping = "System`None"  # NonAssociative, None, Left, Right

    def __init__(self, *args, **kwargs):
        super(BinaryOperator, self).__init__(*args, **kwargs)
        name = self.get_name()
        # Prevent pattern matching symbols from gaining meaning here using
        # Verbatim
        name = "Verbatim[%s]" % name

        # For compatibility, allow grouping symbols in builtins to be
        # specified without System`.
        self.grouping = ensure_context(self.grouping)

        if self.grouping in ("System`None", "System`NonAssociative"):
            op_pattern = "%s[items__]" % name
            replace_items = "items"
        else:
            op_pattern = "%s[x_, y_]" % name
            replace_items = "x, y"

        if self.default_formats:
            operator = self.get_operator_display()
            formatted = 'MakeBoxes[Infix[{%s},"%s",%d,%s], form]' % (
                replace_items,
                operator,
                self.precedence,
                self.grouping,
            )
            formatted_output = 'MakeBoxes[Infix[{%s}," %s ",%d,%s], form]' % (
                replace_items,
                operator,
                self.precedence,
                self.grouping,
            )
            default_rules = {
                "MakeBoxes[{0}, form:StandardForm|TraditionalForm]".format(
                    op_pattern
                ): formatted,
                "MakeBoxes[{0}, form:InputForm|OutputForm]".format(
                    op_pattern
                ): formatted_output,
            }
            default_rules.update(self.rules)
            self.rules = default_rules


class Test(Builtin):
    def apply(self, expr, evaluation) -> Optional[Symbol]:
        "%(name)s[expr_]"
        test_expr = self.test(expr)
        return None if test_expr is None else from_bool(bool(test_expr))


class SympyFunction(SympyObject):
    def apply(self, z, evaluation):
        #
        # Generic apply method that uses the class sympy_name.
        # to call the corresponding sympy function. Arguments are
        # converted to python and the result is converted from sympy
        #
        # "%(name)s[z__]"
        args = z.numerify(evaluation).get_sequence()
        sympy_args = [a.to_sympy() for a in args]
        sympy_fn = getattr(sympy, self.sympy_name)
        try:
            return from_sympy(sympy_fn(*sympy_args))
        except:
            return

    def get_constant(self, precision, evaluation, have_mpmath=False):
        try:
            d = get_precision(precision, evaluation)
        except PrecisionValueError:
            return

        sympy_fn = self.to_sympy()
        if d is None:
            result = self.get_mpmath_function() if have_mpmath else sympy_fn()
            return MachineReal(result)
        else:
            return PrecisionReal(sympy_fn.n(d))

    def get_sympy_function(self, elements=None):
        if self.sympy_name:
            return getattr(sympy, self.sympy_name)
        return None

    def prepare_sympy(self, elements: Iterable) -> Iterable:
        return elements

    def to_sympy(self, expr, **kwargs):
        try:
            if self.sympy_name:
                elements = self.prepare_sympy(expr.elements)
                sympy_args = [element.to_sympy(**kwargs) for element in elements]
                if None in sympy_args:
                    return None
                sympy_function = self.get_sympy_function(elements)
                return sympy_function(*sympy_args)
        except TypeError:
            pass

    def from_sympy(self, sympy_name, elements):
        return to_expression(self.get_name(), *elements)

    def prepare_mathics(self, sympy_expr):
        return sympy_expr


class BoxExpression(BuiltinElement, BoxElement):
    # This is the base class for the "Final form"
    # of formatted expressions.
    #
    # The idea is that this class and their subclasses implement
    # methods of the form ``boxes_to_*`` that now are in ``mathics.core.Expression``.
    # Also, these objects should not be evaluated, so in the evaluation process should be
    # considered "inert". However, it could happend that an Expression having them as an element
    # be evaluable, and try to apply rules. For example,
    # InputForm[ToBoxes[a+b]]
    # should be evaluated to ``Expression(SymbolRowBox, '"a"', '"+"', '"b"')``.
    #
    # Changes to do, after the refactor of mathics.core:
    #

    # * Review the implementation

    attributes = protected | read_protected

    def __new__(cls, *elements, **kwargs):
        instance = super().__new__(cls, *elements, **kwargs)
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
        # self._elements. However, if it didn't happens,
        # we set it with a default value.
        # There should be a better way to implement this
        # behaviour...
        if not hasattr(instance, "_elements"):
            instance._elements = tuple(elements)
        return instance

    @property
    def is_literal(self) -> bool:
        """
        True if the value can't change, i.e. a value is set and it does not
        depend on definition bindings. That is why, in contrast to
        `is_uncertain_final_definitions()` we don't need a `definitions`
        parameter.

        Think about: We will say that a BoxExpression can't change.
        """
        return True

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, value):
        self._elements = value
        return self._elements

    def tex_block(self, tex, only_subsup=False):
        if len(tex) == 1:
            return tex
        else:
            if not only_subsup or "_" in tex or "^" in tex:
                return "{%s}" % tex
            else:
                return tex

    def to_expression(self) -> Expression:
        # FIXME: All classes should store their symbol name.
        # So there should be a self.head.
        return Expression(Symbol(self.get_name()), *self._elements)

    def replace_vars(self, vars, options=None, in_scoping=True, in_function=True):
        expr = self.to_expression()
        result = expr.replace_vars(vars, options, in_scoping, in_function)
        return result

    # Deprecated: remove eventually
    def get_elements(self):
        return self._elements

    def get_head_name(self):
        return self.get_name()

    def get_lookup_name(self):
        return self.get_name()

    def get_sort_key(self) -> tuple:
        return self.to_expression().get_sort_key()

    def get_string_value(self):
        return "-@" + self.get_head_name() + "@-"

    def sameQ(self, expr) -> bool:
        """Mathics SameQ"""
        return expr.sameQ(self)

    def do_format(self, evaluation, format):
        return self

    def format(self, evaluation, fmt):
        expr = Expression(SymbolHoldForm, self.to_expression())
        fexpr = expr.format(evaluation, fmt)
        return fexpr

    def get_head(self):
        return Symbol(self.get_name())

    @property
    def head(self):
        return self.get_head()

    @head.setter
    def head(self, value):
        raise ValueError("BoxExpression.head is write protected.")

    @property
    def leaves(self):
        return self.get_elements()

    @leaves.setter
    def leaves(self, value):
        raise ValueError("BoxExpression.elements is write protected.")

    def flatten_pattern_sequence(self, evaluation) -> "BoxExpression":
        return self

    def flatten_with_respect_to_head(self, symbol):
        return self.to_expression().flatten_with_respect_to_head(symbol)

    def get_option_values(self, elements, **options):
        evaluation = options.get("evaluation", None)
        if evaluation:
            default = evaluation.definitions.get_options(self.get_name()).copy()
            options = ListExpression(*elements).get_option_values(evaluation)
            default.update(options)
        else:
            from mathics.core.parser import parse_builtin_rule

            default = {}
            for option, value in self.options.items():
                option = ensure_context(option)
                default[option] = parse_builtin_rule(value)
        return default

    def boxes_to_text(self, elements, **options) -> str:
        raise BoxConstructError

    def boxes_to_mathml(self, elements, **options) -> str:
        raise BoxConstructError

    def boxes_to_tex(self, elements, **options) -> str:
        raise BoxConstructError


class PatternError(Exception):
    def __init__(self, name, tag, *args):
        super().__init__()
        self.name = name
        self.tag = tag
        self.args = args


class PatternArgumentError(PatternError):
    def __init__(self, name, count, expected):
        super().__init__(name, "argr", count, expected)


class PatternObject(BuiltinElement, Pattern):
    needs_verbatim = True

    arg_counts: List[int] = []

    def init(self, expr):
        super().init(expr)
        if self.arg_counts is not None:
            if len(expr.elements) not in self.arg_counts:
                self.error_args(len(expr.elements), *self.arg_counts)
        self.expr = expr
        self.head = Pattern.create(expr.head)
        self.elements = [Pattern.create(element) for element in expr.elements]

    def error(self, tag, *args):
        raise PatternError(self.get_name(), tag, *args)

    def error_args(self, count, *expected):
        raise PatternArgumentError(self.get_name(), count, *expected)

    def get_attributes(self, definitions) -> int:
        """
        If self has a head, return head's attributes (an attribute bitmask).
        Otherwise return an indication that no attributes have been set.
        """
        if self.head is None:
            # FIXME: _Blank in builtin/patterns.py sets head to None.
            # Figure out if this is the best thing to do and explain why.
            return no_attributes
        return self.head.get_attributes(definitions)

    def get_head_name(self) -> str:
        return self.get_name()

    def get_lookup_name(self) -> str:
        return self.get_name()

    def get_match_candidates(
        self, elements, expression, attributes, evaluation, vars={}
    ):
        return elements

    def get_match_count(self, vars={}):
        return (1, 1)

    def get_sort_key(self, pattern_sort=False) -> tuple:
        return self.expr.get_sort_key(pattern_sort=pattern_sort)


class NegativeIntegerException(Exception):
    pass


@total_ordering
class CountableInteger:
    """
    CountableInteger is an integer specifying a countable amount (including
    zero) that can optionally be specified as an upper bound through UpTo[].
    """

    # currently MMA does not support UpTo[Infinity], but Infinity already shows
    # up in UpTo's parameter error messages as supported option; it would make
    # perfect sense. currently, we stick with MMA's current behaviour and set
    # _support_infinity to False.
    _finite: bool
    _upper_limit: bool
    _integer: Union[str, int]
    _support_infinity = False

    def __init__(self, value="Infinity", upper_limit=True):
        self._finite = value != "Infinity"
        if self._finite:
            assert isinstance(value, int) and value >= 0
            self._integer = value
        else:
            assert upper_limit
            self._integer = None
        self._upper_limit = upper_limit

    def is_upper_limit(self) -> bool:
        return self._upper_limit

    def get_int_value(self) -> int:
        assert self._finite
        return cast(int, self._integer)

    def __eq__(self, other) -> bool:
        if isinstance(other, CountableInteger):
            if self._finite:
                return other._finite and cast(int, self._integer) == other._integer
            else:
                return not other._finite
        elif isinstance(other, int):
            return self._finite and cast(int, self._integer) == other
        else:
            return False

    def __lt__(self, other) -> bool:
        if isinstance(other, CountableInteger):
            if self._finite:
                return other._finite and cast(int, self._integer) < cast(
                    int, other._integer
                )
            else:
                return False
        elif isinstance(other, int):
            return self._finite and cast(int, self._integer) < other
        else:
            return False

    @staticmethod
    def from_expression(expr):
        """
        :param expr: expression from which to build a CountableInteger
        :return: an instance of CountableInteger or None, if the whole
        original expression should remain unevaluated.
        :raises: MessageException, NegativeIntegerException
        """

        if isinstance(expr, Integer):
            py_n = expr.value
            if py_n >= 0:
                return CountableInteger(py_n, upper_limit=False)
            else:
                raise NegativeIntegerException()
        elif expr.get_head_name() == "System`UpTo":
            if len(expr.elements) != 1:
                raise MessageException("UpTo", "argx", len(expr.elements))
            else:
                n = expr.elements[0]
                if isinstance(n, Integer):
                    py_n = n.value
                    if py_n < 0:
                        raise MessageException("UpTo", "innf", expr)
                    else:
                        return CountableInteger(py_n, upper_limit=True)
                elif CountableInteger._support_infinity:
                    if (
                        n.get_head_name() == "System`DirectedInfinity"
                        and len(n.elements) == 1
                    ):
                        if n.elements[0].get_int_value() > 0:
                            return CountableInteger("Infinity", upper_limit=True)
                        else:
                            return CountableInteger(0, upper_limit=True)

        return None  # leave original expression unevaluated


# Backward compatibility
BoxConstruct = BoxExpression
