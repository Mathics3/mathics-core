from typing import Callable

import mathics.core.definitions as definitions

from mathics.builtin.base import Builtin
from mathics.core.element import BaseElement
from mathics.core.symbols import Symbol

form_symbol_to_class = {}


class FormBaseClass(Builtin):
    """
    Base class for a Mathics Form.

    All Forms should subclass this.
    """

    # Mapping from Form and element type to a callable boxing method
    form_box_methods = {}

    # Using "__new__" is not optimal for what we want.
    # We basically want to hook into class construction in order to
    # detect certain class attributes so we can add them to a list.
    # __new__ has this feature. However we do not really need (or want)
    # to do the memory allocation aspect that "__new__" is intended for.
    # We considered __prepare__ and metaclass, instead but could not figure
    # out how to get that to work.
    def __new__(cls, *args, **kwargs):
        """ """
        instance = super().__new__(cls, expression=False)
        name = cls.__name__

        if hasattr(cls, "in_printforms") and cls.in_printforms:
            definitions.PrintForms.add(Symbol(name))
        if hasattr(cls, "in_outputforms") and cls.in_outputforms:
            if name in definitions.OutputForms:
                raise RuntimeError(f"{name} already added to $OutputsForms")
            definitions.OutputForms.add(Symbol(name))
        form_symbol_to_class[Symbol(name)] = cls
        return instance

    @classmethod
    def box(cls, element: BaseElement, evaluation):
        """
        This method is is called for each element that can be boxed.
        ("box" here is a an active verb, not a noun).

        This is a generic routine which calls the specific boxing routine
        that has been regstered in class variable ``form_box_methods`` previously.

        If nothing has been registered, we just return ``element`` back unmodified
        as we do in evaluation.

        Specific and custom method need to be implemented for each Form
        and element_type that perform some kind of boxing.
        """
        method = cls.form_box_methods.get((cls, element.head), None)
        if method is None:
            # The default class should have been registered under FormBaseClass
            method = cls.form_box_methods.get((FormBaseClass, element.head), None)
            if method is None:
                # Just return the element unmodified.
                # Note: this is what we do in evaluation when we don't have a match
                return element

        return method(element, evaluation)

    @classmethod
    def register_box_method(cls, symbol: Symbol, method: Callable):
        """
        Register ``method`` so method(element, ...) is called when
        ``form.box(element, ...)`` is called.

        "form" is something like ``StandardForm``, ``TraditionalForm``, etc.

        To register the default boxing routine, register under the class
        ``FormBaseClass``
        """

        cls.form_box_methods[cls, symbol] = method


def box(element: BaseElement, evaluation, form: Symbol):
    """
    Basically redirects the "box" call from a form symbol name to the "box" method off of
    the Form class named by the symbol.
    """
    form_class = form_symbol_to_class.get(form, None)
    if form_class is None:
        return element
    return form_class.box(element, evaluation)


# FormBaseClass is a public Builtin class that
# should not get added as a definition (and therefore not added to
# to external documentation.

DOES_NOT_ADD_BUILTIN_DEFINITION = [FormBaseClass]
