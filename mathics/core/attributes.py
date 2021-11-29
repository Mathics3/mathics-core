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

from typing import Dict

# fmt: off
nothing           = 0b0000000000000000 #  it is used when there're no attributes

locked            = 0b0000000000000001
protected         = 0b0000000000000010
read_protected    = 0b0000000000000100

constant          = 0b0000000000001000
flat              = 0b0000000000010000
listable          = 0b0000000000100000
numeric_function  = 0b0000000001000000
one_identity      = 0b0000000010000000
orderless         = 0b0000000100000000

hold_first        = 0b0000001000000000
hold_rest         = 0b0000010000000000
hold_all          = 0b0000100000000000
hold_all_complete = 0b0001100000000000

n_hold_first      = 0b0010000000000000
n_hold_rest       = 0b0100000000000000
n_hold_all        = 0b1000000000000000

sequence_hold     = 0b10000000000000000
# fmt: on

attribute_number_to_string: Dict[int, str] = {
    constant: "System`Constant",
    flat: "System`Flat",
    hold_all: "System`HoldAll",
    hold_all_complete: "System`HoldAllComplete",
    hold_first: "System`HoldFirst",
    hold_rest: "System`HoldRest",
    listable: "System`Listable",
    locked: "System`Locked",
    n_hold_all: "System`NHoldAll",
    n_hold_first: "System`NHoldFirst",
    n_hold_rest: "System`NHoldRest",
    numeric_function: "System`NumericFunction",
    one_identity: "System`OneIdentity",
    orderless: "System`Orderless",
    protected: "System`Protected",
    read_protected: "System`ReadProtected",
    sequence_hold: "System`SequenceHold",
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
