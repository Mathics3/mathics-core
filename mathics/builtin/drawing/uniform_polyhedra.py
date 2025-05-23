# -*- coding: utf-8 -*-

"""
Uniform Polyhedra

Uniform polyhedra is the grouping of platonic solids, Archimedean solids,\
and regular star polyhedra.
"""

from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation

# This tells documentation how to sort this module
# Here we are also hiding "drawing" since this can erroneously appear at the top level.
sort_order = "mathics.builtin.uniform-polyhedra"

uniform_polyhedra_names = "cube, tetrahedron, octahedron, dodecahedron, icosahedron"
uniform_polyhedra_set = frozenset(uniform_polyhedra_names.split(", "))


class Cube(Builtin):
    """

    <url>:Cube:
    https://en.wikipedia.org/wiki/Cube</url> (<url>:WMA:
    https://reference.wolfram.com/language/ref/Cube.html</url>)

    <dl>
      <dt>'Cube[]'
      <dd>represents a regular cube centered at the origin with unit edge length.

      <dt>'Cube'[$l$]
      <dd>represents a cube centered at the origin with edge length $l$.

      <dt>'Cube'[{$x$, $y$, $z$}, ...]
      <dd>represents a cube centered at {$x$ $y$, $z$}.
    </dl>

    >> Graphics3D[Cube[]]
     = -Graphics3D-
    """

    summary_text = "produce a cube"
    rules = {
        "Cube[]": """UniformPolyhedron["cube"]""",
        "Cube[l_?NumberQ]": """UniformPolyhedron["cube", {{0, 0, 0}}, l]""",
        "Cube[positions_List, l_?NumberQ]": """UniformPolyhedron["cube", positions, l]""",
    }


class Dodecahedron(Builtin):
    """

    <url>:Dodecahedron:
    https://en.wikipedia.org/wiki/Dodecahedron</url> (<url>:WMA:
    https://reference.wolfram.com/language/ref/Dodecahedron.html</url>)

    <dl>
      <dt>'Dodecahedron[]'
      <dd>a regular dodecahedron centered at the origin with unit edge length.

      <dt>'Dodecahedron'[$l$]
      <dd>a regular dodecahedron centered at the origin with edge length $l$.

      <dt>'Dodecahedron'[{$x$, $y$, $z$}, ...]
      <dd>a regular dodecahedron centered at {$x$ $y$, $z$}.
    </dl>

    >> Graphics3D[Dodecahedron[]]
     = -Graphics3D-
    """

    summary_text = "produce a dodecahedron"
    rules = {
        "Dodecahedron[]": """UniformPolyhedron["dodecahedron"]""",
        "Dodecahedron[l_?NumberQ]": """UniformPolyhedron["dodecahedron", {{0, 0, 0}}, l]""",
        "Dodecahedron[positions_List, l_?NumberQ]": """UniformPolyhedron["dodecahedron", positions, l]""",
    }


class Icosahedron(Builtin):
    """
    <url>:Icosahedron:
    https://en.wikipedia.org/wiki/Icosahedron</url> (<url>:WMA:
    :WMA:
    https://reference.wolfram.com/language/ref/Icosahedron.html</url>)

    <dl>
      <dt>'Icosahedron[]'
      <dd>a regular Icosahedron centered at the origin with unit edge length.

      <dt>'Icosahedron'[$l$]
      <dd>a regular icosahedron centered at the origin with edge length $l$.

      <dt>'Icosahedron'[{$x$, $y$, $z$}, ...]
      <dd>a regular icosahedron centered at {$x$ $y$, $z$}.

    </dl>

    >> Graphics3D[Icosahedron[]]
     = -Graphics3D-
    """

    rules = {
        "Icosahedron[]": """UniformPolyhedron["icosahedron"]""",
        "Icosahedron[l_?NumberQ]": """UniformPolyhedron["icosahedron", {{0, 0, 0}}, l]""",
        "Icosahedron[positions_List, l_?NumberQ]": """UniformPolyhedron["icosahedron", positions, l]""",
    }
    summary_text = "produce an icosahedron"


class Octahedron(Builtin):
    """
    <url>:Octahedron:
    https://en.wikipedia.org/wiki/Octahedron</url> (<url>:WMA:
    :https://reference.wolfram.com/language/ref/Octahedron.html</url>)

    <dl>
      <dt>'Octahedron[]'
      <dd>a regular octahedron centered at the origin with unit edge length.

      <dt>'Octahedron[$l$]'
      <dd>a regular octahedron centered at the origin with edge length $l$.

      <dt>'Octahedron[{$x$, $y$, $z$}, ...]'
      <dd>a regular octahedron centered at {$x$ $y$, $z$}.

    </dl>

    >> Graphics3D[{Red, Octahedron[]}]
     = -Graphics3D-
    """

    rules = {
        "Octahedron[]": """UniformPolyhedron["octahedron"]""",
        "Octahedron[l_?NumberQ]": """UniformPolyhedron["octahedron", {{0, 0, 0}}, l]""",
        "Octahedron[positions_List, l_?NumberQ]": """UniformPolyhedron["octahedron", positions, l]""",
    }
    summary_text = "produce an octahedron"


class Tetrahedron(Builtin):
    """
    <url>:Tetrahedron:
    https://en.wikipedia.org/wiki/Tetrahedron</url> (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/Tetrahedron.html</url>)

    <dl>
      <dt>'Tetrahedron[]'
      <dd>a regular tetrahedron centered at the origin with unit edge length.

      <dt>'Tetrahedron'[$l$]
      <dd>a regular tetrahedron centered at the origin with edge length $l$.

      <dt>'Tetrahedron'[{$x$, $y$, $z$}, ...]
      <dd>a regular tetrahedron centered at {$x$ $y$, $z$}.

    </dl>

    >> Graphics3D[Tetrahedron[{{0,0,0}, {1,1,1}}, 2], Axes->True]
     = -Graphics3D-
    """

    rules = {
        "Tetrahedron[]": """UniformPolyhedron["tetrahedron"]""",
        "Tetrahedron[l_?NumberQ]": """UniformPolyhedron["tetrahedron", {{0, 0, 0}}, l]""",
        "Tetrahedron[positions_List, l_?NumberQ]": """UniformPolyhedron["tetrahedron", positions, l]""",
    }
    summary_text = "produce a tetrahedron"

    def eval_with_length(self, length, evaluation: Evaluation):
        "Tetrahedron[l_?Numeric]"


class UniformPolyhedron(Builtin):
    """
    <url>:Uniform polyhedron:
    https://en.wikipedia.org/wiki/Uniform_polyhedron</url> (<url>:WMA link:
    https://reference.wolfram.com/language/ref/UniformPolyhedron.html</url>)

    <dl>
      <dt>'UniformPolyhedron'["$name$"]
      <dd>return a uniform polyhedron with the given name.
      <dd>Names are "$tetrahedron$", "$octahedron$", "$dodecahedron$", or "$icosahedron$".
    </dl>

    >> Graphics3D[UniformPolyhedron["octahedron"]]
     = -Graphics3D-

    >> Graphics3D[UniformPolyhedron["dodecahedron"]]
     = -Graphics3D-

    >> Graphics3D[{"Brown", UniformPolyhedron["tetrahedron"]}]
     = -Graphics3D-
    """

    messages = {
        "argtype": f"Argument `1` is not one of: {uniform_polyhedra_names}",
    }

    rules = {
        "UniformPolyhedron[name_String]": "UniformPolyhedron[name, {{0, 0, 0}}, 1]",
    }
    summary_text = "produce platonic polyhedra by name"

    def eval(self, name, positions, edgelength, evaluation: Evaluation):
        "UniformPolyhedron[name_String, positions_List, edgelength_?NumberQ]"

        if name.value not in uniform_polyhedra_set:
            evaluation.error("UniformPolyhedron", "argtype", name)

        return
