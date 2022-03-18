# -*- coding: utf-8 -*-

# The builtin's attributes are stored in a bit set.
# Each bit represets a attribute, if that is 0, the builtin doesn't has the
# property, if that is 1, the builtin has the property.

# The Builtin class has the property Protected by default, but if you overrides
# the attributes you need to add Protected if the builtin is not Unprotected
# (the most of the cases).

# To check if a builtin has an attribute, you do:
# ATTRIBUTE_NAME & attributes
# To set all the attributes of a builtin you do:
# attributes = ATTRIBUTE1 | ATTRIBUTE2 | ATTRIBUTE3 | ...
# To add an attribute to a builtin you do:
# attributes = ATTRIBUTE_NAME | attributes
# To remove an attribute you do:
# attributes = ~ATTRIBUTE_NAME & attributes

from typing import Dict, List
from mathics.core.symbols import Symbol


# fmt: off
no_attributes     = 0b0000000000000000

# alphabetical order
constant          = 0b00000000000000001
flat              = 0b00000000000000010
hold_all          = 0b00000000000000100
hold_all_complete = 0b00000000000001000
hold_first        = 0b00000000000010000
hold_rest         = 0b00000000000100000
listable          = 0b00000000001000000
locked            = 0b00000000010000000
n_hold_all        = 0b00000000100000000
n_hold_first      = 0b00000001000000000
n_hold_rest       = 0b00000010000000000
numeric_function  = 0b00000100000000000
one_identity      = 0b00001000000000000
orderless         = 0b00010000000000000
protected         = 0b00100000000000000
read_protected    = 0b01000000000000000
sequence_hold     = 0b10000000000000000
# fmt: on

attribute_number_to_symbol: Dict[int, Symbol] = {
    constant: Symbol("System`Constant"),
    flat: Symbol("System`Flat"),
    hold_all: Symbol("System`HoldAll"),
    hold_all_complete: Symbol("System`HoldAllComplete"),
    hold_first: Symbol("System`HoldFirst"),
    hold_rest: Symbol("System`HoldRest"),
    listable: Symbol("System`Listable"),
    locked: Symbol("System`Locked"),
    n_hold_all: Symbol("System`NHoldAll"),
    n_hold_first: Symbol("System`NHoldFirst"),
    n_hold_rest: Symbol("System`NHoldRest"),
    numeric_function: Symbol("System`NumericFunction"),
    one_identity: Symbol("System`OneIdentity"),
    orderless: Symbol("System`Orderless"),
    protected: Symbol("System`Protected"),
    read_protected: Symbol("System`ReadProtected"),
    sequence_hold: Symbol("System`SequenceHold"),
}

attribute_string_to_number: Dict[str, int] = {
    "System`Constant": constant,
    "System`Flat": flat,
    "System`HoldAll": hold_all,
    "System`HoldAllComplete": hold_all_complete,
    "System`HoldFirst": hold_first,
    "System`HoldRest": hold_rest,
    "System`Listable": listable,
    "System`Locked": locked,
    "System`NHoldAll": n_hold_all,
    "System`NHoldFirst": n_hold_first,
    "System`NHoldRest": n_hold_rest,
    "System`NumericFunction": numeric_function,
    "System`OneIdentity": one_identity,
    "System`Orderless": orderless,
    "System`Protected": protected,
    "System`ReadProtected": read_protected,
    "System`SequenceHold": sequence_hold,
}


def attributes_bitset_to_list(attributes_bitset: int) -> List[int]:
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
