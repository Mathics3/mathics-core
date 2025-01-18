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

from mathics.core.convert.op import builtin_constants
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
from mathics.core.parser.operators import (
    all_operators,
    binary_operators,
    box_operators,
    flat_binary_operators,
    inequality_operators,
    left_binary_operators,
    nonassoc_binary_operators,
    operator_precedences,
    postfix_operators,
    prefix_operators,
    right_binary_operators,
    ternary_operators,
)

special_symbols = builtin_constants.copy()
# FIXME: should rework so we don't have to do this
# We have the character name ImaginaryI and ImaginaryJ, but we should
# have the *operator* name, "I".
special_symbols["\uF74F"] = special_symbols["\uF74E"] = "I"


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
    # Special cases to avoid the Deprecation Warning
    if s in ('"\\!"', '"\\$"', '"\\W+"', '"\\d"'):
        return s[1:-1]

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

    def backtrack(self, pos):
        """
        Rewinds parse state (self.pos and self.current_token) so that
        another parse sequence can be considered.
        """
        assert self.tokeniser.pos >= pos
        self.tokeniser.pos = pos
        self.current_token = None  # See note below on "consume"

    def consume(self):
        """
        We mark that the current token is "consumed" by setting it
        to None.  Then, when parsing is requested, the function
        "next()" will see that the current token is None and
        read a new token".
        """
        self.current_token = None

    def expect(self, expected_tag: str):
        """
        This "expect()" function is the sort of thing one expects to see in
        top-down predictive parsing. In this kind of parsing, a "expected_tag" is, well, expected,
        and here we verify that what was expected is found. When this is not so, then we have
        a syntax error.
        """
        token = self.next_noend()
        if token.tag == expected_tag:
            self.consume()
        else:
            self.tokeniser.sntx_message(token.pos)
            raise InvalidSyntaxError()

    def incomplete(self, pos: int):
        self.tokeniser.incomplete()
        self.backtrack(pos)

    @property
    def is_inside_rowbox(self) -> bool:
        r"""
        Return True iff we parsing inside a RowBox, i.e. RowBox[...]
        or \( ... \)
        """
        return self.box_depth > 0

    def next(self) -> Token:
        if self.current_token is None:
            self.current_token = self.tokeniser.next()
        return self.current_token

    def next_noend(self) -> Token:
        "returns next token which is not END"
        while True:
            token = self.next()
            if token.tag != "END":
                return token
            self.incomplete(token.pos)

    def parse(self, feeder) -> Optional[Node]:
        """
        top-level parsing routine. This kicks off parsing
        by doing some initialization and then calling
        self.parse_e()
        """
        self.feeder = feeder
        self.tokeniser = Tokeniser(feeder)
        self.current_token = None
        self.bracket_depth = 0
        self.box_depth = 0
        return self.parse_e()

    def parse_e(self) -> Optional[Node]:
        """
        Parse the single top-level or "start" expression.
        This is called right after doing parse setup.
        """
        result = []
        while self.next().tag != "END":
            result.append(self.parse_expr(NEVER_ADD_PARENTHESIS))
        if len(result) > 1:
            return Node("Times", *result)
        if len(result) == 1:
            return result[0]
        else:
            return None

    def parse_binary_operator(
        self, expr1, token: Token, expr1_precedence: int
    ) -> Optional[Node]:
        """
        Implements parsing and transformation of binary operators:
           expr1 <binary-operator> expr2
        when it is applicable.

        When called, we have parsed "expr1" and seen <binary-operator> passed as "token". This routine
        may cause expr2 to get scanned and parsed.

        "expr1_precendence" is the precedence of "expr1" and is used
        to determine whether parsing should be interpreted as:

        (... expr1) <binary-operator> expr2

        or:
           ... (expr1 <binary-operator> expr2)


        In the first case, we will return None (no further tokens
        added). A higher level will handle group (... expr1) and
        pass that as expr1 in another call to this routine.

        In this situation, this routine will get called again with a
        new expr1 that contains (... expr1).

        However, in the second case:
           ...(expr1 <binary-operator> expr2),

        we return Node(<binary-operator>, expr1, expr2)
        """
        tag = token.tag
        operator_precedence = binary_operators[tag]
        if expr1_precedence > operator_precedence:
            return None
        self.consume()
        if tag not in right_binary_operators:
            operator_precedence += 1
        expr2 = self.parse_expr(operator_precedence)

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

    def parse_box_expr(self, precedence: int) -> Union[String, Node]:
        r"""
        Parse a box expression returning an AST Node tree for this.

        If there is only an Atom we return a String of that.
        Otherwise we return an AST Node tree for this.

        This code recognizes grammar rules of the form:

        <b_tag_fn(expr1)>
        | \( box-expr \)
        | \( box-expr <box-operator> box-expr \)

        """
        result = None
        new_result = None
        while True:
            if self.is_inside_rowbox:
                token = self.next_noend()
            else:
                token = self.next()
            tag = token.tag
            method = getattr(self, "b_" + tag, None)
            if method is not None:
                new_result = method(result, token, precedence)
            elif tag in box_operators:
                new_result = self.parse_box_operator(result, token, precedence)
            elif tag in ("OtherscriptBox", "RightRowBox"):
                break
            elif tag == "END":
                self.incomplete(token.pos)
            elif result is None and tag != "END":
                self.consume()
                # TODO: handle non-box expressions inside RowBox
                # new_result = self.parse_expr(precedence)
                # if new_result is None:
                #     self.consume()
                #     new_result = String(token.text)
                #     if new_result.value == r"\(":
                #         new_result = self.p_LeftRowBox(token)
                # elif isinstance(new_result, (Symbol, Number)):
                #     new_result = String(new_result.value)
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

    def parse_box_operator(
        self, box_expr1, token: Token, box_expr1_precedence: int
    ) -> Optional[Node]:
        """
        Implements parsing and transformation of box operators:
           box_expr1 <box-operator> box_expr2
        when it is applicable.

        When called, we have parsed "box_expr1" and seen <box-operator> passed as "token". This routine
        may cause box_expr2 to get scanned and parsed.

        "box_expr1_precendence" is the precedence of "box_expr1" and is used
        to determine whether parsing should be interpreted as:

        (... box_expr1) <box-operator> box_expr2

        or:
           ... (box_expr1 <box-operator> box_expr2)

        In the first case, we will return None (no further tokens
        added). A higher level will handle group (... box_expr1) and
        pass that as box_expr1 in another call to this routine.

        In this situation, this routine will get called again with a
        new box_expr1 that contains (... box_expr1).

        However, in the second case:
           ...(box_expr1 <box-operator> box_expr2),

        we return Node(<box-operator>, expr1, expr2)
        """
        tag = token.tag
        operator_precedence = binary_operators[tag]
        if box_expr1_precedence > operator_precedence:
            return None
        self.consume()

        # We don't handle any notion of right associativity yet,
        # if there is such a thing....
        # if tag not in right_box_operators:
        #     operator_precedence += 1

        box_expr2 = self.parse_expr(operator_precedence)

        # Is there such a thing as non-associative box operators?
        # Handle nonassociative box operators
        # if (
        #     tag in nonassoc_binary_operators
        #     and expr1.get_head_name() == tag
        #     and not expr1.parenthesised
        # ):
        #     self.tokeniser.sntx_message(token.pos)
        #     raise InvalidSyntaxError()

        result = Node(tag, box_expr1, box_expr2)

        return result

    def parse_comparison(
        self, expr1, token: Token, expr1_precedence: int
    ) -> Optional[Node]:
        """
        Implements parsing and transformation of comparison (equality and inequality) operators:
           expr1 <comparison-operator> expr2
        when it is applicable.

        When called, we have parsed "expr1" and seen <comparison-operator> passed as "token". This routine
        may cause expr2 to get scanned and parsed.

        "expr1_precendence" is the precedence of "expr1" and is used
        to determine whether parsing should be interpreted as:

        (... expr1) <comparison-operator> expr2

        or:
           ... (expr1 <comparison-operator> expr2)


        In the first case, we will return None (no further tokens
        added) and a higher level of parsing resolve and parse:
           (... expr1) <comparison_operator> expr2

        In this situation, this routine will get called again with a
        new expr1 that contains (... expr1).

        In the latter case, we flatten expressions if expr1 is not
        parenthesized
        """
        tag = token.tag
        operator_precedence = flat_binary_operators[tag]
        if expr1_precedence > operator_precedence:
            return None
        self.consume()
        head = expr1.get_head_name()
        expr2 = self.parse_expr(operator_precedence + 1)
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

    def parse_expr(self, precedence: int) -> Optional[Node]:
        """
        Parse an expression returning an AST Node tree for this.

        This code recognizes grammar rules of the form:

        <e_tag_fn(expr1)>
        | expr1 inequality_operator expr2 ...
        | expr1 binary_operator expr2 ...
        | expr1 ternary_operator expr2 ternary_operator2 expr3 ...
        | expr1 postfix_operator ...
        | box-expr box-operator box-expr2 (* only if inside rowbox *)
        | expr1 expr2 ... (* implicit multiplication *)

        and transforming this into its corresponding Node S-expression form.

        "precedence" is an operator precedence of the parent node which is
        often the operator token seen just before a grouping symbol which probably
        caused "parse_expr" to get called. For example in:
            (a + b) * (c + d)
        or equivalently:
            (a + b) (c + d)
        or
            (a + b)(c + d)

        if we have been called to parse "(c + d)", "precedence" will be the
        precedence for "Times", also sometimes known as "*".
        """
        result = self.parse_p()

        # Note: Number and String below are the mathics.core.parser's Number, String and Symbol,
        # not mathics.core.atom's Number and String, and Symbol.
        if self.is_inside_rowbox and isinstance(result, (Number, Symbol)):
            result = String(result.value)

        while True:
            if self.bracket_depth > 0 or self.is_inside_rowbox:
                token = self.next_noend()
                if token.tag in ("OtherscriptBox", "RightRowBox"):
                    if self.is_inside_rowbox:
                        break
                    else:
                        self.tokeniser.sntx_message(token.pos)
                        raise InvalidSyntaxError()
            else:
                token = self.next()

            tag = token.tag
            method = getattr(self, "e_" + tag, None)
            if method is not None:
                new_result = method(result, token, precedence)
            elif tag in inequality_operators:
                new_result = self.parse_comparison(result, token, precedence)
            elif tag in binary_operators:
                new_result = self.parse_binary_operator(result, token, precedence)
            elif tag in ternary_operators:
                new_result = self.parse_ternary_operator(result, token, precedence)
            elif tag in postfix_operators:
                new_result = self.parse_postfix(result, token, precedence)
            elif (
                tag not in self.halt_tags
                and flat_binary_operators["Times"] >= precedence
            ):
                if self.is_inside_rowbox:
                    if tag in box_operators:
                        new_result = self.parse_box_operator(result, token, precedence)
                    else:
                        # Inside a RowBox, implicit multiplication is treated as
                        # concatenation.
                        child = self.parse_expr(precedence)
                        children = [result, child]
                        new_result = Node("RowBox", Node("List", *children))
                else:
                    # There is an implicit multiplication.
                    operator_precedence = flat_binary_operators["Times"]
                    child = self.parse_expr(operator_precedence + 1)
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
            operator_precedence = prefix_operators[tag]
            child = self.parse_expr(operator_precedence)
            return Node(tag, child)
        elif self.is_inside_rowbox:
            return None
        else:
            self.tokeniser.sntx_message(token.pos)
            raise InvalidSyntaxError()

    def parse_postfix(
        self, expr1, token: Token, expr1_precedence: int
    ) -> Optional[Node]:
        """Implements grammar rule:
          expr : expr1 <postfix-operator>
        when it is applicable.

        When called, we have parsed "expr1" and <prefix-operator> in "token".
        "expr1_precedence" is the precedence of expr1 and is used to determine whether parsing
        should be interpreted as:
            (... expr1) <postfix-operator>

         or:
           ... (expr1 <postfix-operator>)

        In the first case, we return None and at a higher level we may get called
        again with (... expr1) passed as a new expr1 parameter.
        In the latter case, we return Node(<postfix-operator>, expr1)
        """
        tag = token.tag
        prefix_operator_precedence = postfix_operators[tag]
        if prefix_operator_precedence < expr1_precedence:
            return None
        self.consume()
        return Node(tag, expr1)

    # Note: returning a list is different from how most other parse_ routines
    # work and it makes the type system more complicated.
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
                result.append(self.parse_expr(NEVER_ADD_PARENTHESIS))
                token = self.next_noend()
                tag = token.tag
                if tag == "RawComma":
                    self.consume()
                    continue
                elif tag in ("RawRightAssociation", "RawRightBrace", "RawRightBracket"):
                    break
        return result

    def parse_ternary_operator(
        self, expr1, token: Token, expr1_precedence: int
    ) -> Optional[Node]:
        raise NotImplementedError

    # B methods
    #
    # b_xxx methods are called from parse_box_expr.
    # They expect args (Node, Token precedence) and return Node or None.
    # The first argument may be None if the LHS is absent.
    # Used for boxes.

    def b_FormBox(
        self, box_expr1, token: Token, box_expr1_precedence: int
    ) -> Optional[Node]:
        operator_precedence = all_operators["FormBox"]
        if box_expr1_precedence > operator_precedence:
            return None
        if box_expr1 is None:
            box_expr1 = Symbol("StandardForm")  # RawForm
        elif is_symbol_name(box_expr1.value):
            box_expr1 = Symbol(box_expr1.value, context=None)
        else:
            box_expr1 = Node("Removed", String("$$Failure"))
        self.consume()
        box2 = self.parse_box_expr(operator_precedence)
        return Node("FormBox", box2, box_expr1)

    def b_FractionBox(
        self, box_expr1, token: Token, box_expr1_precendence: int
    ) -> Optional[Node]:
        operator_precedence = all_operators["FractionBox"]
        if box_expr1_precendence > operator_precedence:
            return None
        if box_expr1 is None:
            box_expr1 = NullString
        self.consume()
        box_expr2 = self.parse_box_expr(operator_precedence + 1)
        return Node("FractionBox", box_expr1, box_expr2)

    def b_OverscriptBox(
        self, box_expr1, token: Token, box_expr1_precedence: int
    ) -> Optional[Node]:
        operator_precedence = all_operators["OverscriptBox"]
        if box_expr1_precedence > operator_precedence:
            return None
        if box_expr1 is None:
            box_expr1 = NullString
        self.consume()
        box_expr2 = self.parse_box_expr(operator_precedence)
        if self.next().tag == "OtherscriptBox":
            self.consume()
            box_expr3 = self.parse_box_expr(all_operators["UnderoverscriptBox"])
            return Node("UnderoverscriptBox", box_expr1, box_expr3, box_expr2)
        else:
            return Node("OverscriptBox", box_expr1, box_expr2)

    def b_SqrtBox(self, box0, token: Token, p: int) -> Optional[Node]:
        if box0 is not None:
            return None
        self.consume()
        operator_precedence = all_operators["SqrtBox"]
        box_expr1 = self.parse_box_expr(operator_precedence)
        if self.next().tag == "OtherscriptBox":
            self.consume()
            box2 = self.parse_box_expr(operator_precedence)
            return Node("RadicalBox", box_expr1, box2)
        else:
            return Node("SqrtBox", box_expr1)

    def b_SubscriptBox(
        self, box_expr1, token: Token, box_expr1_precedence: int
    ) -> Optional[Node]:
        operator_precedence = all_operators["SubscriptBox"]
        if box_expr1_precedence > operator_precedence:
            return None
        if box_expr1 is None:
            box_expr1 = NullString
        self.consume()
        box_expr2 = self.parse_box_expr(operator_precedence)
        if self.next().tag == "OtherscriptBox":
            self.consume()
            box_expr3 = self.parse_box_expr(all_operators["SubsuperscriptBox"])
            return Node("SubsuperscriptBox", box_expr1, box_expr2, box_expr3)
        else:
            return Node("SubscriptBox", box_expr1, box_expr2)

    def b_SuperscriptBox(
        self, box_expr1, token: Token, box_expr1_precedence: int
    ) -> Optional[Node]:
        operator_precedence = all_operators["SuperscriptBox"]
        if box_expr1_precedence > operator_precedence:
            return None
        if box_expr1 is None:
            box_expr1 = NullString
        self.consume()
        box2 = self.parse_box_expr(operator_precedence)
        if self.next().tag == "OtherscriptBox":
            self.consume()
            box3 = self.parse_box_expr(all_operators["SubsuperscriptBox"])
            return Node("SubsuperscriptBox", box_expr1, box3, box2)
        else:
            return Node("SuperscriptBox", box_expr1, box2)

    def b_UnderscriptBox(
        self, box_expr1, token: Token, box_expr1_precedence: int
    ) -> Optional[Node]:
        operator_precedence = all_operators["UnderscriptBox"]
        if box_expr1_precedence > operator_precedence:
            return None
        if box_expr1 is None:
            box_expr1 = NullString
        self.consume()
        box_expr2 = self.parse_box_expr(operator_precedence)
        if self.next().tag == "OtherscriptBox":
            self.consume()
            box_expr3 = self.parse_box_expr(all_operators["UnderoverscriptBox"])
            return Node("UnderoverscriptBox", box_expr1, box_expr2, box_expr3)
        else:
            return Node("UnderscriptBox", box_expr1, box_expr2)

    # E methods
    #
    # e_xxx methods are called from parse_e.
    # They expect args (Node, Token precedence) and return Node or None.
    # Used for binary and ternary operators.
    # return None if precedence is too low.

    def e_Alternatives(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = flat_binary_operators["Alternatives"]
        if q < p:
            return None
        self.consume()
        expr2 = self.parse_expr(q + 1)
        return Node("Alternatives", expr1, expr2).flatten()

    def e_ApplyList(self, expr1, token: Token, p: int) -> Optional[Node]:
        operator_precedence = right_binary_operators["Apply"]
        if operator_precedence < p:
            return None
        self.consume()
        expr2 = self.parse_expr(operator_precedence)
        expr3 = Node("List", Number1)
        return Node("Apply", expr1, expr2, expr3)

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

    def e_Divide(self, expr1, token: Token, expr1_precedence: int):
        """
        Implements parsing and transformation of Divide
           expr1 /  expr2
        when it is applicable.

        When called, we have parsed "expr1" and seen "/" passed as "token". This routine
        may cause expr2 to get scanned and parsed.

        "expr1_precendence" is the precedence of "expr1" and is used
        to determine whether parsing should be interpreted as:

        (... expr1) / expr2

        or:
           ... (expr1 / expr2)


        In the first case, we will return None (no further tokens
        added). A higher level will handle group (... expr1) and
        pass that as expr1 in another call to this routine.

        However, in the second case:
           ...(expr1 <binary-operator> expr2),

        we return Node(Times, expr1, Node(Power, expr2, -1))
        """

        operator_precedence = left_binary_operators["Divide"]
        if expr1_precedence > operator_precedence:
            return None
        self.consume()
        expr2 = self.parse_expr(operator_precedence + 1)
        return Node("Times", expr1, Node("Power", expr2, NumberM1)).flatten()

    def e_Infix(self, expr1, token: Token, expr1_precedence) -> Optional[Node]:
        """
        Used to implement the rule:
           expr : expr1 '~' expr2 '~' expr3
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
        expr2 = self.parse_expr(operator_precedence + 1)
        self.expect("Infix")
        expr3 = self.parse_expr(operator_precedence + 1)
        return Node(expr2, expr1, expr3)

    def e_Function(self, expr1, token: Token, p: int) -> Optional[Node]:
        operator_precedence = postfix_operators["Function"]
        if operator_precedence < p:
            return None
        # postfix or right-binary determined by symbol
        self.consume()
        if token.text == "&":
            return Node("Function", expr1)
        else:
            expr2 = self.parse_expr(operator_precedence)
            return Node("Function", expr1, expr2)

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

    def e_Minus(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = left_binary_operators["Subtract"]
        if q < p:
            return None
        self.consume()
        expr2 = self.parse_expr(q + 1)
        if isinstance(expr2, Number) and not expr2.value.startswith("-"):
            expr2.value = "-" + expr2.value
        else:
            expr2 = Node("Times", NumberM1, expr2).flatten()
        return Node("Plus", expr1, expr2).flatten()

    def e_Prefix(self, expr1, token: Token, expr1_precedence: int) -> Optional[Node]:
        """
        Used to parse:
           expr1 @ expr2
        into the Node S-expression form of
           expr1(expr2)

        When called, we have parsed expr1 and seen token "@".

        "expr1_precendence" is the precedence of expr1 and is used whether parsing
        should be interpreted as:
           (... expr1) @ expr2

        or:
           ... (expr1 @ expr2)

        In the first case, we return None and at a higher level we may get called
        again with (... expr1) passed as a new expr1 parameter.
        """
        operator_precedence = flat_binary_operators["Prefix"]
        if expr1_precedence > operator_precedence:
            return None
        self.consume()
        expr2 = self.parse_expr(operator_precedence)
        return Node(expr1, expr2)

    def e_Postfix(self, expr1, token: Token, expr1_precedence: int) -> Optional[Node]:
        """
        Used to parse
           expr1 // expr2
        into the Node S-expression form of
           expr2(expr1)

        When called, we have parsed expr1 and seen token "//".

        "expr1_precendence" is the precedence of expr1 and is used whether parsing
        should be interpreted as:
           (... expr1) // expr2

        or:
           ... (expr1 // expr2)

        In the first case, we return None and at a higher level we may get called
        again with (... expr1) passed as a new expr1 parameter.
        """
        operator_precedence = left_binary_operators["Postfix"]
        if expr1_precedence > operator_precedence:
            # Mark the completion of (... expr1)
            return None

        self.consume()

        # Precedence[Postix] is lower than expr1; Postfix[] is left associative.
        expr2 = self.parse_expr(operator_precedence + 1)
        return Node(expr2, expr1)

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
        expr2 = self.parse_expr(q + 1)
        return Node(head, expr1, expr2)

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

            if self.is_inside_rowbox:
                # Handle function calls inside a RowBox.
                result = Node("List", expr, String("["), *seq, String("]"))
            else:
                result = Node(expr, *seq)

            result.parenthesised = True
            return result

    def e_Semicolon(self, expr1, token: Token, expr1_precedence: int) -> Optional[Node]:
        """
        Used to parse
           expr1 ; expr2
        into S-expression:
           CompondExpression(expr1, expr2)

        When called, we have parsed expr1 and seen token ";".

        "expr1_precendence" is the precedence of expr1 and is used whether parsing
        should be interpreted as:
           (... expr1) ; expr2

        or:
           ... (expr1 ; exp2)

        In the first case, we return None and at a higher level we may get called
        again with (... expr1) passed as a new expr1 parameter.
        In the latter case, we return Node(CompoundExpression, expr1, expr2)
        """
        operator_precedence = flat_binary_operators["CompoundExpression"]
        if expr1_precedence > operator_precedence:
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
            expr2 = self.parse_expr(operator_precedence + 1)
        except TranslateError:
            self.backtrack(pos)
            self.feeder.messages = messages
            expr2 = NullSymbol
        return Node("CompoundExpression", expr1, expr2).flatten()

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
                expr2 = self.parse_expr(q + 1)
            except TranslateError:
                expr2 = Symbol("All")
                self.backtrack(token.pos)
                self.feeder.messages = messages
        token = self.next()
        if token.tag == "Span":
            self.consume()
            messages = list(self.feeder.messages)
            try:
                expr3 = self.parse_expr(q + 1)
                return Node("Span", expr1, expr2, expr3)
            except TranslateError:
                self.backtrack(token.pos)
                self.feeder.messages = messages
        return Node("Span", expr1, expr2)

    def e_TagSet(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = all_operators["Set"]
        if q < p:
            return None
        self.consume()
        expr2 = self.parse_expr(q + 1)
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
        expr3 = self.parse_expr(q + 1)
        return Node(head, expr1, expr2, expr3)

    def e_Unset(self, expr1, token: Token, p: int) -> Optional[Node]:
        q = all_operators["Set"]
        if q < p:
            return None
        self.consume()
        return Node("Unset", expr1)

    # P methods
    #
    # p_xxx methods are called from parse_p.
    # Called with one Token and return a Node.
    # Used for prefix operators, brackets and tokens which
    # can uniquely identified by a prefix character or string.

    # FIXME DRY with pre_Decrement
    def p_Decrement(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["PreDecrement"]
        return Node("PreDecrement", self.parse_expr(q))

    def p_Increment(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["PreIncrement"]
        return Node("PreIncrement", self.parse_expr(q))

    def p_Information(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["Information"]
        child = self.parse_expr(q)
        if child.__class__ is not Symbol:
            raise InvalidSyntaxError()
        return Node(
            "Information", child, Node("Rule", Symbol("LongForm"), Symbol("True"))
        )

    def p_Integral(self, token: Token) -> Node:
        self.consume()
        inner_prec, outer_prec = all_operators["Sum"] + 1, all_operators["Power"] - 1
        expr1 = self.parse_expr(inner_prec)
        self.expect("DifferentialD")
        expr2 = self.parse_expr(outer_prec)
        return Node("Integrate", expr1, expr2)

    def p_Factorial2(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["Not"]
        child = self.parse_expr(q)
        return Node("Not", Node("Not", child))

    def p_Filename(self, token: Token) -> Filename:
        result = Filename(token.text)
        self.consume()
        return result

    def p_LeftRowBox(self, token: Token) -> Union[Node, String]:
        self.consume()
        children = []
        self.box_depth += 1
        token = self.next()
        while token.tag not in ("RightRowBox", "OtherscriptBox"):
            newnode = self.parse_box_expr(NEVER_ADD_PARENTHESIS)
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
        result.parenthesised = True
        return result

    def p_Minus(self, token: Token) -> Optional[Node]:
        """
        Used to parse:
           - expr1
        into the Node S-expression form of
           Node(Minus, expr1)
        When called, only token "-" has been seen.
        """
        self.consume()
        q = prefix_operators["Minus"]
        expr = self.parse_expr(q)
        if isinstance(expr, Number) and not expr.value.startswith("-"):
            expr.value = "-" + expr.value
            return expr
        else:
            return Node("Times", NumberM1, expr).flatten()

    def p_MinusPlus(self, token: Token) -> Node:
        """
        Used to parse:
           ∓ expr1
        into the Node S-expression form of
           Node(MinusPlus, expr1)

        When called, only token "∓" has been seen.
        """
        self.consume()
        operator_precedence = operator_precedences["UnaryMinusPlus"]
        return Node("MinusPlus", self.parse_expr(operator_precedence))

    def p_Not(self, token: Token) -> Node:
        self.consume()
        operator_precedence = prefix_operators["Not"]
        child = self.parse_expr(operator_precedence)
        return Node("Not", child)

    # p_Factorial sometimes gets called when p_Not would be more
    # appropriate. In "a;;!b" we can't tell initially if "!" is postfix
    # "Factorial" or prefix "Not".
    # See if we can fix this mess.
    p_Factorial = p_Not

    def p_Number(self, token: Token) -> Number:
        s = token.text

        # sign
        if s[0] == "-":
            s = s[1:]
            sign = -1
        else:
            sign = 1

        # base
        base_parts = s.split("^^")
        if len(base_parts) == 1:
            base, s = 10, base_parts[0]
        else:
            assert len(base_parts) == 2
            base, s = int(base_parts[0]), base_parts[1]
            if not 2 <= base <= 36:
                self.tokeniser.feeder.message("General", "base", base, token.text, 36)
                self.tokeniser.sntx_message(token.pos)
                raise InvalidSyntaxError()

        # mantissa
        mantissa_parts = s.split("*^")
        if len(mantissa_parts) == 1:
            exp, s = 0, mantissa_parts[0]
        else:
            # TODO modify regex and provide error if `exp` is not an int
            exp, s = int(mantissa_parts[1]), mantissa_parts[0]

        # precision/accuracy
        precision_accuracy = s.split("`", 1)
        if len(precision_accuracy) == 1:
            s, suffix = precision_accuracy[0], None
        else:
            s, suffix = precision_accuracy[0], precision_accuracy[1]

        for i, c in enumerate(s.lower()):
            if permitted_digits[c] >= base:
                self.tokeniser.feeder.message("General", "digit", i + 1, s, base)
                self.tokeniser.sntx_message(token.pos)
                raise InvalidSyntaxError()

        result = Number(s, sign=sign, base=base, suffix=suffix, exp=exp)
        self.consume()
        return result

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

    def p_PatternTest(self, token: Token) -> Node:
        self.consume()
        q = prefix_operators["Definition"]
        child = self.parse_expr(q)
        return Node(
            "Information", child, Node("Rule", Symbol("LongForm"), Symbol("False"))
        )

    def p_Plus(self, token: Token):
        """
        Used to parse:
           + expr1
        into the Node S-expression form of:
           Node(Plus, expr1)

        When called, only token "+" has been seen.
        """
        self.consume()
        operator_precedence = prefix_operators["UnaryPlus"]
        # note flattening here even flattens e.g. + a + b
        return Node("Plus", self.parse_expr(operator_precedence)).flatten()

    def p_PlusMinus(self, token: Token) -> Node:
        """
        Used to parse:
           ± expr1
        into the Node S-expression form of:
           Node(PlusMinus, expr1)

        When called, only token "±" has been seen.
        """
        self.consume()
        operator_precedence = operator_precedences["UnaryPlusMinus"]
        return Node("PlusMinus", self.parse_expr(operator_precedence))

    def p_RawLeftAssociation(self, token: Token) -> Node:
        self.consume()
        self.bracket_depth += 1
        seq = self.parse_seq()
        self.expect("RawRightAssociation")
        self.bracket_depth -= 1
        return Node("Association", *seq)

    def p_RawLeftBrace(self, token: Token) -> Node:
        self.consume()
        self.bracket_depth += 1
        seq = self.parse_seq()
        self.expect("RawRightBrace")
        self.bracket_depth -= 1
        return Node("List", *seq)

    def p_RawLeftParenthesis(self, token: Token) -> Node:
        self.consume()
        self.bracket_depth += 1
        result = self.parse_expr(NEVER_ADD_PARENTHESIS)
        self.expect("RawRightParenthesis")
        self.bracket_depth -= 1
        assert result is not None
        result.parenthesised = True
        return result

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

    def p_Span(self, token):
        return self.e_Span(Number1, token, 0)

    def p_String(self, token: Token) -> String:
        result = String(unescape_string(token.text))
        self.consume()
        return result

    def p_Symbol(self, token: Token) -> Symbol:
        symbol_name = special_symbols.get(token.text, token.text)
        result = Symbol(symbol_name, context=None)
        self.consume()
        return result
