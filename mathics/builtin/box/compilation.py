# -*- coding: utf-8 -*-
from mathics.version import __version__  # noqa used in loading to check consistency.

from mathics.builtin.base import BoxConstruct
from mathics.version import __version__  # noqa used in loading to check consistency.


class CompiledCodeBox(BoxConstruct):
    """Routines which get called when Boxing (adding formatting and bounding-box information)
    to CompiledCode.
    """

    def boxes_to_text(self, leaves=None, **options):
        if leaves is None:
            leaves = self._leaves
        return leaves[0].value

    def boxes_to_mathml(self, leaves=None, **options):
        if leaves is None:
            leaves = self._leaves
        return leaves[0].value

    def boxes_to_tex(self, leaves=None, **options):
        if leaves is None:
            leaves = self._leaves
        return leaves[0].value
