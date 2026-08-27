import io
from typing import Optional

from mathics_scanner.errors import IncompleteSyntaxError

from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.parser import MathicsFileLineFeeder
from mathics.core.parser.convert import convert
from mathics.core.parser.util import parser
from mathics.core.systemsymbols import SymbolFailed


def eval_ToExpression_from_str(
    inp: str, evaluation: Evaluation
) -> Optional[BaseElement]:
    s = inp
    short_s = s[:15] + "..." if len(s) > 16 else s
    result = None
    with io.StringIO(s) as f:
        f.name = """ToExpression['%s']""" % short_s
        feeder = MathicsFileLineFeeder(f)
        while not feeder.empty():
            try:
                ast = parser.parse(feeder)
            except SyntaxError:
                return SymbolFailed
            except IncompleteSyntaxError:
                return SymbolFailed
            finally:
                feeder.send_messages(evaluation)
            if ast is None:  # blank line / comment
                continue
            query = convert(ast, evaluation.definitions)
            result = query.evaluate(evaluation)
        return result
