import json

from mathics.core.atoms import String
from mathics.core.convert.python import from_python
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.systemsymbols import SymbolRule


def eval_JSONImport(json_path: str) -> ListExpression:
    """Takes a ZIP file path and returns a list of file names/paths contained inside."""
    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)
        mathics_json = from_python(json_data)
        exprs = [
            Expression(
                SymbolRule,
                String("Data"),
                mathics_json,
            ),
            Expression(
                SymbolRule,
                String("Dataset"),
                mathics_json,
            ),
        ]
        return ListExpression(*exprs)
