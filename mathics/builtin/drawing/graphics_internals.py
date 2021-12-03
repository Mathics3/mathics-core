# -*- coding: utf-8 -*-
# Internal graphics routines.
# No external builtins appear here.
# Also no docstring which may confuse the doc system


from mathics.builtin.base import (
    InstanceableBuiltin,
    BoxConstructError,
)

# Signals to Mathics doc processing not to include this module in its documentation.
no_doc = True

from mathics.core.symbols import system_symbols_dict, Symbol


class _GraphicsElement(InstanceableBuiltin):
    def init(self, graphics, item=None, style=None, opacity=1.0):
        if item is not None and not item.has_form(self.get_name(), None):
            raise BoxConstructError
        self.graphics = graphics
        self.style = style
        self.opacity = opacity
        self.is_completely_visible = False  # True for axis elements

    @staticmethod
    def create_as_style(klass, graphics, item):
        return klass(graphics, item)


def get_class(symbol: Symbol):
    """
    Returns the Builtin graphic primitive associated to the
    Symbol `symbol`
    """
    c = GLOBALS.get(symbol)
    if c is None:
        return GLOBALS3D.get(symbol)
    else:
        return c

    # globals() does not work with Cython, otherwise one could use something
    # like return globals().get(name)


# FIXME: GLOBALS and GLOBALS3D are a horrible names.
# These ares updated in mathics.builtin.graphics in and mathics.builtin.box.graphics3d
GLOBALS = system_symbols_dict({})
GLOBALS3D = system_symbols_dict({})
