import json

from mathics.core.atoms import String
from mathics.core.convert.python import from_python
from mathics.core.element import BaseElement
from mathics.core.expression import Evaluation, Expression
from mathics.core.list import ListExpression
from mathics.core.systemsymbols import SymbolFailed, SymbolRule
from mathics.eval.files_io.files import resolve_file


def eval_JSONImport(json_name: String, evaluation: Evaluation) -> BaseElement:
    """Takes a JSON file path and returns a list of file names/paths contained inside."""
    resolve_info = resolve_file(json_name, "r", evaluation)
    if resolve_info is None:
        return SymbolFailed
    json_path = resolve_info[0]
    if json_path is None:
        return SymbolFailed

    with open(json_path, "r") as json_file:
        try:
            json_data = json.load(json_file)
        except json.decoder.JSONDecodeError as exc:
            evaluation.message("JSON`Import`JSONImport", "dec", String(exc.msg))
            return SymbolFailed
        mathics_json = from_python(json_data)

        # Tag the result by wrapping in a list of rule expressions.
        # We do this so that Import can extract pieces by element name.
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
