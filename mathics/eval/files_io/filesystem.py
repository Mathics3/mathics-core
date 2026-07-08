import os
import os.path as osp
from typing import Optional

from mathics.core.atoms import String
from mathics.core.streams import path_search
from mathics.core.symbols import SymbolNull
from mathics.core.systemsymbols import SymbolFailed


def eval_DeleteFile(paths: list[str]) -> String:
    """Underlying DeleteFile[filename_] after checking filename_ and
    converting this to a Python list (even if it is just a single filename).
    """

    for path in paths:
        try:
            os.remove(path)
        except OSError:
            return SymbolFailed

    return SymbolNull


def eval_FileExtension(path: str) -> str:
    """Underlying implementation for FindExtension[filenamename_String]."""

    filename_base, filename_ext = osp.splitext(path)
    filename_ext = filename_ext.lstrip(".")
    return filename_ext


def eval_FindFile(name: str) -> Optional[String]:
    """Underlying implemenation for FindFile[name_String], but other builtins
    need this kind of function
    Searches for "name" and returns a String value for its absolute path.
    If "name" can't be found, return None.
    The caller will be responsible for deciding what to do, e.g.,
    return $SymbolFailed, or do that with an error message, or ignore.
    """

    result, _ = path_search(name)

    if result is None:
        return None

    return String(osp.abspath(result))
