from mathics.core.evaluation import Evaluation
from mathics.core.systemsymbols import SymbolFailed
from mathics.eval.files_io.filesystem import eval_FindFile
from mathics.eval.import_export.importexport import eval_FileFormat


def filename_check(source, evaluation: Evaluation):
    """
    Checks that 'source' is a string, and exists in the filesystem. If not,
    messages are printed and None is returned.
    """
    # Check that source is a string.
    path = source.to_python()
    if not (isinstance(path, str) and path[0] == path[-1] == '"'):
        evaluation.message("Import", "chtype", source)
        return

    # Resolve source to a file path
    if path[0] == path[-1] == '"':
        path = path[1:-1]

    findfile = eval_FindFile(path)

    if findfile is None:
        evaluation.message("Import", "nffil", source)
        return

    return findfile


def import_setup_check(source, evaluation: Evaluation) -> tuple:
    """
    Checks that 'source' exists as an importable file. If not,
    messages are printed tuple (SymbolFailed, None) is returned.
    """

    findfile = filename_check(source, evaluation)

    if findfile is None:
        return SymbolFailed, None

    return findfile, eval_FileFormat(findfile.value).value
