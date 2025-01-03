# -*- coding: utf-8 -*-
"""
Precedence-climbing Parsing routines for grammar symbols.

See README.md or
https://mathics-development-guide.readthedocs.io/en/latest/extending/code-overview/scanning-and-parsing.html#parser
"""


import string
from typing import Optional, Union

from mathics_scanner import InvalidSyntaxError, TranslateError
from mathics_scanner.tokeniser import Token, Tokeniser, is_symbol_name

from mathics.core.parser.ast import (
    Filename,
    Node,
    NullString,
    NullSymbol,
    Number,
    Number1,
    NumberM1,
    String,
    Symbol,
)
from mathics.core.parser.operators import (  # box_operators,  # Soon to come...
    all_operators,
    binary_operators,
    flat_binary_operators,
    inequality_operators,
    left_binary_operators,
    nonassoc_binary_operators,
    postfix_operators,
    prefix_operators,
    right_binary_operators,
    ternary_operators,
)

special_symbols = {
    "\u03C0": "Pi",  # Pi
    "\uF74D": "E",  # ExponentialE
    "\uF74E": "I",  # ImaginaryI
    "\uF74F": "I",  # ImaginaryJ
    "\u221E": "Infinity",  # Infinity
    "\u00B0": "Degree",  # Degree
}


# An operator precedence value that will ensure that whatever operator
# this is attached to does not have parenthesis surrounding it.
# Operator precedence values are integers; If if an operator
# "op" is greater than the surrounding precedence, then "op"
# will be surrounded by parenthesis, e.g. ... (...op...) ...
# In named-characters.yml of mathics-scanner we start at 0.
# However, negative values would also work.
NEVER_ADD_PARENTHESIS: int = 0

permitted_digits = {c: i for i, c in enumerate(string.digits + string.ascii_lowercase)}
permitted_digits["."] = 0


def unescape_string(s: str) -> str:
    """
    Turn a string representation with quotes and backslashes into
    the equivalent string with the quotes removed and the backslashes
    evaluated.

    For example, '"a\\n\\c"' becomes 'a\nb\nc'
    """
    assert len(s) >= 2 and s[0] == s[-1]
    s = s.encode("raw_unicode_escape").decode("unicode_escape")
    return s[1:-1]


class Parser:
    def __init__(self):
        # no implicit times on these tokens
        self.halt_tags = set(
            [
                "END",
                "RawRightAssociation",
                "RawRightParenthesis",
                "RawComma",
                "RawRightBrace",
                "RawRightBracket",
                "RawColon",
                "DifferentialD",
            ]
        )

    def parse(self, feeder):
        self.feeder = feeder
        self.tokeniser = Tokeniser(feeder)
        self.current_token = None
        self.bracket_depth = 0
        self.box_depth = 0
        return self.parse_e()

    def next(self):
        if self.current_token is None:
            self.current_token = self.tokeniser.next()
        return self.current_token

    def next_noend(self):
        "returns next token which is not END"
        while True:
            token = self.next()
            if token.tag != "END":
                return token
            self.incomplete(token.pos)

    def consume(self):
        self.current_token = None

    def incomplete(self, pos):
        self.tokeniser.incomplete()
        self.backtrack(pos)

    def expect(self, expected_tag):
        token = self.next_noend()
        if token.tag == expected_tag:
            self.consume()
        else:
            self.tokeniser.sntx_message(token.pos)
            raise InvalidSyntaxError()

    def backtrack(self, pos):
        self.tokeniser.pos = pos
        self.current_token = None

    def parse_e(self) -> Union[Node, Optional[list]]:
        """
        Parse the single top-level or "start" expression.
        """
        result = []
        while self.next().tag != "END":
            result.append(self.parse_exp(NEVER_ADD_PARENTHESIS))
        if len(result) > 1:
            return Node("Times", *result)
        if len(result) == 1:
            return result[0]
        else:
            return None

    def parse_exp(self, expr1_precedence: int) -> Optional[Node]:
        """
        Parse an expression.

        Implements grammar rules of the form:

        expr ::= <e_tag_fn(expr1)>
               | expr1 inequality_operator expr2 ...
               | expr1 binary_operator expr2 ...
               | expr1 ternary_operator expr2 ternary_operator2 expr3 ...
               | expr1 postfix_operator ...
               | expr1 expr2 ... (* implicit multiplication *)

        """
        result = self.parse_p()

        # The while loop below flattens expressions.
        while True:
            if self.bracket_depth > 0:
                token = self.next_noend()
            else:
                token = self.next()
            tag = token.tag
            method = getattr(self, "e_" + tag, None)
            if method is not None:
                new_result = method(result, token, expr1_precedence)
            elif tag in inequality_operators:
                new_result = self.parse_inequality(result, token, expr1_precedence)
            elif tag in binary_operators:
                new_result = self.parse_binary(result, token, expr1_precedence)
            elif tag in ternary_operators:
                new_result = self.parse_ternary(result, token, expr1_precedence)
            elif tag in postfix_operators:
                new_result = self.parse_postfix(result, token, expr1_precedence)
            elif (
                tag not in self.halt_tags
                and flat_binary_operators["Times"] >= expr1_precedence
            ):
                # implicit multiplication
                q = flat_binary_operators["Times"]
                child = self.parse_exp(q + 1)
                new_result = Node("Times", result, child).flatten()
            else:
                new_result = None
            if new_result is None:
                break
            else:
                result = new_result
        return result

    def parse_p(self):
        """Parse a "p_"-tagged expression.
        "p_" tags include prefix operators, left-bracketed expressions
        and tokens that can be identified by some prefix, like a number
        or a string.
        """
        token = self.next_noend()
        tag = token.tag
        method = getattr(self, "p_" + tag, None)
        if method is not None:
            return method(token)
        elif tag in prefix_operators:
            self.consume()
            q = prefix_operators[tag]
            child = self.parse_exp(q)
            return Node(tag, child)
        else:
            self.tokeniser.sntx_message(token.pos)
            raise InvalidSyntaxError()

    def parse_box(self, precedence: int) -> Union[String, Node]:
        """
        Return the parsed boxed expression for the current
        sequence of tokens.

        If there is only an Atom we return a String of that.
        Otherwise we return the Node parse expression.
        """
        result = None
        new_result = None
        while True:
            token = self.next()
            tag = token.tag
            method = getattr(self, "b_" + tag, None)
            if method is not None:
                new_result = method(result, token, precedence)
            elif tag in ("OtherscriptBox", "RightRowBox"):
                break
            elif tag == "END":
                self.incomplete(token.pos)
            elif result is None and tag != "END":
                self.consume()
                new_result = String(token.text)
                if new_result.value == r"\(":
                    new_result = self.p_LeftRowBox(token)
            else:
                new_result = None
            if new_result is None:
                break
            else:
                result = new_result
        if result is None:
            result = NullString
        return result

    def parse_seq(self) -> list:
        result: list = []
        while True:
            token = self.next_noend()
            tag = token.tag
            if tag == "RawComma":
                self.tokeniser.feeder.message("Syntax", "com")
                result.append(NullSymbol)
                self.consume()
            elif tag in ("RawRightAssociation", "RawRightBrace", "RawRightBracket"):
                if result:
                    self.tokeniser.feeder.message("Syntax", "com")
                    result.append(NullSymbol)
                break
            else:
                result.append(self.parse_exp(NEVER_ADD_PARENTHESIS))
                token = self.next_noend()
                tag = token.tag
                if tag == "RawComma":
                    self.consume()
                    continue
                elif tag in ("RawRightAssociation", "RawRightBrace", "RawRightBracket"):
                    break
        return result

    def parse_inequality(self, expr1, token: Token, p: int) -> Optional[Node]:
        tag = token.tag
        q = flat_binary_operators[tag]
        if q < p:
            return None
        self.consume()
        head = expr1.get_head_name()
        expr2 = self.parse_exp(q + 1)
        if head == "Inequality" and not expr1.parenthesised:
            expr1.children.append(Symbol(tag))
            expr1.children.append(expr2)
        elif head in inequality_operators and head != tag and not expr1.parenthesised:
            children: list = []
            first = True
            for child in expr1.children:
                if not first:
                    children.append(Symbol(head))
                children.append(child)
                first = False
            children.append(Symbol(tag))
            children.append(expr2)
            expr1 = Node("Inequality", *children)
        else:
            expr1 = Node(tag, expr1, expr2).flatten()
        return expr1

    def parse_binary(
        self, expr1, token: Token, expr1_precedence: int
    ) -> Optional[Node]:
        """
        Implements grammar rule:
           expr ::= expr1 BINARY expr2
        when it is applicable.

        When called, we have parsed expr1 and seen token BINARY. This routine will
        may cause expr2 to get scanned and parsed.

        "expr1_precendence" is the precedence of expr1 and is used whether parsing
        should be interpreted as:
            (expr1) BINARY expr2

         or:
            (expr1 BINARY expr2)


         In the former case, we will return None (no further tokens
         added) and let a higher level of parsing parse:
          (expr1) BINARY expr2.

        In the later case we will return (expr1 BINARY expr2).
        """
        tag = token.tag
        operator_precedence = binary_operators[tag]
        if expr1_precedence > operator_precedence:
            return None
        self.consume()
        if tag not in right_binary_operators:
            operator_precedence += 1
        expr2 = self.parse_exp(operator_precedence)

        # Handle nonassociative operators
        if (
            tag in nonassoc_binary_operators
            and expr1.get_head_name() == tag
            and not expr1.parenthesised
        ):
            self.tokeniser.sntx_message(token.pos)
            raise InvalidSyntaxError()

        result = Node(tag, expr1, expr2)

        # Flatten the tree if required
        if tag in flat_binary_operators:
            result.flatten()

        return result

    def parse_postfix(
        self, expr1, token: Token, expr1_precedence: int
    ) -> Optional[Node]:
        """
        Implements grammar rule:
          expr <- PREFIX_OPERATOR expr1
        when it is applicable.

        When called, we have parsed PREFIX_OPERATOR and expr1. This routine will

        "expr1_precendence" is the precedence of expr1 and is used whether parsing
        should be interpreted as:
            PREFIX_OPERATOR (expr1 ... )

         or:
            (PREFIX_OPERATOR expr1)


         In the former case, we will return None (no further tokens
         added) and let a higher level of parsing parse:
         PREFIX_OPERATOR (expr1 ...)

        In the latter case, we will return a node for (PREFIX_OPERATOR expr1).
        """
        tag = token.tag
        prefix_operator_precedence = postfix_operators[tag]
        if prefix_operator_precedence < expr1_precedence:
            return None
        self.consume()
        return Node(tag, expr1)

    def parse_ternary(
        self, expr1, token: Token, expr1_precedence: int
    ) -> Optional[Node]:
        raise NotImplementedError

    # P methods
    #
    # p_xxx methods are called from parse_p.
    # Called with one Token and return a Node.
    # Used for prefix operators, brackets and tokens which
    # can uniquely identified by a prefix character or string.

    def p_Factorial(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["Not"]
        child = self.parse_exp(q)
        return Node("Not", child)

    def p_Factorial2(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["Not"]
        child = self.parse_exp(q)
        return Node("Not", Node("Not", child))

    def p_RawLeftParenthesis(self, token: Token) -> Node:
        self.consume()
        self.bracket_depth += 1
        result = self.parse_exp(NEVER_ADD_PARENTHESIS)
        self.expect("RawRightParenthesis")
        self.bracket_depth -= 1
        assert result is not None
        result.parenthesised = True
        return result

    def p_RawLeftBrace(self, token: Token) -> Node:
        self.consume()
        self.bracket_depth += 1
        seq = self.parse_seq()
        self.expect("RawRightBrace")
        self.bracket_depth -= 1
        return Node("List", *seq)

    def p_RawLeftAssociation(self, token: Token) -> Node:
        self.consume()
        self.bracket_depth += 1
        seq = self.parse_seq()
        self.expect("RawRightAssociation")
        self.bracket_depth -= 1
        return Node("Association", *seq)

    def p_LeftRowBox(self, token: Token) -> Union[Node, String]:
        self.consume()
        children = []
        self.box_depth += 1
        self.bracket_depth += 1
        token = self.next()
        while token.tag not in ("RightRowBox", "OtherscriptBox"):
            newnode = self.parse_box(NEVER_ADD_PARENTHESIS)
            children.append(newnode)
            token = self.next()
        result: Union[Node, String]
        if len(children) == 0:
            result = NullString
        elif len(children) == 1:
            result = children[0]
        else:
            result = Node("RowBox", Node("List", *children))
        self.expect("RightRowBox")
        self.box_depth -= 1
        self.bracket_depth -= 1
        result.parenthesised = True
        return result

    def p_Number(self, token: Token) -> Number:
        s = token.text

        # sign
        if s[0] == "-":
            s = s[1:]
            sign = -1
        else:
            sign = 1

        # base
        s = s.split("^^")
        if len(s) == 1:
            base, s = 10, s[0]
        else:
            assert len(s) == 2
            base, s = int(s[0]), s[1]
            if not 2 <= base <= 36:
                self.tokeniser.feeder.message("General", "base", base, token.text, 36)
                self.tokeniser.sntx_message(token.pos)
                raise InvalidSyntaxError()

        # mantissa
        s = s.split("*^")
        if len(s) == 1:
            exp, s = 0, s[0]
        else:
            # TODO modify regex and provide error if `exp` is not an int
            exp, s = int(s[1]), s[0]

        # precision/accuracy
        s = s.split("`", 1)
        if len(s) == 1:
            s, suffix = s[0], None
        else:
            s, suffix = s[0], s[1]

        for i, c in enumerate(s.lower()):
            if permitted_digits[c] >= base:
                self.tokeniser.feeder.message("General", "digit", i + 1, s, base)
                self.tokeniser.sntx_message(token.pos)
                raise InvalidSyntaxError()

        result = Number(s, sign=sign, base=base, suffix=suffix, exp=exp)
        self.consume()
        return result

    def p_String(self, token: Token) -> String:
        result = String(unescape_string(token.text))
        self.consume()
        return result

    def p_Symbol(self, token: Token) -> Symbol:
        symbol_name = special_symbols.get(token.text, token.text)
        result = Symbol(symbol_name, context=None)
        self.consume()
        return result

    def p_Filename(self, token: Token) -> Filename:
        result = Filename(token.text)
        self.consume()
        return result

    def p_Span(self, token):
        return self.e_Span(Number1, token, 0)

    def p_Integral(self, token: Token) -> Node:
        self.consume()
        inner_prec, outer_prec = all_operators["Sum"] + 1, all_operators["Power"] - 1
        expr1 = self.parse_exp(inner_prec)
        self.expect("DifferentialD")
        expr2 = self.parse_exp(outer_prec)
        return Node("Integrate", expr1, expr2)

    def p_Pattern(self, token: Token) -> Node:
        self.consume()
        name = text = token.text
        if "." in text:
            name = text[:-2]
            if name:
                return Node(
                    "Optional",
                    Node("Pattern", Symbol(name, context=None), Node("Blank")),
                )
            else:
                return Node("Optional", Node("Blank"))
        pieces = text.split("_")
        count = len(pieces) - 1
        if count == 1:
            name = "Blank"
        elif count == 2:
            name = "BlankSequence"
        elif count == 3:
            name = "BlankNullSequence"
        if pieces[-1]:
            blank = Node(name, Symbol(pieces[-1], context=None))
        else:
            blank = Node(name)
        if pieces[0]:
            return Node("Pattern", Symbol(pieces[0], context=None), blank)
        else:
            return blank

    def p_Minus(self, token: Token) -> Optional[Node]:
        self.consume()
        q = prefix_operators["Minus"]
        expr = self.parse_exp(q)
        if isinstance(expr, Number) and not expr.value.startswith("-"):
            expr.value = "-" + expr.value
            return expr
        else:
            return Node("Times", NumberM1, expr).flatten()

    def p_Plus(self, token: Token):
        self.consume()
        q = prefix_operators["Minus"]
        # note flattening here even flattens e.g. + a + b
        return Node("Plus", self.parse_exp(q)).flatten()

    def p_PlusMinus(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["Minus"]
        return Node("PlusMinus", self.parse_exp(q))

    def p_MinusPlus(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["Minus"]
        return Node("MinusPlus", self.parse_exp(q))

    def p_Out(self, token: Token) -> Node:
        self.consume()
        text = token.text
        if text == "%":
            return Node("Out")
        if text.endswith("%"):
            n = str(-len(text))
        else:
            n = text[1:]
        return Node("Out", Number(n))

    def p_Slot(self, token: Token) -> Node:
        self.consume()
        text = token.text[1:]
        n: Union[Number, String]
        if text == "":
            n = Number1
        else:
            if text.isdigit():
                n = Number(text)
            else:
                n = String(text)
        return Node("Slot", n)

    def p_SlotSequence(self, token: Token) -> Node:
        self.consume()
        text = token.text
        if len(text) == 2:
            n = "1"
        else:
            n = text[2:]
        return Node("SlotSequence", Number(n))

    def p_Increment(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["PreIncrement"]
        return Node("PreIncrement", self.parse_exp(q))

    def p_Decrement(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["PreDecrement"]
        return Node("PreDecrement", self.parse_exp(q))

    def p_PatternTest(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["Definition"]
        child = self.parse_exp(q)
        return Node(
            "Information", child, Node("Rule", Symbol("LongForm"), Symbol("False"))
        )

    def p_Information(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["Information"]
        child = self.parse_exp(q)
        if child.__class__ is not Symbol:
            raise InvalidSyntaxError()
        return Node(
            "Information", child, Node("Rule", Symbol("LongForm"), Symbol("True"))
        )

    # E methods
    #
    # e_xxx methods are called from parse_e.
    # They expect args (Node, Token precedence) and return Node or None.
    # Used for binary and ternary operators.
    # return None if precedence is too low.

    def e_Span(self, expr1, token: Token, p) -> Optional[Node]:
        q = ternary_operators["Span"]
        if q < p:
            return None

        if expr1.get_head_name() == "Span" and not expr1.parenthesised:
            return None
        self.consume()
        # Span[expr1, expr2]
        expr2: Union[Symbol, Node, None]
        token = self.next()
        if token.tag == "Span":
            expr2 = Symbol("All")
        elif token.tag == "END" and self.bracket_depth == 0:
            # So that e.g. 'x = 1 ;;' doesn't wait for newline in the frontend
            expr2 = Symbol("All")
            return Node("Span", expr1, expr2)
        else:
            messages = list(self.feeder.messages)
            try:
                expr2 = self.parse_exp(q + 1)
            except TranslateError:
                expr2 = Symbol("All")
                self.backtrack(token.pos)
                self.feeder.messages = messages
        token = self.next()
        if token.tag == "Span":
            self.consume()
            messages = list(self.feeder.messages)
            try:
                expr3 = self.parse_exp(q + 1)
                return Node("Span", expr1, expr2, expr3)
            except TranslateError:
                self.backtrack(token.pos)
                self.feeder.messages = messages
        return Node("Span", expr1, expr2)

    def e_RawLeftBracket(self, expr, token: Token, p: int) -> Optional[Node]:
        q = all_operators["Part"]
        if q < p:
            return None
        self.consume()
        self.bracket_depth += 1
        token = self.next_noend()
        if token.tag == "RawLeftBracket":
            self.consume()
            seq = self.parse_seq()
            self.expect("RawRightBracket")
            self.expect("RawRightBracket")
            self.bracket_depth -= 1
            return Node("Part", expr, *seq)
        else:
            seq = self.parse_seq()
            self.expect("RawRightBracket")
            self.bracket_depth -= 1
            result = Node(expr, *seq)
            result.parenthesised = True
            return result

    def e_Infix(self, expr1, token: Token, expr1_precedence) -> Optional[Node]:
        """
        Implements the rule:
           expr ::= expr1 '~' expr2 '~' expr3
        when applicable.

        When called, we have parsed expr1 and seen token "~". This routine will
        may cause expr2 ~ expr3 to get scanned and parsed if applicable based on expr1_precedence.

        "expr1_precendence" is the precedence of expr1 and is used whether parsing
        should be interpreted as:
           (expr1) ~ expr2 ~ expr3

        or:
           (expr1 ~ expr2) ~ expr3

        """
        operator_precedence = ternary_operators["Infix"]
        if expr1_precedence > operator_precedence:
            return None
        self.consume()
        expr2 = self.parse_exp(operator_precedence + 1)
        self.expect("Infix")
        expr3 = self.parse_exp(operator_precedence + 1)
        return Node(expr2, expr1, expr3)

    def e_Postfix(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = left_binary_operators["Postfix"]
        if q < p:
            return None
        self.consume()
        # postix has lowest prec and is left assoc
        expr2 = self.parse_exp(q + 1)
        return Node(expr2, expr1)

    def e_Prefix(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = 640
        if 640 < p:
            return None
        self.consume()
        expr2 = self.parse_exp(q)
        return Node(expr1, expr2)

    def e_ApplyList(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = right_binary_operators["Apply"]
        if q < p:
            return None
        self.consume()
        expr2 = self.parse_exp(q)
        expr3 = Node("List", Number1)
        return Node("Apply", expr1, expr2, expr3)

    def e_Function(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = postfix_operators["Function"]
        if q < p:
            return None
        # postfix or right-binary determined by symbol
        self.consume()
        if token.text == "&":
            return Node("Function", expr1)
        else:
            expr2 = self.parse_exp(q)
            return Node("Function", expr1, expr2)

    def e_RawColon(self, expr1, token: Token, p: int) -> Optional[Node]:
        head_name = expr1.get_head_name()
        if head_name == "Symbol":
            head = "Pattern"
        elif head_name in (
            "Blank",
            "BlankSequence",
            "BlankNullSequence",
            "Pattern",
            "Optional",
        ):
            head = "Optional"
        else:
            return None
        q = all_operators[head]
        if p == 151:
            return None
        self.consume()
        expr2 = self.parse_exp(q + 1)
        return Node(head, expr1, expr2)

    def e_Semicolon(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = flat_binary_operators["CompoundExpression"]
        if q < p:
            return None
        self.consume()

        # XXX this has to come before call to self.next()
        pos = self.tokeniser.pos
        messages = list(self.feeder.messages)

        # So that e.g. 'x = 1;' doesn't wait for newline in the frontend
        tag = self.next().tag
        expr2: Union[Symbol, Node, None]
        if tag == "END" and self.bracket_depth == 0:
            expr2 = NullSymbol
            return Node("CompoundExpression", expr1, expr2).flatten()

        # XXX look for next expr otherwise backtrack
        try:
            expr2 = self.parse_exp(q + 1)
        except TranslateError:
            self.backtrack(pos)
            self.feeder.messages = messages
            expr2 = NullSymbol
        return Node("CompoundExpression", expr1, expr2).flatten()

    def e_Minus(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = left_binary_operators["Subtract"]
        if q < p:
            return None
        self.consume()
        expr2 = self.parse_exp(q + 1)
        if isinstance(expr2, Number) and not expr2.value.startswith("-"):
            expr2.value = "-" + expr2.value
        else:
            expr2 = Node("Times", NumberM1, expr2).flatten()
        return Node("Plus", expr1, expr2).flatten()

    def e_TagSet(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = all_operators["Set"]
        if q < p:
            return None
        self.consume()
        expr2 = self.parse_exp(q + 1)
        # examine next token
        token = self.next_noend()
        tag = token.tag
        if tag == "Set":
            head = "TagSet"
        elif tag == "SetDelayed":
            head = "TagSetDelayed"
        elif tag == "Unset":
            head = "TagUnset"
        else:
            self.tokeniser.sntx_message(token.pos)
            raise InvalidSyntaxError()
        self.consume()
        if head == "TagUnset":
            return Node(head, expr1, expr2)
        expr3 = self.parse_exp(q + 1)
        return Node(head, expr1, expr2, expr3)

    def e_Unset(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = all_operators["Set"]
        if q < p:
            return None
        self.consume()
        return Node("Unset", expr1)

    def e_Derivative(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = postfix_operators["Derivative"]
        if q < p:
            return None
        n = 0
        while self.next().tag == "Derivative":
            self.consume()
            n += 1
        head = Node("Derivative", Number(str(n)))
        return Node(head, expr1)

    def e_Divide(self, expr1, token: Token, p: int):
        q = left_binary_operators["Divide"]
        if q < p:
            return None
        self.consume()
        expr2 = self.parse_exp(q + 1)
        return Node("Times", expr1, Node("Power", expr2, NumberM1)).flatten()

    def e_Alternatives(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = flat_binary_operators["Alternatives"]
        if q < p:
            return None
        self.consume()
        expr2 = self.parse_exp(q + 1)
        return Node("Alternatives", expr1, expr2).flatten()

    def e_MessageName(self, expr1, token: Token, p: int) -> Node:
        elements = [expr1]
        while self.next().tag == "MessageName":
            self.consume()
            token = self.next()
            if token.tag == "Symbol":
                # silently convert Symbol to String
                self.consume()
                element = String(token.text)
            elif token.tag == "String":
                element = self.p_String(token)
            else:
                self.tokeniser.sntx_message(token.pos)
                raise InvalidSyntaxError()
            elements.append(element)
        return Node("MessageName", *elements)

    # B methods
    #
    # b_xxx methods are called from parse_box.
    # They expect args (Node, Token precedence) and return Node or None.
    # The first argument may be None if the LHS is absent.
    # Used for boxes.

    def b_SqrtBox(self, box0, token: Token, p: int) -> Optional[Node]:
        if box0 is not None:
            return None
        self.consume()
        q = all_operators["SqrtBox"]
        box1 = self.parse_box(q)
        if self.next().tag == "OtherscriptBox":
            self.consume()
            box2 = self.parse_box(q)
            return Node("RadicalBox", box1, box2)
        else:
            return Node("SqrtBox", box1)

    def b_SuperscriptBox(self, box1, token: Token, p: int) -> Optional[Node]:
        q = all_operators["SuperscriptBox"]
        if q < p:
            return None
        if box1 is None:
            box1 = NullString
        self.consume()
        box2 = self.parse_box(q)
        if self.next().tag == "OtherscriptBox":
            self.consume()
            box3 = self.parse_box(all_operators["SubsuperscriptBox"])
            return Node("SubsuperscriptBox", box1, box3, box2)
        else:
            return Node("SuperscriptBox", box1, box2)

    def b_SubscriptBox(self, box1, token: Token, p: int) -> Optional[Node]:
        q = all_operators["SubscriptBox"]
        if q < p:
            return None
        if box1 is None:
            box1 = NullString
        self.consume()
        box2 = self.parse_box(q)
        if self.next().tag == "OtherscriptBox":
            self.consume()
            box3 = self.parse_box(all_operators["SubsuperscriptBox"])
            return Node("SubsuperscriptBox", box1, box2, box3)
        else:
            return Node("SubscriptBox", box1, box2)

    def b_UnderscriptBox(self, box1, token: Token, p: int) -> Optional[Node]:
        q = all_operators["UnderscriptBox"]
        if q < p:
            return None
        if box1 is None:
            box1 = NullString
        self.consume()
        box2 = self.parse_box(q)
        if self.next().tag == "OtherscriptBox":
            self.consume()
            box3 = self.parse_box(all_operators["UnderoverscriptBox"])
            return Node("UnderoverscriptBox", box1, box2, box3)
        else:
            return Node("UnderscriptBox", box1, box2)

    def b_FractionBox(self, box1, token: Token, p: int) -> Optional[Node]:
        q = all_operators["FractionBox"]
        if q < p:
            return None
        if box1 is None:
            box1 = NullString
        self.consume()
        box2 = self.parse_box(q + 1)
        return Node("FractionBox", box1, box2)

    def b_FormBox(self, box1, token: Token, p: int) -> Optional[Node]:
        q = all_operators["FormBox"]
        if q < p:
            return None
        if box1 is None:
            box1 = Symbol("StandardForm")  # RawForm
        elif is_symbol_name(box1.value):
            box1 = Symbol(box1.value, context=None)
        else:
            box1 = Node("Removed", String("$$Failure"))
        self.consume()
        box2 = self.parse_box(q)
        return Node("FormBox", box2, box1)

    def b_OverscriptBox(self, box1, token: Token, p: int) -> Optional[Node]:
        q = all_operators["OverscriptBox"]
        if q < p:
            return None
        if box1 is None:
            box1 = NullString
        self.consume()
        box2 = self.parse_box(q)
        if self.next().tag == "OtherscriptBox":
            self.consume()
            box3 = self.parse_box(all_operators["UnderoverscriptBox"])
            return Node("UnderoverscriptBox", box1, box3, box2)
        else:
            return Node("OverscriptBox", box1, box2)
