from mathics.core.atoms.associations import Association
from mathics.core.element import BaseElement
from mathics.core.rules import is_rule
from mathics.core.symbols import SymbolList
from mathics.core.systemsymbols import SymbolAssociation


def eval_AssociationQ(expr) -> bool:
    def validate(elements: list[BaseElement]) -> bool:
        for element in elements:
            if is_rule(element):
                pass
            elif element.has_form((SymbolList, SymbolAssociation), None):
                if not validate(element.elements):
                    return False
            else:
                return False
        return True

    if isinstance(expr, Association):
        return True

    # Handle where we still have Expression[SymbolRule, ... ]
    return expr.get_head_name() == "System`Association" and validate(expr.elements)
