"""
Handles Wolfram Language (and Mathics3) package files.


MIME type: application/vnd.wolfram.wl, application/vnd.wolfram.mathematica.package
olfram Language package source format.

Used for storing and exchanging Wolfram Language programs, packages and data.
Plain ASCII text format.

Stores Wolfram Language expressions in InputForm.
Can represent program code, numerical and textual data, 2D raster and vector images, 3D geometries, sound and other kinds of data.
"""

from mathics.core.atoms import String
from mathics.core.element import BaseElement
from mathics.core.expression import Evaluation, Expression
from mathics.core.list import ListExpression
from mathics.core.systemsymbols import SymbolFailed, SymbolRule
from mathics.eval.atomic.strings import eval_ToExpression_from_str
from mathics.eval.files_io.files import resolve_file


def eval_WLImport(path: String, evaluation: Evaluation) -> BaseElement:
    """Takes a Text file path and returns information in it."""

    resolve_info = resolve_file(path, "r", evaluation)
    if resolve_info is None:
        return SymbolFailed
    resolved_path = resolve_info[0]
    with open(resolved_path, "r") as fp:
        data = eval_ToExpression_from_str(fp.read(), evaluation)
        if data is None:
            data = SymbolFailed

        # Tag the result by wrapping in a list of rule expressions.
        # We do this so that Import can extract pieces by element name.

        exprs = [
            Expression(SymbolRule, String("Get"), data),
            Expression(SymbolRule, String("Script"), data),
        ]
        return ListExpression(*exprs)
    return SymbolFailed
