# -*- coding: utf-8 -*-
# Internal graphics routines.
# No external builtins appear here.
# Also no docstring which may confuse the doc system


from mathics.builtin.base import (
    BuiltinElement,
    BoxConstruct,
    BoxConstructError,
    split_name,
)

# Signals to Mathics doc processing not to include this module in its documentation.
no_doc = True

from mathics.core.symbols import system_symbols_dict, Symbol


class _GraphicsDirective(BuiltinElement):
    def __new__(cls, *args, **kwargs):
        # This ensures that all the graphics directive have a well formatted docstring
        # and a summary_text
        instance = super().__new__(cls, *args, **kwargs)
        if not hasattr(instance, "summary_text"):
            article = (
                "an "
                if instance.get_name()[0].lower() in ("a", "e", "i", "o", "u")
                else "a "
            )
            instance.summary_text = (
                "graphics directive setting "
                + article
                + split_name(cls.get_name(short=True)[:-3])
            )
        if not instance.__doc__:
            instance.__doc__ = f"""
                <dl>
                <dt>'{cls.get_name()}[...]'
                <dd>is a graphics directive that sets {cls.get_name().lower()[:3]}
                </dl>
                """
        return instance

    def init(self, graphics, item=None):
        if item is not None and not item.has_form(self.get_name(), None):
            raise BoxConstructError
        self.graphics = graphics

    @staticmethod
    def create_as_style(klass, graphics, item):
        return klass(graphics, item)


class _GraphicsElementBox(BoxConstruct):
    def init(self, graphics, item=None, style=None, opacity=1.0):
        if item is not None and not item.has_form(self.get_name(), None):
            raise BoxConstructError
        self.graphics = graphics
        self.style = style
        self.opacity = opacity
        self.is_completely_visible = False  # True for axis elements


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
