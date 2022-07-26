# -*- coding: utf-8 -*-
import pytest
from test.helper import check_evaluation, session


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg"),
    [
        # Equal (==)
        (
            "ClearAll[g,a,b];",
            "Null",
            None,
        ),
        ('"a"==A', "a == A", "comparable expressions"),
        ('"a"=="a"', "True", "comparable expressions"),
        ('"a"=="b"', "False", "comparable expressions"),
        ('"a"==3', "False", "comparable expressions"),
        ("g[2]==g[3]", "g[2] == g[3]", "not comparable expressions, Issue #200"),
        ("g[a]==g[3]", "g[a] == g[3]", "not comparable expressions"),
        ("g[2]==g[a]", "g[2] == g[a]", "not comparable expressions"),
        ("g[a]==g[b]", "g[a] == g[b]", "not comparable expressions"),
        ("g[a]==g[a]", "True", "identical expressions"),
        ("g[1]==g[1]", "True", "identical expressions"),
        ("a == a == a", "True", "simple chained compare"),
        (
            "E == N[E]",
            "True",
            "compare exact numeric expression with its approximate number",
        ),
        (
            "0.1 ^ 10000 == 0.1 ^ 10000 + 0.1 ^ 10013",
            "True",
            "difference out of precision ignored",
        ),
        (
            "0.1111111111111111 == 0.1111111111111126",
            "True",
            "difference out of precision ignored",
        ),
        (
            "0.1111111111111111 == 0.1111111111111127",
            "False",
            "difference in lower precision detected",
        ),
        ("Equal[Equal[0, 0], True] == True", "True", "Issue260"),
        ("Equal[0, 0] == True", "True", "Issue260"),
        #
        # Unequal (!=)
        ('"a"!=A', "a != A", "comparable expressions"),
        ('"a"!="a"', "False", "comparable expressions"),
        ('"a"!="b"', "True", "comparable expressions"),
        ('"a"!=3', "True", "comparable expressions"),
        ("g[2]!=g[3]", "g[2] != g[3]", "not comparable expressions, Issue #200"),
        ("g[a]!=g[3]", "g[a] != g[3]", "not comparable expressions"),
        ("g[2]!=g[a]", "g[2] != g[a]", "not comparable expressions"),
        ("g[a]!=g[b]", "g[a] != g[b]", "not comparable expressions"),
        ("g[a]!=g[a]", "False", "identical expressions"),
        ("g[1]!=g[1]", "False", "identical expressions"),
        #
        # LessEqual (<=)
        ('"a"<="b"', "a <= b", "not comparable expressions"),
        ('"a"<=3', "a <= 3", "not comparable expressions"),
        ("g[2]<=g[3]", "g[2] <= g[3]", "not comparable expressions, Issue #200"),
        ("g[a]<=g[3]", "g[a] <= g[3]", "not comparable expressions"),
        ("g[2]<=g[a]", "g[2] <= g[a]", "not comparable expressions"),
        ("g[a]<=g[b]", "g[a] <= g[b]", "not comparable expressions"),
        ("g[a]<=g[a]", "g[a] <= g[a]", "not comparable expressions (like in WMA)"),
        ("g[1]<=g[1]", "g[1] <= g[1]", "not comparable expressions (like in WMA)"),
        #
        # Less (<)
        ("{1, 2, 3} < {1, 2, 3}", "{1, 2, 3} < {1, 2, 3}", "Less on a list"),
        ("g[2]<g[3]", "g[2] < g[3]", "not comparable expressions, Issue #200"),
        ("g[a]<g[3]", "g[a] < g[3]", "not comparable expressions"),
        ("g[2]<g[a]", "g[2] < g[a]", "not comparable expressions"),
        ("g[a]<g[b]", "g[a] < g[b]", "not comparable expressions"),
        ("g[a]<g[a]", "g[a] < g[a]", "not comparable expressions (like in WMA)"),
        ("g[1]<g[1]", "g[1] < g[1]", "not comparable expressions (like in WMA)"),
        #
        # chained compare
        ("a != a != b", "False", "Strange MMA behavior"),
        ("a != b != a", "a != b != a", "incomparable values should be unchanged"),
        (
            "g[1]==g[1]==g[2]",
            "g[1] == g[1] == g[2]",
            "WMA does not reduce these expressions.",
        ),
        (
            "g[1]==g[2]==g[1]",
            "g[1] == g[2] == g[1]",
            "WMA does not reduce these expressions.",
        ),
        ("g[1]==g[1]==g[1]", "True", "Equal works over several elements"),
        (
            "g[1]==g[2]!=g[1]",
            "g[1] == g[2] && g[2] != g[1]",
            "Equal mixed with unequality splits",
        ),
        ("g[1]!=g[1]==g[2]", "False", "This evaluates first the inequality"),
    ],
)
def test_compare_many_members(str_expr: str, str_expected: str, fail_msg: str):
    #    if str_expr is None:
    #        reset_session()
    result = session.evaluate(f"ToString[{str_expr}]").value
    print("result:", result)
    assert result == str_expected  # , fail_msg


# SameQ test
@pytest.mark.parametrize(
    ("str_lhs", "str_rhs", "str_expected"),
    [  # Symbol and symbol
        ("A", "B", "False"),
        ("A", "A", "True"),
        # Symbol and Integer
        ("A", "1", "False"),
        ("1", "A", "False"),
        # Integer and MachineReal
        ("1", "1.", "False"),
        ("1.", "1", "False"),
        # Rational and MachineReal
        ("2./9.", "2/9", "False"),
        ("2/9", "2./9.", "False"),
        # Integer and PrecisionReal
        ("1", "1.`3", "False"),
        ("1.`3", "1", "False"),
        # MachineReal and PrecisionReal
        ("1.", "1.`3", "True"),
        ("1.`3", "1.", "True"),
        ("2./9.", ".2222222222222222`16", "True"),
        (".2222222222222222`16", "2./9.", "True"),
        # PrecisionReal and PrecisionReal
        (".222222`5", "N[2/9,4]", "True"),
        # SameQ compare Real numbers upto
        # the smallest accuracy.
        ("N[2/9]", ".2222222222222222", "True"),
        ("N[2/9]", ".2222222222222222`16", "True"),
        # This test gives False because round errors
        # in the last digit.
        ("N[2/9]", ".222`3", "False"),
        # Adding an extra decimal gives True.
        ("N[2/9]", ".2222`3", "True"),
        ("N[2/9, 4]", ".222", "False"),
        ("N[2/9, 4]", ".2222", "False"),
        ("N[2/9, 4]", ".22222", "True"),
        ("N[2/9, 4]", ".222`3", "False"),
        ("N[2/9, 4]", ".2222`3", "True"),
        ("N[2/9, 4]", ".22222`3", "True"),
        ("N[2/9, 4]", ".222`5", "False"),
        ("N[2/9, 4]", ".2222`5", "False"),
        ("N[2/9, 4]", ".22222`5", "True"),
        ("N[2/9, 4]", ".222222`5", "True"),
    ],
)
def test_sameq(str_lhs, str_rhs, str_expected):
    expr = str_lhs + " === " + str_rhs
    print(expr)
    print(session.evaluate(expr))
    check_evaluation(expr, str_expected, to_string_expr=True, to_string_expected=True)


# UnsameQ test
@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [  # UnsameQ returns True with 0 or 1 arguments
        ("UnsameQ[]", "True"),
        ("UnsameQ[expr]", "True"),
        # With 2 or more argments, UnsameQ returns True if all expressions are
        # structurally distinct and False otherwise
        ("x =!= x", "False"),
        ("x =!= y", "True"),
        ("1 =!= 2 =!= 3 =!= 4", "True"),
        ("1 =!= 2 =!= 1 =!= 4", "False"),
        ("UnsameQ[10, 5, 2, 1, 0]", "True"),
        ("UnsameQ[10, 5, 2, 1, 0, 0]", "False"),
    ],
)
def test_unsameq(str_expr, str_expected):
    print(str_expr)
    print(session.evaluate(str_expr))
    check_evaluation(
        str_expr, str_expected, to_string_expr=True, to_string_expected=True
    )


#  The following tests where generated automatically calling wolframscript -c
#  followed by a combination of expressions.
#  This is the code I used to generate them
#
#  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
# import subprocess
# from time import sleep
# exprss = ['2 + 3*a', 'Infinity', '-Infinity', 'Sqrt[I] Infinity', 'a', '"a"', '"1 / 4"', "I", "0", '1 / 4','.25',"Sqrt[2]", "BesselJ[0, 2]", "3+2 I", "2.+ Pi I", "3+I Pi", 'TestFunction["Tengo una vaca lechera"]', "Compile[{x}, Sqrt[x]]", "Graphics[{Disk[{0,0},1]}]"]
# pairs = sum([[(exprss[i], exprss[j]) for j in range(i+1)] for i in range(len(exprss))],[])
# tests = []
#
# for pair in pairs:
#     test = " " + pair[0] + ' == ' + pair[1]
#     result = subprocess.run(['wolframscript', '-c', test], stdout=subprocess.PIPE)
#     sleep(1)
#     res = result.stdout.decode('utf8').strip()
#     if len(res)>0 and res[-1] == '\n':
#         res = res[:-2]
#     newtest = (pair[0], pair[1], res)
#     print(newtest)
#     print("  ", newtest, ",")
#     tests.append(newtest)

tests1 = [
    ("Sqrt[I] Infinity", "2 + 3 a", '"(-1) ^ (1 / 4) Infinity == 2 + 3 a"'),
    ("a", "Sqrt[I] Infinity", '"a == (-1) ^ (1 / 4) Infinity"'),
    ('"a"', "2 + 3 a", '"a == 2 + 3 a"'),
    ('"a"', "Infinity", '"a == Infinity"'),
    ('"a"', "-Infinity", '"a == -Infinity"'),
    ('"a"', "Sqrt[I] Infinity", '"a == (-1) ^ (1 / 4) Infinity"'),
    ('"a"', "a", '"a == a"'),
    ("Graphics[{Disk[{0,0},1]}]", "2 + 3 a", '"-Graphics- == 2 + 3 a"'),
    ("Graphics[{Disk[{0,0},1]}]", "Infinity", '"-Graphics- == Infinity"'),
    ("Graphics[{Disk[{0,0},1]}]", "-Infinity", '"-Graphics- == -Infinity"'),
    (
        "Graphics[{Disk[{0,0},1]}]",
        "Sqrt[I] Infinity",
        '"-Graphics- == (-1) ^ (1 / 4) Infinity"',
    ),
    ("Graphics[{Disk[{0,0},1]}]", "a", '"-Graphics- == a"'),
    ("Graphics[{Disk[{0,0},1]}]", '"a"', '"-Graphics- == a"'),
    ("Graphics[{Disk[{0,0},1]}]", '"1 / 4"', '"-Graphics- == 1 / 4"'),
    ("Graphics[{Disk[{0,0},1]}]", "I", '"-Graphics- == I"'),
    ("Graphics[{Disk[{0,0},1]}]", "0", '"-Graphics- == 0"'),
    ("Graphics[{Disk[{0,0},1]}]", "1 / 4", '"-Graphics- == 1 / 4"'),
    ("Graphics[{Disk[{0,0},1]}]", ".25", '"-Graphics- == 0.25"'),
    ("Graphics[{Disk[{0,0},1]}]", "Sqrt[2]", '"-Graphics- == Sqrt[2]"'),
    ("Graphics[{Disk[{0,0},1]}]", "BesselJ[0, 2]", '"-Graphics- == BesselJ[0, 2]"'),
    ("Graphics[{Disk[{0,0},1]}]", "3+2 I", '"-Graphics- == 3 + 2 I"'),
    ("Graphics[{Disk[{0,0},1]}]", "2.+ Pi I", '"-Graphics- == 2. + 3.14159 I"'),
    ("Graphics[{Disk[{0,0},1]}]", "3+I Pi", '"-Graphics- == 3 + I Pi"'),
    (
        "Graphics[{Disk[{0,0},1]}]",
        'TestFunction["Tengo una vaca lechera"]',
        '"-Graphics- == TestFunction[Tengo una vaca lechera]"',
    ),
    (
        "Graphics[{Disk[{0,0},1]}]",
        "Compile[{x}, Sqrt[x]]",
        '"-Graphics- == CompiledFunction[{x}, Sqrt[x], -PythonizedCode-]"',
    ),
    ('"1 / 4"', "2 + 3 a", '"1 / 4 == 2 + 3 a"'),
    ('"1 / 4"', "Infinity", '"1 / 4 == Infinity"'),
    ('"1 / 4"', "-Infinity", '"1 / 4 == -Infinity"'),
    ('"1 / 4"', "Sqrt[I] Infinity", '"1 / 4 == (-1) ^ (1 / 4) Infinity"'),
    ('"1 / 4"', "a", '"1 / 4 == a"'),
    ("Sqrt[2]", '"1 / 4"', '"Sqrt[2] == 1 / 4"'),
    ("BesselJ[0, 2]", '"1 / 4"', '"BesselJ[0, 2] == 1 / 4"'),
    ("3+I Pi", '"1 / 4"', '"3 + I Pi == 1 / 4"'),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "2 + 3 a",
        '"TestFunction[Tengo una vaca lechera] == 2 + 3 a"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "Infinity",
        '"TestFunction[Tengo una vaca lechera] == Infinity"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "-Infinity",
        '"TestFunction[Tengo una vaca lechera] == -Infinity"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "Sqrt[I] Infinity",
        '"TestFunction[Tengo una vaca lechera] == (-1) ^ (1 / 4) Infinity"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "a",
        '"TestFunction[Tengo una vaca lechera] == a"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        '"a"',
        '"TestFunction[Tengo una vaca lechera] == a"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        '"1 / 4"',
        '"TestFunction[Tengo una vaca lechera] == 1 / 4"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "I",
        '"TestFunction[Tengo una vaca lechera] == I"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "0",
        '"TestFunction[Tengo una vaca lechera] == 0"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "1 / 4",
        '"TestFunction[Tengo una vaca lechera] == 1 / 4"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        ".25",
        '"TestFunction[Tengo una vaca lechera] == 0.25"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "Sqrt[2]",
        '"TestFunction[Tengo una vaca lechera] == Sqrt[2]"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "BesselJ[0, 2]",
        '"TestFunction[Tengo una vaca lechera] == BesselJ[0, 2]"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "3+2 I",
        '"TestFunction[Tengo una vaca lechera] == 3 + 2 I"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "2.+ Pi I",
        '"TestFunction[Tengo una vaca lechera] == 2. + 3.14159 I"',
    ),
    (
        'TestFunction["Tengo una vaca lechera"]',
        "3+I Pi",
        '"TestFunction[Tengo una vaca lechera] == 3 + I Pi"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "2 + 3 a",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == 2 + 3 a"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "Infinity",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == Infinity"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "-Infinity",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == -Infinity"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "Sqrt[I] Infinity",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == (-1) ^ (1 / 4) Infinity"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "a",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == a"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        '"a"',
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == a"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        '"1 / 4"',
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == 1 / 4"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "I",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == I"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "0",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == 0"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "1 / 4",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == 1 / 4"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        ".25",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == 0.25"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "Sqrt[2]",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == Sqrt[2]"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "BesselJ[0, 2]",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == BesselJ[0, 2]"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "3+2 I",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == 3 + 2 I"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "2.+ Pi I",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == 2. + 3.14159 I"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        "3+I Pi",
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == 3 + I Pi"',
    ),
    (
        "Compile[{x}, Sqrt[x]]",
        'TestFunction["Tengo una vaca lechera"]',
        '"CompiledFunction[{x}, Sqrt[x], -PythonizedCode-] == TestFunction[Tengo una vaca lechera]"',
    ),
]

tests2 = [
    (r'"\[Mu]"', r'"μ"', "True"),
    ("2 + 3*a", "2 + 3*a", "True"),
    ("Infinity", "2 + 3*a", "Infinity == 2 + 3 a"),
    ("Infinity", "Infinity", "True"),
    ("-Infinity", "2 + 3 a", "-Infinity == 2 + 3 a"),
    ("-Infinity", "Infinity", "False"),
    ("-Infinity", "-Infinity", "True"),
    ("Sqrt[I] Infinity", "Infinity", "False"),
    ("Sqrt[I] Infinity", "-Infinity", "False"),
    ("Sqrt[I] Infinity", "Sqrt[I] Infinity", "True"),
    ("a", "2 + 3 a", "a == 2 + 3 a"),
    ("a", "Infinity", "a == Infinity"),
    ("a", "-Infinity", "a == -Infinity"),
    ("a", "a", "True"),
    ('"a"', '"a"', "True"),
    ('"1 / 4"', '"a"', "False"),
    ('"1 / 4"', '"1 / 4"', "True"),
    ("I", "2 + 3 a", "I == 2 + 3 a"),
    ("I", "Infinity", "False"),
    ("I", "-Infinity", "False"),
    ("I", "Sqrt[I] Infinity", "False"),
    ("I", "a", "I == a"),
    ("I", '"a"', "False"),
    ("I", '"1 / 4"', "False"),
    ("I", "I", "True"),
    ("0", "2 + 3 a", "0 == 2 + 3 a"),
    ("0", "Infinity", "False"),
    ("0", "-Infinity", "False"),
    ("0", "Sqrt[I] Infinity", "False"),
    ("0", "a", "0 == a"),
    ("0", '"a"', "False"),
    ("0", '"1 / 4"', "False"),
    ("0", "I", "False"),
    ("0", "0", "True"),
    ("1 / 4", "2 + 3 a", "1/4 == 2 + 3 a"),
    ("1 / 4", "Infinity", "False"),
    ("1 / 4", "-Infinity", "False"),
    ("1 / 4", "Sqrt[I] Infinity", "False"),
    ("1 / 4", "a", "1/4 == a"),
    ("1 / 4", '"a"', "False"),
    ("1 / 4", '"1 / 4"', "False"),
    ("1 / 4", "I", "False"),
    ("1 / 4", "0", "False"),
    ("1 / 4", "1 / 4", "True"),
    (".25", "2 + 3 a", "0.25 == 2 + 3 a"),
    (".25", "Infinity", "False"),
    (".25", "-Infinity", "False"),
    (".25", "Sqrt[I] Infinity", "False"),
    (".25", "a", "0.25 == a"),
    (".25", '"a"', "False"),
    (".25", '"1 / 4"', "False"),
    (".25", "I", "False"),
    (".25", "0", "False"),
    (".25", "1 / 4", "True"),
    (".25", ".25", "True"),
    ("Sqrt[2]", "2 + 3 a", "Sqrt[2] == 2 + 3 a"),
    ("Sqrt[2]", "Infinity", "False"),
    ("Sqrt[2]", "-Infinity", "False"),
    ("Sqrt[2]", "Sqrt[I] Infinity", "False"),
    ("Sqrt[2]", "a", "Sqrt[2] == a"),
    ("Sqrt[2]", '"a"', 'Sqrt[2] == "a"'),
    ("Sqrt[2]", "I", "False"),
    ("Sqrt[2]", "0", "False"),
    ("Sqrt[2]", "1 / 4", "False"),
    ("Sqrt[2]", ".25", "False"),
    ("Sqrt[2]", "Sqrt[2]", "True"),
    ("BesselJ[0, 2]", "2 + 3 a", "BesselJ[0, 2] == 2 + 3 a"),
    ("BesselJ[0, 2]", "Infinity", "False"),
    ("BesselJ[0, 2]", "-Infinity", "False"),
    ("BesselJ[0, 2]", "Sqrt[I] Infinity", "False"),
    ("BesselJ[0, 2]", "a", "BesselJ[0, 2] == a"),
    ("BesselJ[0, 2]", '"a"', 'BesselJ[0, 2] == "a"'),
    ("BesselJ[0, 2]", "I", "False"),
    ("BesselJ[0, 2]", "0", "False"),
    ("BesselJ[0, 2]", "1 / 4", "False"),
    ("BesselJ[0, 2]", ".25", "False"),
    ("BesselJ[0, 2]", "Sqrt[2]", "False"),
    ("BesselJ[0, 2]", "BesselJ[0, 2]", "True"),
    ("3+2 I", "2 + 3 a", "3 + 2 I== 2 + 3 a"),
    ("3+2 I", "Infinity", "False"),
    ("3+2 I", "-Infinity", "False"),
    ("3+2 I", "Sqrt[I] Infinity", "False"),
    ("3+2 I", "a", "3 + 2 I== a"),
    ("3+2 I", '"a"', "False"),
    ("3+2 I", '"1 / 4"', "False"),
    ("3+2 I", "I", "False"),
    ("3+2 I", "0", "False"),
    ("3+2 I", "1 / 4", "False"),
    ("3+2 I", ".25", "False"),
    ("3+2 I", "Sqrt[2]", "False"),
    ("3+2 I", "BesselJ[0, 2]", "False"),
    ("3+2 I", "3+2 I", "True"),
    ("2.+ Pi I", "Infinity", "False"),
    ("2.+ Pi I", "-Infinity", "False"),
    ("2.+ Pi I", "Sqrt[I] Infinity", "False"),
    ("2.+ Pi I", '"a"', "False"),
    ("2.+ Pi I", '"1 / 4"', "False"),
    ("2.+ Pi I", "I", "False"),
    ("2.+ Pi I", "0", "False"),
    ("2.+ Pi I", "1 / 4", "False"),
    ("2.+ Pi I", ".25", "False"),
    ("2.+ Pi I", "Sqrt[2]", "False"),
    ("2.+ Pi I", "BesselJ[0, 2]", "False"),
    ("2.+ Pi I", "3+2 I", "False"),
    ("2.+ Pi I", "2.+ Pi I", "True"),
    ("3+I Pi", "2 + 3 a", "3 + I Pi == 2 + 3 a"),
    ("3+I Pi", "Infinity", "False"),
    ("3+I Pi", "-Infinity", "False"),
    ("3+I Pi", "Sqrt[I] Infinity", "False"),
    ("3+I Pi", "a", "3 + I Pi == a"),
    ("3+I Pi", "I", "False"),
    ("3+I Pi", "0", "False"),
    ("3+I Pi", "1 / 4", "False"),
    ("3+I Pi", ".25", "False"),
    ("3+I Pi", "Sqrt[2]", "False"),
    ("3+I Pi", "BesselJ[0, 2]", "False"),
    ("3+I Pi", "3+2 I", "False"),
    ("3+I Pi", "2.+ Pi I", "False"),
    ("3+I Pi", "3+I Pi", "True"),
    (
        'TestFunction["Tengo una vaca lechera"]',
        'TestFunction["Tengo una vaca lechera"]',
        "True",
    ),
    ("Compile[{x}, Sqrt[x]]", "Compile[{x}, Sqrt[x]]", "True"),
    ("Graphics[{Disk[{0,0},1]}]", "Graphics[{Disk[{0,0},1]}]", "True"),
    ("3+I Pi", '"a"', '3 + I Pi == "a"'),
    ("2.+ Pi I", "a", "2. + 3.14159265358979 I == a"),
    ("2.+ Pi I", "2 + 3 a", "2. + 3.14159265358979 I == 2 + 3 a"),
]


@pytest.mark.parametrize(
    ("str_lhs", "str_rhs", "str_expected"),
    tests1,
)
def test_cmp1_no_pass(str_lhs, str_rhs, str_expected):
    if str_lhs == str_rhs:
        expr = str_lhs + " == " + str_rhs
        check_evaluation(
            expr, str_expected, to_string_expr=True, to_string_expected=True
        )
    else:
        expr = str_lhs + " == " + str_rhs
        check_evaluation(
            expr, str_expected, to_string_expr=True, to_string_expected=True
        )
        # Checking commutativity
        str_expected_members = str_expected[1:-1].split(" == ")
        if len(str_expected_members) == 2:
            str_expected = (
                '"' + str_expected_members[1] + " == " + str_expected_members[0] + '"'
            )
        expr = str_rhs + " == " + str_lhs
        check_evaluation(
            expr, str_expected, to_string_expr=True, to_string_expected=True
        )


@pytest.mark.parametrize(
    ("str_lhs", "str_rhs", "str_expected"),
    tests2,
)
def test_cmp2_no_pass(str_lhs, str_rhs, str_expected):
    if str_lhs == str_rhs:
        expr = str_lhs + " == " + str_rhs
        check_evaluation(
            expr, str_expected, to_string_expr=False, to_string_expected=False
        )
    else:
        expr = str_lhs + " == " + str_rhs
        check_evaluation(
            expr, str_expected, to_string_expr=False, to_string_expected=False
        )
        # Checking commutativity
        str_expected_members = str_expected.split("==")
        if len(str_expected_members) == 2:
            str_expected = str_expected_members[1] + " == " + str_expected_members[0]
        expr = str_rhs + " == " + str_lhs
        check_evaluation(
            expr, str_expected, to_string_expr=False, to_string_expected=False
        )
