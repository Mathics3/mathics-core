# -*- coding: utf-8 -*-
import os
import os.path as osp
import sys
from pathlib import Path

import pkg_resources


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


DEBUG = True

DEBUG_PRINT = False
# Either None (no timeout) or a positive integer.
# Unix only
TIMEOUT = None

# specifies a maximum recursion depth is safe for all Python environments
# without setting a custom thread stack size.
DEFAULT_MAX_RECURSION_DEPTH = 512

# max pickle.dumps() size for storing results in DB
# historically 10000 was used on public mathics servers
MAX_STORED_SIZE = 10000

ROOT_DIR = pkg_resources.resource_filename("mathics", "")
if sys.platform.startswith("win"):
    DATA_DIR = osp.join(os.environ["APPDATA"], "Python", "Mathics")
else:
    DATA_DIR = osp.join(
        os.environ.get("APPDATA", osp.expanduser("~/.local/var/mathics/"))
    )

# In contrast to ROOT_DIR, LOCAL_ROOT_DIR is used in building
# LaTeX documentation. When Mathics is installed, we don't want LaTeX file documentation.tex
# to get put in the installation directory, but instead we build documentaiton
# from checked-out source and that is where this should be put.
LOCAL_ROOT_DIR = get_srcdir()

# Location of doctests and test results formated for LaTeX.  This data
# is stoared as a Python Pickle format, but storing this in JSON if
# possible would be preferable and faster

# We need two versions of doctest data, one is in the user space which is updated with
# local packages installed and is user writable.


DOCTEST_LATEX_DATA_PCL = os.environ.get(
    "DOCTEST_LATEX_DATA_PCL", osp.join(DATA_DIR, "doctest_latex_data.pcl")
)

# We need another version of doctest data as a fallback, and that is distributed with the
# package. It is note user writable and not in the user space.

DOCTEST_SYSTEM_LATEX_DATA_PCL = os.environ.get(
    "DOCTEST_SYSTEM_LATEX_DATA_PCL",
    osp.join(LOCAL_ROOT_DIR, "data", "doctest_latex_data.pcl"),
)

DOC_DIR = osp.join(LOCAL_ROOT_DIR, "doc", "documentation")
DOC_LATEX_DIR = osp.join(LOCAL_ROOT_DIR, "doc", "latex")
DOC_LATEX_FILE = osp.join(DOC_LATEX_DIR, "documentation.tex")

# Set this True if you prefer 12 hour time to be the default
TIME_12HOUR = False

# Leave this True unless you have specific reason for not permitting
# users to access local files.
ENABLE_FILES_MODULE = True

# Rocky: this is probably a hack. LoadModule[] needs to handle
# whatever it is that setting this thing did.
default_pymathics_modules = []

character_encoding = os.environ.get(
    "MATHICS_CHARACTER_ENCODING", sys.getdefaultencoding()
)
SYSTEM_CHARACTER_ENCODING = "UTF-8" if character_encoding == "utf-8" else "ASCII"


def get_doctest_latex_data_path(should_be_readable=False, create_parent=False) -> str:
    """Returns a string path where we can find Python Pickle doctest data for LaTeX
    processing.

    If `should_be_readable` is True, the we will check to see whether this file is
    readable (which also means it exists). If not, we'll return the `DOCTEST_SYSTEM_DATA_PATH`.
    """
    doc_user_latex_data_pcl = Path(DOCTEST_LATEX_DATA_PCL)
    base_config_dir = doc_user_latex_data_pcl.parent
    if not base_config_dir.is_dir() and create_parent:
        Path("base_config_dir").mkdir(parents=True, exist_ok=True)

    if should_be_readable:
        return (
            DOCTEST_LATEX_DATA_PCL
            if doc_user_latex_data_pcl.is_file()
            else DOCTEST_SYSTEM_LATEX_DATA_PCL
        )
    else:
        return DOCTEST_LATEX_DATA_PCL
