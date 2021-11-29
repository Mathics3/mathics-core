# -*- coding: utf-8 -*-

# The builtin's attributes are stored in a bit set.
# Each bit represets a attribute, if that is 0, the builtin doesn't has the
# property, if that is 1, the builtin has the property.

# The Builtin class has the property Protected by default, but if you overrides
# the attributes you need to add Protected if the builtin is not Unprotected
# (the most of the cases).

# In this file you will see that every attribute appears twice, in a variable
# declaration and in the attributes_dict dictionary, that variable is used to
# get the string from the attribute number and vice-versa.

# To check if a builtin has an attribute, you do:
# ATTRIBUTE_NAME & attributes
# To set all the attributes of a builtin you do:
# attributes = ATTRIBUTE1 | ATTRIBUTE2 | ATTRIBUTE3 | ...
# To add an attribute to a builtin you do:
# attributes = ATTRIBUTE_NAME | attributes
# To remove an attribute you do:
# attributes = ~ATTRIBUTE_NAME & attributes

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

attributes_dict = {
    constant: "Constant",
    flat: "Flat",
    hold_all: "HoldAll",
    hold_all_complete: "HoldAllComplete",
    hold_first: "HoldFirst",
    hold_rest: "HoldRest",
    listable: "Listable",
    locked: "Locked",
    n_hold_all: "NHoldAll",
    n_hold_first: "NHoldFirst",
    n_hold_rest: "NHoldRest",
    numeric_function: "NumericFunction",
    one_identity: "OneIdentity",
    orderless: "Orderless",
    protected: "Protected",
    read_protected: "ReadProtected",
    sequence_hold: "SequenceHold",
}
