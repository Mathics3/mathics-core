#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Python Setuptools for Mathics core

For the easiest installation:

    pip install -e .

For full installation:

    pip install -e .[full]


This will install the library in the default location. For instructions on
how to customize the install procedure read the output of:

    python setup.py --help install

In addition, there are some other commands:

    python setup.py clean -> will clean all trash (*.pyc and stuff)

To get a full list of available commands, read the output of:

    python setup.py --help-commands

"""

import logging
import os
import os.path as osp
import platform
import sys
from typing import List

from setuptools import Extension, setup
from setuptools.command.build_py import build_py as setuptools_build_py

log = logging.getLogger(__name__)


is_PyPy = platform.python_implementation() == "PyPy" or hasattr(
    sys, "pypy_version_info"
)


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


DEPENDENCY_LINKS: List[str] = []
#     "http://github.com/Mathics3/mathics-scanner/tarball/master#egg=Mathics_Scanner-1.0.0.dev"
# ]

# What should be run through Cython?
EXTENSIONS = []
CMDCLASS = {}

try:
    if is_PyPy:
        raise ImportError
    from Cython.Distutils import build_ext  # type: ignore[import-not-found]
except ImportError:
    pass
else:
    if os.environ.get("USE_CYTHON", False):
        log.info("Running Cython over code base")
        EXTENSIONS_DICT = {
            "core": (
                "expression",
                "symbols",
                "number",
                "rules",
                "pattern",
            ),
            "builtin": [
                "arithmetic",
                "patterns/basic",
                "patterns/composite",
                "patterns/defaults",
                "patterns/restrictions",
                "patterns/rules",
                "graphics",
            ],
            "eval": ("nevaluator", "makeboxes", "test"),
        }
        EXTENSIONS = [
            Extension(
                f"mathics.{parent}.{module}".replace("/", "."),
                ["mathics/%s/%s.py" % (parent, module)],
            )
            for parent, modules in EXTENSIONS_DICT.items()
            for module in modules
        ]
        # EXTENSIONS_SUBDIR_DICT = {
        #     "builtin": [("numbers", "arithmetic"), ("numbers", "numeric"), ("drawing", "graphics")],
        # }
        # EXTENSIONS.append(
        #     Extension(
        #         "mathics.%s.%s.%s" % (parent, module[0], module[1]), ["mathics/%s/%s/%s.py" % (parent, module[0], module[1])]
        #     )
        #     for parent, modules in EXTENSIONS_SUBDIR_DICT.items()
        #     for module in modules
        # )
        CMDCLASS = {"build_ext": build_ext}


class build_py(setuptools_build_py):
    def run(self):
        if not os.path.exists("mathics/data/op-tables.json"):
            os.system(
                "mathics3-generate-json-table"
                " --field=ascii-operator-to-symbol"
                " --field=ascii-operator-to-unicode"
                " --field=ascii-operator-to-wl-unicode"
                " --field=operator-to-ascii"
                " --field=operator-to-unicode"
                " -o mathics/data/op-tables.json"
            )
        if not os.path.exists("mathics/data/operator-tables.json"):
            os.system(
                "mathics3-generate-operator-json-table" " -o operator-tables.json"
            )
        self.distribution.package_data["mathics"].append("data/op-tables.json")
        setuptools_build_py.run(self)


CMDCLASS["build_py"] = build_py


setup(
    cmdclass=CMDCLASS,
    ext_modules=EXTENSIONS,
    dependency_links=DEPENDENCY_LINKS,
    # don't pack Mathics in egg because of media files, etc.
    zip_safe=False,
)
