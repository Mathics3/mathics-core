"""
Color Directives

There are many different way to specify color, and we support many of these.

We can convert between the different color formats.
"""

from math import atan2, cos, exp, pi, radians, sin, sqrt

from mathics.builtin.base import Builtin
from mathics.builtin.colors.color_internals import convert_color
from mathics.builtin.drawing.graphics_internals import _GraphicsDirective, get_class
from mathics.core.atoms import Integer, MachineReal, Real, String
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.element import ImmutableValueMixin
from mathics.core.exceptions import BoxExpressionError
from mathics.core.expression import Evaluation, Expression
from mathics.core.list import ListExpression
from mathics.core.number import MACHINE_EPSILON
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolApply

SymbolOpacity = Symbol("Opacity")


def _cie2000_distance(lab1, lab2):
    # reference: https://en.wikipedia.org/wiki/Color_difference#CIEDE2000
    e = MACHINE_EPSILON
    kL = kC = kH = 1  # common values

    L1, L2 = lab1[0], lab2[0]
    a1, a2 = lab1[1], lab2[1]
    b1, b2 = lab1[2], lab2[2]

    dL = L2 - L1
    Lm = (L1 + L2) / 2
    C1 = sqrt(a1**2 + b1**2)
    C2 = sqrt(a2**2 + b2**2)
    Cm = (C1 + C2) / 2

    a1 = a1 * (1 + (1 - sqrt(Cm**7 / (Cm**7 + 25**7))) / 2)
    a2 = a2 * (1 + (1 - sqrt(Cm**7 / (Cm**7 + 25**7))) / 2)

    C1 = sqrt(a1**2 + b1**2)
    C2 = sqrt(a2**2 + b2**2)
    Cm = (C1 + C2) / 2
    dC = C2 - C1

    h1 = (180 * atan2(b1, a1 + e)) / pi % 360
    h2 = (180 * atan2(b2, a2 + e)) / pi % 360
    if abs(h2 - h1) <= 180:
        dh = h2 - h1
    elif abs(h2 - h1) > 180 and h2 <= h1:
        dh = h2 - h1 + 360
    elif abs(h2 - h1) > 180 and h2 > h1:
        dh = h2 - h1 - 360

    dH = 2 * sqrt(C1 * C2) * sin(radians(dh) / 2)

    Hm = (h1 + h2) / 2 if abs(h2 - h1) <= 180 else (h1 + h2 + 360) / 2
    T = (
        1
        - 0.17 * cos(radians(Hm - 30))
        + 0.24 * cos(radians(2 * Hm))
        + 0.32 * cos(radians(3 * Hm + 6))
        - 0.2 * cos(radians(4 * Hm - 63))
    )

    SL = 1 + (0.015 * (Lm - 50) ** 2) / sqrt(20 + (Lm - 50) ** 2)
    SC = 1 + 0.045 * Cm
    SH = 1 + 0.015 * Cm * T

    rT = (
        -2
        * sqrt(Cm**7 / (Cm**7 + 25**7))
        * sin(radians(60 * exp(-((Hm - 275) ** 2 / 25**2))))
    )
    return sqrt(
        (dL / (SL * kL)) ** 2
        + (dC / (SC * kC)) ** 2
        + (dH / (SH * kH)) ** 2
        + rT * (dC / (SC * kC)) * (dH / (SH * kH))
    )


def _CMC_distance(lab1, lab2, ll, c):
    # reference https://en.wikipedia.org/wiki/Color_difference#CMC_l:c_.281984.29
    L1, L2 = lab1[0], lab2[0]
    a1, a2 = lab1[1], lab2[1]
    b1, b2 = lab1[2], lab2[2]

    dL, da, db = L2 - L1, a2 - a1, b2 - b1
    e = MACHINE_EPSILON

    C1 = sqrt(a1**2 + b1**2)
    C2 = sqrt(a2**2 + b2**2)

    h1 = (180 * atan2(b1, a1 + e)) / pi % 360
    dC = C2 - C1
    dH2 = da**2 + db**2 - dC**2
    F = C1**2 / sqrt(C1**4 + 1900)
    T = (
        0.56 + abs(0.2 * cos(radians(h1 + 168)))
        if (164 <= h1 and h1 <= 345)
        else 0.36 + abs(0.4 * cos(radians(h1 + 35)))
    )

    SL = 0.511 if L1 < 16 else (0.040975 * L1) / (1 + 0.01765 * L1)
    SC = (0.0638 * C1) / (1 + 0.0131 * C1) + 0.638
    SH = SC * (F * T + 1 - F)
    return sqrt((dL / (ll * SL)) ** 2 + (dC / (c * SC)) ** 2 + dH2 / SH**2)


def _component_distance(a, b, i):
    return abs(a[i] - b[i])


def _euclidean_distance(a, b):
    return sqrt(sum((x1 - x2) * (x1 - x2) for x1, x2 in zip(a, b)))


def color_to_expression(components, colorspace):
    if colorspace == "Grayscale":
        converted_color_name = "GrayLevel"
    elif colorspace == "HSB":
        converted_color_name = "Hue"
    else:
        converted_color_name = colorspace + "Color"

    return to_expression(converted_color_name, *components)


def expression_to_color(color):
    try:
        return _ColorObject.create(color)
    except ColorError:
        return None


class _ColorObject(_GraphicsDirective, ImmutableValueMixin):
    formats = {
        # we are adding ImageSizeMultipliers in the rule below, because we do _not_ want color boxes to
        # diminish in size when they appear in lists or rows. we only want the display of colors this
        # way in the notebook, so we restrict the rule to StandardForm.
        (
            ("StandardForm",),
            "%(name)s[x__?(NumericQ[#] && 0 <= # <= 1&)]",
        ): "Style[Graphics[{EdgeForm[Black], %(name)s[x], Rectangle[]}, ImageSize -> 16], "
        + "ImageSizeMultipliers -> {1, 1}]"
    }

    rules = {"%(name)s[x_List]": "Apply[%(name)s, x]"}

    components_sizes = []
    default_components = []

    def init(self, item=None, components=None):
        super(_ColorObject, self).init(None, item)
        if item is not None:
            elements = item.elements
            if len(elements) in self.components_sizes:
                # we must not clip here; we copy the components, without clipping,
                # e.g. RGBColor[-1, 0, 0] stays RGBColor[-1, 0, 0]. this is especially
                # important for color spaces like LAB that have negative components.
                components = [value.round_to_float() for value in elements]
                if None in components:
                    raise ColorError

                # the following lines always extend to the maximum available
                # default_components, so RGBColor[0, 0, 0] will _always_
                # become RGBColor[0, 0, 0, 1]. does not seem the right thing
                # to do in this general context. poke1024

                if len(components) < 3:
                    components.extend(self.default_components[len(components) :])

                self.components = components
            else:
                raise ColorError
        elif components is not None:
            self.components = components

    @staticmethod
    def create(expr):
        head = expr.get_head()
        cls = get_class(head)
        if cls is None:
            raise ColorError
        return cls(expr)

    @staticmethod
    def create_as_style(klass, graphics, item):
        return klass(item)

    def to_css(self):
        rgba = self.to_rgba()
        alpha = rgba[3] if len(rgba) > 3 else None
        return (
            r"rgb(%f%%, %f%%, %f%%)" % (rgba[0] * 100, rgba[1] * 100, rgba[2] * 100),
            alpha,
        )

    def to_js(self):
        return self.to_rgba()

    def to_expr(self):
        return to_expression(self.get_name(), *self.components)

    def to_rgba(self):
        return self.to_color_space("RGB")

    def to_color_space(self, color_space):
        components = convert_color(self.components, self.color_space, color_space)
        if components is None:
            raise ValueError(
                "cannot convert from color space %s to %s."
                % (self.color_space, color_space)
            )
        return components


class CMYKColor(_ColorObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/CMYKColor.html</url>

    <dl>
      <dt>'CMYKColor[$c$, $m$, $y$, $k$]'
      <dd>represents a color with the specified cyan, magenta,
        yellow and black components.
    </dl>

    >> Graphics[MapIndexed[{CMYKColor @@ #1, Disk[2*#2 ~Join~ {0}]} &, IdentityMatrix[4]], ImageSize->Small]
     = -Graphics-
    """

    color_space = "CMYK"
    components_sizes = [3, 4, 5]
    default_components = [0, 0, 0, 0, 1]
    summary_text = "specify a CMYK color"


class ColorDistance(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ColorDistance.html</url>

    <dl>
      <dt>'ColorDistance[$c1$, $c2$]'
      <dd>returns a measure of color distance between the colors $c1$ and $c2$.

      <dt>'ColorDistance[$list$, $c2$]'
      <dd>returns a list of color distances between the colors in $list$ and $c2$.
    </dl>

    The option DistanceFunction specifies the method used to measure the color
    distance. Available options are:

    <ul>
      <li>CIE76: Euclidean distance in the LABColor space
      <li>CIE94: Euclidean distance in the LCHColor space
      <li>CIE2000 or CIEDE2000: CIE94 distance with corrections
      <li>CMC: Color Measurement Committee metric (1984)
      <li>DeltaL: difference in the L component of LCHColor
      <li>DeltaC: difference in the C component of LCHColor
      <li>DeltaH: difference in the H component of LCHColor
    </ul>

    It is also possible to specify a custom distance.

    >> ColorDistance[Magenta, Green]
     = 2.2507
    >> ColorDistance[{Red, Blue}, {Green, Yellow}, DistanceFunction -> {"CMC", "Perceptibility"}]
     = {1.0495, 1.27455}
    #> ColorDistance[Blue, Red, DistanceFunction -> "CIE2000"]
     = 0.557976
    #> ColorDistance[Red, Black, DistanceFunction -> (Abs[#1[[1]] - #2[[1]]] &)]
     = 0.542917

    """

    options = {"DistanceFunction": "Automatic"}

    requires = ("numpy",)

    messages = {
        "invdist": "`1` is not Automatic or a valid distance specification.",
        "invarg": "`1` and `2` should be two colors or a color and a lists of colors or "
        + "two lists of colors of the same length.",
    }

    summary_text = "get distance between two colors"

    # If numpy is not installed, 100 * c1.to_color_space returns
    # a list of 100 x 3 elements, instead of doing elementwise multiplication
    requires = ("numpy",)

    # the docs say LABColor's colorspace corresponds to the CIE 1976 L^* a^* b^* color space
    # with {l,a,b}={L^*,a^*,b^*}/100. Corrections factors are put accordingly.

    _distances = {
        "CIE76": lambda c1, c2: _euclidean_distance(
            c1.to_color_space("LAB")[:3], c2.to_color_space("LAB")[:3]
        ),
        "CIE94": lambda c1, c2: _euclidean_distance(
            c1.to_color_space("LCH")[:3], c2.to_color_space("LCH")[:3]
        ),
        "CIE2000": lambda c1, c2: _cie2000_distance(
            100 * c1.to_color_space("LAB")[:3], 100 * c2.to_color_space("LAB")[:3]
        )
        / 100,
        "CIEDE2000": lambda c1, c2: _cie2000_distance(
            100 * c1.to_color_space("LAB")[:3], 100 * c2.to_color_space("LAB")[:3]
        )
        / 100,
        "DeltaL": lambda c1, c2: _component_distance(
            c1.to_color_space("LCH"), c2.to_color_space("LCH"), 0
        ),
        "DeltaC": lambda c1, c2: _component_distance(
            c1.to_color_space("LCH"), c2.to_color_space("LCH"), 1
        ),
        "DeltaH": lambda c1, c2: _component_distance(
            c1.to_color_space("LCH"), c2.to_color_space("LCH"), 2
        ),
        "CMC": lambda c1, c2: _CMC_distance(
            100 * c1.to_color_space("LAB")[:3], 100 * c2.to_color_space("LAB")[:3], 1, 1
        )
        / 100,
    }

    def eval(self, c1, c2, evaluation: Evaluation, options: dict):
        "ColorDistance[c1_, c2_, OptionsPattern[ColorDistance]]"

        distance_function = options.get("System`DistanceFunction")
        compute = None
        if isinstance(distance_function, String):
            compute = ColorDistance._distances.get(distance_function.get_string_value())
            if not compute:
                evaluation.message("ColorDistance", "invdist", distance_function)
                return
        elif distance_function.has_form("List", 2):
            if distance_function.elements[0].get_string_value() == "CMC":
                if distance_function.elements[1].get_string_value() == "Acceptability":
                    compute = (
                        lambda c1, c2: _CMC_distance(
                            100 * c1.to_color_space("LAB")[:3],
                            100 * c2.to_color_space("LAB")[:3],
                            2,
                            1,
                        )
                        / 100
                    )
                elif (
                    distance_function.elements[1].get_string_value() == "Perceptibility"
                ):
                    compute = ColorDistance._distances.get("CMC")

                elif distance_function.elements[1].has_form("List", 2):
                    if isinstance(
                        distance_function.elements[1].elements[0], Integer
                    ) and isinstance(
                        distance_function.elements[1].elements[1], Integer
                    ):
                        if (
                            distance_function.elements[1].elements[0].get_int_value()
                            > 0
                            and distance_function.elements[1]
                            .elements[1]
                            .get_int_value()
                            > 0
                        ):
                            lightness = (
                                distance_function.elements[1]
                                .elements[0]
                                .get_int_value()
                            )
                            chroma = (
                                distance_function.elements[1]
                                .elements[1]
                                .get_int_value()
                            )
                            compute = (
                                lambda c1, c2: _CMC_distance(
                                    100 * c1.to_color_space("LAB")[:3],
                                    100 * c2.to_color_space("LAB")[:3],
                                    lightness,
                                    chroma,
                                )
                                / 100
                            )

        elif (
            isinstance(distance_function, Symbol)
            and distance_function.get_name() == "System`Automatic"
        ):
            compute = ColorDistance._distances.get("CIE76")
        else:

            def compute(a, b):
                return Expression(
                    SymbolApply,
                    distance_function,
                    ListExpression(
                        to_mathics_list(
                            *a.to_color_space("LAB"), elements_conversion_fn=Real
                        ),
                        to_mathics_list(
                            *b.to_color_space("LAB"), elements_conversion_fn=Real
                        ),
                    ),
                )

        if compute is None:
            evaluation.message("ColorDistance", "invdist", distance_function)
            return

        def distance(a, b):
            try:
                py_a = _ColorObject.create(a)
                py_b = _ColorObject.create(b)
            except ColorError:
                evaluation.message("ColorDistance", "invarg", a, b)
                raise
            result = from_python(compute(py_a, py_b))
            return result

        try:
            if c1.get_head_name() == "System`List":
                if c2.get_head_name() == "System`List":
                    if len(c1.elements) != len(c2.elements):
                        evaluation.message("ColorDistance", "invarg", c1, c2)
                        return
                    else:
                        return to_mathics_list(
                            *[distance(a, b) for a, b in zip(c1.elements, c2.elements)],
                        )
                else:
                    return to_mathics_list(*[distance(c, c2) for c in c1.elements])
            elif c2.get_head_name() == "System`List":
                return ListExpression(*[distance(c1, c) for c in c2.elements])
            else:
                return distance(c1, c2)
        except ColorError:
            return
        except NotImplementedError:
            evaluation.message("ColorDistance", "invdist", distance_function)
            return


class ColorError(BoxExpressionError):
    pass


class GrayLevel(_ColorObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/GrayLevel.html</url>

    <dl>
      <dt>'GrayLevel[$g$]'
      <dd>represents a shade of gray specified by $g$, ranging from
        0 (black) to 1 (white).
      <dt>'GrayLevel[$g$, $a$]'
      <dd>represents a shade of gray specified by $g$ with opacity $a$.
    </dl>
    """

    color_space = "Grayscale"
    components_sizes = [1, 2]
    default_components = [0, 1]

    summary_text = "specify a Grayscale color"


class Hue(_ColorObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Hue.html</url>

    <dl>
      <dt>'Hue[$h$, $s$, $l$, $a$]'
      <dd>represents the color with hue $h$, saturation $s$, lightness $l$ and opacity $a$.

      <dt>'Hue[$h$, $s$, $l$]'
      <dd>is equivalent to 'Hue[$h$, $s$, $l$, 1]'.

      <dt>'Hue[$h$, $s$]'
      <dd>is equivalent to 'Hue[$h$, $s$, 1, 1]'.

      <dt>'Hue[$h$]'
      <dd>is equivalent to 'Hue[$h$, 1, 1, 1]'.
    </dl>

    >> Graphics[Table[{EdgeForm[Gray], Hue[h, s], Disk[{12h, 8s}]}, {h, 0, 1, 1/6}, {s, 0, 1, 1/4}]]
     = -Graphics-

    >> Graphics[Table[{EdgeForm[{GrayLevel[0, 0.5]}], Hue[(-11+q+10r)/72, 1, 1, 0.6], Disk[(8-r) {Cos[2Pi q/12], Sin[2Pi q/12]}, (8-r)/3]}, {r, 6}, {q, 12}]]
     = -Graphics-
    """

    color_space = "HSB"
    components_sizes = [1, 2, 3, 4]
    default_components = [0, 1, 1, 1]

    summary_text = "specify a color with hue, saturation lightness, and opacity"

    def hsl_to_rgba(self) -> tuple:
        h, s, li = self.components[:3]
        if li < 0.5:
            q = li * (1 + s)
        else:
            q = li + s - li * s
        p = 2 * li - q

        rgb = (h + 1 / 3, h, h - 1 / 3)

        def map(value):
            if value < 0:
                value += 1
            if value > 1:
                value -= 1
            return value

        def trans(t):
            if t < 1 / 6:
                return p + ((q - p) * 6 * t)
            elif t < 1 / 2:
                return q
            elif t < 2 / 3:
                return p + ((q - p) * 6 * (2 / 3 - t))
            else:
                return p

        result = tuple([trans(list(map(t))) for t in rgb]) + (self.components[3],)
        return result


class LABColor(_ColorObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/LABColor.html</url>

    <dl>
      <dt>'LABColor[$l$, $a$, $b$]'
      <dd>represents a color with the specified lightness, red/green and yellow/blue
        components in the CIE 1976 L*a*b* (CIELAB) color space.
    </dl>
    """

    color_space = "LAB"
    components_sizes = [3, 4]
    default_components = [0, 0, 0, 1]

    summary_text = "specify a LAB color"


class LCHColor(_ColorObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/LCHColor.html</url>

    <dl>
      <dt>'LCHColor[$l$, $c$, $h$]'
      <dd>represents a color with the specified lightness, chroma and hue
        components in the CIELCh CIELab cube color space.
    </dl>
    """

    color_space = "LCH"
    components_sizes = [3, 4]
    default_components = [0, 0, 0, 1]

    summary_text = "specify a LHC color"


class LUVColor(_ColorObject):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/LUVColor.html</url>

    <dl>
      <dt>'LCHColor[$l$, $u$, $v$]'
      <dd>represents a color with the specified components in the CIE 1976 L*u*v* (CIELUV) color space.
    </dl>
    """

    color_space = "LUV"
    components_sizes = [3, 4]
    default_components = [0, 0, 0, 1]

    summary_text = "specify a LUV color"


class Opacity(_GraphicsDirective):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Opacity.html</url>

    <dl>
      <dt>'Opacity[$level$]'
      <dd> is a graphics directive that sets the opacity to $level$.
    </dl>
    >> Graphics[{Blue, Disk[{.5, 1}, 1], Opacity[.4], Red, Disk[], Opacity[.2], Green, Disk[{-.5, 1}, 1]}]
     = -Graphics-
    >> Graphics3D[{Blue, Sphere[], Opacity[.4], Red, Cuboid[]}]
     = -Graphics3D-
    Notice that 'Opacity' does not overwrite the value of the alpha channel if it is set in a color directive:
    >> Graphics[{Blue, Disk[], RGBColor[1,0,0,1],Opacity[.2], Rectangle[{0,0},{1,1}]}]
     = -Graphics-
    """

    def init(self, item=None, *args, **kwargs):
        if isinstance(item, (int, float)):
            item = Expression(SymbolOpacity, MachineReal(item))
            super(Opacity, self).init(None, item)
        self.opacity = item.elements[0].to_python()

    def to_css(self):
        try:
            if 0.0 <= self.opacity <= 1.0:
                return self.opacity
        except Exception:
            pass
        return None

    @staticmethod
    def create_as_style(klass, graphics, item):
        return klass(item)

    summary_text = "specify a Opacity level"


class RGBColor(_ColorObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/RGBColor.html</url>

    <dl>
      <dt>'RGBColor[$r$, $g$, $b$]'
      <dd>represents a color with the specified red, green and blue
        components.
    </dl>

    >> Graphics[MapIndexed[{RGBColor @@ #1, Disk[2*#2 ~Join~ {0}]} &, IdentityMatrix[3]], ImageSize->Small]
     = -Graphics-

    >> RGBColor[0, 1, 0]
     = RGBColor[0, 1, 0]

    >> RGBColor[0, 1, 0] // ToBoxes
     = StyleBox[GraphicsBox[...], ...]
    """

    color_space = "RGB"
    components_sizes = [3, 4]
    default_components = [0, 0, 0, 1]

    def to_rgba(self):
        return self.components

    summary_text = "specify an RGB color"


class XYZColor(_ColorObject):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/XYZColor.html</url>

    <dl>
      <dt>'XYZColor[$x$, $y$, $z$]'
      <dd>represents a color with the specified components in the CIE 1931 XYZ color space.
    </dl>
    """

    color_space = "XYZ"
    components_sizes = [3, 4]
    default_components = [0, 0, 0, 1]

    summary_text = "specify an XYZ color"
