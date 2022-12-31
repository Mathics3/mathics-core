# -*- coding: utf-8 -*-
from mathics.system_info import mathics_system_info

from .helper import session


def test_system_info():
    info = mathics_system_info(session.definitions)

    from pprint import pprint

    pprint(info)

    expected_keys = set(
        [
            "$BaseDirectory",
            "$HomeDirectory",
            "$InstallationDirectory",
            "$Machine",
            "$MachineName",
            "$ProcessID",
            "$ProcessorType",
            "$PythonImplementation",
            "$RootDirectory",
            "$SystemID",
            "$SystemMemory",
            "$SystemTimeZone",
            "$TemporaryDirectory",
            "$UserName",
            "MachinePrecision",
            "MemoryAvailable[]",
        ]
    )
    assert set(info.keys()) == expected_keys
