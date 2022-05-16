# from .helper import session
from mathics.session import MathicsSession

session = MathicsSession()

# from mathics.builtin.base import BoxConstruct, Predefined


import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ('"4.32313213213`2"', "\\text{4.32`2}", None),
    ],
)
@pytest.mark.xfail
def test_makeboxes_standardform_tex_failing(
    str_expr: str, str_expected: str, msg: str, message=""
):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, "System`StandardForm")
    # Atoms are not still correctly processed as BoxConstruct
    #    assert isinstance(format_result,  BoxConstruct)
    if msg:
        assert (
            format_result.boxes_to_text(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        str_format = format_result.boxes_to_text(evaluation=session.evaluation)
        assert str_format == str_expected


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ('"4.32313213213`2"', "\\text{4.32`2}", None),
    ],
)
@pytest.mark.xfail
def test_makeboxes_outputform_tex_failing(
    str_expr: str, str_expected: str, msg: str, message=""
):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, "System`OutputForm")
    # Atoms are not still correctly processed as BoxConstruct
    #    assert isinstance(format_result,  BoxConstruct)
    if msg:
        assert (
            format_result.boxes_to_text(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        str_format = format_result.boxes_to_text(evaluation=session.evaluation)
        assert str_format == str_expected


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ('"4.32313213213`2"', "4.32`2", None),
        # Boxerror
        ("Subscript[a, 4]", "Subscript[a, 4]", None),
        ("Subsuperscript[a, p, q]", "Subsuperscript[a, p, q]", None),
        (
            "Integrate[F[x],{x,a,g[b]}]",
            "Subsuperscript[∫, a, g[b]]\u2062F[x]\u2062\uf74cx",
            None,
        ),
        # This seems to be wrong...
        ("a^(b/c)", "a^( ( b ) / ( c ) )", None),
        # Boxerror
        (
            "Sqrt[1/(1+1/(1+1/a))]",
            "Sqrt[ ( 1 ) / ( 1+ ( 1 ) / ( 1+ ( 1 ) / ( a )  )  ) ]",
            None,
        ),
    ],
)
@pytest.mark.xfail
def test_makeboxes_standardform_text_failing(
    str_expr: str, str_expected: str, msg: str, message=""
):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, "System`StandardForm")
    # Atoms are not still correctly processed as BoxConstruct
    #    assert isinstance(format_result,  BoxConstruct)
    if msg:
        assert (
            format_result.boxes_to_text(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        str_format = format_result.boxes_to_text(evaluation=session.evaluation)
        assert str_format == str_expected


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ('"4.32313213213`2"', "4.32`2", None),
    ],
)
@pytest.mark.xfail
def test_makeboxes_outputform_text_tofix(
    str_expr: str, str_expected: str, msg: str, message=""
):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, "System`OutputForm")
    # Atoms are not still correctly processed as BoxConstruct
    #    assert isinstance(format_result,  BoxConstruct)
    if msg:
        assert (
            format_result.boxes_to_text(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        assert (
            format_result.boxes_to_text(evaluation=session.evaluation) == str_expected
        )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ('"4.32313213213`2"', "<mtext>4.32`2</mtext>", None),
    ],
)
@pytest.mark.xfail
def test_makeboxes_outputform_mathml_failing(
    str_expr: str, str_expected: str, msg: str, message=""
):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, "System`OutputForm")
    # Atoms are not still correctly processed as BoxConstruct
    #    assert isinstance(format_result,  BoxConstruct)
    if msg:
        assert (
            format_result.boxes_to_mathml(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        str_format = format_result.boxes_to_mathml(evaluation=session.evaluation)
        print(f"<<{str_format}>>")
        print(f"<<{str_expected}>>")
        assert str_format == str_expected


# MathML OutputForm
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ('"4"', "<mtext>4</mtext>", None),
        # The following seems wrong: they should be formatted as numbers
        ("4", "<mn>4</mn>", None),
        ('"4.32"', "<mtext>4.32</mtext>", None),
        ('"1.6*^-19"', "<mtext>1.6*^-19</mtext>", None),
        ('"Hola!"', "<mtext>Hola!</mtext>", None),
        ("a", "<mi>a</mi>", None),
        ("Pi", "<mi>Pi</mi>", None),
        (
            "a^4",
            "<mrow><mi>a</mi> <mtext>&nbsp;^&nbsp;</mtext> <mn>4</mn></mrow>",
            None,
        ),
        (
            "Subscript[a, 4]",
            "<mrow><mi>Subscript</mi> <mo>[</mo> <mrow><mi>a</mi> <mtext>,&nbsp;</mtext> <mn>4</mn></mrow> <mo>]</mo></mrow>",
            None,
        ),
        (
            "Subsuperscript[a, p, q]",
            "<mrow><mi>Subsuperscript</mi> <mo>[</mo> <mrow><mi>a</mi> <mtext>,&nbsp;</mtext> <mi>p</mi> <mtext>,&nbsp;</mtext> <mi>q</mi></mrow> <mo>]</mo></mrow>",
            None,
        ),
        (
            "Integrate[F[x],{x,a,g[b]}]",
            "<mrow><mi>Integrate</mi> <mo>[</mo> <mrow><mrow><mi>F</mi> <mo>[</mo> <mi>x</mi> <mo>]</mo></mrow> <mtext>,&nbsp;</mtext> <mrow><mo>{</mo> <mrow><mi>x</mi> <mtext>,&nbsp;</mtext> <mi>a</mi> <mtext>,&nbsp;</mtext> <mrow><mi>g</mi> <mo>[</mo> <mi>b</mi> <mo>]</mo></mrow></mrow> <mo>}</mo></mrow></mrow> <mo>]</mo></mrow>",
            None,
        ),
        # This seems to be wrong...
        (
            "a^(b/c)",
            "<mrow><mi>a</mi> <mtext>&nbsp;^&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mi>b</mi> <mtext>&nbsp;/&nbsp;</mtext> <mi>c</mi></mrow> <mo>)</mo></mrow></mrow>",
            None,
        ),
        (
            "1/(1+1/(1+1/a))",
            "<mrow><mn>1</mn> <mtext>&nbsp;/&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mn>1</mn> <mtext>&nbsp;+&nbsp;</mtext> <mrow><mn>1</mn> <mtext>&nbsp;/&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mn>1</mn> <mtext>&nbsp;+&nbsp;</mtext> <mrow><mn>1</mn> <mtext>&nbsp;/&nbsp;</mtext> <mi>a</mi></mrow></mrow> <mo>)</mo></mrow></mrow></mrow> <mo>)</mo></mrow></mrow>",
            None,
        ),
        (
            "Sqrt[1/(1+1/(1+1/a))]",
            "<mrow><mi>Sqrt</mi> <mo>[</mo> <mrow><mn>1</mn> <mtext>&nbsp;/&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mn>1</mn> <mtext>&nbsp;+&nbsp;</mtext> <mrow><mn>1</mn> <mtext>&nbsp;/&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mn>1</mn> <mtext>&nbsp;+&nbsp;</mtext> <mrow><mn>1</mn> <mtext>&nbsp;/&nbsp;</mtext> <mi>a</mi></mrow></mrow> <mo>)</mo></mrow></mrow></mrow> <mo>)</mo></mrow></mrow> <mo>]</mo></mrow>",
            None,
        ),
        (
            "Graphics[{}]",
            (
                '<mglyph width="350px" height="350px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMnB4IiBoZWlnaHQ9IjJweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9Ii0xLjAwMDAwMCAtMS4wMDAwMDAgMi4wMDAwMDAgMi4wMDAwMDAiPgogICAgICAgICAgICAgICAgPCEtLUdyYXBoaWNzRWxlbWVudHMtLT4KPC9zdmc+Cg=="/>'
            ),
            None,
        ),
        # These tests requires ``evaluation`` as a parameter.
        (
            "Grid[{{a,b},{c,d}}]",
            (
                '<mtable columnalign="center">\n'
                '<mtr><mtd columnalign="center"><mi>a</mi></mtd><mtd columnalign="center"><mi>b</mi></mtd></mtr>\n'
                '<mtr><mtd columnalign="center"><mi>c</mi></mtd><mtd columnalign="center"><mi>d</mi></mtd></mtr>\n'
                "</mtable>"
            ),
            None,
        ),
        (
            "TableForm[{{a,b},{c,d}}]",
            (
                '<mtable columnalign="center">\n'
                '<mtr><mtd columnalign="center"><mi>a</mi></mtd><mtd columnalign="center"><mi>b</mi></mtd></mtr>\n'
                '<mtr><mtd columnalign="center"><mi>c</mi></mtd><mtd columnalign="center"><mi>d</mi></mtd></mtr>\n'
                "</mtable>"
            ),
            None,
        ),
        (
            "MatrixForm[{{a,b},{c,d}}]",
            (
                '<mtable columnalign="center">\n'
                '<mtr><mtd columnalign="center"><mi>a</mi></mtd><mtd columnalign="center"><mi>b</mi></mtd></mtr>\n'
                '<mtr><mtd columnalign="center"><mi>c</mi></mtd><mtd columnalign="center"><mi>d</mi></mtd></mtr>\n'
                "</mtable>"
            ),
            None,
        ),
        (
            "Graphics[{Text[a^b,{0,0}]}]",
            (
                """<mglyph width="294px" height="350px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEuMHB4IiBoZWlnaHQ9IjI1LjBweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9IjEzNi41MDAwMDAgMTYyLjUwMDAwMCAyMS4wMDAwMDAgMjUuMDAwMDAwIj4KICAgICAgICAgICAgICAgIDwhLS1HcmFwaGljc0VsZW1lbnRzLS0+Cjx0ZXh0IHg9IjE0Ny4wIiB5PSIxNzUuMCIgb3g9IjAiIG95PSIwIiBmb250LXNpemU9IjEwcHgiIHN0eWxlPSJ0ZXh0LWFuY2hvcjplbmQ7IGRvbWluYW50LWJhc2VsaW5lOmhhbmdpbmc7IHN0cm9rZTogcmdiKDAuMDAwMDAwJSwgMC4wMDAwMDAlLCAwLjAwMDAwMCUpOyBzdHJva2Utb3BhY2l0eTogMTsgZmlsbDogcmdiKDAuMDAwMDAwJSwgMC4wMDAwMDAlLCAwLjAwMDAwMCUpOyBmaWxsLW9wYWNpdHk6IDE7IGNvbG9yOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IG9wYWNpdHk6IDEuMCI+YV5iPC90ZXh0Pgo8L3N2Zz4K"/>"""
            ),
            None,
        ),
        (
            "TableForm[{Graphics[{Text[a^b,{0,0}]}], Graphics[{Text[a^b,{0,0}]}]}]",
            (
                """<mtable columnalign="center">
<mtr><mtd columnalign="center"><mglyph width="147px" height="175px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEuMHB4IiBoZWlnaHQ9IjI1LjBweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9IjYzLjAwMDAwMCA3NS4wMDAwMDAgMjEuMDAwMDAwIDI1LjAwMDAwMCI+CiAgICAgICAgICAgICAgICA8IS0tR3JhcGhpY3NFbGVtZW50cy0tPgo8dGV4dCB4PSI3My41IiB5PSI4Ny41IiBveD0iMCIgb3k9IjAiIGZvbnQtc2l6ZT0iMTBweCIgc3R5bGU9InRleHQtYW5jaG9yOmVuZDsgZG9taW5hbnQtYmFzZWxpbmU6aGFuZ2luZzsgc3Ryb2tlOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IHN0cm9rZS1vcGFjaXR5OiAxOyBmaWxsOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IGZpbGwtb3BhY2l0eTogMTsgY29sb3I6IHJnYigwLjAwMDAwMCUsIDAuMDAwMDAwJSwgMC4wMDAwMDAlKTsgb3BhY2l0eTogMS4wIj5hXmI8L3RleHQ+Cjwvc3ZnPgo="/></mtd></mtr>
<mtr><mtd columnalign="center"><mglyph width="147px" height="175px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEuMHB4IiBoZWlnaHQ9IjI1LjBweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9IjYzLjAwMDAwMCA3NS4wMDAwMDAgMjEuMDAwMDAwIDI1LjAwMDAwMCI+CiAgICAgICAgICAgICAgICA8IS0tR3JhcGhpY3NFbGVtZW50cy0tPgo8dGV4dCB4PSI3My41IiB5PSI4Ny41IiBveD0iMCIgb3k9IjAiIGZvbnQtc2l6ZT0iMTBweCIgc3R5bGU9InRleHQtYW5jaG9yOmVuZDsgZG9taW5hbnQtYmFzZWxpbmU6aGFuZ2luZzsgc3Ryb2tlOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IHN0cm9rZS1vcGFjaXR5OiAxOyBmaWxsOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IGZpbGwtb3BhY2l0eTogMTsgY29sb3I6IHJnYigwLjAwMDAwMCUsIDAuMDAwMDAwJSwgMC4wMDAwMDAlKTsgb3BhY2l0eTogMS4wIj5hXmI8L3RleHQ+Cjwvc3ZnPgo="/></mtd></mtr>
</mtable>"""
            ),
            None,
        ),
    ],
)
# @pytest.mark.xfail
def test_makeboxes_outputform_mathml(
    str_expr: str, str_expected: str, msg: str, message=""
):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, "System`OutputForm")
    # Atoms are not still correctly processed as BoxConstruct
    #    assert isinstance(format_result,  BoxConstruct)
    if msg:
        assert (
            format_result.boxes_to_mathml(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        str_format = format_result.boxes_to_mathml(evaluation=session.evaluation)
        print(f"<<{str_format}>>")
        print(f"<<{str_expected}>>")
        assert str_format == str_expected


# Text StandardForm
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ('"4"', "4", None),
        ("4", "4", None),
        ('"4.32"', "4.32", None),
        ("1.6*^-19", "1.6*^-19", None),
        ('"Hola!"', "Hola!", None),
        ("a", "a", None),
        ("Pi", "Pi", None),
        ("a^4", "a^4", None),
        ("1/(1+1/(1+1/a))", " ( 1 ) / ( 1+ ( 1 ) / ( 1+ ( 1 ) / ( a )  )  ) ", None),
        ("Graphics[{}]", "-Graphics-", None),
        # These tests requires ``evaluation`` as a parameter.
        ("Grid[{{a,b},{c,d}}]", "a   b\n\nc   d\n", None),
        ("TableForm[{{a,b},{c,d}}]", "a   b\n\nc   d\n", None),
        ("MatrixForm[{{a,b},{c,d}}]", "(a   b\n\nc   d\n)", None),
        ("Graphics[{Text[a^b,{0,0}]}]", "-Graphics-", None),
        (
            "TableForm[{Graphics[{Text[a^b,{0,0}]}], Graphics[{Text[a^b,{0,0}]}]}]",
            ("-Graphics-\n\n-Graphics-\n"),
            None,
        ),
    ],
)
# @pytest.mark.xfail
def test_makeboxes_standardform_text(
    str_expr: str, str_expected: str, msg: str, message=""
):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, "System`StandardForm")
    # Atoms are not still correctly processed as BoxConstruct
    #    assert isinstance(format_result,  BoxConstruct)
    if msg:
        assert (
            format_result.boxes_to_text(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        str_format = format_result.boxes_to_text(evaluation=session.evaluation)
        assert str_format == str_expected


# Text OutputForm
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ('"4"', "4", None),
        ("4", "4", None),
        ('"4.32"', "4.32", None),
        ("1.6*^-19", "1.6×10^-19", None),
        ('"Hola!"', "Hola!", None),
        ("a", "a", None),
        ("Pi", "Pi", None),
        ("a^4", "a ^ 4", None),
        ("Subscript[a, 4]", "Subscript[a, 4]", None),
        ("Subsuperscript[a, p, q]", "Subsuperscript[a, p, q]", None),
        ("Integrate[F[x],{x,a,g[b]}]", "Integrate[F[x], {x, a, g[b]}]", None),
        ("a^(b/c)", "a ^ (b / c)", None),
        ("1/(1+1/(1+1/a))", "1 / (1 + 1 / (1 + 1 / a))", None),
        ("Sqrt[1/(1+1/(1+1/a))]", "Sqrt[1 / (1 + 1 / (1 + 1 / a))]", None),
        ("Graphics[{}]", "-Graphics-", None),
        # These tests requires ``evaluation`` as a parameter.
        ("Grid[{{a,b},{c,d}}]", "a   b\n\nc   d\n", None),
        ("TableForm[{{a,b},{c,d}}]", "a   b\n\nc   d\n", None),
        ("MatrixForm[{{a,b},{c,d}}]", "a   b\n\nc   d\n", None),
        ("Graphics[{Text[a^b,{0,0}]}]", "-Graphics-", None),
        (
            "TableForm[{Graphics[{Text[a^b,{0,0}]}], Graphics[{Text[a^b,{0,0}]}]}]",
            ("-Graphics-\n\n-Graphics-\n"),
            None,
        ),
    ],
)
# @pytest.mark.xfail
def test_makeboxes_outputform_text(
    str_expr: str, str_expected: str, msg: str, message=""
):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, "System`OutputForm")
    # Atoms are not still correctly processed as BoxConstruct
    #    assert isinstance(format_result,  BoxConstruct)
    if msg:
        assert (
            format_result.boxes_to_text(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        assert (
            format_result.boxes_to_text(evaluation=session.evaluation) == str_expected
        )


# TeX StandardForm
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ('"4"', "\\text{4}", None),
        ("4", "4", None),
        ('"4.32"', "\\text{4.32}", None),
        ("1.6*^-19", "1.6\\text{*${}^{\\wedge}$}-19", None),
        ('"Hola!"', "\\text{Hola!}", None),
        ("Pi", "\\text{Pi}", None),
        ("a", "a", None),
        ("a^4", "a^4", None),
        ("Subscript[a, 4]", "a_4", None),
        ("Subsuperscript[a, p, q]", "a_p^q", None),
        (
            "Integrate[F[x],{x,a,g[b]}]",
            "\\int_a^{g\\left[b\\right]} F\\left[x\\right] \uf74cx",
            None,
        ),
        ("a^(b/c)", "a^{\\frac{b}{c}}", None),
        ("1/(1+1/(1+1/a))", "\\frac{1}{1+\\frac{1}{1+\\frac{1}{a}}}", None),
        (
            "Sqrt[1/(1+1/(1+1/a))]",
            "\\sqrt{\\frac{1}{1+\\frac{1}{1+\\frac{1}{a}}}}",
            None,
        ),
        (
            "Graphics[{}]",
            (
                """\n\\begin{asy}\nusepackage("amsmath");"""
                """\nsize(5.8333cm, 5.8333cm);\n\n\n"""
                """clip(box((-1,-1), (1,1)));\n\n\\end{asy}\n"""
            ),
            None,
        ),
        # These tests requires ``evaluation`` as a parameter.
        ("Grid[{{a,b},{c,d}}]", "\\begin{array}{cc} a & b\\\\ c & d\\end{array}", None),
        (
            "TableForm[{{a,b},{c,d}}]",
            "\\begin{array}{cc} a & b\\\\ c & d\\end{array}",
            None,
        ),
        (
            "MatrixForm[{{a,b},{c,d}}]",
            "\\left(\\begin{array}{cc} a & b\\\\ c & d\\end{array}\\right)",
            None,
        ),
        (
            "Graphics[{Text[a^b,{0,0}]}]",
            (
                '\n\\begin{asy}\nusepackage("amsmath");\nsize(4.9cm, 5.8333cm);\n\n'
                '// InsetBox\nlabel("$a^b$", (147.0,175.0), (0,0), rgb(0, 0, 0));\n\n'
                "clip(box((136.5,162.5), (157.5,187.5)));\n\n\\end{asy}\n"
            ),
            None,
        ),
        (
            "TableForm[{Graphics[{Text[a^b,{0,0}]}], Graphics[{Text[a^b,{0,0}]}]}]",
            (
                '\\begin{array}{c} \n\\begin{asy}\nusepackage("amsmath");\nsize(2.45cm, 2.9167cm);\n\n'
                '// InsetBox\nlabel("$a^b$", (73.5,87.5), (0,0), rgb(0, 0, 0));\n\nclip(box((63,75), (84,100)));\n\n'
                '\\end{asy}\n\\\\ \n\\begin{asy}\nusepackage("amsmath");\n'
                'size(2.45cm, 2.9167cm);\n\n// InsetBox\nlabel("$a^b$", (73.5,87.5), (0,0), rgb(0, 0, 0));\n\n'
                "clip(box((63,75), (84,100)));\n\n\\end{asy}\n\\end{array}"
            ),
            None,
        ),
    ],
)
# @pytest.mark.xfail
def test_makeboxes_standard_tex(str_expr: str, str_expected: str, msg: str, message=""):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, "System`StandardForm")
    # Atoms are not still correctly processed as BoxConstruct
    # assert isinstance(format_result,  BoxConstruct)
    if msg:
        assert (
            format_result.boxes_to_tex(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        strresult = format_result.boxes_to_tex(evaluation=session.evaluation)
        assert strresult == str_expected


# TeX OutputForm
@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ('"4"', "\\text{4}", None),
        ("4", "4", None),
        ('"4.32"', "\\text{4.32}", None),
        ("1.6*^-19", "1.6\\times 10^{-19}", None),
        ('"Hola!"', "\\text{Hola!}", None),
        ("Pi", "\\text{Pi}", None),
        ("a", "a", None),
        ("a^4", "a\\text{ ${}^{\\wedge}$ }4", None),
        ("Subscript[a, 4]", "\\text{Subscript}\\left[a, 4\\right]", None),
        (
            "Subsuperscript[a, p, q]",
            "\\text{Subsuperscript}\\left[a, p, q\\right]",
            None,
        ),
        (
            "Integrate[F[x],{x,a,g[b]}]",
            "\\text{Integrate}\\left[F\\left[x\\right], \\left\\{x, a, g\\left[b\\right]\\right\\}\\right]",
            None,
        ),
        ("a^(b/c)", "a\\text{ ${}^{\\wedge}$ }\\left(b\\text{ / }c\\right)", None),
        (
            "1/(1+1/(1+1/a))",
            "1\\text{ / }\\left(1\\text{ + }1\\text{ / }\\left(1\\text{ + }1\\text{ / }a\\right)\\right)",
            None,
        ),
        (
            "Sqrt[1/(1+1/(1+1/a))]",
            "\\text{Sqrt}\\left[1\\text{ / }\\left(1\\text{ + }1\\text{ / }\\left(1\\text{ + }1\\text{ / }a\\right)\\right)\\right]",
            None,
        ),
        (
            "Graphics[{}]",
            (
                """\n\\begin{asy}\nusepackage("amsmath");"""
                """\nsize(5.8333cm, 5.8333cm);\n\n\n"""
                """clip(box((-1,-1), (1,1)));\n\n\\end{asy}\n"""
            ),
            None,
        ),
        # These tests requires ``evaluation`` as a parameter.
        ("Grid[{{a,b},{c,d}}]", "\\begin{array}{cc} a & b\\\\ c & d\\end{array}", None),
        (
            "TableForm[{{a,b},{c,d}}]",
            "\\begin{array}{cc} a & b\\\\ c & d\\end{array}",
            None,
        ),
        (
            "MatrixForm[{{a,b},{c,d}}]",
            "\\begin{array}{cc} a & b\\\\ c & d\\end{array}",
            None,
        ),
        (
            "Graphics[{Text[a^b,{0,0}]}]",
            (
                '\n\\begin{asy}\nusepackage("amsmath");\nsize(4.9cm, 5.8333cm);\n\n'
                '// InsetBox\nlabel("$a^b$", (147.0,175.0), (0,0), rgb(0, 0, 0));\n\n'
                "clip(box((136.5,162.5), (157.5,187.5)));\n\n\\end{asy}\n"
            ),
            None,
        ),
        (
            "TableForm[{Graphics[{Text[a^b,{0,0}]}], Graphics[{Text[a^b,{0,0}]}]}]",
            (
                '\\begin{array}{c} \n\\begin{asy}\nusepackage("amsmath");\nsize(2.45cm, 2.9167cm);\n\n'
                '// InsetBox\nlabel("$a^b$", (73.5,87.5), (0,0), rgb(0, 0, 0));\n\nclip(box((63,75), (84,100)));\n\n'
                '\\end{asy}\n\\\\ \n\\begin{asy}\nusepackage("amsmath");\n'
                'size(2.45cm, 2.9167cm);\n\n// InsetBox\nlabel("$a^b$", (73.5,87.5), (0,0), rgb(0, 0, 0));\n\n'
                "clip(box((63,75), (84,100)));\n\n\\end{asy}\n\\end{array}"
            ),
            None,
        ),
    ],
)
# @pytest.mark.xfail
def test_makeboxes_output_tex(str_expr: str, str_expected: str, msg: str, message=""):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, "System`OutputForm")
    # Atoms are not still correctly processed as BoxConstruct
    # assert isinstance(format_result,  BoxConstruct)
    if msg:
        assert (
            format_result.boxes_to_tex(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        strresult = format_result.boxes_to_tex(evaluation=session.evaluation)
        assert strresult == str_expected
