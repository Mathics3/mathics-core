from mathics.core.atoms import Integer1, Integer2
from mathics.core.atoms.associations import Association
from mathics.core.convert.expression import to_mathics_list
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolRule


def make_rule(lhs, rhs) -> Expression:
    return Expression(SymbolRule, lhs, rhs)


def test_association_is_literal():
    # Not much here yet.
    rule1 = make_rule(Integer1, Integer2)
    rule_list = to_mathics_list(rule1)
    assert Association(rule_list)
    rule2 = make_rule(Symbol("x"), Integer2)
    rule_list = to_mathics_list(rule2)
    assert Association(rule_list)
