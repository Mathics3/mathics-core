"""
Evaluation routines for handling data in some sort of archive format,
e.g. ZIP, TAR, etc.
"""

import zipfile
from typing import Optional

from mathics.core.atoms import String
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolNull
from mathics.core.systemsymbols import SymbolFailed, SymbolRule
from mathics.eval.files_io.files import resolve_file
from mathics.eval.import_export.importexport import (
    IMPORTERS,
    eval_Import_data_only,
    infer_file_format,
)


def eval_ImportZIP(
    zip_name: String, evaluation: Evaluation, members: Optional[list[str]] = None
) -> ListExpression:
    """If `members` is empty, this function takes a ZIP file path and returns a
    list of file names/paths contained inside.

    "If `members` is given, then extract those members (or files) from the ZIP file.
    """

    zip_path, is_temporary_file = resolve_file(zip_name, "r", evaluation)
    if zip_path is None:
        return SymbolFailed

    # The below "try:" is probably unnecessary since resolve_file should
    # catch errors.
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            if members is None:
                filenames = archive.namelist()
                mathics_filenames = to_mathics_list(*filenames)

                # Wrap metadata or "elements" of of the zip file into
                # list of Rule. The caller can then use
                # rules to pick out specific elements desired.
                exprs = [
                    Expression(
                        SymbolRule,
                        String("FileNames"),
                        mathics_filenames,
                    ),
                    Expression(
                        SymbolRule,
                        String("Summary"),
                        mathics_filenames,
                    ),
                ]

                if filenames:
                    for filename in filenames:
                        exprs.append(
                            Expression(
                                SymbolRule,
                                String(filename),
                                String(archive.read(filename).decode("utf-8")),
                            )
                        )

                return ListExpression(*exprs)

            if members.has_form("List", None):
                elements = members.get_elements()
            else:
                elements = [members]

            for element in elements:
                member = element.value
                file_format = infer_file_format(member, "Text").upper()
                if file_format not in IMPORTERS.keys():
                    evaluation.message("Import", "fmtnosup", file_format)
                    return SymbolFailed

                unzipped_file_data = archive.read(member).decode("utf-8")
                converted_member_data = eval_Import_data_only(
                    unzipped_file_data, file_format, evaluation, {"raw": True}
                )
                result = ListExpression(
                    Expression(SymbolRule, element, converted_member_data)
                )
                return result

    except FileNotFoundError:
        evaluation.message("Import", "nffil", String(zip_path))
        return SymbolFailed
    except PermissionError:
        evaluation.message("Import", "noopen", String(zip_path))
        return SymbolFailed
    except Exception:
        # This seems to be what WMA does.
        return SymbolNull
