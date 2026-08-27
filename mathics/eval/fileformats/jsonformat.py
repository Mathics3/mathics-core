import json

from mathics.core.atoms import String
from mathics.core.convert.python import from_python
from mathics.core.element import BaseElement
from mathics.core.expression import Evaluation, Expression
from mathics.core.list import ListExpression
from mathics.core.systemsymbols import SymbolFailed, SymbolRule
from mathics.eval.files_io.files import resolve_file


def eval_JSONImport(json_name: String, evaluation: Evaluation) -> BaseElement:
    """Takes a JSON file path and returns a information from it
    formatted for Mathics3.

    When there is no error, the information returned is a ListExpression
    containing a Rule for each of WL format Elements, currently "Data", and "Dataset".

    When there is an error, SymbolFailed can be returned.
    """
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
