import zipfile

from mathics.core.atoms import String
from mathics.core.convert.expression import to_mathics_list
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.systemsymbols import SymbolRule


def eval_ImportZIP(zip_path: str) -> ListExpression:
    """Takes a ZIP file path and returns a list of file names/paths contained inside."""
    with zipfile.ZipFile(zip_path, "r") as archive:
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
