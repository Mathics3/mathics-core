"test latex formatter"

from test.helper import reset_session, session

import pytest

from mathics.core.systemsymbols import SymbolStandardForm
from mathics.format.box import format_element

reset_session()
evaluation = session.evaluation


def get_latex(wl_expression):
    wl_expression = session.evaluate(wl_expression)
    print(wl_expression)
    boxes = format_element(wl_expression, evaluation, SymbolStandardForm)
    return boxes.to_tex(show_string_characters=False, evaluation=evaluation).strip()


@pytest.mark.parametrize(
    ("testcase", "expected"),
    [
        ("_", r"\_"),
        ('"_"', r"\text{\_}"),
        ('"["', r"\text{[}"),
        ('"]"', r"\text{]}"),
        ("HoldForm[A[[1,2]]]", r"A[[1, 2]]"),
        ('"wrong ]"', r"\text{wrong ]}"),
        ("Integrate[F[x],x]", r"\int F[x] \, dx"),
        ("Cap[c,b]", r"c \cap b"),
        ("CupCap[c,b]", r"c \stackrel{\smile}{\frown} b"),
        ("Congruent[c,b]", r"c \equiv b"),
        ("Pi", r"\pi"),
        # In symbols and expressions
        (r"\[Alpha]", r"\alpha"),
        # In this case, without the linebreak, the tokeniser
        # produce an error...
        ("\\[Alpha]s\n", r"\text{$\alpha$s}"),
        (r"\[Alpha] s", r"s  \alpha"),
        (r"\[AAcute]", r"\text{\'{a}}"),
        # In this case, without the linebreak, the tokeniser
        # produce an error...
        ("\\[AAcute]s\n", r"\text{\'{a}s}"),
        (r"\[AAcute] s", r"s  \text{\'{a}}"),
        # In strings
        (r'"\[Alpha]"', r"\text{$\alpha$}"),
        (r'"\[Alpha]s"', r"\text{$\alpha$s}"),
        (r'"\[AAcute]"', r"\text{\'{a}}"),
        (r'"M\[AAcute]s!"', r"\text{M\'{a}s!}"),
        # $
        ("$Failed", r"\text{\$Failed}"),
        ('"$Failed"', r"\text{\$Failed}"),
        ("a < b", r"a<b"),
        ('"<a|b>"', r"\text{$<$a$\vert$b$>$}"),
        ('"a & b"', r"\text{a $\&$ b}"),
        ("a&", r"a\&"),
        ('"a # b"', r"\text{a $\#$ b}"),
        ("#1", r"\text{$\#$1}"),
        ("%1", r"\text{$\%$1}"),
        ('"%1"', r"\text{$\%$1}"),
    ],
)
def test_expressions(testcase, expected):
    result = get_latex(testcase)
    assert result == expected
