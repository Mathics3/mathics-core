# -*- coding: utf-8 -*-


import sys

import mathics.core.atoms as atoms
import mathics.core.systemsymbols as system_symbols
from mathics.core.atoms import (
    Complex,
    Integer,
    Integer1,
    Integer2,
    MachineReal,
    MachineReal0,
    Rational,
    RationalOneHalf,
    Real,
    String,
)
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolSameQ

definitions = Definitions(add_builtin=True)


def _symbol_truth_value(x):
    if x is SymbolTrue:
        return True
    elif isinstance(x, Symbol) and x is SymbolFalse:
        return False
    else:
        return "undefined"


def check_group(*group):
    for i, a in enumerate(group):
        for j, b in enumerate(group):
            evaluation = Evaluation(definitions, catch_interrupt=False)
            try:
                is_same_under_sameq = Expression(SymbolSameQ, a, b).evaluate(evaluation)
            except Exception as exc:
                assert False, f"Exception {exc}"

            is_same = a.sameQ(b)
            assert (
                is_same != _symbol_truth_value(is_same_under_sameq),
                f"{repr(a)} and {repr(b)} are inconsistent under .sameQ() and SameQ",
            )

            assert (
                is_same and hash(a) != hash(b),
                f"hashes for {repr(a)} and {repr(b)} are not equal",
            )


seen_hashes = {}


def check_object_dissimilarity(*group):
    """Check that all objects in ``group`` are dissimilar.

    Specifically they should be different Python objects.
    This is tested using the Python object id() function and
    also using the Python ``is`` operator.

    Also, check that all objects __hash__() to the different numbers.
    """
    n = len(group)
    assert n > 0, "Test program is written incorrectly"

    for i, item in enumerate(group):
        j = i + 1
        while j < n:
            second_item = group[j]
            assert id(item) != id(second_item), f"i: {i}, j: {j}"
            assert item.hash != second_item.hash
            assert item is not second_item
            j += 1


def check_object_uniqueness(klass, args, *group):
    """Check that all objects in ``group`` are the same.

    Specifically they should be the same Python object.  This is is
    tested using the object id() function and also using the Python
    ``is`` operator.

    Also, check that all objects __hash__() to the same number

    """
    assert len(group) > 0, "Test program is written incorrectly"
    first_item = group[0]
    unique_id = id(first_item)

    # Test allocating a new object a 3 times
    for _ in range(3):
        new_object = klass(*args)
        assert id(new_object) == unique_id
        assert new_object is first_item

    # Now check __hash__() function or immutability
    # for using the object as a key in a dictionary, or set.

    # See that first object hasn't been seen;
    # Then add it and see that is now found for
    # all objects in the group.

    assert all((item not in seen_hashes for item in group))
    seen_hashes[first_item] = first_item

    # Now check that all of the remaining items are in
    # seen_items and are the same item.

    assert all((seen_hashes[item] is item for item in seen_hashes))


def test_Complex():
    def c(i, r):
        return Complex(MachineReal(i), MachineReal(i))

    check_group(c(1.2, 1.2), c(0.7, 1.8), c(1.8, 0.7), c(-0.7, 1.8), c(0.7, 1.81))


def test_Integer():
    check_group(Integer(5), Integer(3242), Integer(-1372))
    # Integer1 should be predefined; 1.0 is used since
    # we allow floats in the constructor.
    check_object_uniqueness(Integer, [1], Integer1, Integer(1), Integer(1.0))


def test_MachineReal():
    check_group(MachineReal(5), MachineReal(3.5), Integer(1.00001))
    # MachineReal0 should be predefined; `int` and float arguments are allowed
    # `int` arguemnts are converted to float.
    check_object_uniqueness(
        MachineReal, [0.0], MachineReal0, MachineReal(0), MachineReal(0.0)
    )


def test_Rational():
    check_group(
        Rational(1, 3),
        Rational(1, 3),
        Rational(2, 6),
        Rational(-1, 3),
        Rational(-10, 30),
        Rational(10, 5),
    )

    # RationalOneHalf should be predefined; We reduce ratios, so
    # Rationa(1, 2) is Rational(2, 4).
    check_object_uniqueness(
        Rational, [1, 2], RationalOneHalf, Rational(1, 2), Rational(2, 4)
    )


def test_Real():
    check_group(
        Real(1.17361),
        Real(-1.42),
        Real(42.846195714),
        Real(42.846195714),
        Real(42.846195713),
        Real("42.846195713", 18),
        Real("-1.42", 3),
    )


def test_String():
    check_group(String("xy"), String("x"), String("xyz"), String("abc"))


def test_Symbol():
    check_group(Symbol("xy"), Symbol("x"), Symbol("xyz"), Symbol("abc"))


def test_object_dissimilarity():
    """check that different objects type whether they have or different value are different"""

    # fmt: off
    check_object_dissimilarity(
        Complex(Integer(0), Integer(1)),  #  0
        Integer(1),                       #  1
        Integer(2),                       #  2
        MachineReal(1),                   #  3
        MachineReal(2),                   #  4
        MachineReal(5.12345678),          #  5
        Rational(1, 0),                   #  6
        Rational(2, 1),                   #  7
        Real(1.1),                        #  8
        Real(2.1),                        #  9
        String("1"),                      # 10
        String("I"),                      # 11
        Symbol("1"),                      # 12
        Symbol("I"),                      # 13
    )
    # fmt: on

    # See also test_mixed_object_similarity

    # Check that all pre-defined Integers, MachineReals, and Symbols are different.

    symbol_names = {
        key for key in system_symbols.__dict__.keys() if key.startswith("Symbol")
    }
    symbol_names.remove("Symbol")
    symbol_objects = {system_symbols.__dict__[name] for name in symbol_names}

    atom_names = {
        key
        for key in atoms.__dict__.keys()
        if key.startswith("Integer") or key.startswith("MachineReal")
    }
    atom_names = atom_names - set(("Integer", "MachineReal"))
    atom_objects = {atoms.__dict__[name] for name in atom_names}
    check_object_dissimilarity(*symbol_objects, *atom_objects)


def test_mixed_object_canonicalization():
    """check that objects of different types canonicalize to the same Python object"""
    # fmt: off
    check_object_uniqueness(
        Integer, [2],
        Integer2,                         # 0
        Integer(2),                       # 1
        Complex(Integer(2), Integer(0)),  # 2
    )

    # Divide by zero produces the same thing.
    check_object_uniqueness(
        Rational, [1, 0],
        Rational(1, 0),                      # 0
        Rational(1.1, 0),                    # 1
        Rational(2, 0),                      # 2
        Complex(Rational(1, 0), Integer(0)), # 3
    )
    # fmt: on
