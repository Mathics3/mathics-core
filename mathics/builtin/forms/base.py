import mathics.core.definitions as definitions
from mathics.builtin.base import Builtin
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


# FormBaseClass is a public Builtin class that
# should not get added as a definition (and therefore not added to
# to external documentation.

DOES_NOT_ADD_BUILTIN_DEFINITION = [FormBaseClass]
