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

    Each class should provide a `get_sort_key()` method which
    is the primitive from which all other comparisons are based on.
    """

    # FIXME: return type should be a specific kind of Tuple, not a list.
    # FIXME: Describe sensible, and easy to follow rules by which one
    #        can create the kind of tuple for some new kind of element.
    def get_sort_key(self, pattern_sort=False) -> tuple:
        """
        This returns a tuple in a way that
        it can be used to compare in expressions.

        Returns a particular encoded list (better though would be a tuple) that is used
        in ``Sort[]`` comparisons and in the ordering that occurs
        in an M-Expression which has the ``Orderless`` property.

        The encoded tuple/list is selected to have the property: when
        compared against element ``expr`` in a compound expression, if

           `self.get_sort_key() <= expr.get_sort_key()`

        then self comes before expr.

        The values in the positions of the list/tuple are used to indicate how
        comparison should be treated for specific element classes.
        """
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        return (
            hasattr(other, "get_sort_key")
            and self.get_sort_key() == other.get_sort_key()
        )

    def __gt__(self, other) -> bool:
        return self.get_sort_key() > other.get_sort_key()

    def __ge__(self, other) -> bool:
        return self.get_sort_key() >= other.get_sort_key()

    def __le__(self, other) -> bool:
        return self.get_sort_key() <= other.get_sort_key()

    def __lt__(self, other) -> bool:
        return self.get_sort_key() < other.get_sort_key()

    def __ne__(self, other) -> bool:
        return (
            not hasattr(other, "get_sort_key")
        ) or self.get_sort_key() != other.get_sort_key()


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


###  SORT_KEYS prefix for patterns
#
# Pattern sort keys have 3 elements. The first one is a "magic" tuple
# representing different features of the element, like if
# it is an atom or an expression, if is an special pattern like `Blank`
# etc. The first order criteria is that these tuples are in ascending order.
# The second element is the sort_key for the head, and the third,
# is the list of sort_keys associated to each element of the expression,
# finished with ``END_OF_LIST_PATTERN_SORT_KEY`` to ensure that the longest
# list of patterns always come first.

# This is the full sort_key for any Atom.
BASIC_ATOM_PATTERN_SORT_KEY = ((0, 0, 1, 1, 0, 1), 0, 0, 1)
# This is the magic tuple for generic expressions.
BASIC_EXPRESSION_PATTERN_SORT_KEY = (
    2,
    0,
    1,
    1,
    0,
    1,
)
BLANK_WITH_PATTERN_PATTERN_SORT_KEY = (
    2,
    11,
    1,
    1,
    0,
    1,
)
BLANK_GENERAL_PATTERN_SORT_KEY = (
    2,
    21,
    1,
    1,
    0,
    1,
)

BLANKSEQUENCE_WITH_PATTERN_PATTERN_SORT_KEY = (
    2,
    12,
    1,
    1,
    0,
    1,
)
BLANKSEQUENCE_GENERAL_PATTERN_SORT_KEY = (
    2,
    22,
    1,
    1,
    0,
    1,
)

BLANKNULLSEQUENCE_WITH_PATTERN_PATTERN_SORT_KEY = (
    2,
    13,
    1,
    1,
    0,
    1,
)
BLANKNULLSEQUENCE_GENERAL_PATTERN_SORT_KEY = (
    2,
    23,
    1,
    1,
    0,
    1,
)

END_OF_LIST_PATTERN_SORT_KEY = ((4,),)  # Used as the last element in the third
# field.

# Used in the case Alternative[]
EMPTY_ALTERNATIVE_PATTERN_SORT_KEY = ((2, 1),)
OPTIONSPATTERN_SORT_KEY = (2, 40, 0, 1, 1, 0, 1)

VERBATIM_PATTERN_SORT_KEY = (
    3,
    0,
    0,
    0,
    0,
    1,
)

###  SORT_KEYS prefix for expressions

BASIC_ATOM_NUMBER_SORT_KEY = (
    0,
    0,
)
BASIC_ATOM_STRING_OR_BYTEARRAY_SORT_KEY = (
    0,
    1,
)
BASIC_EXPRESSION_SORT_KEY = (
    2,
    2,
)
BASIC_NUMERIC_EXPRESSION_SORT_KEY = (
    1,
    2,
)
GENERAL_EXPRESSION_SORT_KEY = (
    2,
    3,
)
GENERAL_NUMERIC_EXPRESSION_SORT_KEY = (
    1,
    3,
)


LITERAL_EXPRESSION_SORT_KEY = (
    0,
    3,
)
IMAGE_EXPRESSION_SORT_KEY = (
    1,
    3,
)
