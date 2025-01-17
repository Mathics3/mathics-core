# -*- coding: utf-8 -*-

"""
Elements of Lists

Functions for accessing elements of lists using either indices, positions, or \
patterns of criteria.
"""

from itertools import chain

from mathics.builtin.box.layout import RowBox
from mathics.core.atoms import Integer, Integer0, Integer1, Integer3, Integer4, String
from mathics.core.attributes import (
    A_HOLD_FIRST,
    A_HOLD_REST,
    A_N_HOLD_REST,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import Builtin, InfixOperator
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import (
    InvalidLevelspecError,
    MessageException,
    PartDepthError,
    PartError,
    PartRangeError,
)
from mathics.core.expression import Expression, ExpressionInfinity
from mathics.core.list import ListExpression
from mathics.core.rules import Rule
from mathics.core.symbols import Atom, Symbol, SymbolNull, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolAppend,
    SymbolAppendTo,
    SymbolByteArray,
    SymbolDrop,
    SymbolFailed,
    SymbolInfinity,
    SymbolKey,
    SymbolMakeBoxes,
    SymbolMissing,
    SymbolSelect,
    SymbolSequence,
    SymbolSet,
    SymbolTake,
)
from mathics.eval.list.eol import (
    drop_span_selector,
    eval_Part,
    parts,
    take_span_selector,
)
from mathics.eval.lists import delete_one, delete_rec, list_boxes
from mathics.eval.parts import (
    deletecases_with_levelspec,
    python_levelspec,
    set_part,
    walk_levels,
)
from mathics.eval.patterns import Matcher

SymbolDeleteCases = Symbol("System`DeleteCases")
SymbolPrepend = Symbol("System`Prepend")
SymbolPrependTo = Symbol("System`PrependTo")


class Append(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Append.html</url>

    <dl>
      <dt>'Append[$expr$, $elem$]'
      <dd>returns $expr$ with $elem$ appended.
    </dl>

    >> Append[{1, 2, 3}, 4]
     = {1, 2, 3, 4}

    'Append' works on expressions with heads other than 'List':
    >> Append[f[a, b], c]
     = f[a, b, c]

    Unlike 'Join', 'Append' does not flatten lists in $item$:
    >> Append[{a, b}, {c, d}]
     = {a, b, {c, d}}
    """

    summary_text = "add an element at the end of an expression"

    def eval(self, expr, item, evaluation):
        "Append[expr_, item_]"

        if isinstance(expr, Atom):
            evaluation.message(
                "Append", "normal", Integer1, Expression(SymbolAppend, expr, item)
            )
            return

        return expr.restructure(
            expr.head,
            list(chain(expr.elements, [item])),
            evaluation,
            deps=(expr, item),
        )


class AppendTo(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/AppendTo.html</url>

    <dl>
      <dt>'AppendTo[$s$, $elem$]'
      <dd>append $elem$ to value of $s$ and sets $s$ to the result.
    </dl>

    >> s = {};
    >> AppendTo[s, 1]
     = {1}
    >> s
     = {1}

    'Append' works on expressions with heads other than 'List':
    >> y = f[];
    >> AppendTo[y, x]
     = f[x]
    >> y
     = f[x]
    """

    attributes = A_HOLD_FIRST | A_PROTECTED

    summary_text = "add an element at the end of an stored list or expression"

    def eval(self, s, element, evaluation):
        "AppendTo[s_, element_]"
        resolved_s = s.evaluate(evaluation)
        if s == resolved_s:
            evaluation.message("AppendTo", "rvalue", s)
            return

        if not isinstance(resolved_s, Atom):
            result = Expression(
                SymbolSet, s, Expression(SymbolAppend, resolved_s, element)
            )
            return result.evaluate(evaluation)

        evaluation.message(
            "AppendTo", "normal", Integer1, Expression(SymbolAppendTo, s, element)
        )


class Cases(Builtin):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/Cases.html</url>

    <dl>
      <dt>'Cases[$list$, $pattern$]'
      <dd>returns the elements of $list$ that match $pattern$.

      <dt>'Cases[$list$, $pattern$, $ls$]'
      <dd>returns the elements matching at levelspec $ls$.

      <dt>'Cases[$list$, $pattern$, Heads->$bool$]'
      <dd>Match including the head of the expression in the search.
    </dl>

    >> Cases[{a, 1, 2.5, "string"}, _Integer|_Real]
     = {1, 2.5}
    >> Cases[_Complex][{1, 2I, 3, 4-I, 5}]
     = {2 I, 4 - I}

    Find symbols among the elements of an expression:
    >> Cases[{b, 6, \[Pi]}, _Symbol]
     = {b, Pi}

    Also include the head of the expression in the previous search:
    >> Cases[{b, 6, \[Pi]}, _Symbol, Heads -> True]
     = {List, b, Pi}
    """

    rules = {
        "Cases[pattern_][list_]": "Cases[list, pattern]",
    }

    options = {
        "Heads": "False",
    }

    summary_text = "list elements matching a pattern"

    def eval(self, items, pattern, ls, evaluation, options):
        "Cases[items_, pattern_, ls_:{1}, OptionsPattern[]]"
        if isinstance(items, Atom):
            return ListExpression()

        if ls.has_form("Rule", 2):
            if ls.elements[0].get_name() == "System`Heads":
                heads = ls.elements[1] is SymbolTrue
                ls = ListExpression(Integer1)
            else:
                evaluation.message("Position", "level", ls)
                return
        else:
            heads = self.get_option(options, "Heads", evaluation) is SymbolTrue

        try:
            start, stop = python_levelspec(ls)
        except InvalidLevelspecError:
            evaluation.message("Position", "level", ls)
            return

        results = []

        if pattern.has_form("Rule", 2) or pattern.has_form("RuleDelayed", 2):
            match = Matcher(pattern.elements[0], evaluation).match
            rule = Rule(pattern.elements[0], pattern.elements[1])

            def callback(level):
                if match(level, evaluation):
                    result = rule.apply(level, evaluation)
                    result = result.evaluate(evaluation)
                    results.append(result)
                return level

        else:
            match = Matcher(pattern, evaluation).match

            def callback(level):
                if match(level, evaluation):
                    results.append(level)
                return level

        walk_levels(items, start, stop, heads=heads, callback=callback)

        return ListExpression(*results)


class Count(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Count.html</url>

    <dl>
      <dt>'Count[$list$, $pattern$]'
      <dd>returns the number of times $pattern$ appears in $list$.

      <dt>'Count[$list$, $pattern$, $ls$]'
      <dd>counts the elements matching at levelspec $ls$.
    </dl>

    >> Count[{3, 7, 10, 7, 5, 3, 7, 10}, 3]
     = 2

    >> Count[{{a, a}, {a, a, a}, a}, a, {2}]
     = 5
    """

    rules = {
        "Count[pattern_][list_]": "Count[list, pattern]",
        "Count[list_, arguments__]": "Length[Cases[list, arguments]]",
    }
    summary_text = "count the number of occurrences of a pattern"


class Delete(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Delete.html</url>

    <dl>
      <dt>'Delete[$expr$, $i$]'
      <dd>deletes the element at position $i$ in $expr$. The position is counted from the end if $i$ is negative.
      <dt>'Delete[$expr$, {$m$, $n$, ...}]'
      <dd>deletes the element at position {$m$, $n$, ...}.
      <dt>'Delete[$expr$, {{$m1$, $n1$, ...}, {$m2$, $n2$, ...}, ...}]'
      <dd>deletes the elements at several positions.
    </dl>

    Delete the element at position 3:
    >> Delete[{a, b, c, d}, 3]
     = {a, b, d}

    Delete at position 2 from the end:
    >> Delete[{a, b, c, d}, -2]
     = {a, b, d}

    Delete at positions 1 and 3:
    >> Delete[{a, b, c, d}, {{1}, {3}}]
     = {b, d}

    Delete in a 2D array:
    >> Delete[{{a, b}, {c, d}}, {2, 1}]
     = {{a, b}, {d}}

    Deleting the head of a whole expression gives a Sequence object:
    >> Delete[{a, b, c}, 0]
     = Sequence[a, b, c]

    Delete in an expression with any head:
    >> Delete[f[a, b, c, d], 3]
     = f[a, b, d]

    Delete a head to splice in its arguments:
    >> Delete[f[a, b, u + v, c], {3, 0}]
     = f[a, b, u, v, c]

    >> Delete[{a, b, c}, 0]
     = Sequence[a, b, c]

    Delete without the position:
    >> Delete[{a, b, c, d}]
     : Delete called with 1 argument; 2 arguments are expected.
     = Delete[{a, b, c, d}]

    Delete with many arguments:
    >> Delete[{a, b, c, d}, 1, 2]
     : Delete called with 3 arguments; 2 arguments are expected.
     = Delete[{a, b, c, d}, 1, 2]

    Delete the element out of range:
    >> Delete[{a, b, c, d}, 5]
     : Part {5} of {a, b, c, d} does not exist.
     = Delete[{a, b, c, d}, 5]

    #> Delete[{a, b, c, d}, {1, 2}]
     : Part 2 of {a, b, c, d} does not exist.
     = Delete[{a, b, c, d}, {1, 2}]

    Delete the position not integer:
    >> Delete[{a, b, c, d}, {1, n}]
     : Position specification n in {a, b, c, d} is not a machine-sized integer or a list of machine-sized integers.
     = Delete[{a, b, c, d}, {1, n}]
    """

    messages = {
        # FIXME: This message doesn't exist in more modern WMA, and
        # Delete *can* take more than 2 arguments.
        "argr": "Delete called with 1 argument; 2 arguments are expected.",
        "argt": "Delete called with `1` arguments; 2 arguments are expected.",
        "pkspec": "The expression `1` cannot be used as a part specification. Use `2` instead.",
    }
    summary_text = "delete elements from a list at given positions"

    def eval_one(self, expr, position: Integer, evaluation):
        "Delete[expr_, position_Integer]"
        pos = position.value
        try:
            return delete_one(expr, pos)
        except PartRangeError:
            evaluation.message("Part", "partw", ListExpression(position), expr)
        except PartDepthError:
            evaluation.message("Part", "partw", ListExpression(position), expr)

    def eval(self, expr, positions, evaluation):
        "Delete[expr_, positions___]"
        positions = positions.get_sequence()
        if len(positions) > 1:
            evaluation.message("Delete", "argt", Integer(len(positions) + 1))
            return
        elif len(positions) == 0:
            evaluation.message("Delete", "argr")
            return

        positions = positions[0]
        if not positions.has_form("List", None):
            evaluation.message(
                "Delete", "pkspec", positions, Expression(SymbolKey, positions)
            )
            return

        elements = positions.elements
        if len(elements) == 0:
            return expr

        # Create new python list of the positions and sort it

        positions = (
            [t for t in elements]
            if isinstance(elements[0], ListExpression)
            else [positions]
        )
        positions.sort(key=lambda e: e.get_sort_key(pattern_sort=True))
        newexpr = expr
        for position in positions:
            pos = [p.get_int_value() for p in position.get_elements()]
            if None in pos:
                evaluation.message(
                    "Delete", "psl", position.elements[pos.index(None)], expr
                )
                return
            if len(pos) == 0:
                evaluation.message("Delete", "psl", ListExpression(*positions), expr)
                return
            try:
                newexpr = delete_rec(newexpr, pos)
            except PartDepthError as exc:
                evaluation.message("Part", "partw", Integer(exc.index), expr)
                return
            except PartError:
                evaluation.message(
                    "Part", "partw", ListExpression(*(Integer(p) for p in pos)), expr
                )
                return
        return newexpr


# TODO: seems to want to produces a fancy box for failure.
#    rules = {'Failure /: MakeBoxes[Failure[tag_, assoc_Association], StandardForm]' :
# 		'With[{msg = assoc["MessageTemplate"], msgParam = assoc["MessageParameters"], type = assoc["Type"]}, ToBoxes @ Interpretation["Failure" @ Panel @ Grid[{{Style["\[WarningSign]", "Message", FontSize -> 35], Style["Message:", FontColor->GrayLevel[0.5]], ToString[StringForm[msg, Sequence @@ msgParam], StandardForm]}, {SpanFromAbove, Style["Tag:", FontColor->GrayLevel[0.5]], ToString[tag, StandardForm]},{SpanFromAbove,Style["Type:", FontColor->GrayLevel[0.5]],ToString[type, StandardForm]}},Alignment -> {Left, Top}], Failure[tag, assoc]] /; msg =!= Missing["KeyAbsent", "MessageTemplate"] && msgParam =!= Missing["KeyAbsent", "MessageParameters"] && msgParam =!= Missing["KeyAbsent", "Type"]]',
#     }


class DeleteCases(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/DeleteCases.html</url>

    <dl>
      <dt>'DeleteCases[$list$, $pattern$]'
      <dd>returns the elements of $list$ that do not match $pattern$.

      <dt>'DeleteCases[$list$, $pattern$, $levelspec$]'
      <dd> removes all parts of $list on levels specified by $levelspec$ that match pattern (not fully implemented).

      <dt>'DeleteCases[$list$, $pattern$, $levelspec$, $n$]'
      <dd> removes the first $n$ parts of $list$ that match $pattern$.
    </dl>

    >> DeleteCases[{a, 1, 2.5, "string"}, _Integer|_Real]
     = {a, string}

    >> DeleteCases[{a, b, 1, c, 2, 3}, _Symbol]
     = {1, 2, 3}
    """

    messages = {
        "level": "Level specification `1` is not of the form n, {n}, or {m, n}.",
    }
    summary_text = "delete all occurrences of a pattern"

    def eval_ls_n(self, items, pattern, levelspec, n, evaluation):
        "DeleteCases[items_, pattern_, levelspec_:1, n_:System`Infinity]"

        if isinstance(items, Atom):
            evaluation.message(
                "DeleteCases",
                "normal",
                Integer1,
                Expression(SymbolDeleteCases, items, pattern, levelspec, n),
            )
            return
        # If levelspec is specified to a non-trivial value,
        # we need to proceed with this complicate procedure
        # involving 1) decode what is the levelspec means
        # 2) find all the occurrences
        # 3) Set all the occurrences to ```System`Nothing```

        levelspec = python_levelspec(levelspec)

        if n is SymbolInfinity or ExpressionInfinity == n:
            n = -1
        elif isinstance(n, Integer):
            n = n.value
            if n < 0:
                evaluation.message(
                    "DeleteCases",
                    "innf",
                    Integer4,
                    Expression(
                        SymbolDeleteCases,
                        items,
                        pattern,
                        *from_python(levelspec),
                        Integer(n),
                    ),
                )
        else:
            evaluation.message(
                "DeleteCases",
                "innf",
                Integer4,
                Expression(
                    SymbolDeleteCases,
                    items,
                    pattern,
                    *from_python(levelspec),
                    Integer(n),
                ),
            )
            return SymbolNull

        if levelspec[0] != 1 or levelspec[1] != 1:
            return deletecases_with_levelspec(items, pattern, evaluation, levelspec, n)
        # A more efficient way to proceed if levelspec == 1

        match = Matcher(pattern, evaluation).match
        if n == -1:

            def cond(element):
                return not match(element, evaluation)

            return items.filter("List", cond, evaluation)
        else:

            def condn(element):
                nonlocal n
                if n == 0:
                    return True
                elif match(element, evaluation):
                    n = n - 1
                    return False
                else:
                    return True

            return items.filter("List", condn, evaluation)


class Drop(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Drop.html</url>

    <dl>
      <dt>'Drop[$list$, $n$]'
      <dd>returns $list$ with the first $n$ elements removed.
      <dt>'Drop[$list$, -$n$]'
      <dd>returns $list$ with its last $n$ elements removed.
      <dt>'Drop[$list$, {$m$, $n$}]'
      <dd>returns $list$ with elements $m$ though $n$ removed.
    </dl>

    Drop up until the third item from the beginning of a list:

    >> Drop[{a, b, c, d}, 3]
     = {d}

    Drop until the second item from the end of that list:
    >> Drop[{a, b, c, d}, -2]
     = {a, b}

    Drop from the second item to the second-to-the-end item:
    >> Drop[{a, b, c, d, e}, {2, -2}]
     = {a, e}

    Drop a submatrix:
    >> A = Table[i*10 + j, {i, 4}, {j, 4}]
     = {{11, 12, 13, 14}, {21, 22, 23, 24}, {31, 32, 33, 34}, {41, 42, 43, 44}}
    >> Drop[A, {2, 3}, {2, 3}]
     = {{11, 14}, {41, 44}}

    Dropping the 0th element does nothing, and returns the list unmodified:

    >> Drop[{a, b, c, d}, 0]
      = {a, b, c, d}

    Even if the list is empty:

    >> Drop[{}, 0]
      = {}

    See also <url>
    :'Take':
    /doc/reference-of-built-in-symbols/list-functions/elements-of-lists/take/</url>.
    """

    messages = {
        "drop": "Cannot drop positions `1` through `2` in `3`.",
    }
    summary_text = "remove a number of elements from a list"

    def eval(self, items, seqs, evaluation: Evaluation):
        "Drop[items_, seqs___]"

        if seqs is Integer0:
            return items

        seq_tuple = seqs.get_sequence()

        if isinstance(items, Atom):
            evaluation.message(
                "Drop", "normal", Integer1, Expression(SymbolDrop, items, *seq_tuple)
            )
            return

        try:
            return parts(
                items, [drop_span_selector(seq) for seq in seq_tuple], evaluation
            )
        except MessageException as e:
            e.message(evaluation)


class Extract(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Extract.html</url>

    <dl>
      <dt>'Extract[$expr$, $list$]'
      <dd>extracts parts of $expr$ specified by $list$.

      <dt>'Extract[$expr$, {$list1$, $list2$, ...}]'
      <dd>extracts a list of parts.
    </dl>

    'Extract[$expr$, $i$, $j$, ...]' is equivalent to 'Part[$expr$, {$i$, $j$, ...}]'.

    >> Extract[a + b + c, {2}]
     = b
    >> Extract[{{a, b}, {c, d}}, {{1}, {2, 2}}]
     = {{a, b}, d}
    """

    attributes = A_N_HOLD_REST | A_PROTECTED

    rules = {
        "Extract[expr_, list_List]": "Part[expr, Sequence @@ list]",
        "Extract[expr_, {lists___List}]": "Extract[expr, #]& /@ {lists}",
    }
    summary_text = "extract elements that appear at a list of positions"


class First(Builtin):
    """
    <url>:WMA link:
         https://reference.wolfram.com/language/ref/First.html</url>

    <dl>
      <dt>'First[$expr$]'
      <dd>returns the first element in $expr$.

      <dt>'First[$expr$, $def$]'
      <dd>returns the first element in $expr$ if it exists or $def$ otherwise.
    </dl>

    'First[$expr$]' is equivalent to '$expr$[[1]]'.

    >> First[{a, b, c}]
     = a

    The first argument need not be a list:
    >> First[a + b + c]
     = a

    However, the first argument must be Nonatomic when there is a single argument:
    >> First[x]
     : Nonatomic expression expected at position 1 in First[x].
     = First[x]

    Or if it is not, but a second default argument is provided, that is \
    evaluated and returned:

    >> First[10, 1+2]
     = 3

    >> First[{}]
     : {} has zero length and no first element.
     = First[{}]

    As before, the first argument is empty, but a default argument is given, \
    evaluate and return the second argument:
    >> First[{}, 1+2]
     = 3
    """

    attributes = A_HOLD_REST | A_PROTECTED
    messages = {
        "argt": "First called with `1` arguments; 1 or 2 arguments are expected.",
        "nofirst": "`1` has zero length and no first element.",
    }
    summary_text = "first element of a list or expression"

    # FIXME: the code and the code for Last are similar and can be DRY'd
    def eval(self, expr, evaluation: Evaluation, expression: Expression):
        "expression: First[expr__]"

        if isinstance(expr, Atom):
            evaluation.message("First", "normal", Integer1, expression)
            return
        expr_len = len(expr.elements)
        if expr_len == 0:
            evaluation.message("First", "nofirst", expr)
            return
        if expr_len > 2 and expr.head is SymbolSequence:
            evaluation.message("First", "argt", expr_len)
            return

        first_elem = expr.elements[0]

        if expr.head == SymbolSequence or (
            not isinstance(expr, ListExpression)
            and len == 2
            and isinstance(first_elem, Atom)
        ):
            return expr.elements[1]

        return first_elem


class FirstCase(Builtin):
    """
    <url>:WMA link:
         https://reference.wolfram.com/language/ref/FirstCase.html</url>

    <dl>
      <dt> FirstCase[{$e1$, $e2$, ...}, $pattern$]
      <dd>gives the first $ei$ to match $pattern$, or $Missing[\"NotFound\"]$ if none matching pattern is found.

      <dt> FirstCase[{$e1$,$e2$, ...}, $pattern$ -> $rhs$]
      <dd> gives the value of $rhs$ corresponding to the first $ei$ to match pattern.
      <dt> FirstCase[$expr$, $pattern$, $default$]
      <dd> gives $default$ if no element matching $pattern$ is found.

      <dt>FirstCase[$expr$, $pattern$, $default$, $levelspec$]
      <dd>finds only objects that appear on levels specified by $levelspec$.

      <dt>FirstCase[$pattern$]
      <dd>represents an operator form of FirstCase that can be applied to an expression.
    </dl>


    """

    attributes = A_HOLD_REST | A_PROTECTED
    options = Cases.options
    rules = {
        'FirstCase[expr_, pattOrRule_, Shortest[default_:Missing["NotFound"], 1],Shortest[levelspec_:{1}, 2], opts:OptionsPattern[]]': "Replace[Cases[expr, pattOrRule, levelspec, 1, opts],{{} :> default, {match_} :> match}]",
        "FirstCase[pattOrRule_][expr_]": "FirstCase[expr, pattOrRule]",
    }
    summary_text = "first element that matches a pattern"


class FirstPosition(Builtin):
    """
    <url>:WMA link:
         https://reference.wolfram.com/language/ref/FirstPosition.html</url>

    <dl>
      <dt>'FirstPosition[$expr$, $pattern$]'
      <dd>gives the position of the first element in $expr$ that matches $pattern$, or Missing["NotFound"] if no such element is found.

      <dt>'FirstPosition[$expr$, $pattern$, $default$]'
      <dd>gives default if no element matching $pattern$ is found.

      <dt>'FirstPosition[$expr$, $pattern$, $default$, $levelspec$]'
      <dd>finds only objects that appear on levels specified by $levelspec$.
    </dl>

    >> FirstPosition[{a, b, a, a, b, c, b}, b]
     = {2}

    >> FirstPosition[{{a, a, b}, {b, a, a}, {a, b, a}}, b]
     = {1, 3}

    >> FirstPosition[{x, y, z}, b]
     = Missing[NotFound]

    Find the first position at which x^2 to appears:
    >> FirstPosition[{1 + x^2, 5, x^4, a + (1 + x^2)^2}, x^2]
     = {1, 2}
    """

    messages = {
        "level": "Level specification `1` is not of the form n, {n}, or {m, n}.",
    }
    summary_text = "position of the first element matching a pattern"

    def eval(
        self,
        expr,
        pattern,
        evaluation: Evaluation,
        default=None,
        minLevel=None,
        maxLevel=None,
    ):
        "FirstPosition[expr_, pattern_]"

        if expr == pattern:
            return ListExpression()

        result = []

        def check_pattern(input_list, pat, result, beginLevel):
            for i in range(0, len(input_list.elements)):
                nested_level = beginLevel
                result.append(i + 1)
                if input_list.elements[i] == pat:
                    # found the pattern
                    if minLevel is None or nested_level >= minLevel:
                        return True

                else:
                    if isinstance(input_list.elements[i], Expression) and (
                        maxLevel is None or maxLevel > nested_level
                    ):
                        nested_level = nested_level + 1
                        if check_pattern(
                            input_list.elements[i], pat, result, nested_level
                        ):
                            return True

                result.pop()
            return False

        is_found = False
        if isinstance(expr, Expression) and (maxLevel is None or maxLevel > 0):
            is_found = check_pattern(expr, pattern, result, 1)
        if is_found:
            return to_mathics_list(*result)
        else:
            return (
                Expression(SymbolMissing, String("NotFound"))
                if default is None
                else default
            )

    def eval_default(self, expr, pattern, default, evaluation):
        "FirstPosition[expr_, pattern_, default_]"
        return self.eval(expr, pattern, evaluation, default=default)

    def eval_level(self, expr, pattern, default, level, evaluation):
        "FirstPosition[expr_, pattern_, default_, level_]"

        def is_interger_list(expr_list):
            return all(
                isinstance(expr_list.elements[i], Integer)
                for i in range(len(expr_list.elements))
            )

        if level.has_form("List", None):
            len_list = len(level.elements)
            if len_list > 2 or not is_interger_list(level):
                evaluation.message("FirstPosition", "level", level)
                return
            elif len_list == 0:
                min_Level = max_Level = None
            elif len_list == 1:
                min_Level = max_Level = level.elements[0].get_int_value()
            elif len_list == 2:
                min_Level = level.elements[0].get_int_value()
                max_Level = level.elements[1].get_int_value()
        elif isinstance(level, Integer):
            min_Level = 0
            max_Level = level.get_int_value()
        else:
            evaluation.message("FirstPosition", "level", level)
            return

        return self.eval(
            expr,
            pattern,
            evaluation,
            default=default,
            minLevel=min_Level,
            maxLevel=max_Level,
        )


# From backports in CellsToTeX. This functions provides compatibility to WMA 10.
#  TODO:
#  * Add doctests
#  * Translate to python the more complex rules
#  * Complete the support.


class Insert(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Insert.html</url>

    <dl>
      <dt>'Insert[$list$, $elem$, $n$]'
      <dd>inserts $elem$ at position $n$ in $list$. When $n$ is negative, \
          the position is counted from the end.
    </dl>

    >> Insert[{a,b,c,d,e}, x, 3]
     = {a, b, x, c, d, e}

    >> Insert[{a,b,c,d,e}, x, -2]
     = {a, b, c, d, x, e}
    """

    summary_text = "insert an element at a given position"

    def eval(self, expr, elem, n: Integer, evaluation):
        "Insert[expr_List, elem_, n_Integer]"

        py_n = n.value
        new_list = list(expr.get_elements())

        position = py_n - 1 if py_n > 0 else py_n + 1
        new_list.insert(position, elem)
        return expr.restructure(expr.head, new_list, evaluation, deps=(expr, elem))


class Last(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Last.html</url>

    <dl>
      <dt>'Last[$expr$]'
      <dd>returns the last element in $expr$.

      <dt>'Last[$expr$, $def$]'
      <dd>returns the last element in $expr$ if it exists or $def$ otherwise.
    </dl>

    'Last[$expr$]' is equivalent to '$expr$[[-1]]'.

    >> Last[{a, b, c}]
     = c

    The first argument need not be a list:
    >> Last[a + b + c]
     = c

    However, the first argument must be Nonatomic when there is a single argument:
    >> Last[10]
     : Nonatomic expression expected at position 1 in Last[10].
     = Last[10]

    Or if it is not, but a second default argument is provided, that is \
    evaluated and returned:

    >> Last[10, 1+2]
     = 3


    >> Last[{}]
     : {} has zero length and no last element.
     = Last[{}]

    As before, the first argument is empty, but since default argument is given, \
    evaluate and return the second argument:
    >> Last[{}, 1+2]
     = 3
    """

    attributes = A_HOLD_REST | A_PROTECTED
    messages = {
        "argt": "Last called with `1` arguments; 1 or 2 arguments are expected.",
        "nolast": "`1` has zero length and no last element.",
    }
    summary_text = "last element of a list or expression"

    # FIXME: the code and the code for First are similar and can be DRY'd
    def eval(self, expression: Expression, expr, evaluation: Evaluation):
        "expression: Last[expr__]"

        if isinstance(expr, Atom):
            evaluation.message("Last", "normal", Integer1, expression)
            return
        expr_len = len(expr.elements)
        if expr_len == 0:
            evaluation.message("Last", "nolast", expr)
            return
        if expr_len > 2 and expr.head is SymbolSequence:
            evaluation.message("Last", "argt", expr_len)
            return

        return expr.elements[-1]


class Length(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Length.html</url>

    <dl>
      <dt>'Length[$expr$]'
      <dd>returns the number of elements in $expr$.
    </dl>

    Length of a list:
    >> Length[{1, 2, 3}]
     = 3

    'Length' operates on the 'FullForm' of expressions:
    >> Length[Exp[x]]
     = 2
    >> FullForm[Exp[x]]
     = Power[E, x]

    The length of atoms is 0:
    >> Length[a]
     = 0

    Note that rational and complex numbers are atoms, although their
    'FullForm' might suggest the opposite:
    >> Length[1/3]
     = 0
    >> FullForm[1/3]
     = Rational[1, 3]
    """

    summary_text = "number of elements in a list or expression"

    def eval(self, expr, evaluation: Evaluation):
        """Length[expr_]"""

        if isinstance(expr, Atom):
            return Integer0
        else:
            return Integer(len(expr.elements))


class Most(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Most.html</url>

    <dl>
      <dt>'Most[$expr$]'
      <dd>returns $expr$ with the last element removed.
    </dl>

    'Most[$expr$]' is equivalent to '$expr$[[;;-2]]'.

    >> Most[{a, b, c}]
     = {a, b}
    >> Most[a + b + c]
     = a + b
    >> Most[x]
     : Nonatomic expression expected at position 1 in Most[x].
     = Most[x]
    """

    summary_text = "remove the last element"

    def eval(self, expression: Expression, expr, evaluation: Evaluation):
        "expression: Most[expr_]"

        if isinstance(expr, Atom):
            evaluation.message("Most", "normal", Integer1, expression)
            return
        return expr.slice(expr.head, slice(0, -1), evaluation)


class Part(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Part.html</url>

    <dl>
      <dt>'Part[$expr$, $i$]'
      <dd>returns part $i$ of $expr$.
    </dl>

    Extract an element from a list:
    >> A = {a, b, c, d};
    >> A[[3]]
     = c

    Negative indices count from the end:
    >> {a, b, c}[[-2]]
     = b

    'Part' can be applied on any expression, not necessarily lists.
    >> (a + b + c)[[2]]
     = b
    '$expr$[[0]]' gives the head of $expr$:
    >> (a + b + c)[[0]]
     = Plus

    Parts of nested lists:
    >> M = {{a, b}, {c, d}};
    >> M[[1, 2]]
     = b

    You can use 'Span' to specify a range of parts:
    >> {1, 2, 3, 4}[[2;;4]]
     = {2, 3, 4}
    >> {1, 2, 3, 4}[[2;;-1]]
     = {2, 3, 4}

    A list of parts extracts elements at certain indices:
    >> {a, b, c, d}[[{1, 3, 3}]]
     = {a, c, c}

    Get a certain column of a matrix:
    >> B = {{a, b, c}, {d, e, f}, {g, h, i}};
    >> B[[;;, 2]]
     = {b, e, h}

    Extract a submatrix of 1st and 3rd row and the two last columns:
    >> B = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};

    >> B[[{1, 3}, -2;;-1]]
     = {{2, 3}, {8, 9}}

    The 3d column of a matrix:
    >> {{a, b, c}, {d, e, f}, {g, h, i}}[[All, 3]]
     = {c, f, i}

    Further examples:
    >> (a+b+c+d)[[-1;;-2]]
     = 0
    >> x[[2]]
     : Part specification is longer than depth of object.
     = x[[2]]

    Assignments to parts are possible:
    >> B[[;;, 2]] = {10, 11, 12}
     = {10, 11, 12}
    >> B
     = {{1, 10, 3}, {4, 11, 6}, {7, 12, 9}}
    >> B[[;;, 3]] = 13
     = 13
    >> B
     = {{1, 10, 13}, {4, 11, 13}, {7, 12, 13}}
    >> B[[1;;-2]] = t;
    >> B
     = {t, t, {7, 12, 13}}

    >> F = Table[i*j*k, {i, 1, 3}, {j, 1, 3}, {k, 1, 3}];
    >> F[[;; All, 2 ;; 3, 2]] = t;
    >> F
     = {{{1, 2, 3}, {2, t, 6}, {3, t, 9}}, {{2, 4, 6}, {4, t, 12}, {6, t, 18}}, {{3, 6, 9}, {6, t, 18}, {9, t, 27}}}
    >> F[[;; All, 1 ;; 2, 3 ;; 3]] = k;
    >> F
     = {{{1, 2, k}, {2, t, k}, {3, t, 9}}, {{2, 4, k}, {4, t, k}, {6, t, 18}}, {{3, 6, k}, {6, t, k}, {9, t, 27}}}

    Of course, part specifications have precedence over most arithmetic operations:
    >> A[[1]] + B[[2]] + C[[3]] // Hold // FullForm
     = Hold[Plus[Part[A, 1], Part[B, 2], Part[C, 3]]]
    """

    attributes = A_N_HOLD_REST | A_PROTECTED | A_READ_PROTECTED
    summary_text = "get/set any part of an expression"

    def eval_makeboxes(self, list, i, f, evaluation):
        """MakeBoxes[Part[list_, i___],
        f:StandardForm|TraditionalForm|OutputForm|InputForm]"""

        i = i.get_sequence()
        list = Expression(SymbolMakeBoxes, list, f).evaluate(evaluation)
        if f.get_name() in ("System`OutputForm", "System`InputForm"):
            open, close = "[[", "]]"
        else:
            open, close = "\u301a", "\u301b"
        indices = list_boxes(i, f, evaluation, open, close)
        result = RowBox(list, *indices)
        return result

    def eval(self, list, i, evaluation):
        "Part[list_, i___]"

        if list is SymbolFailed:
            return
        indices = i.get_sequence()
        # How to deal with ByteArrays
        if list.get_head() is SymbolByteArray:
            list = list.evaluate(evaluation)
            if len(indices) > 1:
                print(
                    "Part::partd1: Depth of object ByteArray[<3>] "
                    + "is not sufficient for the given part specification."
                )
                return
            idx = indices[0]
            if isinstance(idx, Integer):
                idx = idx.value
                if idx == 0:
                    return SymbolByteArray
                data = list.elements[0].value
                lendata = len(data)
                if idx < 0:
                    idx = data - idx
                    if idx < 0:
                        evaluation.message("Part", "partw", i, list)
                        return
                else:
                    idx = idx - 1
                    if idx > lendata:
                        evaluation.message("Part", "partw", i, list)
                        return
                return Integer(data[idx])
            if idx is Symbol("System`All"):
                return list
            # TODO: handling ranges and lists...
            evaluation.message("Part", "notimplemented")
            return

        # Otherwise...
        result = eval_Part([list], indices, evaluation)
        if result:
            return result


class Pick(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Pick.html</url>

    <dl>
      <dt>'Pick[$list$, $sel$]'
      <dd>returns those items in $list$ that are True in $sel$.

      <dt>'Pick[$list$, $sel$, $patt$]'
      <dd>returns those items in $list$ that match $patt$ in $sel$.
    </dl>

    >> Pick[{a, b, c}, {False, True, False}]
     = {b}

    >> Pick[f[g[1, 2], h[3, 4]], {{True, False}, {False, True}}]
     = f[g[1], h[4]]

    >> Pick[{a, b, c, d, e}, {1, 2, 3.5, 4, 5.5}, _Integer]
     = {a, b, d}
    """

    summary_text = "pick out elements according to a boolean mask"

    def _do(self, items0, sel0, match, evaluation):
        def pick(items, sel):
            for x, s in zip(items, sel):
                if match(s):
                    yield x
                elif not isinstance(x, Atom) and not isinstance(s, Atom):
                    yield x.restructure(
                        x.head, pick(x.elements, s.elements), evaluation
                    )

        r = list(pick([items0], [sel0]))
        if not r:
            return Expression(SymbolSequence)
        else:
            return r[0]

    def eval(self, items, sel, evaluation):
        "Pick[items_, sel_]"
        return self._do(items, sel, lambda s: s is SymbolTrue, evaluation)

    def eval_pattern(self, items, sel, pattern, evaluation):
        "Pick[items_, sel_, pattern_]"

        match = Matcher(pattern, evaluation).match
        return self._do(items, sel, lambda s: match(s, evaluation), evaluation)


class Position(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Position.html</url>

    <dl>
      <dt>'Position[$expr$, $patt$]'
      <dd>returns the list of positions for which $expr$ matches $patt$.

      <dt>'Position[$expr$, $patt$, $ls$]'
      <dd>returns the positions on levels specified by levelspec $ls$.
    </dl>

    >> Position[{1, 2, 2, 1, 2, 3, 2}, 2]
     = {{2}, {3}, {5}, {7}}

    Find positions upto 3 levels deep:

    >> Position[{1 + Sin[x], x, (Tan[x] - y)^2}, x, 3]
     = {{1, 2, 1}, {2}}

    Find all powers of x:

    >> Position[{1 + x^2, x y ^ 2,  4 y,  x ^ z}, x^_]
     = {{1, 2}, {4}}

    Use Position as an operator:

    >> Position[_Integer][{1.5, 2, 2.5}]
     = {{2}}
    """

    options = {"Heads": "True"}

    rules = {
        "Position[pattern_][expr_]": "Position[expr, pattern]",
    }
    summary_text = "positions of matching elements"

    def eval_invalidlevel(self, patt, expr, ls, evaluation, options={}):
        "Position[expr_, patt_, ls_, OptionsPattern[Position]]"

        evaluation.message("Position", "level", ls)
        return

    def eval_level(self, expr, patt, ls, evaluation, options={}):
        """Position[expr_, patt_, Optional[Pattern[ls, _?LevelQ], {0, DirectedInfinity[1]}],
        OptionsPattern[Position]]"""

        try:
            start, stop = python_levelspec(ls)
        except InvalidLevelspecError:
            evaluation.message("Position", "level", ls)
            return

        match = Matcher(patt, evaluation).match
        result = []

        def callback(level, pos):
            if match(level, evaluation):
                result.append(pos)
            return level

        heads = self.get_option(options, "Heads", evaluation) is SymbolTrue
        walk_levels(expr, start, stop, heads=heads, callback=callback, include_pos=True)
        return from_python(result)


class Prepend(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Prepend.html</url>

    <dl>
      <dt>'Prepend[$expr$, $item$]'
      <dd>returns $expr$ with $item$ prepended to its elements.

      <dt>'Prepend[$expr$]'
      <dd>'Prepend[$elem$][$expr$]' is equivalent to 'Prepend[$expr$,$elem$]'.
    </dl>

    'Prepend' is similar to 'Append', but adds $item$ to the beginning
    of $expr$:
    >> Prepend[{2, 3, 4}, 1]
     = {1, 2, 3, 4}

    'Prepend' works on expressions with heads other than 'List':
    >> Prepend[f[b, c], a]
     = f[a, b, c]

    Unlike 'Join', 'Prepend' does not flatten lists in $item$:
    >> Prepend[{c, d}, {a, b}]
     = {{a, b}, c, d}
    """

    summary_text = "add an element at the beginning"

    def eval(self, expr, item, evaluation):
        "Prepend[expr_, item_]"

        if isinstance(expr, Atom):
            evaluation.message(
                "Prepend", "normal", Integer1, Expression(SymbolPrepend, expr, item)
            )
            return

        return expr.restructure(
            expr.head,
            list(chain([item], expr.elements)),
            evaluation,
            deps=(expr, item),
        )


class PrependTo(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/PrependTo.html</url>

    <dl>
      <dt>'PrependTo[$s$, $item$]'
      <dd>prepends $item$ to value of $s$ and sets $s$ to the result.
    </dl>

    Assign s to a list
    >> s = {1, 2, 4, 9}
     = {1, 2, 4, 9}

    Add a new value at the beginning of the list:
    >> PrependTo[s, 0]
     = {0, 1, 2, 4, 9}

    The value assigned to s has changed:
    >> s
     = {0, 1, 2, 4, 9}

    'PrependTo' works with a head other than 'List':
    >> y = f[a, b, c];
    >> PrependTo[y, x]
     = f[x, a, b, c]
    >> y
     = f[x, a, b, c]
    """

    attributes = A_HOLD_FIRST | A_PROTECTED

    summary_text = "add an element at the beginning of an stored list or expression"

    def eval(self, s, item, evaluation):
        "PrependTo[s_, item_]"
        resolved_s = s.evaluate(evaluation)
        if s == resolved_s:
            evaluation.message("PrependTo", "rvalue", s)
            return

        if not isinstance(resolved_s, Atom):
            result = Expression(
                SymbolSet, s, Expression(SymbolPrepend, resolved_s, item)
            )
            return result.evaluate(evaluation)

        evaluation.message(
            "PrependTo", "normal", Integer1, Expression(SymbolPrependTo, s, item)
        )


class ReplacePart(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ReplacePart.html</url>

    <dl>
      <dt>'ReplacePart[$expr$, $i$ -> $new$]'
      <dd>replaces part $i$ in $expr$ with $new$.

      <dt>'ReplacePart[$expr$, {{$i$, $j$} -> $e1$, {$k$, $l$} -> $e2$}]'
      <dd>replaces parts $i$ and $j$ with $e1$, and parts $k$ and $l$ with $e2$.
    </dl>

    >> ReplacePart[{a, b, c}, 1 -> t]
     = {t, b, c}
    >> ReplacePart[{{a, b}, {c, d}}, {2, 1} -> t]
     = {{a, b}, {t, d}}
    >> ReplacePart[{{a, b}, {c, d}}, {{2, 1} -> t, {1, 1} -> t}]
     = {{t, b}, {t, d}}
    >> ReplacePart[{a, b, c}, {{1}, {2}} -> t]
     = {t, t, c}

    Delayed rules are evaluated once for each replacement:
    >> n = 1;
    >> ReplacePart[{a, b, c, d}, {{1}, {3}} :> n++]
     = {1, b, 2, d}

    Non-existing parts are simply ignored:
    >> ReplacePart[{a, b, c}, 4 -> t]
     = {a, b, c}
    You can replace heads by replacing part 0:
    >> ReplacePart[{a, b, c}, 0 -> Times]
     = a b c
    (This is equivalent to 'Apply'.)

    Negative part numbers count from the end:
    >> ReplacePart[{a, b, c}, -1 -> t]
     = {a, b, t}
    """

    messages = {
        "reps": "`1` is not a list of replacement rules.",
    }

    rules = {
        "ReplacePart[expr_, (Rule|RuleDelayed)[i_, new_]]": (
            "ReplacePart[expr, {i -> new}]"
        ),
        "ReplacePart[expr_, Pattern[rule, "
        "Rule|RuleDelayed][{indices___?(Head[#]===List&)}, new_]]": (
            "ReplacePart[expr, rule[#, new]& /@ {indices}]"
        ),
    }
    summary_text = "replace elements at given positions"

    def eval(self, expr, replacements, evaluation):
        "ReplacePart[expr_, {replacements___}]"

        new_expr = expr.copy()
        replacements = replacements.get_sequence()
        for replacement in replacements:
            if not replacement.has_form("Rule", 2) and not replacement.has_form(  # noqa
                "RuleDelayed", 2
            ):
                evaluation.message("ReplacePart", "reps", ListExpression(*replacements))
                return
            position = replacement.elements[0]
            replace = replacement.elements[1]
            if position.has_form("List", None):
                position = position.get_mutable_elements()
            else:
                position = [position]
            for index, pos in enumerate(position):
                value = pos.get_int_value()
                if value is None:
                    position = None
                    break
                else:
                    position[index] = value
            if position is None:
                continue
            try:
                if replacement.get_head_name() == "System`RuleDelayed":
                    replace_value = replace.evaluate(evaluation)
                else:
                    replace_value = replace
                new_expr = set_part(new_expr, position, replace_value)
            except PartError:
                pass

        return new_expr


class Rest(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Rest.html</url>

    <dl>
      <dt>'Rest[$expr$]'
      <dd>returns $expr$ with the first element removed.
    </dl>

    'Rest[$expr$]' is equivalent to '$expr$[[2;;]]'.

    >> Rest[{a, b, c}]
     = {b, c}
    >> Rest[a + b + c]
     = b + c
    >> Rest[x]
     : Nonatomic expression expected at position 1 in Rest[x].
     = Rest[x]
    >> Rest[{}]
     : Cannot take Rest of expression {} with length zero.
     = Rest[{}]
    """

    messages = {
        "norest": "Cannot take Rest of expression `1` with length zero.",
    }
    summary_text = "remove the first element"

    def eval(self, expr, evaluation: Evaluation, expression: Expression):
        "expression: Rest[expr_]"

        if isinstance(expr, Atom):
            evaluation.message("Rest", "normal", Integer1, expression)
            return
        if len(expr.elements) == 0:
            evaluation.message("Rest", "norest", expr)
            return

        return expr.slice(expr.head, slice(1, len(expr.elements)), evaluation)


class Select(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Select.html</url>

    <dl>
      <dt>'Select[{$e1$, $e2$, ...}, $crit$]'
      <dd>returns a list of the elements $ei$ for which $crit$[$ei$] is 'True'.
      <dt>'Select[{$e1$, $e2$, ...}, $crit$, n]'
      <dd>returns a list of the first $n$ elements $ei$ for which $crit$[$ei$] is 'True'.
    </dl>

    Get a list of even numbers up to 10:
    >> Select[Range[10], EvenQ]
     = {2, 4, 6, 8, 10}

    Find numbers that are greater than zero in a list:
    >> Select[{-3, 0, 10, 3, a}, #>0&]
     = {10, 3}

    Find the first number that is list greater than zero in a list:
    >> Select[{-3, 0, 10, 3, a}, #>0&, 1]
     = {10}

    'Select' works on an expression with any head:
    >> Select[f[a, 2, 3], NumberQ]
     = f[2, 3]
    """

    summary_text = "pick elements according to a criterion"

    def eval(self, items, expr, evaluation: Evaluation):
        "Select[items_, expr_]"

        return self.eval_with_n(items, expr, SymbolInfinity, evaluation)

    def eval_with_n(self, items, expr, n, evaluation: Evaluation):
        "Select[items_, expr_, n_]"

        count_is_valid = True
        if n is SymbolInfinity or ExpressionInfinity == n:
            count = None
        elif isinstance(n, Integer):
            count = n.value
            if count < 0:
                count_is_valid = False
        else:
            count_is_valid = False

        if not count_is_valid:
            evaluation.message(
                "Select", "innf", Integer3, Expression(SymbolSelect, items, expr, n)
            )
            return

        if isinstance(items, Atom):
            evaluation.message(
                "Select", "normal", Integer1, Expression(SymbolSelect, items, expr, n)
            )
            return

        def cond(element):
            test = Expression(expr, element)
            return test.evaluate(evaluation) is SymbolTrue

        return items.filter(items.head, cond, evaluation, count=count)


class Span(InfixOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Span.html</url>

    <dl>
      <dt>'Span'
      <dd>is the head of span ranges like '1;;3'.
    </dl>

    >> ;; // FullForm
     = Span[1, All]
    >> 1;;4;;2 // FullForm
     = Span[1, 4, 2]
    >> 2;;-2 // FullForm
     = Span[2, -2]
    >> ;;3 // FullForm
     = Span[1, 3]
    """

    summary_text = "general specification for spans or blocks of elements"


class Take(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Take.html</url>

    <dl>
      <dt>'Take[$expr$, $n$]'
      <dd>returns $expr$ with all but the first $n$ elements removed.
      <dt>'Take[$list$, -$n$]'
      <dd>returns last $n$ elements of $list$.
      <dt>'Take[$list$, {$m$, $n$}]'
      <dd>returns elements $m$ through $n$ of $list$.
    </dl>

    Get the first three elements:
    >> Take[{a, b, c, d}, 3]
     = {a, b, c}

    Get the last two elements:
    >> Take[{a, b, c, d}, -2]
     = {c, d}

    Get the elements from the second element through the next to last element:
    >> Take[{a, b, c, d, e}, {2, -2}]
     = {b, c, d}

    Take a submatrix:
    >> A = {{a, b, c}, {d, e, f}};
    >> Take[A, 2, 2]
     = {{a, b}, {d, e}}

    Take a single column:
    >> Take[A, All, {2}]
     = {{b}, {e}}

    Taking the 0th element does nothing, and returns an empty list:

    >> Take[{a, b, c, d}, 0]
      = {}

    See also <url>
    :'Drop':
    /doc/reference-of-built-in-symbols/list-functions/elements-of-lists/drop/</url>.
    """

    summary_text = "pick a range of elements"

    def eval(self, items, seqs, evaluation):
        "Take[items_, seqs___]"

        if seqs is Integer0:
            return ListExpression()

        seqs = seqs.get_sequence()

        if isinstance(items, Atom):
            evaluation.message(
                "Take", "normal", Integer1, Expression(SymbolTake, items, *seqs)
            )
            return

        try:
            return parts(items, [take_span_selector(seq) for seq in seqs], evaluation)
        except MessageException as e:
            e.message(evaluation)


class UpTo(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/UpTo.html</url>

    <dl>
      <dd> 'UpTo'[$n$]
      <dt> is a symbolic specification that represents up to $n$ objects or \
           positions. If $n$ objects or positions are available, all are used. \
           If fewer are available, only those available are used.
    </dl>
    """

    # TODO: is there as way we can use general's innf?
    messages = {
        "innf": "Expected non-negative integer or infinity at position 1 in ``.",
        "argx": "UpTo expects 1 argument, `1` arguments were given.",
    }
    summary_text = "a certain number of elements, or as many as are available"


# TODO: ArrayRules, BinLists, Ordering, Position, SelectFirst,
#       TakeDrop, TakeList, TakeWhile
