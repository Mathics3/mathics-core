# -*- coding: utf-8 -*-

# The builtin's attributes are stored in a bit set.
# Each bit represets a attribute, if that is 0, the builtin doesn't has the
# property, if that is 1, the builtin has the property.

# The Builtin class has the property Protected by default, but if you overrides
# the attributes you need to add Protected if the builtin is not Unprotected
# (the most of the cases).

# To check if a builtin has an attribute, you do:
#   ATTRIBUTE_NAME & attributes
#
# To set all the attributes of a builtin you do:
#   attributes = ATTRIBUTE1 | ATTRIBUTE2 | ATTRIBUTE3 | ...
#
# To add an attribute to a builtin you do:
#   attributes = ATTRIBUTE_NAME | attributes
#
# To remove an attribute you do:
#   attributes = ~ATTRIBUTE_NAME & attributes

from typing import Dict, Generator

# fmt: off
A_NO_ATTRIBUTES     = 0b0000000000000000

# Symbol is a constant.
A_CONSTANT          = 0b00000000000000001

# Nested occurrences of a function should be automatically flattened.
A_FLAT              = 0b00000000000000010

# All arguments of a function should be left unevaluated.
A_HOLD_ALL          = 0b00000000000000100

# Includes the effects of 'HoldAll' and 'SequenceHold', and also
# protects the function from being affected by the upvalues of any
# arguments.
A_HOLD_ALL_COMPLETE = 0b00000000000001000

# First argument of a function should be left unevaluated.
A_HOLD_FIRST        = 0b00000000000010000

# All but the first argument of a function should be left unevaluated.
A_HOLD_REST         = 0b00000000000100000

# Function should be automatically applied to each element of a list.
A_LISTABLE          = 0b00000000001000000

# prevents attributes on a symbol from being modified.
A_LOCKED            = 0b00000000010000000

# Protects all arguments of a function from numeric evaluation
A_N_HOLD_ALL        = 0b00000000100000000

# Protects the first argument of a function from numeric evaluation.
A_N_HOLD_FIRST      = 0b00000001000000000

# Protects all but the first argument of a function from numeric evaluation.
A_N_HOLD_REST       = 0b00000010000000000

# Symbol is the head of a numeric function.
A_NUMERIC_FUNCTION  = 0b00000100000000000

# '$f$[$x$]' should be treated as equivalent to $x$ in pattern matching.
A_ONE_IDENTITY      = 0b00001000000000000

# elements should automatically be sorted into canonical order
A_ORDERLESS         = 0b00010000000000000

# Prevents values on a symbol from being modified.
A_PROTECTED         = 0b00100000000000000

# Prevents values on a symbol from being read.
A_READ_PROTECTED    = 0b01000000000000000

# prevents 'Sequence' objects from being spliced into a function's arguments
A_SEQUENCE_HOLD     = 0b10000000000000000

attribute_number_to_string: Dict[int, str] = {
    A_CONSTANT:           "System`Constant",
    A_FLAT:               "System`Flat",
    A_HOLD_ALL:           "System`HoldAll",
    A_HOLD_ALL_COMPLETE:  "System`HoldAllComplete",
    A_HOLD_FIRST:         "System`HoldFirst",
    A_HOLD_REST:          "System`HoldRest",
    A_LISTABLE:           "System`Listable",
    A_LOCKED:             "System`Locked",
    A_N_HOLD_ALL:         "System`NHoldAll",
    A_N_HOLD_FIRST:       "System`NHoldFirst",
    A_N_HOLD_REST:        "System`NHoldRest",
    A_NUMERIC_FUNCTION:   "System`NumericFunction",
    A_ONE_IDENTITY:       "System`OneIdentity",
    A_ORDERLESS:          "System`Orderless",
    A_PROTECTED:          "System`Protected",
    A_READ_PROTECTED:     "System`ReadProtected",
    A_SEQUENCE_HOLD:      "System`SequenceHold",
}
# fmt: on

attribute_string_to_number: Dict[str, int] = {
    v: k for k, v in attribute_number_to_string.items()
}


def attributes_bitset_to_list(attributes_bitset: int) -> Generator[str, None, None]:
    bit = 1

    while attributes_bitset >= bit:
        # Bitwise AND.
        # e.g.: 0b1000101 & 0b0000100 = 0b0000100
        # e.g.: 0b0100110 & 0b0011000 = 0b0000000
        if attributes_bitset & bit:
            # Convert the attribute to a string.
            yield attribute_number_to_string[attributes_bitset & bit]

        # Go to the next attribute by doubling "bit".
        # e.g.: 0b010 (2) -> 0b100 (4)
        bit <<= 1
