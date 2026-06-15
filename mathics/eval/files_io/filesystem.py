import os.path as osp
from typing import Optional

from mathics.core.atoms import String
from mathics.core.streams import path_search


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
