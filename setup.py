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

To get a full list of avaiable commands, read the output of:

    python setup.py --help-commands

"""

import os
import os.path as osp
import platform
import re
import sys

from setuptools import Extension, setup

is_PyPy = platform.python_implementation() == "PyPy" or hasattr(
    sys, "pypy_version_info"
)

def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


DEPENDENCY_LINKS = []
#     "http://github.com/Mathics3/mathics-scanner/tarball/master#egg=Mathics_Scanner-1.0.0.dev"
# ]

# What should be run through Cython?
EXTENSIONS = []
CMDCLASS = {}

try:
    if is_PyPy:
        raise ImportError
    from Cython.Distutils import build_ext
except ImportError:
    pass
else:
    if os.environ.get("USE_CYTHON", False):
        print("Running Cython over code base")
        EXTENSIONS_DICT = {
            "core": (
                "expression",
                "symbols",
                "number",
                "rules",
                "pattern",
            ),
            "builtin": ["arithmetic", "patterns", "graphics"],
            "eval": ("nevaluator", "makeboxes", "test"),
        }
        EXTENSIONS = [
            Extension(
                "mathics.%s.%s" % (parent, module),
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


setup(
    cmdclass=CMDCLASS,
    ext_modules=EXTENSIONS,
    packages=[
        "mathics",
        "mathics.algorithm",
        "mathics.compile",
        "mathics.core",
        "mathics.core.convert",
        "mathics.core.parser",
        "mathics.builtin",
        "mathics.builtin.arithfns",
        "mathics.builtin.assignments",
        "mathics.builtin.atomic",
        "mathics.builtin.binary",
        "mathics.builtin.box",
        "mathics.builtin.colors",
        "mathics.builtin.distance",
        "mathics.builtin.exp_structure",
        "mathics.builtin.drawing",
        "mathics.builtin.fileformats",
        "mathics.builtin.files_io",
        "mathics.builtin.forms",
        "mathics.builtin.functional",
        "mathics.builtin.image",
        "mathics.builtin.intfns",
        "mathics.builtin.list",
        "mathics.builtin.matrices",
        "mathics.builtin.numbers",
        "mathics.builtin.numpy_utils",
        "mathics.builtin.pymimesniffer",
        "mathics.builtin.pympler",
        "mathics.builtin.quantum_mechanics",
        "mathics.builtin.scipy_utils",
        "mathics.builtin.specialfns",
        "mathics.builtin.statistics",
        "mathics.builtin.string",
        "mathics.builtin.testing_expressions",
        "mathics.builtin.vectors",
        "mathics.eval",
        "mathics.doc",
        "mathics.format",
    ],
    dependency_links=DEPENDENCY_LINKS,
    package_data={
        "mathics": [
            "data/*.csv",
            "data/*.json",
            "data/*.yml",
            "data/*.yaml",
            "data/*.pcl",
            "data/ExampleData/*",
            "doc/xml/data",
            "doc/tex/data",
            "autoload/*.m",
            "autoload-cli/*.m",
            "autoload/formats/*/Import.m",
            "autoload/formats/*/Export.m",
            "packages/*/*.m",
            "packages/*/Kernel/init.m",
            "requirements-cython.txt",
            "requirements-full.txt",
        ],
        "mathics.doc": ["documentation/*.mdoc", "xml/data"],
        "mathics.builtin.pymimesniffer": ["mimetypes.xml"],
        "pymathics": ["doc/documentation/*.mdoc", "doc/xml/data"],
    },
    # don't pack Mathics in egg because of media files, etc.
    zip_safe=False,
)
