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


def show_lru_cache_statistics():
    """
    Print statistics from LRU caches (@lru_cache of functools)
    """
    from mathics.builtin.atomic.numbers import log_n_b
    from mathics.core.atoms import Integer, Rational
    from mathics.core.builtin import MPMathFunction, run_sympy
    from mathics.core.convert.mpmath import from_mpmath
    from mathics.eval.arithmetic import call_mpmath

    print(f"Integer             {len(Integer._integers)}")
    print(f"Rational            {len(Rational._rationals)}")
    print(f"call_mpmath         {call_mpmath.cache_info()}")
    print(f"log_n_b             {log_n_b.cache_info()}")
    print(f"from_mpmath         {from_mpmath.cache_info()}")
    print(f"get_mpmath_function {MPMathFunction.get_mpmath_function.cache_info()}")

    print(f"run_sympy           {run_sympy.cache_info()}")
