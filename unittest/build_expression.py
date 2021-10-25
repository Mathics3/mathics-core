from timeit import default_timer as timer
from mathics.core.symbols import Symbol
from mathics.core.atoms import Integer
from mathics.core.expression import Expression
from numpy.random import randint


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


def mytimeit(func):
    nsteps = 1
    start = timer()
    func()
    enlapsed = timer() - start
    if enlapsed < 1e-3:
        nsteps = 1000
    elif enlapsed < 1:
        nsteps = 10
    else:
        nsteps = 3

    start = timer()
    for r in range(nsteps):
        func()
    enlapsed = timer() - start
    enlapsed = enlapsed / nsteps
    return time_with_units(enlapsed)


print("build a list of 1000 random `int`s")
print(mytimeit(lambda: ([x for x in randint(0, 100000, 1000)])))

print("build a list of 1000 random `Integer`s")
print(mytimeit(lambda: [Integer(x) for x in randint(0, 100000, 1000)]))

print("build a Symbol labeled by random integers")
print(mytimeit(lambda: Symbol("System`try" + str(randint(0, 100000)))))


print(
    "build an `Expressions` with random heads using random strings as the head parameter:"
)
print(mytimeit(lambda: Expression("System`tryheadstring" + str(randint(0, 100000)))))

print(
    "build an `Expressions` with random heads using a fixed string as the head parameter:"
)
print(mytimeit(lambda: Expression("System`tryheadstringfix")))

symbolhead = Symbol("System`myhead")
print(
    "build an `Expressions` with random heads using a fixed Symbol as the head parameter:"
)
print(mytimeit(lambda: Expression(symbolhead)))


symbolhead = Symbol("System`myhead")
print(
    "build an `Expressions` with random heads using a fixed Symbol as the head parameter and 10 leaves:"
)
print(
    mytimeit(
        lambda: Expression(symbolhead, *(Integer(x) for x in randint(0, 100000, 10)))
    )
)

symbolhead = Symbol("System`myhead")
print(
    "build an `Expressions` with random heads using a fixed Symbol as the head parameter and 1000 leaves:"
)
print(
    mytimeit(
        lambda: Expression(symbolhead, *(Integer(x) for x in randint(0, 100000, 1000)))
    )
)
