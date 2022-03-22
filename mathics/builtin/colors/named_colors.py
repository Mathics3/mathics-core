# -*- coding: utf-8 -*-
"""Named Colors

Mathics has definitions for the most common color names which can be used in a graphics or style specification.
"""

from mathics.builtin.base import Builtin

from mathics.core.symbols import strip_context


class _ColorObject(Builtin):
    text_name = None

    def __init__(self, *args, **kwargs):
        super(_ColorObject, self).__init__(*args, **kwargs)
        if self.text_name is None:
            text_name = strip_context(self.get_name()).lower()
        else:
            text_name = self.text_name
        doc = """
            <dl>
            <dt>'%(name)s'
            <dd>represents the color %(text_name)s in graphics and style directives.
            </dl>

            >> Graphics[{EdgeForm[Black], %(name)s, Disk[]}, ImageSize->Small]
             = -Graphics-

            >> %(name)s // ToBoxes
             = StyleBox[GraphicsBox[...], ...]
        """ % {
            "name": strip_context(self.get_name()),
            "text_name": text_name,
        }
        self.summary_text = f" is the {text_name}"
        if self.__doc__ is None:
            self.__doc__ = doc
        else:
            self.__doc__ = doc + self.__doc__


class Black(_ColorObject):
    """
    <dl>
    <dt>'Black'
    <dd> represents the color black in graphics and style directives.
    </dl>
    >> Black
     = RGBColor[0, 0, 0]
    """

    rules = {"Black": "RGBColor[0, 0, 0]"}


class Blue(_ColorObject):
    """
    <dl>
    <dt>'Blue'
    <dd> represents the color blue in graphics and style directives.
    </dl>
    >> Blue
     = RGBColor[0, 0, 1]
    """

    rules = {"Blue": "RGBColor[0, 0, 1]"}


class Brown(_ColorObject):
    """
    <dl>
    <dt>'Brown'
    <dd> represents the color brown in graphics and style directives.
    </dl>
    >> Brown
     = RGBColor[0.6, 0.4, 0.2]
    """

    rules = {"Brown": "RGBColor[0.6, 0.4, 0.2]"}


class Cyan(_ColorObject):
    """
    <dl>
    <dt>'Cyan'
    <dd> represents the color cyan in graphics and style directives.
    </dl>
    >> Cyan
     = RGBColor[0, 1, 1]
    """

    rules = {"Cyan": "RGBColor[0, 1, 1]"}


class Gray(_ColorObject):
    """
    <dl>
    <dt>'Gray'
    <dd> represents the color gray (50%) in graphics and style directives.
    </dl>
    >> Gray
     = GrayLevel[0.5]
    """

    rules = {"Gray": "GrayLevel[0.5]"}


class Green(_ColorObject):
    """
    <dl>
    <dt>'Green'
    <dd> represents the color green in graphics and style directives.
    </dl>
    >> Green
     = RGBColor[0, 1, 0]
    """

    rules = {"Green": "RGBColor[0, 1, 0]"}


class Magenta(_ColorObject):
    """
    <dl>
    <dt>'Magenta'
    <dd> represents the color magenta blue in graphics and style directives.
    </dl>

    >> Magenta
     = RGBColor[1, 0, 1]
    """

    rules = {"Magenta": "RGBColor[1, 0, 1]"}


class LightBlue(_ColorObject):
    """
    <dl>
    <dt>'LightBlue'
    <dd> represents the color light blue in graphics and style directives.
    </dl>

    >> Graphics[{LightBlue, EdgeForm[Black], Disk[]}]
     = -Graphics-

    >> Plot[Sin[x], {x, 0, 2 Pi}, Background -> LightBlue]
     = -Graphics-
    """

    text_name = "light blue"
    rules = {"LightBlue": "RGBColor[0.87, 0.94, 1]"}


class LightBrown(_ColorObject):
    text_name = "light brown"
    rules = {"LightBrown": "Lighter[Brown, 0.85]"}


class LightCyan(_ColorObject):
    text_name = "light cyan"
    rules = {"LightCyan": "Lighter[Cyan, 0.9]"}


class LightGray(_ColorObject):
    text_name = "light gray"
    rules = {"LightGray": "Lighter[Gray]"}


class LightGreen(_ColorObject):
    text_name = "light green"
    rules = {"LightGreen": "Lighter[Green, 0.88]"}


class LightMagenta(_ColorObject):
    text_name = "light magenta"
    rules = {"LightMagenta": "Lighter[Magenta]"}


class LightOrange(_ColorObject):
    text_name = "light orange"
    summary_text = "LightOrange summary still not available"
    rules = {"LightOrange": "RGBColor[1, 0.9, 0.8]"}


class LightPink(_ColorObject):
    text_name = "light pink"
    rules = {"LightPink": "Lighter[Pink, 0.85]"}


class LightPurple(_ColorObject):
    text_name = "light purple"
    rules = {"LightPurple": "Lighter[Purple, 0.88]"}


class LightRed(_ColorObject):
    text_name = "light red"
    rules = {"LightRed": "Lighter[Red, 0.85]"}


class LightYellow(_ColorObject):
    text_name = "light yellow"
    rules = {"LightYellow": "Lighter[Yellow]"}


class Pink(_ColorObject):
    rules = {"Pink": "RGBColor[1.0, 0.5, 0.5]"}


class Purple(_ColorObject):
    rules = {"Purple": "RGBColor[0.5, 0, 0.5]"}


class Orange(_ColorObject):
    rules = {"Orange": "RGBColor[1, 0.5, 0]"}


class Red(_ColorObject):
    """
    <dl>
    <dt>'Red'
    <dd> represents the color red in graphics and style directives.
    </dl>

    >> Red
     = RGBColor[1, 0, 0]
    """

    rules = {"Red": "RGBColor[1, 0, 0]"}


class Yellow(_ColorObject):
    """
    <dl>
    <dt>'Yellow'
    <dd> represents the color yellow in graphics and style directives.
    </dl>

    >> Yellow
     = RGBColor[1, 1, 0]
    """

    rules = {"Yellow": "RGBColor[1, 1, 0]"}


class White(_ColorObject):
    """
    <dl>
    <dt>'White'
    <dd> represents the color white in graphics and style directives.
    </dl>

    >> White
     = GrayLevel[1]
    """

    rules = {"White": "GrayLevel[1]"}
