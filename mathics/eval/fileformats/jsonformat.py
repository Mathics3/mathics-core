import json

from mathics.core.atoms import String
from mathics.core.convert.python import from_python
from mathics.core.expression import Evaluation


def eval_JSONImport(source_path: str, evaluation: Evaluation):
    with open(source_path, "r") as f:
        try:
            json_dict = json.load(f)
        except json.decoder.JSONDecodeError as exc:
            evaluation.message("JSON`Import`JSONImport", "dec", String(exc.msg))
            return None
    return from_python(json_dict)
