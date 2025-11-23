"""
Common utilities for plotting
"""


from mathics.core.atoms import NumericArray
from mathics.core.convert.expression import to_mathics_list
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.systemsymbols import (
    SymbolGraphics,
    SymbolGraphics3D,
    SymbolGraphicsComplex,
    SymbolLine,
    SymbolPolygon,
    SymbolRule,
    SymbolVertexColors,
)


# TODO: this will be extended with support for GraphicsComplex in a
# subsequent PR, which may involve a little more refactoring
class GraphicsGenerator:

    """
    Support for generating Graphics and Graphics3D expressions
    """

    # TODO: more precise typing?
    graphics: list

    # 2 or 3
    dim: int

    def __init__(self, dim: int):
        self.dim = dim
        self.graphics = []

    # add polygons and lines, optionally with vertex colors
    def add_thing(self, thing_symbol, things, colors):
        arg = tuple(to_mathics_list(*thing) for thing in things)
        arg = ListExpression(*arg) if len(arg) > 1 else arg[0]
        if colors:
            color_arg = tuple(to_mathics_list(*color) for color in colors)
            color_arg = (
                ListExpression(*color_arg) if len(color_arg) > 1 else color_arg[0]
            )
            color_rule = Expression(SymbolRule, SymbolVertexColors, color_arg)
            self.graphics.append(Expression(thing_symbol, arg, color_rule))
        else:
            self.graphics.append(Expression(thing_symbol, arg))

    def add_polyxyzs(self, poly_xyzs, colors=None):
        """Add polygons specified by explicit xy[z] coordinates"""
        self.add_thing(SymbolPolygon, poly_xyzs, colors)

    def add_linexyzs(self, line_xyzs, colors=None):
        """Add lines specified by explicit xy[z] coordinates"""
        self.add_thing(SymbolLine, line_xyzs, colors)

    def add_color(self, symbol, components):
        from mathics.core.convert.expression import to_expression
        expr = to_expression(symbol, *components)
        self.graphics.append(expr)

    def add_complex(self, xyzs, lines=None, polys=None):
        complex = [NumericArray(xyzs)]
        if polys is not None:
            polys_expr = Expression(SymbolPolygon, NumericArray(polys))
            complex.append(polys_expr)
        if lines is not None:
            polys_expr = Expression(SymbolLines, NumericArray(lines))
            complex.append(lines_expr)
        gc_expr = Expression(SymbolGraphicsComplex, *complex)
        self.graphics.append(gc_expr)

    def generate(self, options):
        """
        Generates Graphics[3D] expression from supplied lines, polygons (etc.)
        """
        graphics_expr = Expression(
            SymbolGraphics3D if self.dim == 3 else SymbolGraphics,
            ListExpression(*self.graphics),
            *options,
        )

        return graphics_expr
