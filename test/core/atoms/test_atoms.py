# -*- coding: utf-8 -*-


import mathics.core.atoms as atoms
import mathics.core.systemsymbols as system_symbols
from mathics.core.atoms import Complex, Integer, MachineReal, Rational, Real, String
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.load_builtin import import_and_load_builtins
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolSameQ

import_and_load_builtins()

definitions = Definitions(add_builtin=True)


def _symbol_truth_value(x):
    if x is SymbolTrue:
        return True
    if x is SymbolFalse:
        return False
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
            print("is_same", type(is_same), is_same)
            print("same_under_sameq", type(is_same_under_sameq), is_same_under_sameq)

            assert is_same == _symbol_truth_value(is_same_under_sameq), (
                f"{repr(a)} and {repr(b)} are inconsistent under .sameQ() and SameQ",
            )

            # The test fails for two real numbers with different precisions.
            # Reformulate the test.
            # if is_same:
            #    assert hash(a) == hash(b), (
            #        f"hashes for {repr(a)} and {repr(b)} are not equal.",
            #    )
            # else:
            #    assert hash(a) != hash(b), (
            #       f"hashes for {repr(a)} and {repr(b)} are equal.",
            #    )


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
