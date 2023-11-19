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

INSTALL_REQUIRES = [
    "Mathics-Scanner >= 1.3.0",
    "scikit-image >= 0.17", # FindMinimum can use this; used by Image as well
    # Pillow 9.1.0 supports BigTIFF with big-endian byte order.
    # ExampleData image hedy.tif is in this format.
    # Pillow 9.2 handles sunflowers.jpg
]

# Ensure user has the correct Python version
# Address specific package dependencies based on Python version
if sys.version_info < (3, 6):
    print("Mathics does not support Python %d.%d" % sys.version_info[:2])
    sys.exit(-1)
elif sys.version_info[:2] == (3, 6):
    INSTALL_REQUIRES += [
        "recordclass",
        "numpy",
        "llvmlite<0.37",
        "pillow >= 8.4.0",
        "sympy>=1.8",
    ]
    if is_PyPy:
        print("Mathics does not support PyPy Python 3.6" % sys.version_info[:2])
        sys.exit(-1)
else:
    INSTALL_REQUIRES += [
        "numpy<1.25",
        "llvmlite",
        "sympy>=1.8",
        "pillow >= 9.2",
    ]

# if not is_PyPy:
#     INSTALL_REQUIRES += ["recordclass"]


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


def read(*rnames):
    return open(osp.join(get_srcdir(), *rnames)).read()


long_description = read("README.rst") + "\n"

# stores __version__ in the current namespace
exec(compile(open("mathics/version.py").read(), "mathics/version.py", "exec"))

EXTRAS_REQUIRE = {}
for kind in ("dev", "full", "cython"):
    extras_require = []
    requirements_file = f"requirements-{kind}.txt"
    for line in open(requirements_file).read().split("\n"):
        if line and not line.startswith("#"):
            requires = re.sub(r"([^#]+)(\s*#.*$)?", r"\1", line)
            extras_require.append(requires)
    EXTRAS_REQUIRE[kind] = extras_require

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
        INSTALL_REQUIRES += ["cython>=0.15.1"]

# General Requirements
INSTALL_REQUIRES += [
    "mpmath>=1.2.0",
    "palettable",
    "pint",
    "python-dateutil",
    "requests",
    "setuptools",
]

print(f'Installation requires "{", ".join(INSTALL_REQUIRES)}')


def subdirs(root, file="*.*", depth=10):
    for k in range(depth):
        yield root + "*/" * k + file


setup(
    name="Mathics3",
    cmdclass=CMDCLASS,
    ext_modules=EXTENSIONS,
    version=__version__,
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
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
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
    entry_points={
        "console_scripts": [
            "mathics = mathics.main:main",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # don't pack Mathics in egg because of media files, etc.
    zip_safe=False,
    # metadata for upload to PyPI
    maintainer="Mathics Group",
    maintainer_email="mathics-devel@googlegroups.com",
    description="A general-purpose computer algebra system.",
    license="GPL",
    url="https://mathics.org/",
    download_url="https://github.com/Mathics3/mathics-core/releases",
    keywords=["Mathematica", "Wolfram", "Interpreter", "Shell", "Math", "CAS"],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Interpreters",
    ],
    # TODO: could also include long_description, download_url,
)
