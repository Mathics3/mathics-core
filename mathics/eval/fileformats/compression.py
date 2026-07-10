"""
Evaluation routines for handling data in some sort of archive format,
e.g. ZIP, TAR, etc.
"""

import zipfile
from typing import Optional

from mathics.core.atoms import String
from mathics.core.convert.expression import to_mathics_list
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolList, SymbolNull
from mathics.core.systemsymbols import SymbolFailed, SymbolRule
from mathics.eval.files_io.files import resolve_file
from mathics.eval.import_export.importexport import (
    IMPORTERS,
    eval_Import_data_only,
    filetype_from_path,
)


def eval_ImportZIP(
    zip_name: String, evaluation: Evaluation, members: Optional[list[String]] = None
) -> BaseElement:
    """If `members` is empty, this function takes a ZIP file path and returns a
    list of file names/paths contained inside.

    "If `members` is given, then extract those members (or files) from the ZIP file.

    If there is no problem, the format for the extraction is a ListExpression of Rules.
    The LHS of the Rule is the member name, and the RHS of the Rule is content value.
    Otherwise, we return SymbolFailed or SymbolNull.
    """

    resolved = resolve_file(zip_name, "r", evaluation)
    if resolved is None:
        return SymbolFailed

    zip_path = resolved[0]

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

            elements = [members] if isinstance(members, String) else members[1:]
            rules = []
            for element in elements:
                member = element.value
                file_format = filetype_from_path(member, check_exists=False)
                if file_format not in IMPORTERS.keys():
                    evaluation.message("Import", "fmtnosup", file_format)
                    return SymbolFailed

                unzipped_file_data = archive.read(member).decode("utf-8")
                converted_member_data = eval_Import_data_only(
                    unzipped_file_data, file_format, evaluation, {"raw": True}
                )
                rule = Expression(SymbolRule, element, converted_member_data)
                rules.append(rule)
            return ListExpression(*rules)

    except FileNotFoundError:
        evaluation.message("Import", "nffil", String(zip_path))
        return SymbolFailed
    except PermissionError:
        evaluation.message("Import", "noopen", String(zip_path))
        return SymbolFailed
    except Exception:
        # This seems to be what WMA does.
        return SymbolNull
