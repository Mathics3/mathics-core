# -*- coding: utf-8 -*-
"""
Various Exception objects used in Mathics3.
"""


class BoxExpressionError(Exception):
    pass


# Backward compatibility
BoxConstructError = BoxExpressionError


class IllegalStepSpecification(Exception):
    pass


class InvalidLevelspecError(Exception):
    pass


class PartError(Exception):
    pass


class PartDepthError(PartError):
    def __init__(self, index=0):
        self.index = index


class PartRangeError(PartError):
    pass


class MessageException(Exception):
    def __init__(self, *message):
        self._message = message

    def message(self, evaluation):
        """
        Transfer this exception to evaluation's ``message`` method.
        """
        evaluation.message(*self._message)
