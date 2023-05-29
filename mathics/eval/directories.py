"""
Directory and Directory Operations related constants.

Many of these do do depend on the evaluation context. Conversions to Sympy are
used just as a last resource.
"""

import os
import tempfile

INITIAL_DIR = os.getcwd()
DIRECTORY_STACK = [INITIAL_DIR]
SYS_ROOT_DIR = "/" if os.name == "posix" else "\\"
TMP_DIR = tempfile.gettempdir()
