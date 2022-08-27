# -*- coding: utf-8 -*-
"""
Binary Types
"""


from mathics.builtin.base import Builtin


class Byte(Builtin):
    """
    <dl>
      <dt>'Byte'
      <dd>is a data type for 'Read'.
    </dl>
    """

    summary_text = "single byte of data, returned as an integer"


# This tells documentation how to sort this module
sort_order = "mathics.builtin.binary-types"


# TODO: Bit Integer8, Integer14, UnsignedInteger8, Real32, Real64, Real128, Complex64, Complex128, Complex256, Character8, Character16, TerminatedStrring
