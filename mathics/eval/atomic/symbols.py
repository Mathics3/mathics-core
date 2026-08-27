"""
Evaluation methods for mathics.builtin.atomic.atomic.
"""

from mathics.core.symbols import Symbol


def eval_SymbolQ(expr) -> bool:
    """Return True if expr is an Symbol."""
    return isinstance(expr, Symbol)
