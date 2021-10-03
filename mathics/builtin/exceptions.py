# -*- coding: utf-8 -*-
from mathics.version import __version__  # noqa used in loading to check consistency.


class BoxConstructError(Exception):
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
        evaluation.message(*self._message)
