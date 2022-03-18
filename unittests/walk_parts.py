from timeit import default_timer as timer

from mathics.session import MathicsSession
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, Atom
from mathics.core.atoms import Integer
from mathics.core.symbols import SymbolList
from mathics.core.systemsymbols import SymbolAll

session = MathicsSession(add_builtin=False)

from mathics.algorithm.parts import walk_parts
from numpy.random import randint


global_idx = 0


def time_with_units(enlapsed):
    unit = "s"
    if enlapsed < 0:
        return "~ 0ns"
    if enlapsed < 1:
        enlapsed = enlapsed * 1000
        unit = "ms"
    if enlapsed < 1:
        enlapsed = enlapsed * 1000
        unit = "us"
    if enlapsed < 1:
        enlapsed = enlapsed * 1000
        unit = "ns"
    enlapsed = float(int(enlapsed * 1000)) / 1000.0
    return f"{enlapsed}{unit}"


def build_basic_list(n):
    global global_idx
    old_global_idx = global_idx
    global_idx = global_idx + n
    return Expression(
        SymbolList, *[Integer(k) for k in range(old_global_idx, global_idx)]
    )


def build_deep_list(deep, n):
    if deep == 1:
        return build_basic_list(n)

    return Expression(SymbolList, *[build_deep_list(deep - 1, n) for k in range(0, n)])


deep_array = build_deep_list(5, 6)
shallow_array = build_deep_list(1, 60)


def test_deep_copy():
    global global_idx, deep_array
    test1 = deep_array.copy()
    return


def test_shallow_copy():
    global global_idx, shallow_array
    test1 = shallow_array.copy()
    return


def test_assign_deep_element():
    global global_idx, deep_array
    test1 = deep_array.copy()
    global_idx += 1
    walk_parts(
        [test1],
        [Integer(1), Integer(3), Integer(2), Integer(1), Integer(2)],
        session.evaluation,
        Integer(global_idx),
    )


def test_assign_shallow_element():
    global global_idx, shallow_array
    test1 = shallow_array.copy()
    global_idx += 1
    walk_parts([test1], [Integer(37)], session.evaluation, Integer(global_idx))


def test_access_deep_element():
    global global_idx, deep_array
    test1 = deep_array.copy()
    res = walk_parts(
        [test1],
        [Integer(1), Integer(3), Integer(2), Integer(1), Integer(2)],
        session.evaluation,
        None,
    )


def test_access_shallow_element():
    global global_idx, shallow_array
    test1 = shallow_array.copy()
    walk_parts([test1], [Integer(37)], session.evaluation, None)


def test_access_block_element():
    global global_idx, deep_array
    test1 = deep_array.copy()
    global_idx += 1
    return walk_parts(
        [test1],
        [
            Integer(1),
            Expression("System`Span", Integer(1), Integer(3), Integer(2)),
            SymbolAll,
            Integer(2),
            Integer(1),
        ],
        session.evaluation,
        None,
    )


def test_update_block_element():
    global global_idx, deep_array
    test1 = deep_array.copy()
    global_idx += 1
    return walk_parts(
        [test1],
        [
            Integer(1),
            Expression("System`Span", Integer(1), Integer(3), Integer(2)),
            SymbolAll,
            Integer(2),
            Integer(1),
        ],
        session.evaluation,
        Integer(global_idx),
    )


start_time = timer()
for i in range(1000):
    test_shallow_copy()
shallow_copy_time = (timer() - start_time) / 1000.0
print(
    "time to copy the shallow expression example:", time_with_units(shallow_copy_time)
)


start_time = timer()
for i in range(100):
    test_deep_copy()
deep_copy_time = (timer() - start_time) / 100.0
print("time to copy the deep expression example:", time_with_units(deep_copy_time))


start_time = timer()
for i in range(1000):
    test_assign_shallow_element()
enlapsed = (timer() - start_time - shallow_copy_time) / 1000.0
print("time to assign to the shallow expression example:", time_with_units(enlapsed))


start_time = timer()
for i in range(100):
    test_assign_deep_element()
enlapsed = (timer() - start_time - deep_copy_time) / 100.0
print("time to assign to the deep expression example:", time_with_units(enlapsed))


start_time = timer()
for i in range(1000):
    test_access_shallow_element()
enlapsed = (timer() - start_time - shallow_copy_time) / 1000.0
print("time to access the shallow expression example:", time_with_units(enlapsed))


start_time = timer()
for i in range(100):
    test_access_deep_element()
enlapsed = (timer() - start_time - deep_copy_time) / 100.0
print("time to access the deep expression example:", time_with_units(enlapsed))


start_time = timer()
for i in range(100):
    test_access_block_element()
enlapsed = (timer() - start_time - deep_copy_time) / 100.0
print(
    "time to access block from the deep expression example:", time_with_units(enlapsed)
)


start_time = timer()
for i in range(100):
    test_update_block_element()
enlapsed = (timer() - start_time - deep_copy_time) / 100.0
print(
    "time to update block from the deep expression example:", time_with_units(enlapsed)
)
