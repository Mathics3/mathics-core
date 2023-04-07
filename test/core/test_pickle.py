import io
import pickle

import pytest

from mathics.builtin.box.graphics import GraphicsBox
from mathics.core.atoms import Integer, MachineReal, PrecisionReal, String
from mathics.core.expression import Expression
from mathics.core.symbols import Atom, Symbol, strip_context
from mathics.core.systemsymbols import SymbolGet

test_elements = {
    "Symbol": Symbol("System`A"),
    "Expression": Expression(Symbol("Global`F"), Symbol("Global`x")),
    "NestedExpression": Expression(
        Symbol("Global`F"), Expression(Symbol("Global`F"), Symbol("Global`x"))
    ),
    "Integer": Integer(37),
    "String": String("hello world"),
    "MachineReal": MachineReal("3.2"),
    "PrecisionReal": PrecisionReal("3.2"),
    "GraphicsBox": GraphicsBox(),
}


def test_pickle_elements():
    for key, val in test_elements.items():
        print(key)
        file_dump = io.BytesIO(b"")
        pickle.dump(val, file_dump)
        file_load = io.BytesIO(file_dump.getvalue())
        load_val = pickle.load(file_load)
        assert val.sameQ(load_val)
