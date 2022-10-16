# -*- coding: utf-8 -*-


from mathics.builtin.base import BinaryOperator, Predefined, PrefixOperator, Builtin
from mathics.builtin.lists import InvalidLevelspecError, python_levelspec, walk_levels
from mathics.core.expression import Expression

from mathics.core.attributes import (
    A_FLAT,
    A_HOLD_ALL,
    A_ONE_IDENTITY,
    A_ORDERLESS,
    A_PROTECTED,
    A_LOCKED,
)


from mathics.core.symbols import (
    Symbol,
    SymbolTrue,
    SymbolFalse,
)

from mathics.core.systemsymbols import (
    SymbolAnd,
    SymbolImplies,
    SymbolNot,
    SymbolOr,
    SymbolXor,
)

SymbolEquivalent = Symbol("Equivalent")


class Or(BinaryOperator):
    """
    <dl>
    <dt>'Or[$expr1$, $expr2$, ...]'
    <dt>'$expr1$ || $expr2$ || ...'
        <dd>evaluates each expression in turn, returning 'True'
        as soon as an expression evaluates to 'True'. If all
        expressions evaluate to 'False', 'Or' returns 'False'.
    </dl>

    >> False || True
     = True

    If an expression does not evaluate to 'True' or 'False', 'Or'
    returns a result in symbolic form:
    >> a || False || b
     = a || b
    """

    attributes = A_FLAT | A_HOLD_ALL | A_ONE_IDENTITY | A_PROTECTED
    operator = "||"
    precedence = 215
    summary_text = "logic (inclusive) disjunction"

    #    rules = {
    #        "Or[a_]": "a",
    #        "Or[a_, a_]": "a",
    #        "Or[pred1___, a_, pred2___, a_, pred3___]": "Or[pred1, a, pred2, pred3]",
    #    }
    def apply(self, args, evaluation):
        "Or[args___]"

        args = args.get_sequence()
        elements = []
        for arg in args:
            result = arg.evaluate(evaluation)
            if result is SymbolTrue:
                return SymbolTrue
            elif result != SymbolFalse:
                elements.append(result)
        if elements:
            if len(elements) == 1:
                return elements[0]
            else:
                return Expression(SymbolOr, *elements)
        else:
            return SymbolFalse


class And(BinaryOperator):
    """
    <dl>
    <dt>'And[$expr1$, $expr2$, ...]'
    <dt>'$expr1$ && $expr2$ && ...'
        <dd>evaluates each expression in turn, returning 'False'
        as soon as an expression evaluates to 'False'. If all
        expressions evaluate to 'True', 'And' returns 'True'.
    </dl>

    >> True && True && False
     = False

    If an expression does not evaluate to 'True' or 'False', 'And'
    returns a result in symbolic form:
    >> a && b && True && c
     = a && b && c
    """

    attributes = A_FLAT | A_HOLD_ALL | A_ONE_IDENTITY | A_PROTECTED
    operator = "&&"
    precedence = 215
    summary_text = "logic conjunction"
    #    rules = {
    #        "And[a_]": "a",
    #        "And[a_, a_]": "a",
    #        "And[pred1___, a_, pred2___, a_, pred3___]": "And[pred1, a, pred2, pred3]",
    #    }

    def apply(self, args, evaluation):
        "And[args___]"

        args = args.get_sequence()
        elements = []
        for arg in args:
            result = arg.evaluate(evaluation)
            if result is SymbolFalse:
                return SymbolFalse
            elif result is not SymbolTrue:
                elements.append(result)
        if elements:
            if len(elements) == 1:
                return elements[0]
            else:
                return Expression(SymbolAnd, *elements)
        else:
            return SymbolTrue


class Not(PrefixOperator):
    """
    <dl>
    <dt>'Not[$expr$]'
    <dt>'!$expr$'
        <dd>negates the logical expression $expr$.
    </dl>

    >> !True
     = False
    >> !False
     = True
    >> !b
     = !b
    """

    operator = "!"
    precedence = 230

    rules = {
        "Not[True]": "False",
        "Not[False]": "True",
        "Not[Not[expr_]]": "expr",
    }
    summary_text = "logic negation"


class Nand(Builtin):
    """
    <dl>
    <dt>'Nand[$expr1$, $expr2$, ...]'
    <dt>$expr1$ \u22BC $expr2$ \u22BC ...
        <dd> Implements the logical NAND function.  The same as 'Not[And['$expr1$, $expr2$, ...']]'
    </dl>
    >> Nand[True, False]
     = True
    """

    operator = "\u22BC"
    rules = {
        "Nand[expr___]": "Not[And[expr]]",
    }
    summary_text = "negation of logic conjunction"


class Nor(Builtin):
    """
    <dl>
    <dt>'Nor[$expr1$, $expr2$, ...]'
    <dt>$expr1$ \u22BD $expr2$ \u22BD ...
        <dd>Implements the logical NOR function.  The same as 'Not[Or['$expr1$, $expr2$, ...']]'
    </dl>
    >> Nor[True, False]
     = False
    """

    operator = "\u22BD"
    rules = {
        "Nor[expr___]": "Not[Or[expr]]",
    }
    summary_text = "negation of logic (inclusive) disjunction"


class Implies(BinaryOperator):
    """
    <dl>
    <dt>'Implies[$expr1$, $expr2$]'
    <dt>$expr1$ \u21D2 $expr2$
        <dd>evaluates each expression in turn, returning 'True'
        as soon as the first expression evaluates to 'False'. If the
        first expression evaluates to 'True', 'Implies' returns the
        second expression.
    </dl>

    >> Implies[False, a]
     = True
    >> Implies[True, a]
     = a

    If an expression does not evaluate to 'True' or 'False', 'Implies'
    returns a result in symbolic form:
    >> Implies[a, Implies[b, Implies[True, c]]]
     = a \u21D2 b \u21D2 c
    """

    operator = "\u21D2"
    precedence = 200
    grouping = "Right"
    summary_text = "logic implication"

    def apply(self, x, y, evaluation):
        "Implies[x_, y_]"

        result0 = x.evaluate(evaluation)
        if result0 is SymbolFalse:
            return SymbolTrue
        elif result0 is SymbolTrue:
            return y.evaluate(evaluation)
        else:
            return Expression(SymbolImplies, result0, y.evaluate(evaluation))


class Equivalent(BinaryOperator):
    """
    <dl>
      <dt>'Equivalent[$expr1$, $expr2$, ...]'
      <dt>$expr1$ \u29E6 $expr2$ \u29E6 ...

      <dd>is equivalent to
        ($expr1$ && $expr2$ && ...) || (!$expr1$ && !$expr2$ && ...)
    </dl>

    >> Equivalent[True, True, False]
     = False

    If all expressions do not evaluate to 'True' or 'False', 'Equivalent'
    returns a result in symbolic form:
    >> Equivalent[a, b, c]
     = a \u29E6 b \u29E6 c
     Otherwise, 'Equivalent' returns a result in DNF
    >> Equivalent[a, b, True, c]
     = a && b && c
    #> Equivalent[]
     = True
    #> Equivalent[a]
     = True
    """

    attributes = A_ORDERLESS | A_PROTECTED
    operator = "\u29E6"
    precedence = 205
    summary_text = "logic equivalence"

    def apply(self, args, evaluation):
        "Equivalent[args___]"

        args = args.get_sequence()
        argc = len(args)
        if argc == 0 or argc == 1:
            return SymbolTrue
        flag = False
        for arg in args:
            result = arg.evaluate(evaluation)
            if result is SymbolFalse or result is SymbolTrue:
                flag = not flag
                break
        if flag:
            return Expression(
                SymbolOr,
                Expression(SymbolAnd, *args),
                Expression(SymbolAnd, *[Expression(SymbolNot, arg) for arg in args]),
            ).evaluate(evaluation)
        else:
            return Expression(SymbolEquivalent, *args)


class Xor(BinaryOperator):
    """
    <dl>
      <dt>'Xor[$expr1$, $expr2$, ...]'
      <dt>$expr1$ \u22BB $expr2$ \u22BB ...

      <dd>evaluates each expression in turn, returning 'True'
        as soon as not all expressions evaluate to the same value. If all
        expressions evaluate to the same value, 'Xor' returns 'False'.
    </dl>

    >> Xor[False, True]
     = True
    >> Xor[True, True]
     = False

    If an expression does not evaluate to 'True' or 'False', 'Xor'
    returns a result in symbolic form:
    >> Xor[a, False, b]
     = a \u22BB b
    #> Xor[]
     = False
    #> Xor[a]
     = a
    #> Xor[False]
     = False
    #> Xor[True]
     = True
    #> Xor[a, b]
     = a \u22BB b
    """

    attributes = A_FLAT | A_ONE_IDENTITY | A_ORDERLESS | A_PROTECTED
    operator = "\u22BB"
    precedence = 215
    summary_text = "logic (exclusive) disjunction"

    def apply(self, args, evaluation):
        "Xor[args___]"

        args = args.get_sequence()
        elements = []
        flag = True
        for arg in args:
            result = arg.evaluate(evaluation)
            if result is SymbolTrue:
                flag = not flag
            elif result != SymbolFalse:
                elements.append(result)
        if elements and flag:
            if len(elements) == 1:
                return elements[0]
            else:
                return Expression(SymbolXor, *elements)
        elif elements and not flag:
            if len(elements) == 1:
                return Expression(SymbolNot, elements[0])
            else:
                return Expression(SymbolNot, Expression(SymbolXor, *elements))
        else:
            return Symbol(repr(not flag))


class True_(Predefined):
    """
    <dl>
      <dt>'True'
      <dd>represents the Boolean true value.
    </dl>
    """

    attributes = A_LOCKED | A_PROTECTED
    name = "True"
    summary_text = "boolean constant for True"


class False_(Predefined):
    """
    <dl>
    <dt>'False'
        <dd>represents the Boolean false value.
    </dl>
    """

    attributes = A_LOCKED | A_PROTECTED
    name = "False"
    summary_text = "boolean constant for False"


class _ShortCircuit(Exception):
    def __init__(self, result):
        self.result = result


class _ManyTrue(Builtin):
    rules = {
        "%(name)s[list_List, test_]": "%(name)s[list, test, 1]",
        "%(name)s[test_][list_List]": "%(name)s[list, test]",
    }

    def _short_circuit(self, what):
        raise NotImplementedError

    def _no_short_circuit(self):
        raise NotImplementedError

    def apply(self, expr, test, level, evaluation):
        "%(name)s[expr_, test_, level_]"

        try:
            start, stop = python_levelspec(level)
        except InvalidLevelspecError:
            evaluation.message("Level", "level", level)
            return

        def callback(node):
            self._short_circuit(
                Expression(test, node).evaluate(evaluation) is SymbolTrue
            )
            return node

        try:
            walk_levels(expr, start, stop, callback=callback)
        except _ShortCircuit as e:
            return e.result

        return self._no_short_circuit()


class NoneTrue(_ManyTrue):
    """
    <dl>
    <dt>'NoneTrue[{$expr1$, $expr2$, ...}, $test$]'
        <dd>returns True if no application of $test$ to $expr1$, $expr2$, ... evaluates to True.
    <dt>'NoneTrue[$list$, $test$, $level$]'
        <dd>returns True if no application of $test$ to items of $list$ at $level$ evaluates to True.
    <dt>'NoneTrue[$test$]'
        <dd>gives an operator that may be applied to expressions.
    </dl>

    >> NoneTrue[{1, 3, 5}, EvenQ]
     = True

    >> NoneTrue[{1, 4, 5}, EvenQ]
     = False

    #> NoneTrue[{}, EvenQ]
     = True
    """

    summary_text = "all the elements are False"

    def _short_circuit(self, what):
        if what:
            raise _ShortCircuit(SymbolFalse)

    def _no_short_circuit(self):
        return SymbolTrue


class AnyTrue(_ManyTrue):
    """
    <dl>
    <dt>'AnyTrue[{$expr1$, $expr2$, ...}, $test$]'
        <dd>returns True if any application of $test$ to $expr1$, $expr2$, ... evaluates to True.
    <dt>'AnyTrue[$list$, $test$, $level$]'
        <dd>returns True if any application of $test$ to items of $list$ at $level$ evaluates to True.
    <dt>'AnyTrue[$test$]'
        <dd>gives an operator that may be applied to expressions.
    </dl>

    >> AnyTrue[{1, 3, 5}, EvenQ]
     = False

    >> AnyTrue[{1, 4, 5}, EvenQ]
     = True

    #> AnyTrue[{}, EvenQ]
     = False
    """

    summary_text = "some of the elements are True"

    def _short_circuit(self, what):
        if what:
            raise _ShortCircuit(SymbolTrue)

    def _no_short_circuit(self):
        return SymbolFalse


class AllTrue(_ManyTrue):
    """
    <dl>
    <dt>'AllTrue[{$expr1$, $expr2$, ...}, $test$]'
        <dd>returns True if all applications of $test$ to $expr1$, $expr2$, ... evaluate to True.
    <dt>'AllTrue[$list$, $test$, $level$]'
        <dd>returns True if all applications of $test$ to items of $list$ at $level$ evaluate to True.
    <dt>'AllTrue[$test$]'
        <dd>gives an operator that may be applied to expressions.
    </dl>

    >> AllTrue[{2, 4, 6}, EvenQ]
     = True

    >> AllTrue[{2, 4, 7}, EvenQ]
     = False

    #> AllTrue[{}, EvenQ]
     = True
    """

    summary_text = "all the elements are True"

    def _short_circuit(self, what):
        if not what:
            raise _ShortCircuit(SymbolFalse)

    def _no_short_circuit(self):
        return SymbolTrue
