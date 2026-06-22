from mathics.core.builtin import String
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolFailed, SymbolFileExtension
from mathics.eval.files_io.filesystem import eval_FindFile
from mathics.eval.import_export.importexport import eval_FileFormat


def check_filename(tag: str, filename: String, evaluation: Evaluation):
    """
    Checks that 'file' is a string (with leading and trailing double quotes).
    If it isn't a string we use 'tag" in a 'chtype' error message.
    Otherwise, we strip the quotes off the tring and return that.
    """
    path = filename.value
    if not (isinstance(path, str) and path[0] == path[-1] == '"'):
        evaluation.message(tag, "chtype", filename)
    path = path[1:-1]
    return path


def check_import_filename_and_open(source: String, evaluation: Evaluation):
    """
    Checks that 'source' is a string, and exists in the filesystem. If not,
    and Import message is printed and None is returned.
    """

    if not (path := check_filename("Import", source, evaluation)):
        return

    # Resolve source to a file path
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

    findfile = check_import_filename_and_open(source, evaluation)

    if findfile is None:
        return SymbolFailed, None

    return findfile, eval_FileFormat(findfile.value).value


def infer_form(self, filename, evaluation: Evaluation):
    ext = Expression(SymbolFileExtension, filename).evaluate(evaluation)
    ext = ext.get_string_value().lower()
    # TODO: This dictionary should be accessible from the WL API
    # to allow defining specific converters
    return self._extdict.get(ext)
