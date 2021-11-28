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
Nothing         = 0b0000000000000000 #  it is used when there're no attributes

Locked          = 0b0000000000000001
Protected       = 0b0000000000000010
ReadProtected   = 0b0000000000000100

Constant        = 0b0000000000001000
Flat            = 0b0000000000010000
Listable        = 0b0000000000100000
NumericFunction = 0b0000000001000000
OneIdentity     = 0b0000000010000000
Orderless       = 0b0000000100000000

HoldFirst       = 0b0000001000000000
HoldRest        = 0b0000010000000000
HoldAll         = 0b0000100000000000
HoldAllComplete = 0b0001100000000000

NHoldFirst      = 0b0010000000000000
NHoldRest       = 0b0100000000000000
NHoldAll        = 0b1000000000000000

SequenceHold    = 0b10000000000000000
# fmt: on

attributes_dict = {
    Constant: "Constant",
    Flat: "Flat",
    HoldAll: "HoldAll",
    HoldAllComplete: "HoldAllComplete",
    HoldFirst: "HoldFirst",
    HoldRest: "HoldRest",
    Listable: "Listable",
    Locked: "Locked",
    NHoldAll: "NHoldAll",
    NHoldFirst: "NHoldFirst",
    NHoldRest: "NHoldRest",
    NumericFunction: "NumericFunction",
    OneIdentity: "OneIdentity",
    Orderless: "Orderless",
    Protected: "Protected",
    ReadProtected: "ReadProtected",
    SequenceHold: "SequenceHold",
}
