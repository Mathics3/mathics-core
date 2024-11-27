# -*- coding: utf-8 -*-

import platform
import sys
from importlib import import_module
from typing import Dict, Tuple

from mpmath import __version__ as mpmath_version
from numpy import __version__ as numpy_version
from sympy import __version__ as sympy_version

from mathics.version import __version__

# version_info contains a list of Python packages
# and the versions infsalled or "Not installed"
# if the package is not installed and "No version information"
# if we can't get version information.
version_info: Dict[str, str] = {
    "mathics": __version__,
    "mpmath": mpmath_version,
    "numpy": numpy_version,
    "python": platform.python_implementation() + " " + sys.version.split("\n")[0],
    "sympy": sympy_version,
}


# optional_software contains a list of Python packages
# that add functionality but are optional
optional_software: Tuple[str, ...] = (
    "cython",
    "lxml",
    "matplotlib",
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
        package_version = (
            mod.__version__
            if hasattr(mod, "__version__")
            else mod.__dict__.get("__version__", "No version information")
        )
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
Copyright (C) 2011-2024 The Mathics3 Team.
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
See the documentation for the full license."""


def disabled_breakpoint():
    """
    This breakpoint handler can be used as a dummy breakpoint
    handler function which does not stop in Mathics3 when `Breakpoint[]` is
    called. In effect, it disables, going into a Python breakpoint handler.

    Here is how to set this from inside Mathics3:
        SetEnvironment["PYTHONBREAKPOINT" -> "mathics.disabled_breakpoint"];

    Or when invoking `mathics` from a POSIX shell:

       PYTHONBREAKPOINT=mathics.disabled_breakpoint mathics # other arguments

    See https://docs.python.org/3/library/functions.html#breakpoint for information on
    the Python builtin breakpoint() function

    """
    # Note that we were called. In Django and other front-ends, the
    # print message below will appear on the console; it might not be user
    # visible by default.
    print("Hit disabled breakpoint.")
