# -*- coding: utf-8 -*-
"""
Definition Attributes

While a definition like 'cube[x_] = x^3' gives a way to specify \
<em>values</em> of a function, <em>attributes</em> allow a way to \
specify general properties of functions and symbols. This is \
independent of the parameters they take and the values they produce.

The builtin-attributes having a predefined meaning in \\Mathics which \
are described below.

However in contrast to \\Mathematica, you can set any symbol as an attribute.
"""

# This tells documentation how to sort this module
sort_order = "mathics.builtin.definition-attributes"


from mathics.core.assignment import get_symbol_list
from mathics.core.atoms import String
from mathics.core.attributes import (
    A_HOLD_ALL,
    A_HOLD_FIRST,
    A_LISTABLE,
    A_LOCKED,
    A_PROTECTED,
    attribute_string_to_number,
    attributes_bitset_to_list,
)
from mathics.core.builtin import Builtin, Predefined
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolNull

SymbolClearAttributes = Symbol("ClearAttributes")
SymbolSetAttributes = Symbol("SetAttributes")
SymbolProtected = Symbol("Protected")


class Attributes(Builtin):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/Attributes.html</url>

    <dl>
      <dt>'Attributes'[$symbol$]
      <dd>returns the attributes of $symbol$.

      <dt>'Attributes'["$string$"]
      <dd>returns the attributes of 'Symbol'["$string$"].

      <dt>'Attributes'[$symbol$] = {$attr_1$, $attr_2$}
      <dd>sets the attributes of $symbol$, replacing any existing attributes.
    </dl>

    >> Attributes[Plus]
     = {Flat, Listable, NumericFunction, OneIdentity, Orderless, Protected}

    >> Attributes["Plus"]
     = {Flat, Listable, NumericFunction, OneIdentity, Orderless, Protected}

    'Attributes' always considers the head of an expression:
    >> Attributes[a + b + c]
     = {Flat, Listable, NumericFunction, OneIdentity, Orderless, Protected}

    You can assign values to 'Attributes' to set attributes:

    >> Attributes[f] = {Flat, Orderless}
     = {Flat, Orderless}
    >> f[b, f[a, c]]
     = f[a, b, c]
    Attributes must be symbols:
    >> Attributes[f] := {a + b}
     : Argument a + b at position 1 is expected to be a symbol.
     = $Failed
    Use 'Symbol' to convert strings to symbols:
    >> Attributes[f] = Symbol["Listable"]
     = Listable
    >> Attributes[f]
     = {Listable}
    """

    attributes = A_HOLD_ALL | A_LISTABLE | A_PROTECTED
    messages = {
        "attnf": "`1` is not a known attribute.",
    }
    summary_text = "find the attributes of a symbol"

    def eval(self, expr, evaluation):
        "Attributes[expr_]"

        if isinstance(expr, String):
            expr = Symbol(expr.value)
        name = expr.get_lookup_name()

        attributes = attributes_bitset_to_list(
            evaluation.definitions.get_attributes(name)
        )
        attributes_symbols = [Symbol(attribute) for attribute in attributes]
        return ListExpression(*attributes_symbols)


class ClearAttributes(Builtin):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/ClearAttributes.html</url>

    <dl>
      <dt>'ClearAttributes'[$symbol$, $attrib$]
      <dd>removes $attrib$ from $symbol$'s attributes.
    </dl>

    >> SetAttributes[f, Flat]
    >> Attributes[f]
     = {Flat}
    >> ClearAttributes[f, Flat]
    >> Attributes[f]
     = {}
    Attributes that are not even set are simply ignored:
    >> ClearAttributes[{f}, {Flat}]
    >> Attributes[f]
     = {}
    """

    attributes = A_HOLD_FIRST | A_PROTECTED
    summary_text = "clear the attributes of a symbol"

    def eval(self, symbols, attributes, evaluation):
        "ClearAttributes[symbols_, attributes_]"

        symbols = get_symbol_list(
            symbols, lambda item: evaluation.message("ClearAttributes", "sym", item, 1)
        )
        if symbols is None:
            return
        values = get_symbol_list(
            attributes,
            lambda item: evaluation.message("ClearAttributes", "sym", item, 2),
        )
        if values is None:
            return
        for symbol in symbols:
            if A_LOCKED & evaluation.definitions.get_attributes(symbol):
                evaluation.message("ClearAttributes", "locked", Symbol(symbol))
            else:
                for value in values:
                    try:
                        evaluation.definitions.clear_attribute(
                            symbol, attribute_string_to_number[value]
                        )
                    except KeyError:
                        evaluation.message("Attributes", "attnf", Symbol(value))
        return SymbolNull


class Constant(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Constant.html</url>

    <dl>
      <dt>'Constant'
      <dd>is an attribute that indicates that a symbol is a constant.
    </dl>

    Mathematical constants like 'E' have attribute 'Constant':
    >> Attributes[E]
     = {Constant, Protected, ReadProtected}

    Constant symbols cannot be used as variables in 'Solve' and
    related functions:
    >> Solve[x + E == 0, E]
     : E is not a valid variable.
     = Solve[x + E == 0, E]
    """

    summary_text = "treat as a constant in differentiation, etc"


class Flat(Predefined):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/Flat.html</url>

    <dl>
      <dt>'Flat'
      <dd>is an attribute that specifies that nested occurrences of \
        a function should be automatically flattened.
    </dl>

    A symbol with the 'Flat' attribute represents an associative \
    mathematical operation:

    >> SetAttributes[f, Flat]
    >> f[a, f[b, c]]
     = f[a, b, c]

    'Flat' is taken into account in pattern matching:
    >> f[a, b, c] /. f[a, b] -> d
     = f[d, c]
    """

    summary_text = "attribute for associative symbols"


class HoldAll(Predefined):
    """
    <url>
     :WMA link:
      https://reference.wolfram.com/language/ref/HoldAll.html</url>

    <dl>
      <dt>'HoldAll'
      <dd>is an attribute specifying that all arguments of a \
          function should be left unevaluated.
    </dl>

    >> Attributes[Function]
     = {HoldAll, Protected}
    """

    summary_text = "attribute for symbols that keep unevaluated all their elements"


class HoldAllComplete(Predefined):
    """
    <url>
    :WMA link:
      https://reference.wolfram.com/language/ref/HoldAllComplete.html</url>

    <dl>
      <dt>'HoldAllComplete'
      <dd>is an attribute that includes the effects of 'HoldAll' and \
         'SequenceHold', and also protects the function from being \
          affected by the upvalues of any arguments.
    </dl>

    'HoldAllComplete' even prevents upvalues from being used, and \
    includes 'SequenceHold'.

    >> SetAttributes[f, HoldAllComplete]
    >> f[a] ^= 3;
    >> f[a]
     = f[a]
    >> f[Sequence[a, b]]
     = f[Sequence[a, b]]
    """

    summary_text = "attribute for symbols that keep unevaluated all \
                    their elements, and discards upvalues"


class HoldFirst(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/HoldFirst.html</url>

    <dl>
      <dt>'HoldFirst'
      <dd>is an attribute specifying that the first argument of a \
         function should be left unevaluated.
    </dl>

    >> Attributes[Set]
     = {HoldFirst, Protected, SequenceHold}
    """

    summary_text = "attribute for symbols that keep unevaluated their \
                    first element"


class HoldRest(Predefined):
    """
      <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/HoldRest.html</url>

    <dl>
      <dt>'HoldRest'
      <dd>is an attribute specifying that all but the first argument \
          of a function should be left unevaluated.
    </dl>

    >> Attributes[If]
     = {HoldRest, Protected}
    """

    summary_text = (
        "attribute for symbols that keep unevaluated all but their first element"
    )


class Listable(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Listable.html</url>

    <dl>
      <dt>'Listable'
      <dd>is an attribute specifying that a function should be \
        automatically applied to each element of a list.
    </dl>

    >> SetAttributes[f, Listable]
    >> f[{1, 2, 3}, {4, 5, 6}]
     = {f[1, 4], f[2, 5], f[3, 6]}
    >> f[{1, 2, 3}, 4]
     = {f[1, 4], f[2, 4], f[3, 4]}
    >> {{1, 2}, {3, 4}} + {5, 6}
     = {{6, 7}, {9, 10}}
    """

    summary_text = "automatically thread over lists appearing in arguments"


class Locked(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Locked.html</url>

    <dl>
      <dt>'Locked'
      <dd>is an attribute that prevents attributes on a symbol from \
        being modified.
    </dl>

    The attributes of 'Locked' symbols cannot be modified:
    >> Attributes[lock] = {Flat, Locked};
    >> SetAttributes[lock, {}]
     : Symbol lock is locked.
    >> ClearAttributes[lock, Flat]
     : Symbol lock is locked.
    >> Attributes[lock] = {}
     : Symbol lock is locked.
     = {}
    >> Attributes[lock]
     = {Flat, Locked}

    However, their values might be modified (as long as they are not 'Protected' too):
    >> lock = 3
     = 3
    """

    attributes = A_PROTECTED | A_LOCKED
    summary_text = "keep all attributes locked (settable but not clearable)"


class NHoldAll(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/NHoldAll.html</url>

    <dl>
      <dt>'NHoldAll'
      <dd>is an attribute that protects all arguments of a \
         function from numeric evaluation.
    </dl>

    >> N[f[2, 3]]
     = f[2., 3.]
    >> SetAttributes[f, NHoldAll]
    >> N[f[2, 3]]
     = f[2, 3]
    """

    summary_text = "prevent numerical evaluation of elements"


class NHoldFirst(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/NHoldFirst.html</url>

    <dl>
      <dt>'NHoldFirst'
      <dd>is an attribute that protects the first argument of a \
        function from numeric evaluation.
    </dl>
    """

    summary_text = "prevent numerical evaluation of the first element"


class NHoldRest(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/NHoldRest.html</url>

    <dl>
      <dt>'NHoldRest'
      <dd>is an attribute that protects all but the first argument
        of a function from numeric evaluation.
    </dl>
    """

    summary_text = "prevent numerical evaluation of all but the first element"


class NumericFunction(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/NumericFunction.html</url>

    <dl>
      <dt>'NumericFunction'
      <dd>is an attribute that indicates that a symbol is the head of a numeric function.
    </dl>

    Mathematical functions like 'Sqrt' have attribute 'NumericFunction':
    >> Attributes[Sqrt]
     = {Listable, NumericFunction, Protected}

    Expressions with a head having this attribute, and with all the elements \
    being numeric expressions, are considered numeric expressions:
    >> NumericQ[Sqrt[1]]
     = True
    >> NumericQ[a]=True; NumericQ[Sqrt[a]]
     = True
    >> NumericQ[a]=False; NumericQ[Sqrt[a]]
     = False
    """

    summary_text = "treat as a numeric function"


class OneIdentity(Predefined):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/OneIdentity.html</url>

    <dl>
      <dt>'OneIdentity'
      <dd>is an attribute assigned to a symbol, say $f$, indicating that $f[x]$, $f[f[x]]$, etc. are all \
          equivalent to $x$ in pattern matching.
    </dl>

    >> a /. f[x_:0, u_] -> {u}
     = a

    Here is how 'OneIdentity' changes the pattern matched above :

    >> SetAttributes[f, OneIdentity]
    >> a /. f[x_:0, u_] -> {u}
     = {a}

    However, without a default argument, the pattern does not match:
    >> a /. f[u_] -> {u}
     = a

    'OneIdentity' does not change evaluation:
    >> f[a]
     = f[a]
    """

    summary_text = "attribute for idempotent symbols"


class Orderless(Predefined):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/Orderless.html</url>

    <dl>
      <dt>'Orderless'
      <dd>is an attribute that can be assigned to a symbol $f$ to \
        indicate that the elements $ei$ in expressions of the form \
        $f$[$e_1$, $e_2$, ...] should automatically be sorted into \
        canonical order. This property is accounted for in pattern \
        matching.
    </dl>

    The elements of an 'Orderless' function are automatically sorted:
    >> SetAttributes[f, Orderless]
    >> f[c, a, b, a + b, 3, 1.0]
     = f[1., 3, a, b, c, a + b]

    A symbol with the 'Orderless' attribute represents a commutative \
    mathematical operation.
    >> f[a, b] == f[b, a]
     = True

    'Orderless' affects pattern matching:
    >> SetAttributes[f, Flat]
    >> f[a, b, c] /. f[a, c] -> d
     = f[b, d]

    """

    summary_text = "attribute for commutative symbols"


class Protect(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Protect.html</url>

    <dl>
      <dt>'Protect'[$s_1$, $s_2$, ...]
      <dd>sets the attribute 'Protected' for the symbols $si$.

      <dt>'Protect'[$str_1$, $str_2$, ...]
      <dd>protects all symbols whose names textually match $stri$.
    </dl>

    >> A = {1, 2, 3};
    >> Protect[A]
    >> A[[2]] = 4;
     : Symbol A is Protected.
    >> A
     = {1, 2, 3}
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "protect a symbol against redefinitions"

    def eval(self, symbols, evaluation):
        "Protect[symbols___]"
        protected = SymbolProtected
        items = []

        if isinstance(symbols, Symbol):
            symbols = [symbols]
        elif isinstance(symbols, String):
            symbols = [symbols]
        elif isinstance(symbols, Expression):
            if symbols.get_head_name() in ("System`Sequence", "System`List"):
                symbols = symbols.elements
            else:
                evaluation.message("Protect", "ssym", symbols)
                return SymbolNull

        for symbol in symbols:
            if isinstance(symbol, Symbol):
                items.append(symbol)
            else:
                pattern = symbol.get_string_value()
                if not pattern or pattern == "":
                    evaluation.message("Protect", "ssym", symbol)
                    continue

                if pattern[0] == "`":
                    pattern = evaluation.definitions.get_current_context() + pattern[1:]
                names = evaluation.definitions.get_matching_names(pattern)
                for defn in names:
                    symbol = Symbol(defn)
                    if not A_LOCKED & evaluation.definitions.get_attributes(defn):
                        items.append(symbol)

        Expression(SymbolSetAttributes, ListExpression(*items), protected).evaluate(
            evaluation
        )
        return SymbolNull


class Protected(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Protected.html</url>

    <dl>
      <dt>'Protected'
      <dd>is an attribute that prevents values on a symbol from
        being modified.
    </dl>

    Values of 'Protected' symbols cannot be modified:
    >> Attributes[p] = {Protected};
    >> p = 2;
     : Symbol p is Protected.
    >> f[p] ^= 3;
     : Tag p in f[p] is Protected.
    >> Format[p] = "text";
     : Symbol p is Protected.

    However, attributes might still be set:
    >> SetAttributes[p, Flat]
    >> Attributes[p]
     = {Flat, Protected}
    Thus, you can easily remove the attribute 'Protected':
    >> Attributes[p] = {};
    >> p = 2
     = 2
    You can also use 'Protect' or 'Unprotect', resp.
    >> Protect[p]
    >> Attributes[p]
     = {Protected}
    >> Unprotect[p]

    If a symbol is 'Protected' and 'Locked', it can never be changed again:
    >> SetAttributes[p, {Protected, Locked}]
    >> p = 2
     : Symbol p is Protected.
     = 2
    >> Unprotect[p]
     : Symbol p is locked.
    """

    summary_text = "attribute of protected symbols"


class ReadProtected(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ReadProtected.html</url>

    <dl>
      <dt>'ReadProtected'
      <dd>is an attribute that prevents values on a symbol from \
          being read.
    </dl>

    Values associated with 'ReadProtected' symbols cannot be seen in \
    'Definition':

    >> ClearAll[p]
    >> p = 3;
    >> Definition[p]
     = p = 3
    >> SetAttributes[p, ReadProtected]
    >> Definition[p]
     = Attributes[p] = {ReadProtected}
    """

    summary_text = "attribute of symbols with hidden definitions"


class SequenceHold(Predefined):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/SequenceHold.html</url>

    <dl>
      <dt>'SequenceHold'
      <dd>is an attribute that prevents 'Sequence' objects from being \
        spliced into a function's arguments.
    </dl>

    Normally, 'Sequence' will be spliced into a function:

    >> f[Sequence[a, b]]
     = f[a, b]
    It does not for 'SequenceHold' functions:
    >> SetAttributes[f, SequenceHold]
    >> f[Sequence[a, b]]
     = f[Sequence[a, b]]

    E.g., 'Set' has attribute 'SequenceHold' to allow assignment of sequences to variables:

    >> s = Sequence[a, b];
    >> s
     = Sequence[a, b]
    >> Plus[s]
     = a + b
    """

    summary_text = "attribute for symbols that do not expand sequences"


class SetAttributes(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SetAttributes.html</url>

    <dl>
      <dt>'SetAttributes'[$symbol$, $attrib$]
      <dd>adds $attrib$ to the list of $symbol$'s attributes.
    </dl>

    >> SetAttributes[f, Flat]
    >> Attributes[f]
     = {Flat}

    Multiple attributes can be set at the same time using lists:
    >> SetAttributes[{f, g}, {Flat, Orderless}]
    >> Attributes[g]
     = {Flat, Orderless}
    """

    attributes = A_HOLD_FIRST | A_PROTECTED

    messages = {
        "unknownattr": f"`1` should be one of {', '.join(attribute_string_to_number.keys())}"
    }
    summary_text = "set attributes for a symbol"

    def eval(self, symbols, attributes, evaluation):
        "SetAttributes[symbols_, attributes_]"

        symbols = get_symbol_list(
            symbols, lambda item: evaluation.message("SetAttributes", "sym", item, 1)
        )
        if symbols is None:
            return
        values = get_symbol_list(
            attributes, lambda item: evaluation.message("SetAttributes", "sym", item, 2)
        )
        if values is None:
            return
        for symbol in symbols:
            if A_LOCKED & evaluation.definitions.get_attributes(symbol):
                evaluation.message("SetAttributes", "locked", Symbol(symbol))
            else:
                for value in values:
                    try:
                        evaluation.definitions.set_attribute(
                            symbol, attribute_string_to_number[value]
                        )
                    except KeyError:
                        evaluation.message("Attributes", "attnf", Symbol(value))
        return SymbolNull

    def eval_arg_error(self, args, evaluation):
        "SetAttributes[args___]"
        # We should only come here when we don't have 2 args, because
        # eval() should be called otherwise.
        nargs = len(args.elements) if isinstance(args, Expression) else 1
        evaluation.message("SetAttributes", "argrx", "SetAttributes", nargs, 2)


class Unprotect(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Unprotect.html</url>

    <dl>
      <dt>'Unprotect'[$s_1$, $s_2$, ...]
      <dd>removes the attribute 'Protected' for the symbols $si$.

      <dt>'Unprotect'[$str$]
      <dd>unprotects symbols whose names textually match $str$.
    </dl>
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "remove protection against redefinitions"

    def eval(self, symbols, evaluation):
        "Unprotect[symbols___]"
        protected = SymbolProtected
        items = []
        if isinstance(symbols, Symbol):
            symbols = [symbols]
        elif isinstance(symbols, Expression):
            symbols = symbols.elements
        elif isinstance(symbols, String):
            symbols = [symbols]
        else:
            symbols = symbols.get_sequence()

        for symbol in symbols:
            if isinstance(symbol, Symbol):
                items.append(symbol)
            else:
                pattern = symbol.get_string_value()
                if not pattern or pattern == "":
                    evaluation.message("Unprotect", "ssym", symbol)
                    continue

                if pattern[0] == "`":
                    pattern = evaluation.definitions.get_current_context() + pattern[1:]
                names = evaluation.definitions.get_matching_names(pattern)
                for defn in names:
                    symbol = Symbol(defn)
                    if not A_LOCKED & evaluation.definitions.get_attributes(defn):
                        items.append(symbol)

        Expression(
            SymbolClearAttributes,
            ListExpression(*items),
            protected,
        ).evaluate(evaluation)
        return SymbolNull
