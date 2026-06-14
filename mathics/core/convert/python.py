# -*- coding: utf-8 -*-
"""
Conversions between Python and Mathics3
"""

from dataclasses import dataclass
from typing import Any, Final, Optional

import numpy

from mathics.core.atoms import (
    ByteArray,
    Complex,
    Integer,
    NumericArray,
    Rational,
    Real,
    String,
)
from mathics.core.number import get_type
from mathics.core.symbols import (
    BaseElement,
    BooleanType,
    SymbolFalse,
    SymbolNull,
    SymbolTrue,
)
from mathics.core.systemsymbols import SymbolAssociation, SymbolRule


def from_bool(arg: bool) -> BooleanType:
    """
    Conversion from a bool to something Mathics3 can use.
    """
    return SymbolTrue if arg else SymbolFalse


def from_complex(arg: complex) -> Complex:
    """
    Conversion from a Python complex to Complex.

    Care is taken to preserve integer-ness of the
    real and imaginary parts.
    """
    convert_fn = Integer if isinstance(arg.real, int) else Real
    real_value = convert_fn(arg.real)
    convert_fn = Integer if isinstance(arg.imag, int) else Real
    imag_value = convert_fn(arg.imag)
    return Complex(real_value, imag_value)


@dataclass(frozen=True)
class ToPythonOptions:
    """
    Stores options associated with the to_python[] builtin.

    One initialized, this structure is immutable or frozen.
    """

    use_associations: Optional[bool] = None
    """'True" if ordering should be lowercase first, 'False" if should uppercase first,
      and 'None' if we should use the natural alphabet ordering case."""

    @classmethod
    def from_dict(cls, options: dict[str, Any]) -> "ToPythonOptions":
        """Factory method that normalizes, type-checks, and builds the frozen structure
        from a raw dict[str, str].
        """

        # This will hold our cleaned, type-converted parameters
        processed_args: dict[str, Any] = {
            "use_associations": False,
        }

        # Iterate through the user-provided options dictionary
        for key, option_value in options.items():

            if not key:
                raise TypeError(f"ToPythonOptions: bad key: {key}")

            # Type parsing and validation based on the target field name
            processed_args[key] = option_value

        # Initialize and return the frozen dataclass using our verified arguments
        return cls(**processed_args)


DEFAULT_PYTHON_OPTIONS: Final[ToPythonOptions] = ToPythonOptions.from_dict(
    {"use_associations": False}
)

# Historically, from_python() was identified as a bottleneck.

# A large part of this was due to the inefficient monolithic
# non-specialized interpreter that forced everything into an single
# Expression class which tried to handle anything given it using
# conversions.

# Also, through vague or lazy coding this cause a lot of
# unnecessary conversions.

# We may be out of those days, but we should still
# be mindful that this routine can be the source
# of a bottleneck. So care may be warranted to make
# sure from_python() isn't too slow.

# TODO:
#  I think there are number of subtleties to be explained here.
#  In particular, the expression might been the result of evaluation
#  a SymPy expression which contains SymPy symbols.
#
#  If the end result is to go back into Mathics3 for further
#  evaluation, then probably no problem.  However if the end result
#  is produce say a Python string, then at a minimum we may want to
#  convert backtick (context) symbols into some Python identifier
#  symbol like underscore.


def from_python(arg: Any, options=DEFAULT_PYTHON_OPTIONS) -> BaseElement:
    """Converts a Python expression into a Mathics3 expression."""
    from mathics.core.convert.expression import to_mathics_list
    from mathics.core.expression import Expression
    from mathics.core.list import ListExpression

    if isinstance(arg, BaseElement):
        return arg

    number_type = get_type(arg)

    # We should investigate whether this could be sped up
    # using a dictionary lookup on type.
    if arg is None:
        return SymbolNull
    if isinstance(arg, bool):
        return from_bool(arg)
    if isinstance(arg, int) or number_type == "z":
        return Integer(arg)
    elif isinstance(arg, float) or number_type == "f":
        return Real(arg)
    elif number_type == "q":
        return Rational(arg)
    elif isinstance(arg, complex) or number_type == "c":
        return from_complex(arg)
    elif isinstance(arg, str):
        return String(arg)
        # if arg[0] == arg[-1] == '"':
        #     return String(arg[1:-1])
        # else:
        #     return Symbol(arg)
    elif isinstance(arg, dict):
        if options.use_associations:
            return association_from_dict(arg, options)
        entries = [
            Expression(
                SymbolRule,
                from_python(key),
                from_python(value),
            )
            for key, value in arg.items()
        ]
        return ListExpression(*entries)
    elif isinstance(arg, list) or isinstance(arg, tuple):
        return to_mathics_list(*arg, elements_conversion_fn=from_python)
    elif isinstance(arg, bytearray) or isinstance(arg, bytes):
        return ByteArray(arg)
    elif isinstance(arg, numpy.ndarray):
        return NumericArray(arg)
    else:
        raise NotImplementedError


def association_from_dict(arg: dict, options: ToPythonOptions) -> BaseElement:
    from mathics.core.expression import Expression

    entries = [
        Expression(
            SymbolRule,
            from_python(key, options),
            from_python(value, options),
        )
        for key, value in arg.items()
    ]
    return Expression(SymbolAssociation, *entries)
