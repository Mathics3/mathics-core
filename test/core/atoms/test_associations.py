from mathics.core.atoms import Integer1, Integer2
from mathics.core.atoms.associations import Association
from mathics.core.convert.expression import to_mathics_list
from mathics.core.expression import Expression
from mathics.core.rules import is_rule
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolRule


def make_rule(lhs, rhs) -> Expression:
    return Expression(SymbolRule, lhs, rhs)


def test_association_is_literal():
    # Not much here yet.
    rule1 = make_rule(Integer1, Integer2)
    assert is_rule(rule1)
    rule_list = to_mathics_list(rule1)
    association1 = Association(rule_list)
    assert isinstance(association1, Association)
    assert association1.python == {1: 2}
    association1.update([(Integer1, Integer1)])
    assert association1.python == {1: 1}
    rule2 = make_rule(Symbol("x"), Integer2)
    rule_list = to_mathics_list(rule2)
    association2 = Association(rule_list)
    assert isinstance(association2, Association)
