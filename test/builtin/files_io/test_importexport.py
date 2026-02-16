# -*- coding: utf-8 -*-
import os
import os.path as osp
import sys
import tempfile
from test.helper import check_evaluation, check_evaluation_as_in_cli, evaluate, session

import pytest

from mathics.builtin.atomic.strings import to_python_encoding
from mathics.core.systemsymbols import SymbolFailed

# def test_import():
#     eaccent = "\xe9"
#     for str_expr, str_expected, message in (
#         (
#             """StringTake[Import["ExampleData/Middlemarch.txt", CharacterEncoding -> "ISO8859-1"], {49, 69}]""",
#             f"des plaisirs pr{eaccent}sents",
#             "accented characters in Import",
#         ),
#     ):
#         check_evaluation(str_expr, str_expected, message)


def run_export(temp_dirname: str, short_name: str, file_data: str, character_encoding):
    file_path = osp.join(temp_dirname, short_name)
    expr = rf'Export["{file_path}", {file_data}'
    expr += (
        rf', CharacterEncoding -> "{character_encoding}"' if character_encoding else ""
    )
    expr += "]"
    result = session.evaluate(expr)
    assert result.to_python(string_quotes=False) == file_path
    return file_path


def check_data(
    temp_dirname: str,
    short_name: str,
    file_data: str,
    character_encoding=None,
    expected_data=None,
):
    file_path = run_export(
        temp_dirname, short_name, rf'"{file_data}"', character_encoding
    )
    if expected_data is None:
        expected_data = file_data
    assert (
        open(file_path, "r", encoding=to_python_encoding(character_encoding)).read()
        == expected_data
    )


# Github Action Windows CI servers have problems with releasing files using
# a tempfile.TemporaryDirectory context manager.
# Leave out until we figure how to work around this.
if not (os.environ.get("CI", False) or sys.platform in ("win32",)):

    def test_export():
        with tempfile.TemporaryDirectory(prefix="mtest-") as temp_dirname:
            # Check exporting text files (file extension ".txt")
            check_data(temp_dirname, "add_expr.txt", "1 + x + y")
            check_data(temp_dirname, "AAcute.txt", "\u00c1", "ISOLatin1")
            check_data(temp_dirname, "AAcuteUTF.txt", "\u00c1", "UTF-8")

            # Check exporting CSV files (file extension ".csv")
            file_path = run_export(
                temp_dirname, "csv_list.csv", "{{1, 2, 3}, {4, 5, 6}}", None
            )
            assert open(file_path, "r").read() == "1,2,3\n4,5,6"

            # Check exporting SVG files (file extension ".svg")
            file_path = run_export(
                temp_dirname, "sine.svg", "Plot[Sin[x], {x,0,1}]", None
            )
            data = open(file_path, "r").read().strip()
            if data.startswith("$Failed"):
                pytest.skip("SVG export of Plot failed mysteriously")
            else:
                assert data.startswith("<svg")
                assert data.endswith("</svg>")


"""

        ## Compression
        ## #> Export["abc.txt", 1+x, "ZIP"]    (* MMA Bug - Export::type *)
        ##  : {ZIP} is not a valid set of export elements for the Text format.
        ##  = $Failed
        ## #> Export["abc.txt", 1+x, "BZIP"]   (* MMA Bug - General::stop *)
        ##  : {BZIP} is not a valid set of export elements for the Text format.
        ##  = $Failed
        ## #> Export["abc.txt", 1+x, {"BZIP", "ZIP", "Text"}]
        ##  = abc.txt
        ## #> Export["abc.txt", 1+x, {"GZIP", "Text"}]
        ##  = abc.txt
        ## #> Export["abc.txt", 1+x, {"BZIP2", "Text"}]
        ##  = abc.txt

        ## Doesn't work on Microsoft Windows
        ## S> FileFormat["ExampleData/benzene.xyz"]
        ##  = XYZ

"""


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (r'Quiet[URLFetch["https://", {}]]', None, "$Failed", None),
        # (r'Quiet[URLFetch["https://www.example.com", {}]]', None,
        #  "...", None),
        (
            'Import["ExampleData/ExampleData.tx"]',
            ("File not found during Import.",),
            "$Failed",
            None,
        ),
        (
            "Import[x]",
            ("First argument x is not a valid file, directory, or URL specification.",),
            "$Failed",
            None,
        ),
        ## CSV
        (
            'Import["ExampleData/numberdata.csv", "Elements"]',
            None,
            "{Data, Grid}",
            None,
        ),
        (
            'Import["ExampleData/numberdata.csv", "Data"]',
            None,
            "{{0.88, 0.60, 0.94}, {0.76, 0.19, 0.51}, {0.97, 0.04, 0.26}, {0.33, 0.74, 0.79}, {0.42, 0.64, 0.56}}",
            None,
        ),
        (
            'Import["ExampleData/numberdata.csv"]',
            None,
            "{{0.88, 0.60, 0.94}, {0.76, 0.19, 0.51}, {0.97, 0.04, 0.26}, {0.33, 0.74, 0.79}, {0.42, 0.64, 0.56}}",
            None,
        ),
        (
            'Import["ExampleData/numberdata.csv", "FieldSeparators" -> "."]',
            None,
            "{{0, 88,0, 60,0, 94}, {0, 76,0, 19,0, 51}, {0, 97,0, 04,0, 26}, {0, 33,0, 74,0, 79}, {0, 42,0, 64,0, 56}}",
            None,
        ),
        (
            'Import["ExampleData/Middlemarch.txt"];',
            ("An invalid unicode sequence was encountered and ignored.",),
            "Null",
            None,
        ),
        ## Import with format
        (
            'Import["ExampleData/Testosterone.svg"];',
            ("SVG is not a supported Import format.",),
            "Null",
            None,
        ),
        (
            'Import["ExampleData/Testosterone.svg", "XML"] // Head',
            None,
            "XMLObject[Document]",
            None,
        ),
        (
            'Import["ExampleData/Testosterone.svg", {"XML"}] // Head',
            None,
            "XMLObject[Document]",
            None,
        ),
        (
            'Import["ExampleData/Testosterone.svg", {"XML", "XML"}];',
            ("The Import element XML is not present when importing as XML.",),
            "Null",
            None,
        ),
        ## XML
        (
            'MatchQ[Import["ExampleData/InventionNo1.xml", "Tags"],{__String}]',
            None,
            "True",
            None,
        ),
        ("ImportString[x]", ("First argument x is not a string.",), "$Failed", None),
        ## CSV
        (
            'datastring = "0.88, 0.60, 0.94\\n.076, 0.19, .51\\n0.97, 0.04, .26";ImportString[datastring, "Elements"]',
            None,
            "{Data, Lines, Plaintext, String, Words}",
            None,
        ),
        ('ImportString[datastring, {"CSV","Elements"}]', None, "{Data, Grid}", None),
        (
            'ImportString[datastring, {"CSV", "Data"}]',
            None,
            "{{0.88,  0.60,  0.94}, {.076,  0.19,  .51}, {0.97,  0.04,  .26}}",
            None,
        ),
        (
            "ImportString[datastring]",
            None,
            "0.88, 0.60, 0.94\n.076, 0.19, .51\n0.97, 0.04, .26",
            None,
        ),
        (
            'ImportString[datastring, "CSV","FieldSeparators" -> "."]',
            None,
            "{{0, 88, 0, 60, 0, 94}, {076, 0, 19, , 51}, {0, 97, 0, 04, , 26}}",
            None,
        ),
        ## Invalid Filename
        (
            'Export["abc.", 1+2]',
            ("Cannot infer format of file abc..",),
            "$Failed",
            None,
        ),
        (
            'Export[".ext", 1+2]',
            ("Cannot infer format of file .ext.",),
            "$Failed",
            None,
        ),
        (
            "Export[x, 1+2]",
            ("First argument x is not a valid file specification.",),
            "$Failed",
            None,
        ),
        ## Explicit Format
        (
            'Export["abc.txt", 1+x, "JPF"]',
            ("{JPF} is not a valid set of export elements for the Text format.",),
            "$Failed",
            None,
        ),
        (
            'Export["abc.txt", 1+x, {"JPF"}]',
            ("{JPF} is not a valid set of export elements for the Text format.",),
            "$Failed",
            None,
        ),
        ## FORMATS
        ## ASCII text
        ('FileFormat["ExampleData/BloodToilTearsSweat.txt"]', None, "Text", None),
        ('FileFormat["ExampleData/MadTeaParty.gif"]', None, "GIF", None),
        ('FileFormat["ExampleData/moon.tif"]', None, "TIFF", None),
        ('FileFormat["ExampleData/numberdata.csv"]', None, "CSV", None),
        ('FileFormat["ExampleData/EinsteinSzilLetter.txt"]', None, "Text", None),
        ('FileFormat["ExampleData/BloodToilTearsSweat.txt"]', None, "Text", None),
        ('FileFormat["ExampleData/colors.json"]', None, "JSON", None),
        (
            'FileFormat["ExampleData/some-typo.extension"]',
            ("File not found during FileFormat[ExampleData/some-typo.extension].",),
            "$Failed",
            None,
        ),
        ('FileFormat["ExampleData/Testosterone.svg"]', None, "SVG", None),
        ('FileFormat["ExampleData/colors.json"]', None, "JSON", None),
        ('FileFormat["ExampleData/InventionNo1.xml"]', None, "XML", None),
    ],
)
def test_private_doctests_importexport(str_expr, msgs, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


def test_inividually():
    # Test Export where we cannot infer the export type from the file extension;
    # here it is: ".jcp".
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jcp") as tmp:
        filename = tmp.name
        expr = f'Export["{filename}", 1+x,' + "{}]"
        result = evaluate(expr)
        outs = [out.text for out in session.evaluation.out]
        assert result == SymbolFailed
        assert outs == [f"Cannot infer format of file {filename}."]

    # Check that exporting with an empty list of elements is okay.
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt") as tmp:
        filename = tmp.name
        expr = f'Export["{filename}", 1+x' + "{}]"
        result = evaluate(expr)
        outs = [out.text for out in session.evaluation.out]
        assert outs == []


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            r'System`Convert`B64Dump`B64Encode["∫ f  x"]',
            None,
            r"4oirIGYg752MIHg=",
            None,
        ),
        (
            r'System`Convert`B64Dump`B64Decode["4oirIGYg752MIHg="]',
            None,
            r"∫ f  x",
            None,
        ),
    ],
)
def test_b64encode(str_expr, msgs, str_expected, fail_msg):
    """special case"""
    check_evaluation_as_in_cli(str_expr, str_expected, fail_msg, msgs)
