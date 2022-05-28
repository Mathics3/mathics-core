# from .helper import session
from mathics.session import MathicsSession
import os

session = MathicsSession()

# from mathics.builtin.base import BoxConstruct, Predefined


import pytest

#
#  Aim of the tests:
#
# In these tests, we check that the current behavior of makeboxes does not change
# without noticing that it could affect compatibility with WL and with
# mathics-django. Also looking at some issues in the current behavior regarding
# the WL standard (for instance, how to represent $a^(b/c)$) and the Mathics
# own implementation (BoxError raising in some simple conditions).
# These test should be updated as we fix pending issues.


# Set this to 0 in case mathml tests must be considered xfail. With True, ensures the
# compatibility with the current mathics-django branch.

MATHML_STRICT = (
    int(os.environ.get("MATHML_STRICT", "0")) == 1
)  # To set to True set ENV var to "1"


# This dict contains all the tests. The main key is an expression to be evaluated and
# formatted. For each expression, we have a base message, and tests for each output box
# mode ("text", "mathml" and "tex"). On each mode, we have a dict for the different formats.
# If the value associated with a format is a string and the message does not
# finish with "- Fragile!", the test is considered mandatory,
# (not xfail), and the assert message is the base message.
# If there is a tuple instead, the test is against the first element of the tuple,
# and allowed to fail. In this case, the assert message is the
# concatenation of the base message and the second element of the tuple.


all_test = {
    # Checking basic formats for atoms
    "-4": {
        "msg": "An Integer",
        "text": {
            "System`StandardForm": "-4",
            "System`TraditionalForm": "-4",
            "System`InputForm": "-4",
            "System`OutputForm": "-4",
        },
        "mathml": {
            "System`StandardForm": ("<mn>-4</mn>", "must be <mn>-4</mn>"),
            "System`TraditionalForm": ("<mn>-4</mn>", "must be <mn>-4</mn>"),
            "System`InputForm": "<mtext>-4</mtext>",
            "System`OutputForm": "<mtext>-4</mtext>",
        },
        "tex": {
            "System`StandardForm": "-4",
            "System`TraditionalForm": "-4",
            "System`InputForm": "-4",
            "System`OutputForm": "-4",
        },
    },
    "-4.32": {
        "msg": "A MachineReal number",
        "text": {
            "System`StandardForm": "-4.32",
            "System`TraditionalForm": "-4.32",
            "System`InputForm": "-4.32",
            "System`OutputForm": "-4.32",
        },
        "mathml": {
            "System`StandardForm": (
                "<mn>-4.32</mn>",
                "must be <mn>, not <mtext>",
            ),
            "System`TraditionalForm": (
                "<mn>-4.32</mn>",
                "must be <mn>, not <mtext>",
            ),
            "System`InputForm": "<mtext>-4.32</mtext>",
            "System`OutputForm": "<mtext>-4.32</mtext>",
        },
        "tex": {
            "System`StandardForm": "-4.32",
            "System`TraditionalForm": "-4.32",
            "System`InputForm": "-4.32",
            "System`OutputForm": "-4.32",
        },
    },
    "-4.32`4": {
        "msg": "A PrecisionReal number",
        "text": {
            "System`StandardForm": "-4.320",
            "System`TraditionalForm": "-4.320",
            "System`InputForm": "-4.320",
            "System`OutputForm": "-4.320",
        },
        "mathml": {
            "System`StandardForm": (
                "<mn>-4.320</mn>",
                "must be <mn>, not <mtext>",
            ),
            "System`TraditionalForm": (
                "<mn>-4.320</mn>",
                "must be <mn>, not <mtext>",
            ),
            "System`InputForm": "<mtext>-4.320</mtext>",
            "System`OutputForm": "<mtext>-4.320</mtext>",
        },
        "tex": {
            "System`StandardForm": "-4.320",
            "System`TraditionalForm": "-4.320",
            "System`InputForm": "-4.320",
            "System`OutputForm": "-4.320",
        },
    },
    "-4.326563712`2": {
        "msg": "A Real number",
        "text": {
            "System`StandardForm": "-4.3",
            "System`TraditionalForm": "-4.3",
            "System`InputForm": "-4.3",
            "System`OutputForm": "-4.3",
        },
        "mathml": {
            "System`StandardForm": (
                "<mn>-4.3</mn>",
                "must be <mn>, not <mtext>",
            ),
            "System`TraditionalForm": (
                "<mn>-4.3</mn>",
                "must be <mn>, not <mtext>",
            ),
            "System`InputForm": "<mtext>-4.3</mtext>",
            "System`OutputForm": "<mtext>-4.3</mtext>",
        },
        "tex": {
            "System`StandardForm": "-4.3",
            "System`TraditionalForm": "-4.3",
            "System`InputForm": "-4.3",
            "System`OutputForm": "-4.3",
        },
    },
    '"Hola!"': {
        "msg": "A String",
        "text": {
            "System`StandardForm": "Hola!",
            "System`TraditionalForm": "Hola!",
            "System`InputForm": "Hola!",
            "System`OutputForm": "Hola!",
        },
        "mathml": {
            "System`StandardForm": "<mtext>Hola!</mtext>",
            "System`TraditionalForm": "<mtext>Hola!</mtext>",
            "System`InputForm": "<mtext>Hola!</mtext>",
            "System`OutputForm": "<mtext>Hola!</mtext>",
        },
        "tex": {
            "System`StandardForm": "\\text{Hola!}",
            "System`TraditionalForm": "\\text{Hola!}",
            "System`InputForm": "\\text{Hola!}",
            "System`OutputForm": "\\text{Hola!}",
        },
    },
    # String with special characters
    '"\\[Pi] is a trascendental number"': {
        "msg": "A String",
        "text": {
            "System`StandardForm": "π is a trascendental number",
            "System`TraditionalForm": "π is a trascendental number",
            "System`InputForm": "π is a trascendental number",
            "System`OutputForm": "π is a trascendental number",
        },
        "mathml": {
            "System`StandardForm": "<mtext>π&nbsp;is&nbsp;a&nbsp;trascendental&nbsp;number</mtext>",
            "System`TraditionalForm": "<mtext>π&nbsp;is&nbsp;a&nbsp;trascendental&nbsp;number</mtext>",
            "System`InputForm": "<mtext>π&nbsp;is&nbsp;a&nbsp;trascendental&nbsp;number</mtext>",
            "System`OutputForm": "<mtext>π&nbsp;is&nbsp;a&nbsp;trascendental&nbsp;number</mtext>",
        },
        "tex": {
            "System`StandardForm": "\\text{π is a trascendental number}",
            "System`TraditionalForm": "\\text{π is a trascendental number}",
            "System`InputForm": "\\text{π is a trascendental number}",
            "System`OutputForm": "\\text{π is a trascendental number}",
        },
    },
    '"-4.32"': {
        "msg": "A String with a number",
        "text": {
            "System`StandardForm": "-4.32",
            "System`TraditionalForm": "-4.32",
            "System`InputForm": "-4.32",
            "System`OutputForm": "-4.32",
        },
        "mathml": {
            "System`StandardForm": "<mtext>-4.32</mtext>",
            "System`TraditionalForm": "<mtext>-4.32</mtext>",
            "System`InputForm": "<mtext>-4.32</mtext>",
            "System`OutputForm": "<mtext>-4.32</mtext>",
        },
        "tex": {
            "System`StandardForm": "\\text{-4.32}",
            "System`TraditionalForm": "\\text{-4.32}",
            "System`InputForm": "\\text{-4.32}",
            "System`OutputForm": "\\text{-4.32}",
        },
    },
    # Symbols
    "a": {
        "msg": "A Symbol",
        "text": {
            "System`StandardForm": "a",
            "System`TraditionalForm": "a",
            "System`InputForm": "a",
            "System`OutputForm": "a",
        },
        "mathml": {
            "System`StandardForm": "<mi>a</mi>",
            "System`TraditionalForm": "<mi>a</mi>",
            "System`InputForm": "<mi>a</mi>",
            "System`OutputForm": "<mi>a</mi>",
        },
        "tex": {
            "System`StandardForm": "a",
            "System`TraditionalForm": "a",
            "System`InputForm": "a",
            "System`OutputForm": "a",
        },
    },
    "\\[Pi]": {
        "msg": "A greek letter Symbol",
        "text": {
            "System`StandardForm": "π",
            "System`TraditionalForm": "π",
            "System`InputForm": "Pi",
            "System`OutputForm": "Pi",
        },
        "mathml": {
            "System`StandardForm": "<mi>π</mi>",
            "System`TraditionalForm": "<mi>π</mi>",
            "System`InputForm": "<mi>Pi</mi>",
            "System`OutputForm": "<mi>Pi</mi>",
        },
        "tex": {
            "System`StandardForm": "π",
            "System`TraditionalForm": "π",
            "System`InputForm": "\\text{Pi}",
            "System`OutputForm": "\\text{Pi}",
        },
    },
    # Boxed expressions.
    "a^4": {
        "msg": "SuperscriptBox",
        "text": {
            "System`StandardForm": "a^4",
            "System`TraditionalForm": "a^4",
            "System`InputForm": "a^4",
            "System`OutputForm": "a ^ 4",
        },
        "mathml": {
            "System`StandardForm": (
                "<msup><mi>a</mi> <mn>4</mn></msup>",
                "must be <mn> instead of <mtext>",
            ),
            "System`TraditionalForm": (
                "<msup><mi>a</mi> <mn>4</mn></msup>",
                "must be <mn> instead of <mtext>",
            ),
            "System`InputForm": (
                "<mrow><mi>a</mi> <mo>^</mo> <mtext>4</mtext></mrow>",
                "must be <mtext> instead of <mn> in this case",
            ),
            "System`OutputForm": (
                "<mrow><mi>a</mi> <mtext>&nbsp;^&nbsp;</mtext> <mtext>4</mtext></mrow>",
                "must be <mtext> instead of <mn> in this case",
            ),
        },
        "tex": {
            "System`StandardForm": "a^4",
            "System`TraditionalForm": "a^4",
            "System`InputForm": "a{}^{\\wedge}4",
            "System`OutputForm": "a\\text{ ${}^{\\wedge}$ }4",
        },
    },
    "Subscript[a, 4]": {
        "msg": "SubscriptBox",
        "text": {
            "System`StandardForm": ("Subscript[a, 4]", "BoxError"),
            "System`TraditionalForm": ("Subscript[a, 4]", "BoxError"),
            "System`InputForm": "Subscript[a, 4]",
            "System`OutputForm": "Subscript[a, 4]",
        },
        "mathml": {
            "System`StandardForm": (
                "<msub><mi>a</mi> <mn>4</mn></msub>",
                "must be <mn> instead <mtext>",
            ),
            "System`TraditionalForm": (
                "<msub><mi>a</mi> <mn>4</mn></msub>",
                "must be <mn> instead <mtext>",
            ),
            "System`InputForm": (
                "<mrow><mi>Subscript</mi> <mo>[</mo> <mrow><mi>a</mi> <mtext>,&nbsp;</mtext> <mtext>4</mtext></mrow> <mo>]</mo></mrow>",
                "must be <mtext> instead <mn>",
            ),
            "System`OutputForm": (
                "<mrow><mi>Subscript</mi> <mo>[</mo> <mrow><mi>a</mi> <mtext>,&nbsp;</mtext> <mtext>4</mtext></mrow> <mo>]</mo></mrow>",
                "must be <mtext> instead <mn>",
            ),
        },
        "tex": {
            "System`StandardForm": "a_4",
            "System`TraditionalForm": "a_4",
            "System`InputForm": "\\text{Subscript}\\left[a, 4\\right]",
            "System`OutputForm": "\\text{Subscript}\\left[a, 4\\right]",
        },
    },
    "Subsuperscript[a, p, q]": {
        "msg": "SubsuperscriptBox",
        "text": {
            "System`StandardForm": "Subsuperscript[a, p, q]",
            "System`TraditionalForm": "Subsuperscript[a, p, q]",
            "System`InputForm": "Subsuperscript[a, p, q]",
            "System`OutputForm": "Subsuperscript[a, p, q]",
        },
        "mathml": {
            "System`StandardForm": "<msubsup><mi>a</mi> <mi>p</mi> <mi>q</mi></msubsup>",
            "System`TraditionalForm": "<msubsup><mi>a</mi> <mi>p</mi> <mi>q</mi></msubsup>",
            "System`InputForm": "<mrow><mi>Subsuperscript</mi> <mo>[</mo> <mrow><mi>a</mi> <mtext>,&nbsp;</mtext> <mi>p</mi> <mtext>,&nbsp;</mtext> <mi>q</mi></mrow> <mo>]</mo></mrow>",
            "System`OutputForm": "<mrow><mi>Subsuperscript</mi> <mo>[</mo> <mrow><mi>a</mi> <mtext>,&nbsp;</mtext> <mi>p</mi> <mtext>,&nbsp;</mtext> <mi>q</mi></mrow> <mo>]</mo></mrow>",
        },
        "tex": {
            "System`StandardForm": "a_p^q",
            "System`TraditionalForm": "a_p^q",
            "System`InputForm": "\\text{Subsuperscript}\\left[a, p, q\\right]",
            "System`OutputForm": "\\text{Subsuperscript}\\left[a, p, q\\right]",
        },
    },
    # Here I use Integrate to simplify the input.
    "Integrate[F[x], {x, a, g[b]}]": {
        "msg": "Non trivial SubsuperscriptBox",
        "text": {
            "System`StandardForm": "Subsuperscript[∫, a, g[b]]\u2062F[x]\u2062\uf74cx",
            "System`TraditionalForm": "Subsuperscript[∫, a, g(b)]\u2062F(x)\u2062\uf74cx",
            "System`InputForm": "Integrate[F[x], {x, a, g[b]}]",
            "System`OutputForm": "Integrate[F[x], {x, a, g[b]}]",
        },
        "mathml": {
            "System`StandardForm": '<mrow><msubsup><mo>∫</mo> <mi>a</mi> <mrow><mi>g</mi> <mo>[</mo> <mi>b</mi> <mo>]</mo></mrow></msubsup> <mo form="prefix" lspace="0" rspace="0.2em">\u2062</mo> <mrow><mi>F</mi> <mo>[</mo> <mi>x</mi> <mo>]</mo></mrow> <mo form="prefix" lspace="0" rspace="0.2em">\u2062</mo> <mrow><mtext>\uf74c</mtext> <mi>x</mi></mrow></mrow>',
            "System`TraditionalForm": '<mrow><msubsup><mo>∫</mo> <mi>a</mi> <mrow><mi>g</mi> <mo>(</mo> <mi>b</mi> <mo>)</mo></mrow></msubsup> <mo form="prefix" lspace="0" rspace="0.2em">\u2062</mo> <mrow><mi>F</mi> <mo>(</mo> <mi>x</mi> <mo>)</mo></mrow> <mo form="prefix" lspace="0" rspace="0.2em">\u2062</mo> <mrow><mtext>\uf74c</mtext> <mi>x</mi></mrow></mrow>',
            "System`InputForm": "<mrow><mi>Integrate</mi> <mo>[</mo> <mrow><mrow><mi>F</mi> <mo>[</mo> <mi>x</mi> <mo>]</mo></mrow> <mtext>,&nbsp;</mtext> <mrow><mo>{</mo> <mrow><mi>x</mi> <mtext>,&nbsp;</mtext> <mi>a</mi> <mtext>,&nbsp;</mtext> <mrow><mi>g</mi> <mo>[</mo> <mi>b</mi> <mo>]</mo></mrow></mrow> <mo>}</mo></mrow></mrow> <mo>]</mo></mrow>",
            "System`OutputForm": "<mrow><mi>Integrate</mi> <mo>[</mo> <mrow><mrow><mi>F</mi> <mo>[</mo> <mi>x</mi> <mo>]</mo></mrow> <mtext>,&nbsp;</mtext> <mrow><mo>{</mo> <mrow><mi>x</mi> <mtext>,&nbsp;</mtext> <mi>a</mi> <mtext>,&nbsp;</mtext> <mrow><mi>g</mi> <mo>[</mo> <mi>b</mi> <mo>]</mo></mrow></mrow> <mo>}</mo></mrow></mrow> <mo>]</mo></mrow>",
        },
        "tex": {
            "System`StandardForm": "\\int_a^{g\\left[b\\right]} F\\left[x\\right] \uf74cx",
            "System`TraditionalForm": "\\int_a^{g\\left(b\\right)} F\\left(x\\right) \uf74cx",
            "System`InputForm": "\\text{Integrate}\\left[F\\left[x\\right], \\left\\{x, a, g\\left[b\\right]\\right\\}\\right]",
            "System`OutputForm": "\\text{Integrate}\\left[F\\left[x\\right], \\left\\{x, a, g\\left[b\\right]\\right\\}\\right]",
        },
    },
    # Nested compound expressions:
    "a^(b/c)": {
        "msg": "SuperscriptBox with a nested expression.",
        "text": {
            "System`StandardForm": (
                "a^(b/c)",
                "must be a^(b/c) instead of a^((b)/(c))",
            ),
            "System`TraditionalForm": (
                "a^(b/c)",
                "must be a^(b/c) instead of a^((b)/(c))",
            ),
            "System`InputForm": "a^(b / c)",
            "System`OutputForm": "a ^ (b / c)",
        },
        "mathml": {
            "System`StandardForm": "<msup><mi>a</mi> <mfrac><mi>b</mi> <mi>c</mi></mfrac></msup>",
            "System`TraditionalForm": "<msup><mi>a</mi> <mfrac><mi>b</mi> <mi>c</mi></mfrac></msup>",
            "System`InputForm": "<mrow><mi>a</mi> <mo>^</mo> <mrow><mo>(</mo> <mrow><mi>b</mi> <mtext>&nbsp;/&nbsp;</mtext> <mi>c</mi></mrow> <mo>)</mo></mrow></mrow>",
            "System`OutputForm": "<mrow><mi>a</mi> <mtext>&nbsp;^&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mi>b</mi> <mtext>&nbsp;/&nbsp;</mtext> <mi>c</mi></mrow> <mo>)</mo></mrow></mrow>",
        },
        "tex": {
            "System`StandardForm": "a^{\\frac{b}{c}}",
            "System`TraditionalForm": "a^{\\frac{b}{c}}",
            "System`InputForm": "a{}^{\\wedge}\\left(b\\text{ / }c\\right)",
            "System`OutputForm": "a\\text{ ${}^{\\wedge}$ }\\left(b\\text{ / }c\\right)",
        },
    },
    "1/(1+1/(1+1/a))": {
        "msg": "FractionBox",
        "text": {
            "System`StandardForm": (
                "1 / (1+1 / (1+1 / a))",
                "must be 1 / (1+1 / (1+1 / a))",
            ),
            "System`TraditionalForm": (
                "1 / (1+1 / (1+1 / a))",
                "must be 1 / (1+1 / (1+1 / a))",
            ),
            "System`InputForm": "1 / (1 + 1 / (1 + 1 / a))",
            "System`OutputForm": "1 / (1 + 1 / (1 + 1 / a))",
        },
        "mathml": {
            "System`StandardForm": (
                "<mfrac><mn>1</mn> <mrow><mn>1</mn> <mo>+</mo> <mfrac><mn>1</mn> <mrow><mn>1</mn> <mo>+</mo> <mfrac><mn>1</mn> <mi>a</mi></mfrac></mrow></mfrac></mrow></mfrac>",
                "must be <mn> instead <mtext>",
            ),
            "System`TraditionalForm": (
                "<mfrac><mn>1</mn> <mrow><mn>1</mn> <mo>+</mo> <mfrac><mn>1</mn> <mrow><mn>1</mn> <mo>+</mo> <mfrac><mn>1</mn> <mi>a</mi></mfrac></mrow></mfrac></mrow></mfrac>",
                "must be <mn> instead <mtext>",
            ),
            "System`InputForm": (
                "<mrow><mtext>1</mtext> <mtext>&nbsp;/&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mtext>1</mtext> <mtext>&nbsp;+&nbsp;</mtext> <mrow><mtext>1</mtext> <mtext>&nbsp;/&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mtext>1</mtext> <mtext>&nbsp;+&nbsp;</mtext> <mrow><mtext>1</mtext> <mtext>&nbsp;/&nbsp;</mtext> <mi>a</mi></mrow></mrow> <mo>)</mo></mrow></mrow></mrow> <mo>)</mo></mrow></mrow>",
                "must be <mtext> instead <mn>",
            ),
            "System`OutputForm": (
                "<mrow><mtext>1</mtext> <mtext>&nbsp;/&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mtext>1</mtext> <mtext>&nbsp;+&nbsp;</mtext> <mrow><mtext>1</mtext> <mtext>&nbsp;/&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mtext>1</mtext> <mtext>&nbsp;+&nbsp;</mtext> <mrow><mtext>1</mtext> <mtext>&nbsp;/&nbsp;</mtext> <mi>a</mi></mrow></mrow> <mo>)</mo></mrow></mrow></mrow> <mo>)</mo></mrow></mrow>",
                "must be <mtext> instead <mn>",
            ),
        },
        "tex": {
            "System`StandardForm": "\\frac{1}{1+\\frac{1}{1+\\frac{1}{a}}}",
            "System`TraditionalForm": "\\frac{1}{1+\\frac{1}{1+\\frac{1}{a}}}",
            "System`InputForm": "1\\text{ / }\\left(1\\text{ + }1\\text{ / }\\left(1\\text{ + }1\\text{ / }a\\right)\\right)",
            "System`OutputForm": "1\\text{ / }\\left(1\\text{ + }1\\text{ / }\\left(1\\text{ + }1\\text{ / }a\\right)\\right)",
        },
    },
    "Sqrt[1/(1+1/(1+1/a))]": {
        "msg": "SqrtBox",
        "text": {
            "System`StandardForm": (
                "Sqrt[1 / (1+1 / (1+1 / a))]",
                "must be Sqrt[1 / (1+1 / (1+1 / a))]",
            ),
            "System`TraditionalForm": (
                "Sqrt[1 / (1+1 / (1+1 / a))]",
                "must be Sqrt[1 / (1+1 / (1+1 / a))]",
            ),
            "System`InputForm": "Sqrt[1 / (1 + 1 / (1 + 1 / a))]",
            "System`OutputForm": "Sqrt[1 / (1 + 1 / (1 + 1 / a))]",
        },
        "mathml": {
            "System`StandardForm": (
                "<msqrt> <mfrac><mn>1</mn> <mrow><mn>1</mn> <mo>+</mo> <mfrac><mn>1</mn> <mrow><mn>1</mn> <mo>+</mo> <mfrac><mn>1</mn> <mi>a</mi></mfrac></mrow></mfrac></mrow></mfrac> </msqrt>",
                "must be...",
            ),
            "System`TraditionalForm": (
                "<msqrt> <mfrac><mn>1</mn> <mrow><mn>1</mn> <mo>+</mo> <mfrac><mn>1</mn> <mrow><mn>1</mn> <mo>+</mo> <mfrac><mn>1</mn> <mi>a</mi></mfrac></mrow></mfrac></mrow></mfrac> </msqrt>",
                "must be...",
            ),
            "System`InputForm": (
                "<mrow><mi>Sqrt</mi> <mo>[</mo> <mrow><mtext>1</mtext> <mtext>&nbsp;/&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mtext>1</mtext> <mtext>&nbsp;+&nbsp;</mtext> <mrow><mtext>1</mtext> <mtext>&nbsp;/&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mtext>1</mtext> <mtext>&nbsp;+&nbsp;</mtext> <mrow><mtext>1</mtext> <mtext>&nbsp;/&nbsp;</mtext> <mi>a</mi></mrow></mrow> <mo>)</mo></mrow></mrow></mrow> <mo>)</mo></mrow></mrow> <mo>]</mo></mrow>",
                "must be...",
            ),
            "System`OutputForm": (
                "<mrow><mi>Sqrt</mi> <mo>[</mo> <mrow><mtext>1</mtext> <mtext>&nbsp;/&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mtext>1</mtext> <mtext>&nbsp;+&nbsp;</mtext> <mrow><mtext>1</mtext> <mtext>&nbsp;/&nbsp;</mtext> <mrow><mo>(</mo> <mrow><mtext>1</mtext> <mtext>&nbsp;+&nbsp;</mtext> <mrow><mtext>1</mtext> <mtext>&nbsp;/&nbsp;</mtext> <mi>a</mi></mrow></mrow> <mo>)</mo></mrow></mrow></mrow> <mo>)</mo></mrow></mrow> <mo>]</mo></mrow>",
                "must be ...",
            ),
        },
        "tex": {
            "System`StandardForm": "\\sqrt{\\frac{1}{1+\\frac{1}{1+\\frac{1}{a}}}}",
            "System`TraditionalForm": "\\sqrt{\\frac{1}{1+\\frac{1}{1+\\frac{1}{a}}}}",
            "System`InputForm": "\\text{Sqrt}\\left[1\\text{ / }\\left(1\\text{ + }1\\text{ / }\\left(1\\text{ + }1\\text{ / }a\\right)\\right)\\right]",
            "System`OutputForm": "\\text{Sqrt}\\left[1\\text{ / }\\left(1\\text{ + }1\\text{ / }\\left(1\\text{ + }1\\text{ / }a\\right)\\right)\\right]",
        },
    },
    # Grids, arrays and matrices
    "Grid[{{a,b},{c,d}}]": {
        "msg": "GridBox",
        "text": {
            "System`StandardForm": "a   b\n\nc   d\n",
            "System`TraditionalForm": "a   b\n\nc   d\n",
            "System`InputForm": "Grid[{{a, b}, {c, d}}]",
            "System`OutputForm": "a   b\n\nc   d\n",
        },
        "mathml": {
            "System`StandardForm": '<mtable columnalign="center">\n<mtr><mtd columnalign="center"><mi>a</mi></mtd><mtd columnalign="center"><mi>b</mi></mtd></mtr>\n<mtr><mtd columnalign="center"><mi>c</mi></mtd><mtd columnalign="center"><mi>d</mi></mtd></mtr>\n</mtable>',
            "System`TraditionalForm": '<mtable columnalign="center">\n<mtr><mtd columnalign="center"><mi>a</mi></mtd><mtd columnalign="center"><mi>b</mi></mtd></mtr>\n<mtr><mtd columnalign="center"><mi>c</mi></mtd><mtd columnalign="center"><mi>d</mi></mtd></mtr>\n</mtable>',
            "System`InputForm": "<mrow><mi>Grid</mi> <mo>[</mo> <mrow><mo>{</mo> <mrow><mrow><mo>{</mo> <mrow><mi>a</mi> <mtext>,&nbsp;</mtext> <mi>b</mi></mrow> <mo>}</mo></mrow> <mtext>,&nbsp;</mtext> <mrow><mo>{</mo> <mrow><mi>c</mi> <mtext>,&nbsp;</mtext> <mi>d</mi></mrow> <mo>}</mo></mrow></mrow> <mo>}</mo></mrow> <mo>]</mo></mrow>",
            "System`OutputForm": '<mtable columnalign="center">\n<mtr><mtd columnalign="center"><mi>a</mi></mtd><mtd columnalign="center"><mi>b</mi></mtd></mtr>\n<mtr><mtd columnalign="center"><mi>c</mi></mtd><mtd columnalign="center"><mi>d</mi></mtd></mtr>\n</mtable>',
        },
        "tex": {
            "System`StandardForm": "\\begin{array}{cc} a & b\\\\ c & d\\end{array}",
            "System`TraditionalForm": "\\begin{array}{cc} a & b\\\\ c & d\\end{array}",
            "System`InputForm": "\\text{Grid}\\left[\\left\\{\\left\\{a, b\\right\\}, \\left\\{c, d\\right\\}\\right\\}\\right]",
            "System`OutputForm": "\\begin{array}{cc} a & b\\\\ c & d\\end{array}",
        },
    },
    "TableForm[{{a,b},{c,d}}]": {
        "msg": "GridBox in a table",
        "text": {
            "System`StandardForm": "a   b\n\nc   d\n",
            "System`TraditionalForm": "a   b\n\nc   d\n",
            "System`InputForm": "TableForm[{{a, b}, {c, d}}]",
            "System`OutputForm": "a   b\n\nc   d\n",
        },
        "mathml": {
            "System`StandardForm": '<mtable columnalign="center">\n<mtr><mtd columnalign="center"><mi>a</mi></mtd><mtd columnalign="center"><mi>b</mi></mtd></mtr>\n<mtr><mtd columnalign="center"><mi>c</mi></mtd><mtd columnalign="center"><mi>d</mi></mtd></mtr>\n</mtable>',
            "System`TraditionalForm": '<mtable columnalign="center">\n<mtr><mtd columnalign="center"><mi>a</mi></mtd><mtd columnalign="center"><mi>b</mi></mtd></mtr>\n<mtr><mtd columnalign="center"><mi>c</mi></mtd><mtd columnalign="center"><mi>d</mi></mtd></mtr>\n</mtable>',
            "System`InputForm": "<mrow><mi>TableForm</mi> <mo>[</mo> <mrow><mo>{</mo> <mrow><mrow><mo>{</mo> <mrow><mi>a</mi> <mtext>,&nbsp;</mtext> <mi>b</mi></mrow> <mo>}</mo></mrow> <mtext>,&nbsp;</mtext> <mrow><mo>{</mo> <mrow><mi>c</mi> <mtext>,&nbsp;</mtext> <mi>d</mi></mrow> <mo>}</mo></mrow></mrow> <mo>}</mo></mrow> <mo>]</mo></mrow>",
            "System`OutputForm": '<mtable columnalign="center">\n<mtr><mtd columnalign="center"><mi>a</mi></mtd><mtd columnalign="center"><mi>b</mi></mtd></mtr>\n<mtr><mtd columnalign="center"><mi>c</mi></mtd><mtd columnalign="center"><mi>d</mi></mtd></mtr>\n</mtable>',
        },
        "tex": {
            "System`StandardForm": "\\begin{array}{cc} a & b\\\\ c & d\\end{array}",
            "System`TraditionalForm": "\\begin{array}{cc} a & b\\\\ c & d\\end{array}",
            "System`InputForm": "\\text{TableForm}\\left[\\left\\{\\left\\{a, b\\right\\}, \\left\\{c, d\\right\\}\\right\\}\\right]",
            "System`OutputForm": "\\begin{array}{cc} a & b\\\\ c & d\\end{array}",
        },
    },
    "MatrixForm[{{a,b},{c,d}}]": {
        "msg": "GridBox in a matrix",
        "text": {
            "System`StandardForm": "(a   b\n\nc   d\n)",
            "System`TraditionalForm": "(a   b\n\nc   d\n)",
            "System`InputForm": "MatrixForm[{{a, b}, {c, d}}]",
            "System`OutputForm": "a   b\n\nc   d\n",
        },
        "mathml": {
            "System`StandardForm": '<mrow><mo>(</mo> <mtable columnalign="center">\n<mtr><mtd columnalign="center"><mi>a</mi></mtd><mtd columnalign="center"><mi>b</mi></mtd></mtr>\n<mtr><mtd columnalign="center"><mi>c</mi></mtd><mtd columnalign="center"><mi>d</mi></mtd></mtr>\n</mtable> <mo>)</mo></mrow>',
            "System`TraditionalForm": '<mrow><mo>(</mo> <mtable columnalign="center">\n<mtr><mtd columnalign="center"><mi>a</mi></mtd><mtd columnalign="center"><mi>b</mi></mtd></mtr>\n<mtr><mtd columnalign="center"><mi>c</mi></mtd><mtd columnalign="center"><mi>d</mi></mtd></mtr>\n</mtable> <mo>)</mo></mrow>',
            "System`InputForm": "<mrow><mi>MatrixForm</mi> <mo>[</mo> <mrow><mo>{</mo> <mrow><mrow><mo>{</mo> <mrow><mi>a</mi> <mtext>,&nbsp;</mtext> <mi>b</mi></mrow> <mo>}</mo></mrow> <mtext>,&nbsp;</mtext> <mrow><mo>{</mo> <mrow><mi>c</mi> <mtext>,&nbsp;</mtext> <mi>d</mi></mrow> <mo>}</mo></mrow></mrow> <mo>}</mo></mrow> <mo>]</mo></mrow>",
            "System`OutputForm": '<mtable columnalign="center">\n<mtr><mtd columnalign="center"><mi>a</mi></mtd><mtd columnalign="center"><mi>b</mi></mtd></mtr>\n<mtr><mtd columnalign="center"><mi>c</mi></mtd><mtd columnalign="center"><mi>d</mi></mtd></mtr>\n</mtable>',
        },
        "tex": {
            "System`StandardForm": "\\left(\\begin{array}{cc} a & b\\\\ c & d\\end{array}\\right)",
            "System`TraditionalForm": "\\left(\\begin{array}{cc} a & b\\\\ c & d\\end{array}\\right)",
            "System`InputForm": "\\text{MatrixForm}\\left[\\left\\{\\left\\{a, b\\right\\}, \\left\\{c, d\\right\\}\\right\\}\\right]",
            "System`OutputForm": "\\begin{array}{cc} a & b\\\\ c & d\\end{array}",
        },
    },
    # Boxes including Graphics.
    # These tests could require to be re-generated
    "Graphics[{}]": {
        "msg": "GraphicsBox - Fragile!",
        "text": {
            "System`StandardForm": "-Graphics-",
            "System`TraditionalForm": "-Graphics-",
            "System`InputForm": "Graphics[{}]",
            "System`OutputForm": "-Graphics-",
        },
        "mathml": {
            "System`StandardForm": '<mglyph width="350px" height="350px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMnB4IiBoZWlnaHQ9IjJweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9Ii0xLjAwMDAwMCAtMS4wMDAwMDAgMi4wMDAwMDAgMi4wMDAwMDAiPgogICAgICAgICAgICAgICAgPCEtLUdyYXBoaWNzRWxlbWVudHMtLT4KPC9zdmc+Cg=="/>',
            "System`TraditionalForm": '<mglyph width="350px" height="350px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMnB4IiBoZWlnaHQ9IjJweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9Ii0xLjAwMDAwMCAtMS4wMDAwMDAgMi4wMDAwMDAgMi4wMDAwMDAiPgogICAgICAgICAgICAgICAgPCEtLUdyYXBoaWNzRWxlbWVudHMtLT4KPC9zdmc+Cg=="/>',
            "System`InputForm": "<mrow><mi>Graphics</mi> <mo>[</mo> <mrow><mo>{</mo> <mo>}</mo></mrow> <mo>]</mo></mrow>",
            "System`OutputForm": '<mglyph width="350px" height="350px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMnB4IiBoZWlnaHQ9IjJweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9Ii0xLjAwMDAwMCAtMS4wMDAwMDAgMi4wMDAwMDAgMi4wMDAwMDAiPgogICAgICAgICAgICAgICAgPCEtLUdyYXBoaWNzRWxlbWVudHMtLT4KPC9zdmc+Cg=="/>',
        },
        "tex": {
            "System`StandardForm": '\n\\begin{asy}\nusepackage("amsmath");\nsize(5.8333cm, 5.8333cm);\n\n\nclip(box((-1,-1), (1,1)));\n\n\\end{asy}\n',
            "System`TraditionalForm": '\n\\begin{asy}\nusepackage("amsmath");\nsize(5.8333cm, 5.8333cm);\n\n\nclip(box((-1,-1), (1,1)));\n\n\\end{asy}\n',
            "System`InputForm": "\\text{Graphics}\\left[\\left\\{\\right\\}\\right]",
            "System`OutputForm": '\n\\begin{asy}\nusepackage("amsmath");\nsize(5.8333cm, 5.8333cm);\n\n\nclip(box((-1,-1), (1,1)));\n\n\\end{asy}\n',
        },
    },
    "Graphics[{Text[a^b,{0,0}]}]": {
        "msg": "Nontrivial Graphics - Fragile!",
        "text": {
            "System`StandardForm": "-Graphics-",
            "System`TraditionalForm": "-Graphics-",
            "System`InputForm": "Graphics[{Text[Power[a, b], {0, 0}]}]",
            "System`OutputForm": "-Graphics-",
        },
        "mathml": {
            "System`StandardForm": '<mglyph width="294px" height="350px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEuMHB4IiBoZWlnaHQ9IjI1LjBweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9IjEzNi41MDAwMDAgMTYyLjUwMDAwMCAyMS4wMDAwMDAgMjUuMDAwMDAwIj4KICAgICAgICAgICAgICAgIDwhLS1HcmFwaGljc0VsZW1lbnRzLS0+Cjx0ZXh0IHg9IjE0Ny4wIiB5PSIxNzUuMCIgb3g9IjAiIG95PSIwIiBmb250LXNpemU9IjEwcHgiIHN0eWxlPSJ0ZXh0LWFuY2hvcjplbmQ7IGRvbWluYW50LWJhc2VsaW5lOmhhbmdpbmc7IHN0cm9rZTogcmdiKDAuMDAwMDAwJSwgMC4wMDAwMDAlLCAwLjAwMDAwMCUpOyBzdHJva2Utb3BhY2l0eTogMTsgZmlsbDogcmdiKDAuMDAwMDAwJSwgMC4wMDAwMDAlLCAwLjAwMDAwMCUpOyBmaWxsLW9wYWNpdHk6IDE7IGNvbG9yOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IG9wYWNpdHk6IDEuMCI+YV5iPC90ZXh0Pgo8L3N2Zz4K"/>',
            "System`TraditionalForm": '<mglyph width="294px" height="350px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEuMHB4IiBoZWlnaHQ9IjI1LjBweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9IjEzNi41MDAwMDAgMTYyLjUwMDAwMCAyMS4wMDAwMDAgMjUuMDAwMDAwIj4KICAgICAgICAgICAgICAgIDwhLS1HcmFwaGljc0VsZW1lbnRzLS0+Cjx0ZXh0IHg9IjE0Ny4wIiB5PSIxNzUuMCIgb3g9IjAiIG95PSIwIiBmb250LXNpemU9IjEwcHgiIHN0eWxlPSJ0ZXh0LWFuY2hvcjplbmQ7IGRvbWluYW50LWJhc2VsaW5lOmhhbmdpbmc7IHN0cm9rZTogcmdiKDAuMDAwMDAwJSwgMC4wMDAwMDAlLCAwLjAwMDAwMCUpOyBzdHJva2Utb3BhY2l0eTogMTsgZmlsbDogcmdiKDAuMDAwMDAwJSwgMC4wMDAwMDAlLCAwLjAwMDAwMCUpOyBmaWxsLW9wYWNpdHk6IDE7IGNvbG9yOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IG9wYWNpdHk6IDEuMCI+YV5iPC90ZXh0Pgo8L3N2Zz4K"/>',
            "System`InputForm": "<mrow><mi>Graphics</mi> <mo>[</mo> <mrow><mo>{</mo> <mrow><mi>Text</mi> <mo>[</mo> <mrow><mrow><mi>Power</mi> <mo>[</mo> <mrow><mi>a</mi> <mtext>,&nbsp;</mtext> <mi>b</mi></mrow> <mo>]</mo></mrow> <mtext>,&nbsp;</mtext> <mrow><mo>{</mo> <mrow><mtext>0</mtext> <mtext>,&nbsp;</mtext> <mtext>0</mtext></mrow> <mo>}</mo></mrow></mrow> <mo>]</mo></mrow> <mo>}</mo></mrow> <mo>]</mo></mrow>",
            "System`OutputForm": '<mglyph width="294px" height="350px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEuMHB4IiBoZWlnaHQ9IjI1LjBweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9IjEzNi41MDAwMDAgMTYyLjUwMDAwMCAyMS4wMDAwMDAgMjUuMDAwMDAwIj4KICAgICAgICAgICAgICAgIDwhLS1HcmFwaGljc0VsZW1lbnRzLS0+Cjx0ZXh0IHg9IjE0Ny4wIiB5PSIxNzUuMCIgb3g9IjAiIG95PSIwIiBmb250LXNpemU9IjEwcHgiIHN0eWxlPSJ0ZXh0LWFuY2hvcjplbmQ7IGRvbWluYW50LWJhc2VsaW5lOmhhbmdpbmc7IHN0cm9rZTogcmdiKDAuMDAwMDAwJSwgMC4wMDAwMDAlLCAwLjAwMDAwMCUpOyBzdHJva2Utb3BhY2l0eTogMTsgZmlsbDogcmdiKDAuMDAwMDAwJSwgMC4wMDAwMDAlLCAwLjAwMDAwMCUpOyBmaWxsLW9wYWNpdHk6IDE7IGNvbG9yOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IG9wYWNpdHk6IDEuMCI+YV5iPC90ZXh0Pgo8L3N2Zz4K"/>',
        },
        "tex": {
            "System`StandardForm": '\n\\begin{asy}\nusepackage("amsmath");\nsize(4.9cm, 5.8333cm);\n\n// InsetBox\nlabel("$a^b$", (147.0,175.0), (0,0), rgb(0, 0, 0));\n\nclip(box((136.5,162.5), (157.5,187.5)));\n\n\\end{asy}\n',
            "System`TraditionalForm": '\n\\begin{asy}\nusepackage("amsmath");\nsize(4.9cm, 5.8333cm);\n\n// InsetBox\nlabel("$a^b$", (147.0,175.0), (0,0), rgb(0, 0, 0));\n\nclip(box((136.5,162.5), (157.5,187.5)));\n\n\\end{asy}\n',
            "System`InputForm": "\\text{Graphics}\\left[\\left\\{\\text{Text}\\left[\\text{Power}\\left[a, b\\right], \\left\\{0, 0\\right\\}\\right]\\right\\}\\right]",
            "System`OutputForm": '\n\\begin{asy}\nusepackage("amsmath");\nsize(4.9cm, 5.8333cm);\n\n// InsetBox\nlabel("$a^b$", (147.0,175.0), (0,0), rgb(0, 0, 0));\n\nclip(box((136.5,162.5), (157.5,187.5)));\n\n\\end{asy}\n',
        },
    },
    "TableForm[{Graphics[{Text[a^b,{0,0}]}], Graphics[{Text[a^b,{0,0}]}]}]": {
        "msg": "A table of graphics - Fragile!",
        "text": {
            "System`StandardForm": "-Graphics-\n\n-Graphics-\n",
            "System`TraditionalForm": "-Graphics-\n\n-Graphics-\n",
            "System`InputForm": "TableForm[{Graphics[{Text[Power[a, b], {0, 0}]}], Graphics[{Text[Power[a, b], {0, 0}]}]}]",
            "System`OutputForm": "-Graphics-\n\n-Graphics-\n",
        },
        "mathml": {
            "System`StandardForm": '<mtable columnalign="center">\n<mtr><mtd columnalign="center"><mglyph width="147px" height="175px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEuMHB4IiBoZWlnaHQ9IjI1LjBweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9IjYzLjAwMDAwMCA3NS4wMDAwMDAgMjEuMDAwMDAwIDI1LjAwMDAwMCI+CiAgICAgICAgICAgICAgICA8IS0tR3JhcGhpY3NFbGVtZW50cy0tPgo8dGV4dCB4PSI3My41IiB5PSI4Ny41IiBveD0iMCIgb3k9IjAiIGZvbnQtc2l6ZT0iMTBweCIgc3R5bGU9InRleHQtYW5jaG9yOmVuZDsgZG9taW5hbnQtYmFzZWxpbmU6aGFuZ2luZzsgc3Ryb2tlOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IHN0cm9rZS1vcGFjaXR5OiAxOyBmaWxsOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IGZpbGwtb3BhY2l0eTogMTsgY29sb3I6IHJnYigwLjAwMDAwMCUsIDAuMDAwMDAwJSwgMC4wMDAwMDAlKTsgb3BhY2l0eTogMS4wIj5hXmI8L3RleHQ+Cjwvc3ZnPgo="/></mtd></mtr>\n<mtr><mtd columnalign="center"><mglyph width="147px" height="175px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEuMHB4IiBoZWlnaHQ9IjI1LjBweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9IjYzLjAwMDAwMCA3NS4wMDAwMDAgMjEuMDAwMDAwIDI1LjAwMDAwMCI+CiAgICAgICAgICAgICAgICA8IS0tR3JhcGhpY3NFbGVtZW50cy0tPgo8dGV4dCB4PSI3My41IiB5PSI4Ny41IiBveD0iMCIgb3k9IjAiIGZvbnQtc2l6ZT0iMTBweCIgc3R5bGU9InRleHQtYW5jaG9yOmVuZDsgZG9taW5hbnQtYmFzZWxpbmU6aGFuZ2luZzsgc3Ryb2tlOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IHN0cm9rZS1vcGFjaXR5OiAxOyBmaWxsOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IGZpbGwtb3BhY2l0eTogMTsgY29sb3I6IHJnYigwLjAwMDAwMCUsIDAuMDAwMDAwJSwgMC4wMDAwMDAlKTsgb3BhY2l0eTogMS4wIj5hXmI8L3RleHQ+Cjwvc3ZnPgo="/></mtd></mtr>\n</mtable>',
            "System`TraditionalForm": '<mtable columnalign="center">\n<mtr><mtd columnalign="center"><mglyph width="147px" height="175px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEuMHB4IiBoZWlnaHQ9IjI1LjBweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9IjYzLjAwMDAwMCA3NS4wMDAwMDAgMjEuMDAwMDAwIDI1LjAwMDAwMCI+CiAgICAgICAgICAgICAgICA8IS0tR3JhcGhpY3NFbGVtZW50cy0tPgo8dGV4dCB4PSI3My41IiB5PSI4Ny41IiBveD0iMCIgb3k9IjAiIGZvbnQtc2l6ZT0iMTBweCIgc3R5bGU9InRleHQtYW5jaG9yOmVuZDsgZG9taW5hbnQtYmFzZWxpbmU6aGFuZ2luZzsgc3Ryb2tlOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IHN0cm9rZS1vcGFjaXR5OiAxOyBmaWxsOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IGZpbGwtb3BhY2l0eTogMTsgY29sb3I6IHJnYigwLjAwMDAwMCUsIDAuMDAwMDAwJSwgMC4wMDAwMDAlKTsgb3BhY2l0eTogMS4wIj5hXmI8L3RleHQ+Cjwvc3ZnPgo="/></mtd></mtr>\n<mtr><mtd columnalign="center"><mglyph width="147px" height="175px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEuMHB4IiBoZWlnaHQ9IjI1LjBweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9IjYzLjAwMDAwMCA3NS4wMDAwMDAgMjEuMDAwMDAwIDI1LjAwMDAwMCI+CiAgICAgICAgICAgICAgICA8IS0tR3JhcGhpY3NFbGVtZW50cy0tPgo8dGV4dCB4PSI3My41IiB5PSI4Ny41IiBveD0iMCIgb3k9IjAiIGZvbnQtc2l6ZT0iMTBweCIgc3R5bGU9InRleHQtYW5jaG9yOmVuZDsgZG9taW5hbnQtYmFzZWxpbmU6aGFuZ2luZzsgc3Ryb2tlOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IHN0cm9rZS1vcGFjaXR5OiAxOyBmaWxsOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IGZpbGwtb3BhY2l0eTogMTsgY29sb3I6IHJnYigwLjAwMDAwMCUsIDAuMDAwMDAwJSwgMC4wMDAwMDAlKTsgb3BhY2l0eTogMS4wIj5hXmI8L3RleHQ+Cjwvc3ZnPgo="/></mtd></mtr>\n</mtable>',
            "System`InputForm": "<mrow><mi>TableForm</mi> <mo>[</mo> <mrow><mo>{</mo> <mrow><mrow><mi>Graphics</mi> <mo>[</mo> <mrow><mo>{</mo> <mrow><mi>Text</mi> <mo>[</mo> <mrow><mrow><mi>Power</mi> <mo>[</mo> <mrow><mi>a</mi> <mtext>,&nbsp;</mtext> <mi>b</mi></mrow> <mo>]</mo></mrow> <mtext>,&nbsp;</mtext> <mrow><mo>{</mo> <mrow><mtext>0</mtext> <mtext>,&nbsp;</mtext> <mtext>0</mtext></mrow> <mo>}</mo></mrow></mrow> <mo>]</mo></mrow> <mo>}</mo></mrow> <mo>]</mo></mrow> <mtext>,&nbsp;</mtext> <mrow><mi>Graphics</mi> <mo>[</mo> <mrow><mo>{</mo> <mrow><mi>Text</mi> <mo>[</mo> <mrow><mrow><mi>Power</mi> <mo>[</mo> <mrow><mi>a</mi> <mtext>,&nbsp;</mtext> <mi>b</mi></mrow> <mo>]</mo></mrow> <mtext>,&nbsp;</mtext> <mrow><mo>{</mo> <mrow><mtext>0</mtext> <mtext>,&nbsp;</mtext> <mtext>0</mtext></mrow> <mo>}</mo></mrow></mrow> <mo>]</mo></mrow> <mo>}</mo></mrow> <mo>]</mo></mrow></mrow> <mo>}</mo></mrow> <mo>]</mo></mrow>",
            "System`OutputForm": '<mtable columnalign="center">\n<mtr><mtd columnalign="center"><mglyph width="147px" height="175px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEuMHB4IiBoZWlnaHQ9IjI1LjBweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9IjYzLjAwMDAwMCA3NS4wMDAwMDAgMjEuMDAwMDAwIDI1LjAwMDAwMCI+CiAgICAgICAgICAgICAgICA8IS0tR3JhcGhpY3NFbGVtZW50cy0tPgo8dGV4dCB4PSI3My41IiB5PSI4Ny41IiBveD0iMCIgb3k9IjAiIGZvbnQtc2l6ZT0iMTBweCIgc3R5bGU9InRleHQtYW5jaG9yOmVuZDsgZG9taW5hbnQtYmFzZWxpbmU6aGFuZ2luZzsgc3Ryb2tlOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IHN0cm9rZS1vcGFjaXR5OiAxOyBmaWxsOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IGZpbGwtb3BhY2l0eTogMTsgY29sb3I6IHJnYigwLjAwMDAwMCUsIDAuMDAwMDAwJSwgMC4wMDAwMDAlKTsgb3BhY2l0eTogMS4wIj5hXmI8L3RleHQ+Cjwvc3ZnPgo="/></mtd></mtr>\n<mtr><mtd columnalign="center"><mglyph width="147px" height="175px" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEuMHB4IiBoZWlnaHQ9IjI1LjBweCIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgICAgICAgICAgICAgIHZlcnNpb249IjEuMSIKICAgICAgICAgICAgICAgIHZpZXdCb3g9IjYzLjAwMDAwMCA3NS4wMDAwMDAgMjEuMDAwMDAwIDI1LjAwMDAwMCI+CiAgICAgICAgICAgICAgICA8IS0tR3JhcGhpY3NFbGVtZW50cy0tPgo8dGV4dCB4PSI3My41IiB5PSI4Ny41IiBveD0iMCIgb3k9IjAiIGZvbnQtc2l6ZT0iMTBweCIgc3R5bGU9InRleHQtYW5jaG9yOmVuZDsgZG9taW5hbnQtYmFzZWxpbmU6aGFuZ2luZzsgc3Ryb2tlOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IHN0cm9rZS1vcGFjaXR5OiAxOyBmaWxsOiByZ2IoMC4wMDAwMDAlLCAwLjAwMDAwMCUsIDAuMDAwMDAwJSk7IGZpbGwtb3BhY2l0eTogMTsgY29sb3I6IHJnYigwLjAwMDAwMCUsIDAuMDAwMDAwJSwgMC4wMDAwMDAlKTsgb3BhY2l0eTogMS4wIj5hXmI8L3RleHQ+Cjwvc3ZnPgo="/></mtd></mtr>\n</mtable>',
        },
        "tex": {
            "System`StandardForm": '\\begin{array}{c} \n\\begin{asy}\nusepackage("amsmath");\nsize(2.45cm, 2.9167cm);\n\n// InsetBox\nlabel("$a^b$", (73.5,87.5), (0,0), rgb(0, 0, 0));\n\nclip(box((63,75), (84,100)));\n\n\\end{asy}\n\\\\ \n\\begin{asy}\nusepackage("amsmath");\nsize(2.45cm, 2.9167cm);\n\n// InsetBox\nlabel("$a^b$", (73.5,87.5), (0,0), rgb(0, 0, 0));\n\nclip(box((63,75), (84,100)));\n\n\\end{asy}\n\\end{array}',
            "System`TraditionalForm": '\\begin{array}{c} \n\\begin{asy}\nusepackage("amsmath");\nsize(2.45cm, 2.9167cm);\n\n// InsetBox\nlabel("$a^b$", (73.5,87.5), (0,0), rgb(0, 0, 0));\n\nclip(box((63,75), (84,100)));\n\n\\end{asy}\n\\\\ \n\\begin{asy}\nusepackage("amsmath");\nsize(2.45cm, 2.9167cm);\n\n// InsetBox\nlabel("$a^b$", (73.5,87.5), (0,0), rgb(0, 0, 0));\n\nclip(box((63,75), (84,100)));\n\n\\end{asy}\n\\end{array}',
            "System`InputForm": "\\text{TableForm}\\left[\\left\\{\\text{Graphics}\\left[\\left\\{\\text{Text}\\left[\\text{Power}\\left[a, b\\right], \\left\\{0, 0\\right\\}\\right]\\right\\}\\right], \\text{Graphics}\\left[\\left\\{\\text{Text}\\left[\\text{Power}\\left[a, b\\right], \\left\\{0, 0\\right\\}\\right]\\right\\}\\right]\\right\\}\\right]",
            "System`OutputForm": '\\begin{array}{c} \n\\begin{asy}\nusepackage("amsmath");\nsize(2.45cm, 2.9167cm);\n\n// InsetBox\nlabel("$a^b$", (73.5,87.5), (0,0), rgb(0, 0, 0));\n\nclip(box((63,75), (84,100)));\n\n\\end{asy}\n\\\\ \n\\begin{asy}\nusepackage("amsmath");\nsize(2.45cm, 2.9167cm);\n\n// InsetBox\nlabel("$a^b$", (73.5,87.5), (0,0), rgb(0, 0, 0));\n\nclip(box((63,75), (84,100)));\n\n\\end{asy}\n\\end{array}',
        },
    },
}


def load_tests(key):
    """
    This function takes the full set of tests, pick the ones corresponding to one
    of the final formats ("text", "tex", "mathml") and produce two list:
    the first with the mandatory tests, and the other with "fragile" tests
    """
    global all_tests
    global MATHML_STRICT
    mandatory_tests = []
    fragile_tests = []
    for expr in all_test:
        base_msg = all_test[expr]["msg"]
        expected_fmt = all_test[expr][key]
        fragil_set = len(base_msg) > 8 and base_msg[-8:] == "Fragile!"
        for form in expected_fmt:
            tst = expected_fmt[form]
            fragile = fragil_set
            must_be = False
            if not isinstance(tst, str):
                tst, extra_msg = tst
                if len(extra_msg) > 7 and extra_msg[:7] == "must be":
                    must_be = True
                elif len(extra_msg) > 8 and extra_msg[:7] == "Fragile!":
                    fragile = True
                msg = base_msg + " - " + extra_msg
            else:
                msg = base_msg

            # discard Fragile for "text", "tex" or if
            # MATHML_STRICT is True
            if key != "mathml" or MATHML_STRICT:
                fragile = False
            full_test = (expr, tst, form, msg)
            if fragile or must_be:
                fragile_tests.append(full_test)
            else:
                mandatory_tests.append(full_test)

    return mandatory_tests, fragile_tests


mandatory_tests, fragile_tests = load_tests("text")

if fragile_tests:

    @pytest.mark.parametrize(
        ("str_expr", "str_expected", "form", "msg"),
        fragile_tests,
    )
    @pytest.mark.xfail
    def test_makeboxes_text_fragile(str_expr, str_expected, form, msg):
        result = session.evaluate(str_expr)
        format_result = result.format(session.evaluation, form)
        if msg:
            assert (
                format_result.boxes_to_text(evaluation=session.evaluation)
                == str_expected
            ), msg
        else:
            strresult = format_result.boxes_to_text(evaluation=session.evaluation)
            assert strresult == str_expected


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "form", "msg"),
    mandatory_tests,
)
def test_makeboxes_text(str_expr, str_expected, form, msg):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, form)
    if msg:
        assert (
            format_result.boxes_to_text(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        strresult = format_result.boxes_to_text(evaluation=session.evaluation)
        assert strresult == str_expected


mandatory_tests, fragile_tests = load_tests("tex")

if fragile_tests:

    @pytest.mark.parametrize(
        ("str_expr", "str_expected", "form", "msg"),
        fragile_tests,
    )
    @pytest.mark.xfail
    def test_makeboxes_tex_fragile(str_expr, str_expected, form, msg):
        result = session.evaluate(str_expr)
        format_result = result.format(session.evaluation, form)
        if msg:
            assert (
                format_result.boxes_to_tex(evaluation=session.evaluation)
                == str_expected
            ), msg
        else:
            strresult = format_result.boxes_to_text(evaluation=session.evaluation)
            assert strresult == str_expected


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "form", "msg"),
    mandatory_tests,
)
def test_makeboxes_tex(str_expr, str_expected, form, msg):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, form)
    if msg:
        assert (
            format_result.boxes_to_tex(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        strresult = format_result.boxes_to_text(evaluation=session.evaluation)
        assert strresult == str_expected


mandatory_tests, fragile_tests = load_tests("mathml")

if fragile_tests:

    @pytest.mark.parametrize(
        ("str_expr", "str_expected", "form", "msg"),
        fragile_tests,
    )
    @pytest.mark.xfail
    def test_makeboxes_mathml_fragile(str_expr, str_expected, form, msg):
        result = session.evaluate(str_expr)
        format_result = result.format(session.evaluation, form)
        if msg:
            assert (
                format_result.boxes_to_tex(evaluation=session.evaluation)
                == str_expected
            ), msg
        else:
            strresult = format_result.boxes_to_text(evaluation=session.evaluation)
            assert strresult == str_expected


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "form", "msg"),
    mandatory_tests,
)
def test_makeboxes_mathml(str_expr, str_expected, form, msg):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, form)
    if msg:
        assert (
            format_result.boxes_to_mathml(evaluation=session.evaluation) == str_expected
        ), msg
    else:
        strresult = format_result.boxes_to_mathml(evaluation=session.evaluation)
        assert strresult == str_expected
