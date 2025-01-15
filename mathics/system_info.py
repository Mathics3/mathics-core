# -*- coding: utf-8 -*-
"""
Mathics3 System Information that front-ends can use to show as
configuration information.

Some of these we get from mathics.settings and are configurable
via Environment Variables.
"""

import os
import platform
import sys

import mathics.builtin.atomic.numbers as numeric
import mathics.builtin.datentime as datentime
import mathics.builtin.directories.system_directories as system_directories
import mathics.builtin.directories.user_directories as user_directories
import mathics.builtin.system as msystem
from mathics.core.evaluation import Evaluation
from mathics.settings import MAX_STR_DIGITS, SYSTEM_CHARACTER_ENCODING, TIME_12HOUR


# Largest number of digits Python allows in a string.
def python_implementation() -> str:
    """
    Returns the Python implementation, e.g Pyston, PyPy, CPython...
    """
    if hasattr(sys, "pyston_version_info"):
        custom_version_info = sys.pyston_version_info
        python_implementation = "Pyston"
    elif hasattr(sys, "pypy_version_info"):
        custom_version_info = sys.pypy_version_info
        python_implementation = "PyPy"
    else:
        custom_version_info = sys.version_info
        python_implementation = platform.python_implementation()
    return f"{python_implementation} {'.'.join((str(i) for i in custom_version_info))}"


def mathics_system_info(defs):
    def eval(name, needs_head=True):
        evaled = name().evaluate(evaluation)
        if needs_head:
            return evaled.head.to_python(string_quotes=False)
        else:
            return evaled.to_python(string_quotes=False)

    evaluation = Evaluation(defs, output=None)
    return {
        "$BaseDirectory": eval(system_directories.BaseDirectory_),
        "$HomeDirectory": eval(user_directories.HomeDirectory),
        "$InstallationDirectory": eval(system_directories.InstallationDirectory),
        "$Machine": sys.platform,
        "$MachineName": platform.uname().node,
        "$ProcessID": os.getppid(),
        "$ProcessorType": platform.machine(),
        "$PythonImplementation": python_implementation(),
        "$RootDirectory": eval(system_directories.RootDirectory),
        "$SystemID": sys.platform,
        "$SystemMemory": eval(msystem.SystemMemory),
        "$SystemTimeZone": eval(datentime.SystemTimeZone),
        "$TemporaryDirectory": eval(system_directories.TemporaryDirectory),
        "$UserName": eval(msystem.UserName),
        "MachinePrecision": eval(numeric.MachinePrecision_),
        "MaximumDigitsInString": MAX_STR_DIGITS,
        "MemoryAvailable[]": eval(msystem.MemoryAvailable, needs_head=False),
        "SystemCharacterEncoding": SYSTEM_CHARACTER_ENCODING,
        "Time12Hour": TIME_12HOUR,
    }
