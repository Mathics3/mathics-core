from typing import NamedTuple


class AlgebraicOptions(NamedTuple):
    """
    Holds option values for some common algebraic builtin-functions.

    Attributes:
        modulus (int): The integer modulus for modular arithmetic (0 if none).
        trig (bool): Whether to apply trigonometric identities/rewrites.
    """

    modulus: int = 0
    trig: bool = False
