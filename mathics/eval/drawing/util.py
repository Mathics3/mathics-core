"""
Common utilities for plotting
"""

import itertools

from mathics.core.atoms import NumericArray
from mathics.core.convert.expression import to_mathics_list
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import (
    SymbolGraphics,
    SymbolGraphics3D,
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

    # TODO: more precise types
    # TODO: consider pre-zipping so only one for polys and one for lines
    # TODO: consider whether we need to store these or can we just generate as we go?
    poly_xyzs: list
    poly_xyzs_colors: list
    line_xyzs: list
    line_xyzs_colors: list
    complexes: list

    # 2 or 3
    dim: int

    def __init__(self, dim: int):
        self.dim = dim
        self.poly_xyzs = []
        self.poly_xyzs_colors = []
        self.line_xyzs = []
        self.line_xyzs_colors = []
        self.complexes = []

    # TODO: is this correct if some polys have colors and some don't?
    def add_polyxyzs(self, poly_xyzs, colors=None):
        """Add polygons specified by explicit xy[z] coordinates"""
        self.poly_xyzs.append(poly_xyzs)
        if colors:
            self.poly_xyzs_colors.append(colors)

    def add_linexyzs(self, line_xyzs, colors=None):
        """Add lines specified by explicit xy[z] coordinates"""
        self.line_xyzs.append(line_xyzs)
        if colors:
            self.line_xyzs_colors.append(colors)

    def add_complex(self, xyzs, lines, polys):
        self.complexes.append((xyzs, lines, polys))

    def generate(self, options):
        """
        Generates Graphics[3D] expression from supplied lines, polygons (etc.)
        """

        # holds the elements of the final Graphics[3D] expr
        graphics = []

        # add polygons and lines, optionally with vertex colors
        def add_thing(thing_symbol, thingss, colorss):
            for things, colors in itertools.zip_longest(thingss, colorss):
                arg = tuple(to_mathics_list(*thing) for thing in things)
                arg = ListExpression(*arg) if len(arg) > 1 else arg[0]
                if colors:
                    color_arg = tuple(to_mathics_list(*color) for color in colors)
                    color_arg = (
                        ListExpression(*color_arg)
                        if len(color_arg) > 1
                        else color_arg[0]
                    )
                    color_rule = Expression(SymbolRule, SymbolVertexColors, color_arg)
                    graphics.append(Expression(thing_symbol, arg, color_rule))
                else:
                    graphics.append(Expression(thing_symbol, arg))

        add_thing(SymbolPolygon, self.poly_xyzs, self.poly_xyzs_colors)
        add_thing(SymbolLine, self.line_xyzs, self.line_xyzs_colors)

        # add complexes
        for xyzs, lines, polys in self.complexes:
            # TODO: lines
            xyzs_expr = NumericArray(xyzs)
            polys_expr = Expression(SymbolPolygon, NumericArray(polys))
            # TODO: move to systemsymbols
            SymbolGraphicsComplex = Symbol("System`GraphicsComplex")
            gc_expr = Expression(SymbolGraphicsComplex, xyzs_expr, polys_expr)
            graphics.append(gc_expr)

        # generate Graphics[3D] expression
        graphics_expr = Expression(
            SymbolGraphics3D if self.dim == 3 else SymbolGraphics,
            ListExpression(*graphics),
            *options,
        )

        return graphics_expr
