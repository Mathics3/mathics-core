# -*- coding: utf-8 -*-

import sys
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg"),
    [
        ## Write as Bytes then Read
        (
            "WbR[bytes_, form_] := Module[{stream, res}, stream = OpenWrite[BinaryFormat -> True]; BinaryWrite[stream, bytes]; stream = OpenRead[Close[stream], BinaryFormat -> True]; res = BinaryRead[stream, form]; DeleteFile[Close[stream]]; res];",
            "Null",
            None,
        ),
        ## Byte
        (
            'WbR[{149, 2, 177, 132}, {"Byte", "Byte", "Byte", "Byte"}]',
            "{149, 2, 177, 132}",
            None,
        ),
        (
            '(# == WbR[#, Table["Byte", {50}]]) & [RandomInteger[{0, 255}, 50]]',
            "True",
            None,
        ),
        ## Character8
        (
            'WbR[{97, 98, 99}, {"Character8", "Character8", "Character8"}]',
            "{a, b, c}",
            None,
        ),
        (
            'WbR[{34, 60, 39}, {"Character8", "Character8", "Character8"}]',
            "{\", <, '}",
            None,
        ),
        ## Character16
        (
            'WbR[{97, 0, 98, 0, 99, 0}, {"Character16", "Character16", "Character16"}]',
            "{a, b, c}",
            None,
        ),
        (
            'ToCharacterCode[WbR[{50, 154, 182, 236}, {"Character16", "Character16"}]]',
            "{{39474}, {60598}}",
            None,
        ),
        ## #> WbR[ {91, 146, 206, 54}, {"Character16", "Character16"}]
        ##  = {\\:925b, \\:36ce}
        ## Complex64
        (
            'z=WbR[{80, 201, 77, 239, 201, 177, 76, 79}, "Complex64"];z // InputForm',
            "-6.368779889243691*^28 + 3.434203392*^9*I",
            None,
        ),
        ("z // Precision", "MachinePrecision", None),
        (
            'z=.;WbR[{158, 2, 185, 232, 18, 237, 0, 102}, "Complex64"] // InputForm',
            "-6.989488623351118*^24 + 1.522090212973691*^23*I",
            None,
        ),
        (
            'WbR[{195, 142, 38, 160, 238, 252, 85, 188}, "Complex64"] // InputForm',
            "-1.4107982814807285*^-19 - 0.013060791417956352*I",
            None,
        ),
        ## Complex128
        (
            'WbR[{15,114,1,163,234,98,40,15,214,127,116,15,48,57,208,180},"Complex128"] // InputForm',
            "1.1983977035653814*^-235 - 2.6465639149433955*^-54*I",
            None,
        ),
        (
            'z=WbR[{148,119,12,126,47,94,220,91,42,69,29,68,147,11,62,233},"Complex128"]; z // InputForm',
            "3.2217026714156333*^134 - 8.98364297498066*^198*I",
            None,
        ),
        ("z // Precision", "MachinePrecision", None),
        (
            'WbR[{15,42,80,125,157,4,38,97, 0,0,0,0,0,0,240,255}, "Complex128"]',
            "-I Infinity",
            None,
        ),
        (
            'WbR[{15,42,80,125,157,4,38,97, 0,0,0,0,0,0,240,127}, "Complex128"]',
            "I Infinity",
            None,
        ),
        (
            'WbR[{15,42,80,125,157,4,38,97, 1,0,0,0,0,0,240,255}, "Complex128"]',
            "Indeterminate",
            None,
        ),
        (
            'WbR[{0,0,0,0,0,0,240,127, 15,42,80,125,157,4,38,97}, "Complex128"]',
            "Infinity",
            None,
        ),
        (
            'WbR[{0,0,0,0,0,0,240,255, 15,42,80,125,157,4,38,97}, "Complex128"]',
            "-Infinity",
            None,
        ),
        (
            'WbR[{1,0,0,0,0,0,240,255, 15,42,80,125,157,4,38,97}, "Complex128"]',
            "Indeterminate",
            None,
        ),
        (
            'WbR[{0,0,0,0,0,0,240,127, 0,0,0,0,0,0,240,127}, "Complex128"]',
            "Indeterminate",
            None,
        ),
        (
            'WbR[{0,0,0,0,0,0,240,127, 0,0,0,0,0,0,240,255}, "Complex128"]',
            "Indeterminate",
            None,
        ),
        ## Complex256
        ## TODO
        ## Integer8
        (
            'WbR[{149, 2, 177, 132}, {"Integer8", "Integer8", "Integer8", "Integer8"}]',
            "{-107, 2, -79, -124}",
            None,
        ),
        (
            'WbR[{127, 128, 0, 255}, {"Integer8", "Integer8", "Integer8", "Integer8"}]',
            "{127, -128, 0, -1}",
            None,
        ),
        ## Integer16
        (
            'WbR[{149, 2, 177, 132, 112, 24}, {"Integer16", "Integer16", "Integer16"}]',
            "{661, -31567, 6256}",
            None,
        ),
        (
            'WbR[{0, 0, 255, 0, 255, 255, 128, 127, 128, 128}, Table["Integer16", {5}]]',
            "{0, 255, -1, 32640, -32640}",
            None,
        ),
        ## Integer24
        (
            'WbR[{152, 173, 160, 188, 207, 154}, {"Integer24", "Integer24"}]',
            "{-6247016, -6631492}",
            None,
        ),
        (
            'WbR[{145, 173, 231, 49, 90, 30}, {"Integer24", "Integer24"}]',
            "{-1593967, 1989169}",
            None,
        ),
        ## Integer32
        (
            'WbR[{209, 99, 23, 218, 143, 187, 236, 241}, {"Integer32", "Integer32"}]',
            "{-636001327, -236143729}",
            None,
        ),
        (
            'WbR[{15, 31, 173, 120, 245, 100, 18, 188}, {"Integer32", "Integer32"}]',
            "{2024611599, -1139645195}",
            None,
        ),
        ## Integer64
        (
            'WbR[{211, 18, 152, 2, 235, 102, 82, 16}, "Integer64"]',
            "1176115612243989203",
            None,
        ),
        (
            'WbR[{37, 217, 208, 88, 14, 241, 170, 137}, "Integer64"]',
            "-8526737900550694619",
            None,
        ),
        ## Integer128
        (
            'WbR[{140,32,24,199,10,169,248,117,123,184,75,76,34,206,49,105}, "Integer128"]',
            "139827542997232652313568968616424513676",
            None,
        ),
        (
            'WbR[{101,57,184,108,43,214,186,120,153,51,132,225,56,165,209,77}, "Integer128"]',
            "103439096823027953602112616165136677221",
            None,
        ),
        (
            'WbR[{113,100,125,144,211,83,140,24,206,11,198,118,222,152,23,219}, "Integer128"]',
            "-49058912464625098822365387707690163087",
            None,
        ),
        ## Real32
        (
            'WbR[{81, 72, 250, 79, 52, 227, 104, 90}, {"Real32", "Real32"}] // InputForm',
            "{8.398086656*^9, 1.6388001768669184*^16}",
            None,
        ),
        (
            'WbR[{251, 22, 221, 117, 165, 245, 18, 75}, {"Real32", "Real32"}] // InputForm',
            "{5.605291528399748*^32, 9.631141*^6}",
            None,
        ),
        (
            'z=WbR[{126, 82, 143, 43}, "Real32"]; z // InputForm',
            "1.0183657302847982*^-12",
            None,
        ),
        ("z // Precision", "MachinePrecision", None),
        ('WbR[{0, 0, 128, 127}, "Real32"]', "Infinity", None),
        ('WbR[{0, 0, 128, 255}, "Real32"]', "-Infinity", None),
        ('WbR[{1, 0, 128, 255}, "Real32"]', "Indeterminate", None),
        ('WbR[{1, 0, 128, 127}, "Real32"]', "Indeterminate", None),
        ## Real64
        (
            'WbR[{45, 243, 20, 87, 129, 185, 53, 239}, "Real64"] // InputForm',
            "-5.146466194262116*^227",
            None,
        ),
        (
            'WbR[{192, 60, 162, 67, 122, 71, 74, 196}, "Real64"] // InputForm',
            "-9.695316988087658*^20",
            None,
        ),
        (
            'z=WbR[{15, 42, 80, 125, 157, 4, 38, 97}, "Real64"]; z// InputForm',
            "9.67355569763742*^159",
            None,
        ),
        ("z // Precision", "MachinePrecision", None),
        ('WbR[{0, 0, 0, 0, 0, 0, 240, 127}, "Real64"]', "Infinity", None),
        ('WbR[{0, 0, 0, 0, 0, 0, 240, 255}, "Real64"]', "-Infinity", None),
        ('WbR[{1, 0, 0, 0, 0, 0, 240, 127}, "Real64"]', "Indeterminate", None),
        ('WbR[{1, 0, 0, 0, 0, 0, 240, 255}, "Real64"]', "Indeterminate", None),
        ## Real128
        ## 0x0000
        ('WbR[{0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0}, "Real128"]', "0.×10^-4965", None),
        ('WbR[{0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,128}, "Real128"]', "0.×10^-4965", None),
        ## 0x0001 - 0x7FFE
        (
            'WbR[{0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,255,63}, "Real128"]',
            "1.00000000000000000000000000000000",
            None,
        ),
        (
            'WbR[{0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,255,191}, "Real128"]',
            "-1.00000000000000000000000000000000",
            None,
        ),
        (
            'WbR[{135, 62, 233, 137, 22, 208, 233, 210, 133, 82, 251, 92, 220, 216, 255, 63}, "Real128"]',
            "1.84711247573661489653389674493896",
            None,
        ),
        (
            'WbR[{135, 62, 233, 137, 22, 208, 233, 210, 133, 82, 251, 92, 220, 216, 207, 72}, "Real128"]',
            "2.45563355727491021879689747166252×10^679",
            None,
        ),
        (
            'z=WbR[{74, 95, 30, 234, 116, 130, 1, 84, 20, 133, 245, 221, 113, 110, 219, 212}, "Real128"]',
            "-4.52840681592341879518366539335138×10^1607",
            None,
        ),
        ("z // Precision", "33.", None),
        ## 0x7FFF
        (
            'z=.;WbR[{0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,255,127}, "Real128"]',
            "Infinity",
            None,
        ),
        ('WbR[{0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,255,255}, "Real128"]', "-Infinity", None),
        (
            'WbR[{1,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,255,127}, "Real128"]',
            "Indeterminate",
            None,
        ),
        (
            'WbR[{1,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,255,255}, "Real128"]',
            "Indeterminate",
            None,
        ),
        ## TerminatedString
        ('WbR[{97, 98, 99, 0}, "TerminatedString"]', "abc", None),
        (
            'WbR[{49, 50, 51, 0, 52, 53, 54, 0, 55, 56, 57}, Table["TerminatedString", {3}]]',
            "{123, 456, EndOfFile}",
            None,
        ),
        ('WbR[{0}, "TerminatedString"] // InputForm', '""', None),
        ## UnsignedInteger8
        (
            'WbR[{96, 94, 141, 162, 141}, Table["UnsignedInteger8", {5}]]',
            "{96, 94, 141, 162, 141}",
            None,
        ),
        (
            '(#==WbR[#,Table["UnsignedInteger8",{50}]])&[RandomInteger[{0, 255}, 50]]',
            "True",
            None,
        ),
        ## UnsignedInteger16
        (
            'WbR[{54, 71, 106, 185, 147, 38, 5, 231}, Table["UnsignedInteger16", {4}]]',
            "{18230, 47466, 9875, 59141}",
            None,
        ),
        (
            'WbR[{0, 0, 128, 128, 255, 255}, Table["UnsignedInteger16", {3}]]',
            "{0, 32896, 65535}",
            None,
        ),
        ## UnsignedInteger24
        (
            'WbR[{78, 35, 226, 225, 84, 236}, Table["UnsignedInteger24", {2}]]',
            "{14820174, 15488225}",
            None,
        ),
        (
            'WbR[{165, 2, 82, 239, 88, 59}, Table["UnsignedInteger24", {2}]]',
            "{5374629, 3889391}",
            None,
        ),
        ## UnsignedInteger32
        (
            'WbR[{213,143,98,112,141,183,203,247}, Table["UnsignedInteger32", {2}]]',
            "{1885507541, 4157323149}",
            None,
        ),
        (
            'WbR[{148,135,230,22,136,141,234,99}, Table["UnsignedInteger32", {2}]]',
            "{384206740, 1676316040}",
            None,
        ),
        ## UnsignedInteger64
        (
            'WbR[{95, 5, 33, 229, 29, 62, 63, 98}, "UnsignedInteger64"]',
            "7079445437368829279",
            None,
        ),
        (
            'WbR[{134, 9, 161, 91, 93, 195, 173, 74}, "UnsignedInteger64"]',
            "5381171935514265990",
            None,
        ),
        ## UnsignedInteger128
        (
            'WbR[{108,78,217,150,88,126,152,101,231,134,176,140,118,81,183,220}, "UnsignedInteger128"]',
            "293382001665435747348222619884289871468",
            None,
        ),
        (
            'WbR[{53,83,116,79,81,100,60,126,202,52,241,48,5,113,92,190}, "UnsignedInteger128"]',
            "253033302833692126095975097811212718901",
            None,
        ),
        ## EndOfFile
        (
            'WbR[{148}, {"Integer32", "Integer32","Integer32"}]',
            "{EndOfFile, EndOfFile, EndOfFile}",
            None,
        ),
    ],
)
def test_private_doctests_io(str_expr, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg"),
    [
        ("Head[ByteArray[{1}]]", "ByteArray", None),
    ],
)
def test_ByteArray(str_expr, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg"),
    [
        ("ByteOrdering", "1" if sys.byteorder == "big" else "-1", None),
        ("ByteOrdering == -1 || ByteOrdering == 1", "True", None),
        (
            "$ByteOrdering == ByteOrdering",
            "True",
            "By default, ByteOrdering must be equal to the System $ByteOrdering",
        ),
        (
            "$ByteOrdering == -1 || $ByteOrdering == 1",
            "True",
            "Possible bit ordering are 1 and -1",
        ),
    ],
)
def test_ByteOrdering(str_expr, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
    )


@pytest.mark.skip(reason="NumericArray[] builtin not written yet.")
@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("NumericArray[{{1,2},{3,4}}]", "<Integer64, 2×2>"),
        ("ToString[NumericArray[{{1,2},{3,4}}]]", "<Integer64, 2×2>"),
        ("Head[NumericArray[{1,2}]]", "NumericArray"),
        ("AtomQ[NumericArray[{1,2}]]", "True"),
        ("First[NumericArray[{1,2,3}]]", "1"),
        ("First[NumericArray[{{1,2}, {3,4}}]]", "<Integer64, 2>"),
        ("Last[NumericArray[{1,2,3}]]", "3"),
        ("Last[NumericArray[{{1,2}, {3,4}}]]", "<Integer64, 2>"),
        ("Normal[NumericArray[{{1,2}, {3,4}}]]", "{{1, 2}, {3, 4}}"),
    ],
)
def test_basics(str_expr, str_expected):
    check_evaluation(str_expr, str_expected, hold_expected=True)


@pytest.mark.skip(reason="NumericArray[] builtin not written yet.")
def test_type_conversion():
    # Move below imports to the top when we've implementated NumericArray[]
    from test.helper import evaluate

    import numpy as np

    from mathics.core.atoms import NumericArray

    expr = evaluate("NumericArray[{1,2}]")
    assert isinstance(expr, NumericArray)
    assert expr.value.dtype == np.int64
    expr = evaluate('NumericArray[{1,2}, "ComplexReal32"]')
    assert expr.value.dtype == np.complex64
