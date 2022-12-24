# -*- coding: utf-8 -*-

import os
import platform
import sys

import mathics.builtin.atomic.numbers as numeric
import mathics.builtin.datentime as datentime
import mathics.builtin.files_io.filesystem as filesystem
import mathics.builtin.system as msystem
from mathics.core.evaluation import Evaluation


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
        "$SystemID": sys.platform,
        "$UserName": eval(msystem.UserName),
        "$SystemMemory": eval(msystem.SystemMemory),
        "MemoryAvailable[]": eval(msystem.MemoryAvailable, needs_head=False),
        "$SystemTimeZone": eval(datentime.SystemTimeZone),
        "MachinePrecision": eval(numeric.MachinePrecision_),
        "$BaseDirectory": eval(filesystem.BaseDirectory_),
        "$RootDirectory": eval(filesystem.RootDirectory),
        "$SystemID": sys.platform,
        "$SystemMemory": eval(msystem.SystemMemory),
        "$SystemTimeZone": eval(datentime.SystemTimeZone),
        "$TemporaryDirectory": eval(filesystem.TemporaryDirectory),
        "$UserName": eval(msystem.UserName),
        "MachinePrecision": eval(numeric.MachinePrecision_),
        "MemoryAvailable[]": eval(msystem.MemoryAvailable, needs_head=False),
    }
