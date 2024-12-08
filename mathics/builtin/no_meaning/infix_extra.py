"""
Infix Operators that require Additional Mathics3 Modules

Some Infix operators require loading Mathics3 Modules before the operators is used in a special way.

Right now, this happens for directed and undirected edges of a network graph. Before issuing 'LoadModule["pymathics.graph"]', \
the operators here have no meaning and can be user defined like other operators that have no pre-set meaning.
"""

from mathics.core.attributes import A_NO_ATTRIBUTES
from mathics.core.builtin import InfixOperator


class DirectedEdge(InfixOperator):
    """
    <url>
    :WML link:
    https://reference.wolfram.com/language/ref/DirectedEdge.html</url>

    <dl>
      <dt>'DirectedEdge[$x$, $y$, ...]'
      <dd>displays $x$ → $y$ → ...

      Directed edges are typically used in network graphs. In Mathics3, \
      network graphs are supported through a Mathics3 module.

      Issue 'LoadModule["pymathics.graph"]' after 'pip' installing Python package \
     'pymathics-graph'.
    </dl>

    >> DirectedEdge[x, y, z]
     = x → y → z

    >> a \\[DirectedEdge] b
     = a → b

    """

    formats = {
        (("InputForm", "OutputForm", "StandardForm"), "DirectedEdge[args__]"): (
            'Infix[{args}, "→"]'
        ),
    }

    attributes = A_NO_ATTRIBUTES
    default_formats = False  # Don't use any default format rules. Instead, see belo.

    operator = "→"
    summary_text = 'DirectedEdge infix operator "→"'


class UndirectedEdge(InfixOperator):
    """
    <url>
    :WML link:
    https://reference.wolfram.com/language/ref/UndirectedEdge.html</url>

    <dl>
      <dt>'UndrectedEdge[$x$, $y$, ...]'
      <dd>displays $x$ ↔ $y$ ↔ ...

      Undirected edges are typically used in network graphs. In Mathics3, \
      network graphs are supported through a Mathics3 module.

      Issue 'LoadModule["pymathics.graph"]' after 'pip' installing Python package \
     'pymathics-graph'.
    </dl>

    >> UndirectedEdge[x, y, z]
     = x ↔ y ↔ z

    >> a \\[UndirectedEdge] b
     = a ↔ b

    """

    formats = {
        (("InputForm", "OutputForm", "StandardForm"), "UndirectedEdge[args__]"): (
            'Infix[{args}, "↔"]'
        ),
    }

    attributes = A_NO_ATTRIBUTES
    default_formats = False  # Don't use any default format rules. Instead, see belo.

    operator = "↔"
    summary_text = 'UndirectedEdge infix operator "↔"'
