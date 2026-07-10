"""
Handles Western character encoding and the Unicode standard.
UTF (Unicode Transformation Format) and UCS (Universal Character Set) mapping methods are supported.
"""

from mathics.core.atoms import String
from mathics.core.element import BaseElement
from mathics.core.expression import Evaluation, Expression
from mathics.core.list import ListExpression
from mathics.core.systemsymbols import SymbolFailed, SymbolRule
from mathics.eval.files_io.files import resolve_file


def eval_TextImport(path: String, evaluation: Evaluation) -> BaseElement:
    """Takes a Text file path and returns information in it."""
    resolve_info = resolve_file(path, "r", evaluation)
    if resolve_info is None:
        return SymbolFailed
    resolved_path = resolve_info[0]
    if resolved_path is None:
        return SymbolFailed

    with open(resolved_path, "r") as fp:
        try:
            data = fp.read()
            # run ToExpression
        except Exception as exc:
            evaluation.message("TextImport", "dec", String(exc))
            return SymbolFailed

        # Tag the result by wrapping in a list of rule expressions.
        # We do this so that Import can extract pieces by element name.
        data_string = String(data)
        exprs = [
            Expression(SymbolRule, String("Data"), data_string),
            Expression(SymbolRule, String("String"), data_string),
        ]
        return ListExpression(*exprs)
