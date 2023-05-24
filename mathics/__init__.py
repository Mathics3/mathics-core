# -*- coding: utf-8 -*-

import platform
import sys
from importlib import import_module
from typing import Dict

import mpmath
import numpy
import sympy

from mathics.version import __version__

# version_info contains a list of Python packages
# and the versions infsalled or "Not installed"
# if the package is not installed and "No version information"
# if we can't get version infomation.
version_info: Dict[str, str] = {
    "mathics": __version__,
    "mpmath": mpmath.__version__,
    "numpy": numpy.__version__,
    "python": platform.python_implementation() + " " + sys.version.split("\n")[0],
    "sympy": sympy.__version__,
}


# optional_software contains a list of Python packages
# that add functionality but are optional
optional_software: Dict[str, str] = (
    "cython",
    "lxml",
    "networkx",
    "nltk",
    "psutil",
    "skimage",
    "scipy",
    "wordcloud",
)

for package in optional_software:
    try:
        mod = import_module(package)
        package_version = mod.__dict__.get("__version__", "No version information")
    except ImportError:
        package_version = "Not installed"

    version_info[package] = package_version

version_string = """Mathics {mathics}
on {python}
using SymPy {sympy}, mpmath {mpmath}, numpy {numpy}""".format(
    **version_info
)


if "cython" in version_info:
    version_string += f", cython {version_info['cython']}"


license_string = """\
Copyright (C) 2011-2023 The Mathics Team.
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
See the documentation for the full license."""
