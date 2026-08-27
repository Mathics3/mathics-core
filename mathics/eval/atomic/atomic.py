"""
Evaluation methods for mathics.builtin.atomic.atomic.
"""

from mathics.core.symbols import Atom


def eval_AtomQ(expr) -> bool:
    """Return True if expr is an Atom."""
    return isinstance(expr, Atom)
