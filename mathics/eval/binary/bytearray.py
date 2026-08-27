"""
Evaluation methods for mathics.builtin.binary.bytearray.
"""

from mathics.core.atoms import ByteArray


def eval_ByteArrayQ(expr) -> bool:
    """Return True if expr is a ByteArray atom."""
    return isinstance(expr, ByteArray)
