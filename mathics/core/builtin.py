# -*- coding: utf-8 -*-
"""
Class definitions used in mathics.builtin modules that define the
base Mathics3's classes: Predefined, Builtin, Test, Operator (and from that
UnaryOperator, InfixOperator, PrefixOperator, PostfixOperator, etc.),
SympyFunction, MPMathFunction, etc.
"""

import importlib
import importlib.util
import re
from abc import ABC
from functools import total_ordering
from itertools import chain
from types import ModuleType
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)

import mpmath
import sympy

import mathics.core.parser.operators

# Note: it is important *not* to use:
#   from mathics.eval.tracing import run_sympy
# but, instead, import the module, as below, and then
# access ``run_sympy`` using ``tracing.run_sympy.``
#
# This allows us to change where ``tracing.run_sympy`` points to at
# run time.
import mathics.eval.tracing as tracing
from mathics.core.atoms import (
    Integer,
    Integer0,
    Integer1,
    IntegerM1,
    MachineReal,
    Number,
    PrecisionReal,
    String,
)
from mathics.core.attributes import (
    A_HOLD_ALL,
    A_LISTABLE,
    A_NO_ATTRIBUTES,
    A_NUMERIC_FUNCTION,
    A_PROTECTED,
)
from mathics.core.convert.expression import to_expression
from mathics.core.convert.op import ascii_operator_to_symbol, operator_to_unicode
from mathics.core.convert.python import from_bool
from mathics.core.convert.sympy import from_sympy
from mathics.core.definitions import Definition, Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import MessageException
from mathics.core.expression import Expression
from mathics.core.interrupt import BreakInterrupt, ContinueInterrupt, ReturnInterrupt
from mathics.core.list import ListExpression
from mathics.core.number import PrecisionValueError, dps, get_precision, min_prec
from mathics.core.parser.operators import OPERATOR_DATA
from mathics.core.parser.util import PyMathicsDefinitions, SystemDefinitions
from mathics.core.pattern import BasePattern
from mathics.core.rules import BaseRule, FunctionApplyRule, Rule
from mathics.core.symbols import (
    BaseElement,
    BooleanType,
    Symbol,
    SymbolFalse,
    SymbolPlus,
    SymbolPower,
    SymbolTimes,
    SymbolTrue,
    ensure_context,
    strip_context,
)
from mathics.core.systemsymbols import (
    SymbolDefault,
    SymbolLessEqual,
    SymbolMessageName,
    SymbolRule,
    SymbolSequence,
)
from mathics.eval.arithmetic import eval_mpmath_function
from mathics.eval.numbers.numbers import cancel
from mathics.eval.numerify import numerify
from mathics.eval.scoping import dynamic_scoping
from mathics.eval.sympy import eval_sympy


# Exceptions...
class NegativeIntegerException(Exception):
    pass


# Has to come before PatternArgumentError
class PatternError(Exception):
    def __init__(self, name, tag, *args):
        super().__init__()
        self.name = name
        self.tag = tag
        self.args = args


class PatternArgumentError(PatternError):
    def __init__(self, name, count, expected):
        super().__init__(name, "argr", count, expected)


class Builtin:
    """
    A base class for a Built-in function symbols, like List, or
    variables, like $SystemID, and Built-in Objects, like
    DateTimeObject.

    Some of the class variables of the Builtin object are used to
    create a definition object for that built-in symbol.  In particular,
    there are (transformation) rules, attributes, (error) messages,
    options, and other things.

    Function application pattern matching
    -------------------------------------

    Method names of a builtin-class that start with the word ``eval``
    are evaluation methods that will get called when the docstring of
    that method matches the expression to be evaluated.

    For example:

    ```
        def eval(x, evaluation):
             "F[x_Real]"
             return Expression(Symbol("G"), x*2)
    ```

    adds a ``FunctionApplyRule`` to the symbol's definition object that implements
    ``F[x_]->G[x*2]``.

    As shown in the example above, leading argument names of the
    function are the arguments mentioned in the names given up to the
    first underscore ``_``.  So the single parameter in the above is
    ``x``. The method must also have an evaluation parameter, and may
    have an optional `options` parameter.

    If the ``eval*`` method returns ``None``, the replacement fails,
    and the expression keeps its original form.

    For rules including ``OptionsPattern``
    ```
        def eval_with_options(x, evaluation: Evaluation, options: dict):
             '''F[x_Real, OptionsPattern[]]'''
             ...
    ```

    the options are stored as a dictionary in the last parameter. For
    example, if the rule is applied to ``F[x, Method->Automatic]`` the
    expression is replaced by the output of ``eval_with_options(x,
    evaluation, {"System`Method": Symbol("Automatic")})

    The method ``contribute`` stores the definition of the ``Builtin``
    ` `Symbol`` into a set of ``Definitions``. For example,

    ```
    definitions = Definitions(add_builtin=False)
    List(expression=False).contribute(definitions)
    ```

    produces a ``Definitions`` object with just one definition, for
    the ``Symbol`` ``System`List``.

    Notice that for creating a Builtin, we must pass to the
    constructor the option ``expression=False``. Otherwise, an
    Expression object is created, with the ``Symbol`` associated to
    the definition as the ``Head``.  For example,

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
    attributes: int = A_PROTECTED
    _is_numeric: bool = False
    rules: Dict[str, Any] = {}
    formats: Dict[str, Any] = {}
    messages: Dict[str, Any] = {}
    options: Dict[str, Any] = {}
    defaults: Dict[Optional[int], str] = {}

    def __getnewargs_ex__(self):
        return tuple(), {
            "expression": False,
        }

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

    def contribute(self, definitions: Definitions, is_pymodule=False):
        from mathics.core.parser import parse_builtin_rule

        name = self.get_name()
        attributes = self.attributes
        options = {}
        # Set the default context
        if not self.context:
            self.context = "Pymathics`" if is_pymodule else "System`"
            # get_name takes the context from the class, not from the
            # instance, so even if we set the context here,
            # self.get_name() does not includes the context.
            name = self.context + name

        # - 'Strict': warn and fail with unsupported options
        # - 'Warn': warn about unsupported options, but continue
        # - 'Ignore': allow unsupported options, do not warn

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
                    definitions.builtin[option] = Definition(name=option)

        # Check if the given options are actually supported by the
        # Builtin.  If not, we might issue an "optx" error and
        # abort. Using '$OptionSyntax' in your Builtin's 'options',
        # you can specify the exact behaviour using one of the
        # following values:

        if option_syntax in ("Strict", "System`Strict"):
            check_options = DefaultOptionChecker(self, options, True)
        elif option_syntax in ("Warn", "System`Warn"):
            check_options = DefaultOptionChecker(self, options, False)
        elif option_syntax in ("Ignore", "System`Ignore"):
            check_options = None
        else:
            raise ValueError(
                f"illegal option mode {option_syntax}; check $OptionSyntax."
            )

        rules: List[BaseRule] = []
        definition_class = (
            PyMathicsDefinitions() if is_pymodule else SystemDefinitions()
        )

        for pattern, function in self.get_functions(
            prefix="eval", is_pymodule=is_pymodule
        ):
            pat_attr = attributes if pattern.get_head_name() == name else None
            rules.append(
                FunctionApplyRule(
                    name,
                    pattern,
                    function,
                    check_options,
                    attributes=pat_attr,
                    system=True,
                )
            )
        for pattern, function in self.get_functions(is_pymodule=is_pymodule):
            pat_attr = attributes if pattern.get_head_name() == name else None
            rules.append(
                FunctionApplyRule(
                    name,
                    pattern,
                    function,
                    check_options,
                    attributes=pat_attr,
                    system=True,
                )
            )
        for pattern_str, replace_str in self.rules.items():
            pattern_str = pattern_str % {"name": name}
            pattern = parse_builtin_rule(pattern_str, definition_class)
            replace_str = replace_str % {"name": name}
            pat_attr = attributes if pattern.get_head_name() == name else None
            rules.append(
                Rule(
                    pattern,
                    parse_builtin_rule(replace_str),
                    attributes=pat_attr,
                    system=not is_pymodule,
                )
            )

        box_rules = []
        # FIXME: Why a special case for System`MakeBoxes? Remove this
        if name != "System`MakeBoxes":
            new_rules = []
            for rule in rules:
                if rule.pattern.get_head_name() == "System`MakeBoxes":
                    box_rules.append(rule)
                else:
                    new_rules.append(rule)
            rules = new_rules

        def extract_forms(pattern):
            """Handle a tuple of (forms, pattern) as well as a pattern
            on the left-hand side of a format rule. 'forms' can be
            an empty string (=> the rule applies to all forms), or a
            form name (like 'System`TraditionalForm'), or a sequence
            of form names.
            """

            def contextify_form_name(f):
                """Handle adding 'System`' to a form name, unless it's ""
                (meaning the rule applies to all forms).
                """
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

        formatvalues: Dict[str, List[BaseRule]] = {"": []}
        for pattern, function in self.get_functions("format_"):
            forms, pattern = extract_forms(pattern)
            pat_attr = attributes if pattern.get_head_name() == name else None
            for form in forms:
                if form not in formatvalues:
                    formatvalues[form] = []
                formatvalues[form].append(
                    FunctionApplyRule(
                        name, pattern, function, None, attributes=pat_attr, system=True
                    )
                )
        for pattern, replace in self.formats.items():
            forms, pattern = extract_forms(pattern)
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
            rules=tuple(rules),
            rules_dict={
                "formatvalues": formatvalues,
                "messages": messages,
                "options": options,
                "defaultvalues": defaults,
            },
            attributes=attributes,
            builtin=self,
            is_numeric=self._is_numeric,
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

    def get_functions(self, prefix="eval", is_pymodule=False):
        from mathics.core.parser import parse_builtin_rule

        unavailable_function = self._get_unavailable_function()
        for name in dir(self):
            if name.startswith(prefix):
                function = getattr(self, name)
                pattern = function.__doc__
                if pattern is None:  # Fixes PyPy bug
                    continue
                else:
                    # TODO: consider to use a more sophisticated
                    # regular expression, which handles breaklines
                    # more properly, that supports format names
                    # with contexts (context`name) and be less
                    # fragile against leaving spaces between the
                    # elements.
                    m = re.match(
                        r"[(]([\w,]+),[ ]*[)]\:\s*(.*)", pattern.replace("\n", " ")
                    )
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
    def get_option(options, name, evaluation, pop=False) -> Optional[BaseElement]:
        return get_option(options, name, evaluation, pop)

    def _get_unavailable_function(self) -> Optional[Callable]:
        """
        If some of the required libraries for a symbol are not available,
        returns a default function that override the ``eval_`` methods
        of the class. Otherwise, returns ``None``.
        """
        requires = getattr(self, "requires", [])
        return None if check_requires_list(requires) else UnavailableFunction(self)

    def get_option_string(self, *params) -> Tuple[Optional[str], Optional[BaseElement]]:
        """
        Return a tuple of a `str` representing the option name,
        and the proper Mathics value of the option.
        If the value does not have a name, the name is None.
        """
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
    options: Dict[str, Any]

    def __new__(cls, *args, **kwargs):
        new_kwargs = kwargs.copy()
        # In a Builtin element, we never return an Expression object,
        # so we create it with the option `expression=False`.
        new_kwargs["expression"] = False
        instance = super().__new__(cls, *args, **new_kwargs)
        # If `expression` is not `False`, we need to initialize the object:
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


# This has to come before SympyFunction
class SympyObject(Builtin):
    sympy_name: Optional[str] = None

    mathics_to_sympy: Dict[str, str] = {}

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

    def to_sympy(self, expr=None, **kwargs):
        raise NotImplementedError

    def from_sympy(self, elements: Tuple[BaseElement, ...]) -> Expression:
        raise NotImplementedError


# This has to come before MPMathFunction
class SympyFunction(SympyObject):
    def eval(self, elements, evaluation: Evaluation):
        # Note: we omit a docstring here, so as not to confuse
        # function signature collector ``contribute``.

        # Generic eval method that uses the class sympy_name.
        # to call the corresponding sympy function. Arguments are
        # converted to python and the result is converted from sympy
        #
        # "%(name)s[elements]"
        return eval_sympy(self, elements, evaluation)

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

    def get_sympy_function(self, elements=None) -> Optional[Callable]:
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
                if sympy_function is not None:
                    return tracing.run_sympy(sympy_function, *sympy_args)
        except TypeError:
            pass

    def from_sympy(self, elements: Tuple[BaseElement, ...]) -> Expression:
        return Expression(Symbol(self.get_name()), *elements)

    def prepare_mathics(self, sympy_expr):
        return sympy_expr


class MPMathFunction(SympyFunction):
    # These below attributes are the default attributes:
    #
    # * functions take lists as an argument
    # * functions take numeric values only
    # * functions can't be changed
    #
    # However hey are not correct for some derived classes, like
    # InverseErf or InverseErfc.
    # So those classes should expclicitly set/override this.
    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    mpmath_name: Optional[str] = None
    nargs = {1}

    def get_mpmath_function(self, args):
        if self.mpmath_name is None or len(args) not in self.nargs:
            return None
        return getattr(mpmath, self.mpmath_name)

    def eval(self, z, evaluation: Evaluation):
        "%(name)s[z__]"

        args = numerify(z, evaluation).get_sequence()

        # if no arguments are inexact attempt to use sympy
        if all(not x.is_inexact() for x in args):
            result = to_expression(self.get_name(), *args).to_sympy()
            result = self.prepare_mathics(result)
            result = from_sympy(result)
            # evaluate elements to convert e.g. Plus[2, I] -> Complex[2, 1]
            if isinstance(result, Expression):
                return result.evaluate_elements(evaluation)
            else:
                return result

        if not all(isinstance(arg, Number) for arg in args):
            return
        # mypy isn't yet smart enough to recognise that we can only reach this point if all args are Numbers
        args = cast(Sequence[Number], args)

        mpmath_function = self.get_mpmath_function(tuple(args))
        if mpmath_function is None:
            return

        if any(arg.is_machine_precision() for arg in args):
            prec = None
        else:
            prec = min_prec(*args)
            d = dps(prec)
            args = tuple([arg.round(d) for arg in args])

        return eval_mpmath_function(
            mpmath_function, *cast(Sequence[Number], args), prec=prec
        )


class MPMathMultiFunction(MPMathFunction):
    sympy_names: Optional[Dict[int, str]] = None
    mpmath_names: Optional[Dict[int, str]] = None

    def get_sympy_names(self):
        if self.sympy_names is None:
            return [self.sympy_name]
        return self.sympy_names.values()

    def get_function(self, module, names, fallback_name, elements):
        try:
            name = fallback_name
            if names is not None:
                name = names[len(elements)]
            if name is None:
                return None
            return getattr(module, name)
        except KeyError:
            return None

    def get_sympy_function(self, elements):
        return self.get_function(sympy, self.sympy_names, self.sympy_name, elements)

    def get_mpmath_function(self, elements):
        return self.get_function(mpmath, self.mpmath_names, self.mpmath_name, elements)


class DefaultOptionChecker:
    """
    Callable class that is used in checking that options are valid.

    If initialized with ``strict`` set to True,
    then a instantance calls will return True only if all
    options listed in ``options_to_check`` are in the constructor's
    list of options. In either case, when an option is not in the
    constructor list, give an "optx" message.
    """

    def __init__(self, builtin, options, strict: bool):
        self.name = builtin.get_name()
        self.strict = strict
        self.options = options

    def __call__(self, options_to_check, evaluation):
        option_name = self.name
        options = self.options
        strict = self.strict

        for key, value in options_to_check.items():
            short_key = strip_context(key)
            if not has_option(options, short_key, evaluation):
                evaluation.message(
                    option_name,
                    "optx",
                    Expression(SymbolRule, String(short_key), value),
                    strip_context(option_name),
                )
                if strict:
                    return False
        return True


class UnavailableFunction:
    """
    Callable class used when the evaluation function is not available.
    """

    def __init__(self, builtin):
        self.name = builtin.get_name()

    def __call__(self, **kwargs):
        kwargs["evaluation"].message(
            "General",
            "pyimport",  # see messages.py for error message definition
            strip_context(self.name),
        )


def check_requires_list(requires: list) -> bool:
    """
    Check if module names in ``requires`` can be imported and return
    True if they can, or False if not.

    """
    for package in requires:
        lib_is_installed = True
        try:
            lib_is_installed = importlib.util.find_spec(package) is not None
        except ImportError:
            # print("XXX requires import error", requires)
            lib_is_installed = False
        if not lib_is_installed:
            # print("XXX requires not found error", requires)
            return False
    return True


def get_option(
    options: dict, name, evaluation, pop=False, evaluate=True
) -> Optional[BaseElement]:
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


mathics_to_python: Dict[str, Any] = {}  # here we have: name -> string


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
    _integer: Union[str, int, None]
    _support_infinity = False

    def __init__(self, value: Union[int, str] = "Infinity", upper_limit=True):
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


class AtomBuiltin(Builtin):
    """
    This class is used to define Atoms other than those ones in core, but also
    have the Builtin function/variable/object properties.
    """

    # allows us to define eval functions, rules, messages, etc. for Atoms
    # which are by default not in the definitions' contribution pipeline.
    # see Image[] for an example of this.

    @classmethod
    def get_name(cls, short=False) -> str:
        name = super().get_name(short=short)
        return re.sub(r"Atom$", "", name)


class IterationFunction(Builtin, ABC):
    attributes = A_HOLD_ALL | A_PROTECTED
    allow_loopcontrol = False
    throw_iterb = True

    def get_result(self, elements) -> Expression:
        raise NotImplementedError

    def eval_symbol(self, expr, iterator, evaluation):
        "%(name)s[expr_, iterator_Symbol]"
        iterator = iterator.evaluate(evaluation)
        if iterator.has_form(["List", "Range", "Sequence"], None):
            elements = iterator.elements
            if len(elements) == 1:
                return self.eval_max(expr, *elements, evaluation)
            elif len(elements) == 2:
                if elements[1].has_form(["List", "Sequence"], None):
                    seq = Expression(SymbolSequence, *(elements[1].elements))
                    return self.eval_list(expr, elements[0], seq, evaluation)
                else:
                    return self.eval_range(expr, *elements, evaluation)
            elif len(elements) == 3:
                return self.eval_iter_nostep(expr, *elements, evaluation)
            elif len(elements) == 4:
                return self.eval_iter(expr, *elements, evaluation)

        if self.throw_iterb:
            evaluation.message(self.get_name(), "iterb")
        return

    def eval_range(self, expr, i, imax, evaluation):
        "%(name)s[expr_, {i_Symbol, imax_}]"

        imax = imax.evaluate(evaluation)
        if imax.has_form("Range", None):
            # FIXME: this should work as an iterator in Python3, not
            # building the sequence explicitly...
            seq = Expression(SymbolSequence, *(imax.evaluate(evaluation).elements))
            return self.eval_list(expr, i, seq, evaluation)
        elif imax.has_form("List", None):
            seq = Expression(SymbolSequence, *(imax.elements))
            return self.eval_list(expr, i, seq, evaluation)
        else:
            return self.eval_iter(expr, i, Integer1, imax, Integer1, evaluation)

    def eval_max(self, expr, imax, evaluation):
        "%(name)s[expr_, {imax_}]"

        # Even though `imax` should be an integral value, its type does not
        # have to be an Integer.

        result = []

        def do_iteration():
            evaluation.check_stopped()
            try:
                result.append(expr.evaluate(evaluation))
            except ContinueInterrupt:
                if self.allow_loopcontrol:
                    pass
                else:
                    raise
            except BreakInterrupt:
                if self.allow_loopcontrol:
                    raise StopIteration
                else:
                    raise
            except ReturnInterrupt as e:
                if self.allow_loopcontrol:
                    return e.expr
                else:
                    raise

        if isinstance(imax, Integer):
            try:
                for _ in range(imax.value):
                    do_iteration()
            except StopIteration:
                pass

        else:
            imax = imax.evaluate(evaluation)
            imax = numerify(imax, evaluation)
            if isinstance(imax, Number):
                imax = imax.round()
            py_max = imax.get_float_value()
            if py_max is None:
                if self.throw_iterb:
                    evaluation.message(self.get_name(), "iterb")
                return

            index = 0
            try:
                while index < py_max:
                    do_iteration()
                    index += 1
            except StopIteration:
                pass

        return self.get_result(result)

    def eval_iter_nostep(self, expr, i, imin, imax, evaluation):
        "%(name)s[expr_, {i_Symbol, imin_, imax_}]"
        return self.eval_iter(expr, i, imin, imax, Integer1, evaluation)

    def eval_iter(self, expr, i, imin, imax, di, evaluation):
        "%(name)s[expr_, {i_Symbol, imin_, imax_, di_}]"

        if isinstance(self, SympyFunction) and di.get_int_value() == 1:
            whole_expr = to_expression(
                self.get_name(), expr, ListExpression(i, imin, imax)
            )
            sympy_expr = whole_expr.to_sympy(evaluation=evaluation)
            if sympy_expr is None:
                return None

            # apply Together to produce results similar to Mathematica
            result = sympy.together(sympy_expr)
            result = from_sympy(result)
            result = cancel(result)

            if not result.sameQ(whole_expr):
                return result
            return

        index = Integer0
        imin = imin.evaluate(evaluation)
        imax = imax.evaluate(evaluation)
        di = di.evaluate(evaluation)

        # (imax - imin) / di
        normalised_range = Expression(
            Symbol("System`Chop"),
            Expression(
                SymbolTimes,
                Expression(SymbolPlus, imax, Expression(SymbolTimes, IntegerM1, imin)),
                Expression(SymbolPower, di, IntegerM1),
            ),
        ).evaluate(evaluation)

        result = []
        while True:
            cont = Expression(SymbolLessEqual, index, normalised_range).evaluate(
                evaluation
            )
            if cont is SymbolFalse:
                break
            if cont is not SymbolTrue:
                if self.throw_iterb:
                    evaluation.message(self.get_name(), "iterb")
                return

            evaluation.check_stopped()
            try:
                item = dynamic_scoping(
                    expr.evaluate,
                    {
                        i.name: (
                            Expression(
                                SymbolPlus, imin, Expression(SymbolTimes, di, index)
                            ).evaluate(evaluation)
                            if index.value > 0
                            else imin
                        )
                    },
                    evaluation,
                )
                result.append(item)
            except ContinueInterrupt:
                if self.allow_loopcontrol:
                    pass
                else:
                    raise
            except BreakInterrupt:
                if self.allow_loopcontrol:
                    break
                else:
                    raise
            except ReturnInterrupt as e:
                if self.allow_loopcontrol:
                    return e.expr
                else:
                    raise
            index = Expression(SymbolPlus, index, Integer1).evaluate(evaluation)
        return self.get_result(result)

    def eval_list(self, expr, i, items, evaluation):
        "%(name)s[expr_, {i_Symbol, {items___}}]"

        items = items.evaluate(evaluation).get_sequence()
        result = []
        for item in items:
            evaluation.check_stopped()
            try:
                item = dynamic_scoping(expr.evaluate, {i.name: item}, evaluation)
                result.append(item)
            except ContinueInterrupt:
                if self.allow_loopcontrol:
                    pass
                else:
                    raise
            except BreakInterrupt:
                if self.allow_loopcontrol:
                    break
                else:
                    raise
            except ReturnInterrupt as e:
                if self.allow_loopcontrol:
                    return e.expr
                else:
                    raise
        return self.get_result(result)

    def eval_multi(self, expr, first, sequ, evaluation):
        "%(name)s[expr_, first_, sequ__]"

        sequ = sequ.get_sequence()
        name = self.get_name()
        return to_expression(name, to_expression(name, expr, *sequ), first)


class Operator(Builtin):
    """
    Base Class for operators: binary, unary, nullary, prefix postfix, ...
    """

    operator: Optional[str] = None
    precedence: Optional[int] = None
    precedence_parse = None
    needs_verbatim = False

    default_formats = True

    def get_precedence(self, name: str) -> int:
        operator_info = OPERATOR_DATA.get("operator-precedences")
        assert isinstance(
            operator_info, dict
        ), 'Internal error: "operator-precedences" should be found in operators.json'
        precedence = operator_info.get(name)
        assert isinstance(
            precedence, int
        ), f'Internal error: "precedence" field for "{name}" should be an integer; is {precedence}'
        return precedence

    def get_operator(self) -> Optional[str]:
        name = self.__class__.__name__
        return operator_to_unicode.get(name)

    def get_operator_display(self) -> Optional[str]:
        if hasattr(self, "operator_display"):
            return self.operator_display
        else:
            return self.operator


# Note: Metaprogramming in mathics.builtin.no_meaning fails if
# we inherit from ABC
class InfixOperator(Operator):
    """
    Class for Mathics3 built-in Infix Operators. Infix operators are
    represented with an operator in between each argument. A common
    and special case is when the number of operands is two. This is
    called a binary operator.

    In Mathics3, many operators that are conventionally thought of as
    binary operators, like Plus (+) allow an accept more than two
    arguments.

    """

    # Note: grouping must be Python string, not a Symbol.
    grouping = "System`None"  # NonAssociative, None, Left, Right

    def __init__(self, *args, **kwargs):
        super(InfixOperator, self).__init__(*args, **kwargs)
        name = self.get_name(short=True)

        # Pick up operator string from JSON table if
        # it appears there.
        operator_string = self.get_operator()
        if operator_string:
            self.operator = operator_string
        # else:
        #     if self.operator is None:
        #         breakpoint()
        #     print("FIX UP", self.operator, name)

        self.precedence = self.get_precedence(name)

        # Prevent pattern matching symbols from gaining meaning here using
        # Verbatim
        verbatim_name = f"Verbatim[{name}]"

        # For compatibility, allow grouping symbols in builtins to be
        # specified without System`.
        self.grouping = ensure_context(self.grouping)

        if self.grouping in ("System`None", "System`NonAssociative"):
            op_pattern = f"{verbatim_name}[items__]"
            replace_items = "items"
        else:
            op_pattern = f"{verbatim_name}[x_, y_]"
            replace_items = "x, y"

        operator = ascii_operator_to_symbol.get(self.operator, self.__class__.__name__)

        if self.default_formats:
            if name not in ("Rule", "RuleDelayed"):
                formats = {
                    op_pattern: "HoldForm[Infix[{%s}, %s, %d, %s]]"
                    % (replace_items, operator, self.precedence, self.grouping)
                }
                formats.update(self.formats)
                self.formats = formats
            formatted = "MakeBoxes[Infix[{%s}, %s, %d,%s], form]" % (
                replace_items,
                operator,
                self.precedence,
                self.grouping,
            )
            default_rules = {
                "MakeBoxes[{0}, form:StandardForm|TraditionalForm]".format(
                    op_pattern
                ): formatted,
                f"MakeBoxes[{op_pattern}, form:InputForm|OutputForm]": formatted,
            }
            default_rules.update(self.rules)
            self.rules = default_rules


class NoMeaningInfixOperator(InfixOperator):
    """
    Operators that have no pre-defined meaning are derived from this class.
    """

    # This will be used to create a docstring
    __doc_pattern__ = r"""
    <url>
    :WML link:
    https://reference.wolfram.com/language/ref/{operator_name}.html</url>

    <dl>
      <dt>'{operator_name}[$x$, $y$, ...]'
      <dd>displays $x$ {operator_string} $y$ {operator_string} ...
    </dl>

    >> {operator_name}[x, y, z]
     = x {operator_string} y {operator_string} z

    >> a \[{operator_name}] b
     = a {operator_string} b

    """
    __formats_pattern__ = r"""{lbrace}
                    (
                           ("InputForm", "OutputForm", "StandardForm"),
                        f"{operator_name}[args__]",
                    ): (('Infix[{lbrace}args{rbrace}, {operator_string}"]'))
                {rbrace}"""

    attributes = A_NO_ATTRIBUTES
    default_formats = False  # Don't use any default format rules. Instead, see below.

    operator = "This should be overwritten"
    summary_text = "This should be overwritten"


class Predefined(Builtin, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.symbol = Symbol(self.get_name())

    def get_functions(self, prefix="eval", is_pymodule=False) -> List[Callable]:
        functions = list(super().get_functions(prefix))
        if prefix == "eval" and hasattr(self, "evaluate"):
            functions.append((self.symbol, self.evaluate))
        return functions


# Has to come before PostfixOperator and PrefixOperator
# Note: Metaprogramming in mathics.builtin.no_meaning fails if
# we inherit from ABC
class UnaryOperator(Operator):
    """
    Class for Unary Operators, (e.g. Not, Factorial)
    """

    def __init__(self, format_function, *args, **kwargs):
        super().__init__(*args, **kwargs)
        name = self.get_name(short=True)

        # Pick up operator string from JSON table if
        # it appears there.
        if self.operator is None:
            operator_string = self.get_operator()
            if operator_string:
                self.operator = operator_string
            # else:
            #     if self.operator is None:
            #         breakpoint()
            #     print("FIX UP", self.operator, name)

        self.precedence = self.get_precedence(name)
        if self.needs_verbatim:
            name = f"Verbatim[{name}"
        if self.default_formats:
            op_pattern = f"{name}[item_]"
            if op_pattern not in self.formats:
                operator = self.get_operator_display()
                if operator is not None:
                    form = '%s[{HoldForm[item]},"%s",%d]' % (
                        format_function,
                        operator,
                        self.precedence,
                    )
                    self.formats[op_pattern] = form


# Note: Metaprogramming in mathics.builtin.no_meaning fails if
# we inherit from ABC
class PostfixOperator(UnaryOperator):
    """
    Class for Builtin Postfix Unary Operators, e.g. Factorial (!)
    """

    def __init__(self, *args, **kwargs):
        super().__init__("Postfix", *args, **kwargs)


# Has to be after PostfixOperator
class NoMeaningPostfixOperator(PostfixOperator):
    """
    Postfix Operators that have no pre-defined meaning are derived from this class.
    """

    # This will be used to create a docstring
    __doc_pattern__ = r"""
    <url>
    :WML link:
    https://reference.wolfram.com/language/ref/{operator_name}.html</url>

    <dl>
      <dt>'{operator_name}[$x$]'
      <dd>displays $x$ {operator_string}
    </dl>

    >> {operator_name}[x]
     = x {operator_string}

    >> x \[{operator_name}]
     = x {operator_string}

    """
    attributes = A_NO_ATTRIBUTES
    default_formats = False  # Don't use any default format rules. Instead, see below.

    operator = "This should be overwritten"
    summary_text = "This should be overwritten"


# Note: Metaprogramming in mathics.builtin.no_meaning fails if
# we inherit from ABC
class PrefixOperator(UnaryOperator):
    """
    Class for Builtin Prefix Unary Operators, e.g. Not ("¬")
    """

    def __init__(self, *args, **kwargs):
        super().__init__("Prefix", *args, **kwargs)


# Has to be after PrefixOperator
class NoMeaningPrefixOperator(PrefixOperator):
    """
    Prefix Operators that have no pre-defined meaning are derived from this class.
    """

    # This will be used to create a docstring
    __doc_pattern__ = r"""
    <url>
    :WML link:
    https://reference.wolfram.com/language/ref/{operator_name}.html</url>

    <dl>
      <dt>'{operator_name}[$x$]'
      <dd>displays {operator_string} $x$
    </dl>

    >> {operator_name}[x]
     = {operator_string}x

    >> \[{operator_name}]x
     = {operator_string}x

    """
    attributes = A_NO_ATTRIBUTES
    default_formats = False  # Don't use any default format rules. Instead, see below.

    operator = "This should be overwritten"
    summary_text = "This should be overwritten"


def add_no_meaning_builtin_classes(
    create_operator_class: Callable,
    affix: str,
    mathics3_format_function_name: str,
    operator_base_class: Union[
        NoMeaningInfixOperator, NoMeaningPostfixOperator, NoMeaningPrefixOperator
    ],
    builtin_module: ModuleType,
):
    """
    Creates all of the operators (infix, postfix, prefix) that
    have no pre-set builtin meaning.
    """
    operator_key = f"no-meaning-{affix}-operators"
    for operator_name, operator_tuple in OPERATOR_DATA[operator_key].items():
        operator_string = operator_tuple[0]
        generated_operator_class = create_operator_class(
            operator_name,
            operator_base_class,
            operator_string,
            mathics3_format_function_name,
        )

        if affix == "infix":
            mathics.core.parser.operators.flat_binary_operators[
                operator_name
            ] = operator_tuple[1]
        elif affix == "postfix":
            mathics.core.parser.operators.postfix_operators[
                operator_name
            ] = operator_tuple[1]
        elif affix == "prefix":
            mathics.core.parser.operators.prefix_operators[
                operator_name
            ] = operator_tuple[1]

        # Put the newly-created Builtin class inside the module under
        # mathics.builtin.no_meaning.xxx.
        setattr(builtin_module, operator_name, generated_operator_class)


class PatternObject(BuiltinElement, BasePattern):
    needs_verbatim = True

    arg_counts: List[int] = []
    options: Dict[str, Any]

    def init(self, expr: Expression, evaluation: Optional[Evaluation] = None):
        super().init(expr, evaluation=evaluation)
        if self.arg_counts is not None:
            if len(expr.elements) not in self.arg_counts:
                self.error_args(len(expr.elements), *self.arg_counts)
        self.expr = expr
        self.head = BasePattern.create(expr.head, evaluation=evaluation)
        self.elements = [
            BasePattern.create(element, evaluation=evaluation)
            for element in expr.elements
        ]

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
            return A_NO_ATTRIBUTES
        return self.head.get_attributes(definitions)

    def get_head(self) -> Symbol:
        return Symbol(self.get_name())

    def get_head_name(self) -> str:
        return self.get_name()

    def get_lookup_name(self) -> str:
        return self.get_name()

    def get_match_candidates(
        self, elements: Tuple[BaseElement], pattern_context: dict
    ) -> Tuple[BaseElement]:
        return elements

    def get_match_count(self, vars_dict: Optional[dict] = None):
        return (1, 1)

    def get_sort_key(self, pattern_sort=False) -> tuple:
        return self.expr.get_sort_key(pattern_sort=pattern_sort)


class Test(Builtin, ABC):
    def eval(self, expr, evaluation: Evaluation) -> Optional[BooleanType]:
        # Note: in the docstring below, we need to use %(name)s for
        # subclasses like ExactNumberQ to work with function-application
        # pattern matching.
        """%(name)s[expr_]"""
        test_expr = self.test(expr)
        return None if test_expr is None else from_bool(bool(test_expr))

    def test(self, expr) -> bool:
        """Subclasses of test must implement a boolean test function"""
        raise NotImplementedError
