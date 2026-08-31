"""Core to Mathics3 are patterns which match symbolic expressions. Patterns
are built up in a custom pattern notation.
The parts of a pattern are called "Pattern Objects".

While there is a built-in function which allows users to match parts of
expressions, patterns are also used in applying transformation
rules and deciding functions that get applied.

See also: mathics.core.rules and
https://reference.wolfram.com/language/tutorial/PatternsAndTransformationRules.html
"""

from .base import (
    AtomPattern,
    BasePattern,
    ExpressionPattern,
    StopGenerator,
    pattern_objects,
)

__all__ = [
    "AtomPattern",
    "BasePattern",
    "ExpressionPattern",
    "StopGenerator",
    "pattern_objects",
]
