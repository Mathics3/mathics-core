# -*- coding: utf-8 -*-
"""
Mathics3 global system settings.

Some of the values can be adjusted via Environment Variables.
"""

import os
import os.path as osp
import sys
from pathlib import Path
from typing import List


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


DEBUG = True
DEBUG_PRINT = False

# Maximum recursion depth is safe for all Python environments
# without setting a custom thread stack size.
DEFAULT_MAX_RECURSION_DEPTH = 512

# Maximum number of digits allows in a string representation of a string number.
# We picked this to be able to handle 1989 ^ 1989.
DEFAULT_MAX_STR_DIGITS = 7000
str_digits: str = os.environ.get("MATHICS_MAX_STR_DIGITS", str(DEFAULT_MAX_STR_DIGITS))
MAX_STR_DIGITS = (
    int(DEFAULT_MAX_STR_DIGITS) if str_digits.isnumeric() else DEFAULT_MAX_STR_DIGITS
)

# Let Python know what value of MAX_STR_DIGITS to use.
if hasattr(sys, "set_int_max_str_digits"):
    # pyston 2.3.5
    sys.set_int_max_str_digits(MAX_STR_DIGITS)
else:
    MAX_STR_DIGITS = -1

# Either None (no timeout) or a positive integer.
# Unix only
TIMEOUT = None

# max pickle.dumps() size for storing results in DB
# historically 10000 was used on public mathics servers
MAX_STORED_SIZE = 10000

ROOT_DIR = osp.dirname(__file__)
if sys.platform.startswith("win"):
    DATA_DIR = osp.join(os.environ["APPDATA"], "Python", "Mathics3")
else:
    DATA_DIR = osp.join(
        os.environ.get("APPDATA", osp.expanduser("~/.local/var/Mathics3/"))
    )
USER_PACKAGE_DIR = osp.join(DATA_DIR, "Packages")

# In contrast to ROOT_DIR, LOCAL_ROOT_DIR is used in building
# LaTeX documentation. When Mathics3 is installed, we don't want LaTeX file documentation.tex
# to get put in the installation directory, but instead we build documentation
# from checked-out source and that is where this should be put.
LOCAL_ROOT_DIR = get_srcdir()

# Location of doctests and test results formatted for LaTeX.  This data
# is stoared as a Python Pickle format, but storing this in JSON if
# possible would be preferable and faster

# We need two versions of doctest data, one is in the user space which is updated with
# local packages installed and is user writable.

DOC_DIR = osp.join(LOCAL_ROOT_DIR, "doc", "documentation")

# Set this True if you prefer 12 hour time to be the default
TIME_12HOUR = False

# Leave this True unless you have specific reason for not permitting
# users to access local files.
ENABLE_FILES_MODULE = True

# Leave this True unless you have specific reason for not permitting
# users to execute system commands.
# If MATHICS3_SANDBOX environment variable is set, this defaults to False.
ENABLE_SYSTEM_COMMANDS = (
    os.environ.get(
        "MATHICS3_ENABLE_SYSTEM_COMMANDS",
        str(
            not (
                os.environ.get("MATHICS3_SANDBOX")
                or sys.platform in ("emscripten", "wasi")
            )
        ),
    ).lower()
    == "true"
)


# Rocky: this is probably a hack. LoadModule[] needs to handle
# whatever it is that setting this thing did.
default_pymathics_modules: List[str] = []

character_encoding = os.environ.get(
    "MATHICS_CHARACTER_ENCODING", sys.getdefaultencoding()
)
SYSTEM_CHARACTER_ENCODING = "UTF-8" if character_encoding == "utf-8" else "ASCII"


def ensure_directory(directory: str):
    """
    Create directory `directory` if it does not exist.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        os.makedirs(directory)
