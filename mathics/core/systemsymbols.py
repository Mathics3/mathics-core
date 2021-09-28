# cython: language_level=3
# -*- coding: utf-8 -*-

from mathics.core.symbols import (
    Symbol,
    SymbolList,
    SymbolMakeBoxes,
    SymbolTrue,
    SymbolFalse,
    SymbolN,
    SymbolNull,
)

# Some other common Symbols. This list is sorted in alpabetic order.
SymbolAborted = Symbol("$Aborted")
SymbolAssociation = Symbol("Association")
SymbolByteArray = Symbol("ByteArray")
SymbolCatalan = Symbol("Catalan")
SymbolComplexInfinity = Symbol("ComplexInfinity")
SymbolDirectedInfinity = Symbol("DirectedInfinity")
SymbolE = Symbol("E")
SymbolEulerGamma = Symbol("EulerGamma")
SymbolFailed = Symbol("$Failed")
SymbolGoldenRatio = Symbol("GoldenRatio")
SymbolGreater = Symbol("Greater")
SymbolInfinity = Symbol("Infinity")
SymbolLess = Symbol("Less")
SymbolMachinePrecision = Symbol("MachinePrecision")
SymbolNumberQ = Symbol("NumberQ")
SymbolNumericQ = Symbol("NumericQ")
SymbolPi = Symbol("Pi")
SymbolRule = Symbol("Rule")
SymbolSequence = Symbol("Sequence")
SymbolStringQ = Symbol("StringQ")
SymbolUndefined = Symbol("Undefined")
