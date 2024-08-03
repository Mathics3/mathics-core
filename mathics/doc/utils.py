# -*- coding: utf-8 -*-

import os.path as osp
import pickle
import re
import unicodedata
from os import makedirs
from typing import Dict


def load_doctest_data(data_path, quiet=False) -> Dict[tuple, dict]:
    """
    Read doctest information from PCL file and return this.

    The return value is a dictionary of test results. The key is a tuple
    of:
    * Part name,
    * Chapter name,
    * [Guide Section name],
    * Section name,
    * Subsection name,
    * test number
    and the value is a dictionary of a Result.getdata() dictionary.
    """
    if not quiet:
        print(f"Loading LaTeX internal data from {data_path}")
    with open_ensure_dir(data_path, "rb") as doc_data_fp:
        return pickle.load(doc_data_fp)


def open_ensure_dir(f, *args, **kwargs):
    try:
        return open(f, *args, **kwargs)
    except (IOError, OSError):
        d = osp.dirname(f)
        if d and not osp.exists(d):
            makedirs(d)
        return open(f, *args, **kwargs)


def print_and_log(logfile, *args):
    """
    Print a message and also log it to global LOGFILE.
    """
    msg_lines = [a.decode("utf-8") if isinstance(a, bytes) else a for a in args]
    string = "".join(msg_lines)
    print(string)
    if logfile is not None:
        logfile.write(string)


def slugify(value: str) -> str:
    """
    Converts to lowercase, removes non-word characters apart from '$',
    and converts spaces to hyphens. Also strips leading and trailing
    whitespace.

    Based on the Django version, but modified to preserve '$'.
    """
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    value = re.sub(r"[^$`\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s`]+", "-", value)
