# -*- coding: utf-8 -*-

import os
import platform
import sys

import mathics.builtin.atomic.numbers as numeric
import mathics.builtin.datentime as datentime
import mathics.builtin.files_io.filesystem as filesystem
import mathics.builtin.system as msystem
from mathics.core.evaluation import Evaluation


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
        "$BaseDirectory": eval(filesystem.BaseDirectory_),
        "$HomeDirectory": eval(filesystem.HomeDirectory),
        "$InstallationDirectory": eval(filesystem.InstallationDirectory),
        "$Machine": sys.platform,
        "$MachineName": platform.uname().node,
        "$ProcessID": os.getppid(),
        "$ProcessorType": platform.machine(),
        "$PythonImplementation": python_implementation(),
        "$RootDirectory": eval(filesystem.RootDirectory),
        "$SystemID": sys.platform,
        "$SystemMemory": eval(msystem.SystemMemory),
        "$SystemTimeZone": eval(datentime.SystemTimeZone),
        "$TemporaryDirectory": eval(filesystem.TemporaryDirectory),
        "$UserName": eval(msystem.UserName),
        "MachinePrecision": eval(numeric.MachinePrecision_),
        "MemoryAvailable[]": eval(msystem.MemoryAvailable, needs_head=False),
    }
