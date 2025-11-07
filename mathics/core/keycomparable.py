"""
Base classes for canonical order.

"""


class KeyComparable:
    """

    Some Mathics3/WL Symbols have an "OrderLess" attribute
    which is used in the evaluation process to arrange items in a list.

    To do that, we need a way to compare Symbols, and that is what
    this class is for.

    This class adds the boilerplate Python comparison operators that
    you expect in Python programs for comparing Python objects.

    This class is not complete in of itself, it is intended to be
    mixed into other classes.

    Each class should provide a `element_order` property which
    is the primitive from which all other comparisons are based on.

    The class also contains a `pattern_precedence` property that provides
    the sort key used to order a list of rules according to the
    precedence they have in the evaluation loop.
    """

    @property
    def element_order(self) -> tuple:
        """Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.

        This is used in ``Sort[]`` comparisons and in the ordering
        that occurs in an M-Expression which has the ``Orderless``
        property.

        The encoded tuple/list is selected to have the property: when
        compared against element ``expr`` in a compound expression, if

           `self.element_order <= expr.element_order`

        then self comes before expr.

        The values in the positions of the tuple are used to indicate how
        comparison should be treated for specific element classes.

        """
        raise NotImplementedError

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        return (
            hasattr(other, "element_order")
            and self.element_order == other.element_order
        )

    def __gt__(self, other) -> bool:
        return self.element_order > other.element_order

    def __ge__(self, other) -> bool:
        return self.element_order >= other.element_order

    def __le__(self, other) -> bool:
        return self.element_order <= other.element_order

    def __lt__(self, other) -> bool:
        return self.element_order < other.element_order

    def __ne__(self, other) -> bool:
        return (
            not hasattr(other, "element_order")
        ) or self.element_order != other.element_order


class Monomial:
    """
    An object to sort monomials, used in Expression.get_sort_key and
    Symbol.get_sort_key.
    """

    def __init__(self, exps_dict):
        self.exps = exps_dict

    def __cmp(self, other) -> int:
        self_exps = self.exps.copy()
        other_exps = other.exps.copy()
        for var in self.exps:
            if var in other.exps:
                dec = min(self_exps[var], other_exps[var])
                self_exps[var] -= dec
                if not self_exps[var]:
                    del self_exps[var]
                other_exps[var] -= dec
                if not other_exps[var]:
                    del other_exps[var]
        self_exps = sorted((var, exp) for var, exp in self_exps.items())
        other_exps = sorted((var, exp) for var, exp in other_exps.items())

        index = 0
        self_len = len(self_exps)
        other_len = len(other_exps)
        while True:
            if index >= self_len and index >= other_len:
                return 0
            if index >= self_len:
                return -1  # self < other
            if index >= other_len:
                return 1  # self > other
            self_var, self_exp = self_exps[index]
            other_var, other_exp = other_exps[index]
            if self_var < other_var:
                return -1
            if self_var > other_var:
                return 1
            if self_exp != other_exp:
                if index + 1 == self_len or index + 1 == other_len:
                    # smaller exponents first
                    if self_exp < other_exp:
                        return -1
                    elif self_exp == other_exp:
                        return 0
                    else:
                        return 1
                else:
                    # bigger exponents first
                    if self_exp < other_exp:
                        return 1
                    elif self_exp == other_exp:
                        return 0
                    else:
                        return -1
            index += 1
        return 0

    def __eq__(self, other) -> bool:
        return self.__cmp(other) == 0

    def __le__(self, other) -> bool:
        return self.__cmp(other) <= 0

    def __lt__(self, other) -> bool:
        return self.__cmp(other) < 0

    def __ge__(self, other) -> bool:
        return self.__cmp(other) >= 0

    def __gt__(self, other) -> bool:
        return self.__cmp(other) > 0

    def __ne__(self, other) -> bool:
        return self.__cmp(other) != 0


###  SORT_KEYS prefix for pattern_precedence
#
# Pattern sort keys have 3 elements. The first one is a "magic" 4-bytes
# integer number representing different features of the element, like if
# it is an atom or an expression, if is an special pattern like `Blank`
# etc. The first order criteria is that these numbers are in ascending order.
# The second element is the sort_key for the head, and the third,
# is the list of sort_keys associated to each element of the expression,
# finished with ``END_OF_LIST_PATTERN_SORT_KEY`` to ensure that the longest
# list of patterns always come first.

# Let' s start by defining the basic magic numbers:

# EXPRESSION BIT
PATTERN_SORT_KEY_IS_EXPRESSION = 0x00020000
PATTERN_SORT_KEY_VERBATIM = 0x00030000
PATTERN_SORT_KEY_LAST = 0xFFFFFFFFFFFF

# Blank and friends
PATTERN_SORT_KEY_EMPTY_ALTERNATIVES = 0x00000100
PATTERN_SORT_KEY_BLANK_WITH_HEAD = 0x00000B00
PATTERN_SORT_KEY_BLANKSEQUENCE_WITH_HEAD = 0x00000C00
PATTERN_SORT_KEY_BLANKNULLSEQUENCE_WITH_HEAD = 0x00000D00

PATTERN_SORT_KEY_BLANK_PURE = 0x00001500
PATTERN_SORT_KEY_BLANKSEQUENCE_PURE = 0x00001600
PATTERN_SORT_KEY_BLANKNULLSEQUENCE_PURE = 0x00001700

# OPTIONSPATTERN
PATTERN_SORT_KEY_OPTIONSPATTERN = 0x00002800

# Lower bits
PATTERN_SORT_KEY_NOT_PATTERNTEST = 0x00000001
PATTERN_SORT_KEY_OPTIONAL = 0x00000002
PATTERN_SORT_KEY_UNNAMED_PATTERN = 0x00000004
PATTERN_SORT_KEY_INCONDITIONAL = 0x00000008

# Used to mark a magic code as conditional or pattern test
PATTERN_SORT_KEY_CONDITIONAL = PATTERN_SORT_KEY_LAST - PATTERN_SORT_KEY_INCONDITIONAL
PATTERN_SORT_KEY_PATTERNTEST = PATTERN_SORT_KEY_LAST - PATTERN_SORT_KEY_NOT_PATTERNTEST
PATTERN_SORT_KEY_NAMEDPATTERN = PATTERN_SORT_KEY_LAST - PATTERN_SORT_KEY_UNNAMED_PATTERN


# Now, the basic combinations of these magic numbers, used on sort keys

# This is the numeric magic code for any Atom.
MAGIC_ATOM_SORT_KEY = (
    PATTERN_SORT_KEY_INCONDITIONAL
    + PATTERN_SORT_KEY_UNNAMED_PATTERN
    + PATTERN_SORT_KEY_NOT_PATTERNTEST
)

# The numeric magic code for an expression
BASIC_EXPRESSION_PATTERN_SORT_KEY = MAGIC_ATOM_SORT_KEY + PATTERN_SORT_KEY_IS_EXPRESSION

# Blanks
BLANK_WITH_PATTERN_PATTERN_SORT_KEY = (
    BASIC_EXPRESSION_PATTERN_SORT_KEY + PATTERN_SORT_KEY_BLANK_WITH_HEAD
)  # Blank[A] (`pat_`)
BLANK_GENERAL_PATTERN_SORT_KEY = (
    BASIC_EXPRESSION_PATTERN_SORT_KEY + PATTERN_SORT_KEY_BLANK_PURE
)  # Blank[] (`pat_`)
BLANKSEQUENCE_WITH_PATTERN_PATTERN_SORT_KEY = (
    BASIC_EXPRESSION_PATTERN_SORT_KEY + PATTERN_SORT_KEY_BLANKSEQUENCE_WITH_HEAD
)  # BlankSequence[A] (`pat__A`)
BLANKSEQUENCE_GENERAL_PATTERN_SORT_KEY = (
    BASIC_EXPRESSION_PATTERN_SORT_KEY + PATTERN_SORT_KEY_BLANKSEQUENCE_PURE
)  # BlankSequence[] (`pat__`)

BLANKNULLSEQUENCE_WITH_PATTERN_PATTERN_SORT_KEY = (
    BASIC_EXPRESSION_PATTERN_SORT_KEY + PATTERN_SORT_KEY_BLANKNULLSEQUENCE_WITH_HEAD
)  # BlankNullSequence[A] (`pat___A`)
BLANKNULLSEQUENCE_GENERAL_PATTERN_SORT_KEY = (
    BASIC_EXPRESSION_PATTERN_SORT_KEY + PATTERN_SORT_KEY_BLANKNULLSEQUENCE_PURE
)  # BlankNullSequence[] (`pat___`)


# Used in the case Alternative[]
EMPTY_ALTERNATIVE_PATTERN_SORT_KEY = (
    PATTERN_SORT_KEY_IS_EXPRESSION + PATTERN_SORT_KEY_EMPTY_ALTERNATIVES
)  # Alternatives[]
# OptionsPatterns
OPTIONSPATTERN_SORT_KEY = (
    BASIC_EXPRESSION_PATTERN_SORT_KEY + PATTERN_SORT_KEY_OPTIONSPATTERN
)  # OptionsPattern[]
# Verbatim
VERBATIM_PATTERN_SORT_KEY = (
    PATTERN_SORT_KEY_VERBATIM | BASIC_EXPRESSION_PATTERN_SORT_KEY
)  # Verbatim[expr]

# Now, two pattern sort keys that are used many times:
# Atoms
BASIC_ATOM_PATTERN_SORT_KEY = (MAGIC_ATOM_SORT_KEY, 0, 0)
# and "end of list" to ensure that patterns with more elements come first.
END_OF_LIST_PATTERN_SORT_KEY = (
    PATTERN_SORT_KEY_LAST,
)  # Used as the last element in the third field.


###  SORT_KEYS prefix for expression_order

BASIC_ATOM_NUMBER_SORT_KEY = 0x00
BASIC_ATOM_STRING_OR_BYTEARRAY_SORT_KEY = 0x01
BASIC_ATOM_BYTEARRAY_SORT_KEY = 0x02
LITERAL_EXPRESSION_SORT_KEY = 0x03

BASIC_NUMERIC_EXPRESSION_SORT_KEY = 0x12
GENERAL_NUMERIC_EXPRESSION_SORT_KEY = 0x13
IMAGE_EXPRESSION_SORT_KEY = 0x13

BASIC_EXPRESSION_SORT_KEY = 0x22
GENERAL_EXPRESSION_SORT_KEY = 0x23
