import zipfile
from typing import Optional

from mathics.core.atoms import String
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.systemsymbols import SymbolFailed, SymbolRule
from mathics.eval.import_export.importexport import (
    IMPORTERS,
    eval_Import_data_only,
    infer_file_format,
)


def eval_ImportZIP(
    zip_path: str, evaluation: Evaluation, members: Optional[list[str]] = None
) -> ListExpression:
    """Takes a ZIP file path and returns a list of file names/paths contained inside."""
    with zipfile.ZipFile(zip_path, "r") as archive:
        if members is None:
            filenames = archive.namelist()
            mathics_filenames = to_mathics_list(*filenames)
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

        for member in members:
            file_format = infer_file_format(member).upper()
            if file_format not in IMPORTERS.keys():
                evaluation.message("Import", "fmtnosup", file_format)
                return SymbolFailed

            file_data = archive.read(member)
            # FIXME: this handles one member. What do we do if we have more?
            return eval_Import_data_only(file_data.value, file_format, evaluation, {})
