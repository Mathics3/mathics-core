from mathics.doc.doc_entries import normalize_indent
from mathics.doc.rst_parser import rst_to_native

RST_EXAMPLES = (
    (
        """
        See the picture:

        .. image:: picture.jpeg
            :height: 100px
            :width: 200 px
            :scale: 50 %
            :loading: embed
            :alt: alternate text
            :align: right

        The previous image ilustrates something.

        Then, let's consider the following code:

        .. code:: python
            def f(x):
                return x**2

            f(2)

        which computes the square of 2.

        In Mathics, the same can be done in the following way:
        
        .. code:: mathics
            F[x_]:=x^2
            F[2]
        """,
        """
    See the picture:

    <imgpng  src=' picture.jpeg' height='100px' width='200 px' scale='50 %' loading='embed' alt='alternate text' align='right'>
    The previous image ilustrates something.

    Then, let's consider the following code:

    <python>
    def f(x):
        return x**2

    f(2)
    </python>
    which computes the square of 2.

    In Mathics, the same can be done in the following way:

        >> F[x_]:=x^2
           F[2]

""",
    ),
)


def test_rst_parser():
    """
    Test the convertion of RsT text to
    the native syntax.
    """
    for text, expected in RST_EXAMPLES:
        result = rst_to_native(normalize_indent(text))
        assert normalize_indent(expected) == result
