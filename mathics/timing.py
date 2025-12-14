# -*- coding: utf-8 -*-
"""
Mathics timing method(s) and timing context manager.
"""

import os
import time

MIN_ELAPSE_REPORT = int(os.environ.get("MIN_ELAPSE_REPORT", "0"))


# A small, simple timing tool
def timeit(method):
    """Add this as a decorator to time parts of the code.

    For example:
        @timeit
        def long_running_function():
            ...
    """

    def timed(*args, **kw):
        method_name = method.__name__
        # print(f"{date.today()}	{method_name} starts")
        t_start = time.time()
        result = method(*args, **kw)
        t_end = time.time()
        elapsed = (t_end - t_start) * 1000
        if elapsed > MIN_ELAPSE_REPORT:
            if "log_time" in kw:
                name = kw.get("log_name", method.__name__.upper())
                kw["log_time"][name] = elapsed
            else:
                print("%r  %2.2f ms" % (method_name, elapsed))
        # print(f"{date.today()}	{method_name} ends")
        return result

    return timed


class TimeitContextManager:
    """Add this as a context manager to time parts of the code.

    For example:
        with TimeitContextManager("testing my loop"):
           for x in collection:
               ...
    """

    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        # print(f"{date.today()}	{method_name} starts")
        self.t_start = time.time()

    def __exit__(self, exc_type, exc_value, exc_tb):
        t_end = time.time()
        elapsed = (t_end - self.t_start) * 1000
        if elapsed > MIN_ELAPSE_REPORT:
            print("%r  %2.2f ms" % (self.name, elapsed))


class Timer:
    """
    Times a block of code. May be used as a decorator or as a context manager:

        # decorator
        @Timer(name):
        def f(...):
            ...

        # context manager
        with Timer(name):
            ...

    Timings are nested (in execution order), and the output prints the nested
    timings as an "upside-down" indented outline, with an outer level printed after
    all nested inner levels, supporting both detailed and summary timings.

    Timing.level controls how deeply nested timings are displayed:
    -1 all, 0 none, 1 only top level, etc.  Default is 0. Use MATHICS3_TIMING
    environment variable to change.
    """

    level = int(os.getenv("MATHICS3_TIMING", "0"))
    timers: list = []

    def __init__(self, name):
        self.name = name

    def __call__(self, fun):
        def timed_fun(*args, **kwargs):
            with self:
                return fun(*args, **kwargs)

        return timed_fun

    @staticmethod
    def start(name):
        Timer.timers.append((name, time.time()))

    @staticmethod
    def stop():
        name, start = Timer.timers.pop()
        ms = (time.time() - start) * 1000
        if Timer.level < 0 or len(Timer.timers) < Timer.level:
            print(f"{'  '*len(Timer.timers)}{name}: {ms:.1f} ms")

    def __enter__(self):
        if self.name:
            Timer.start(self.name)

    def __exit__(self, *args):
        if self.name:
            Timer.stop()


def show_lru_cache_statistics():
    """
    Print statistics from LRU caches (@lru_cache of functools)
    """
    from mathics.builtin.atomic.numbers import log_n_b
    from mathics.core.atoms import Integer, Rational
    from mathics.core.builtin import MPMathFunction
    from mathics.core.convert.mpmath import from_mpmath
    from mathics.eval.arithmetic import run_mpmath

    print(f"Integer             {len(Integer._integers)}")
    print(f"Rational            {len(Rational._rationals)}")
    print(f"run_mpmath         {run_mpmath.cache_info()}")
    print(f"log_n_b             {log_n_b.cache_info()}")
    print(f"from_mpmath         {from_mpmath.cache_info()}")
    print(f"get_mpmath_function {MPMathFunction.get_mpmath_function.cache_info()}")
