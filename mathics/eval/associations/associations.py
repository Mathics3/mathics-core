from mathics.core.atoms.associations import Association
from mathics.core.element import BaseElement
from mathics.core.rules import is_rule


def eval_AssociationQ(expr) -> bool:
    def validate(elements: list[BaseElement]) -> bool:
        for element in elements:
            if is_rule(element):
                pass
            elif element.has_form(("List", "Association"), None):
                if not validate(element.elements):
                    return False
            else:
                return False
        return True

    if isinstance(expr, Association):
        return True

    # Handle where we still have Expression[SymbolRule, ... ]
    return expr.get_head_name() == "System`Association" and validate(expr.elements)
