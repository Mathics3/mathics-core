# -*- coding: utf-8 -*-

"""
Uniform Polyhedra

Uniform polyhedra is the grouping of platonic solids, Archimedean solids,\
and regular star polyhedra.
"""

# This tells documentation how to sort this module
# Here we are also hiding "drawing" since this can erroneously appear at the top level.
sort_order = "mathics.builtin.uniform-polyhedra"

from mathics.builtin.base import Builtin
from mathics.core.evaluation import Evaluation

uniform_polyhedra_names = "tetrahedron, octahedron, dodecahedron, icosahedron"
uniform_polyhedra_set = frozenset(uniform_polyhedra_names.split(", "))


class Dodecahedron(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Dodecahedron.html</url>

    <dl>
      <dt>'Dodecahedron[]'
      <dd>a regular dodecahedron centered at the origin with unit edge length.
    </dl>

    >> Graphics3D[Dodecahedron[]]
     = -Graphics3D-
    """

    summary_text = "a dodecahedron"
    rules = {
        "Dodecahedron[]": """UniformPolyhedron["dodecahedron"]""",
        "Dodecahedron[l_?NumberQ]": """UniformPolyhedron["dodecahedron", {{0, 0, 0}}, l]""",
        "Dodecahedron[positions_List, l_?NumberQ]": """UniformPolyhedron["dodecahedron", positions, l]""",
    }


class Icosahedron(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Icosahedron.html</url>

    <dl>
      <dt>'Icosahedron[]'
      <dd>a regular Icosahedron centered at the origin with unit edge length.
    </dl>

    >> Graphics3D[Icosahedron[]]
     = -Graphics3D-
    """

    rules = {
        "Icosahedron[]": """UniformPolyhedron["icosahedron"]""",
        "Icosahedron[l_?NumberQ]": """UniformPolyhedron["icosahedron", {{0, 0, 0}}, l]""",
        "Icosahedron[positions_List, l_?NumberQ]": """UniformPolyhedron["icosahedron", positions, l]""",
    }
    summary_text = "an icosahedron"


class Octahedron(Builtin):
    """
    <url>:WMA link
    :https://reference.wolfram.com/language/ref/Octahedron.html</url>

    <dl>
      <dt>'Octahedron[]'
      <dd>a regular octahedron centered at the origin with unit edge length.
    </dl>

    >> Graphics3D[{Red, Octahedron[]}]
     = -Graphics3D-
    """

    rules = {
        "Octahedron[]": """UniformPolyhedron["octahedron"]""",
        "Octahedron[l_?NumberQ]": """UniformPolyhedron["octahedron", {{0, 0, 0}}, l]""",
        "Octahedron[positions_List, l_?NumberQ]": """UniformPolyhedron["octahedron", positions, l]""",
    }
    summary_text = "an octahedron"


class Tetrahedron(Builtin):
    """
    <url>:WMA link
    :https://reference.wolfram.com/language/ref/Tetrahedron.html</url>

    <dl>
      <dt>'Tetrahedron[]'
      <dd>a regular tetrahedron centered at the origin with unit edge length.
    </dl>

    >> Graphics3D[Tetrahedron[{{0,0,0}, {1,1,1}}, 2], Axes->True]
     = -Graphics3D-
    """

    rules = {
        "Tetrahedron[]": """UniformPolyhedron["tetrahedron"]""",
        "Tetrahedron[l_?NumberQ]": """UniformPolyhedron["tetrahedron", {{0, 0, 0}}, l]""",
        "Tetrahedron[positions_List, l_?NumberQ]": """UniformPolyhedron["tetrahedron", positions, l]""",
    }
    summary_text = "a tetrahedron"

    def eval_with_length(self, length, evaluation: Evaluation):
        "Tetrahedron[l_?Numeric]"


class UniformPolyhedron(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/UniformPolyhedron.html</url>

    <dl>
      <dt>'UniformPolyhedron["name"]'
      <dd>return a uniform polyhedron with the given name.
      <dd>Names are "tetrahedron", "octahedron", "dodecahedron", or "icosahedron".
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
    summary_text = "platonic polyhedra by name"

    def eval(self, name, positions, edgelength, evaluation: Evaluation):
        "UniformPolyhedron[name_String, positions_List, edgelength_?NumberQ]"

        if name.value not in uniform_polyhedra_set:
            evaluation.error("UniformPolyhedron", "argtype", name)

        return
