# -*- coding: utf-8 -*-
"""
System-related binary handling
"""

import sys

from mathics.builtin.base import Predefined
from mathics.core.atoms import Integer, Integer1, IntegerM1


class ByteOrdering(Predefined):
    """
    <dl>
      <dt>'ByteOrdering'
      <dd> is an option for BinaryRead, BinaryWrite, and related functions that specifies what ordering
    of bytes should be assumed for your computer system..
    </dl>

    X> ByteOrdering
     = 1

    #> ByteOrdering == -1 || ByteOrdering == 1
     = True
    """

    name = "ByteOrdering"
    rules = {"ByteOrdering": "$ByteOrdering"}
    summary_text = "ordering of the bits in a byte"


class ByteOrdering_(Predefined):
    """
    <dl>
      <dt>'$ByteOrdering'
      <dd>returns the native ordering of bytes in binary data on your computer system.
    </dl>

    X> $ByteOrdering
     = 1

    #> $ByteOrdering == -1 || $ByteOrdering == 1
     = True
    """

    name = "$ByteOrdering"
    summary_text = "native machine byte ordering of the computer system"

    def evaluate(self, evaluation) -> Integer:
        return Integer1 if sys.byteorder == "big" else IntegerM1
