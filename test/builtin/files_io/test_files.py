# -*- coding: utf-8 -*-
"""
Unit tests from builtins/files_io/files.py
"""
import os
import os.path as osp
import sys
from tempfile import NamedTemporaryFile
from test.helper import check_evaluation, evaluate

import pytest

from mathics.core.parser.convert import canonic_filename


def test_compress():
    for text in ("", "abc", " "):
        str_expr = f'Uncompress[Compress["{text}"]]'
        str_expected = f'"{text}"'
        check_evaluation(
            str_expr, str_expected, to_string_expr=False, to_string_expected=False
        )


def test_unprotected():
    for str_expr, str_expected, message in (
        ("Attributes[$Path]", "{}", ""),
        ("Attributes[$InstallationDirectory]", "{}", ""),
    ):
        check_evaluation(str_expr, str_expected, message)


def test_get_and_put():
    temp_filename = canonic_filename(
        evaluate('$TemporaryDirectory<>"/testfile"').to_python()
    )
    temp_filename_strip = temp_filename[1:-1]
    check_evaluation(f"40! >> {temp_filename_strip}", "Null")
    check_evaluation(f"<< {temp_filename_strip}", "40!")
    check_evaluation(f"DeleteFile[{temp_filename}]", "Null")


def test_get_input():
    # Check that $InputFileName and $Input are set inside running a Get[].
    script_path = canonic_filename(
        osp.normpath(
            osp.join(osp.dirname(__file__), "..", "..", "data", "inputfile-bug.m")
        )
    )

    check_evaluation(f'Get["{script_path}"]', script_path, hold_expected=True)

    script_path = canonic_filename(
        osp.normpath(osp.join(osp.dirname(__file__), "..", "..", "data", "input-bug.m"))
    )
    check_evaluation(f'Get["{script_path}"]', script_path, hold_expected=True)


@pytest.mark.skipif(
    sys.platform in ("win32",), reason="$Path does not work on Windows?"
)
def test_get_path_search():
    # Check that AppendTo[$Path] works in conjunction with Get[]
    dirname = osp.normpath(osp.join(osp.dirname(__file__), "..", "..", "data"))
    evaled = evaluate(f"""AppendTo[$Path, "{dirname}"]""")
    assert evaled.has_form("List", 1, None)
    check_evaluation('Get["fortytwo.m"]', "42")


@pytest.mark.skipif(
    sys.platform in ("win32",),
    reason="Need to fix some sort of Unicode decode problem on Windows",
)
def test_temp_stream():
    temp_filename = evaluate("Close[OpenWrite[BinaryFormat -> True]]").value
    assert osp.exists(
        temp_filename
    ), f"temporary filename {temp_filename} should appear"
    result = evaluate(f"""DeleteFile["{temp_filename}"]""").to_python()
    assert result is None
    assert not osp.exists(
        temp_filename
    ), f"temporary filename {temp_filename} should not appear"


@pytest.mark.skipif(
    sys.platform in ("win32",),
    reason="Need to fix some sort of Unicode decode problem on Windows",
)
def test_close():
    temp_filename = evaluate("Close[OpenWrite[]]").value
    assert osp.exists(
        temp_filename
    ), f"temporary filename {temp_filename} should appear"
    result = evaluate(f"""DeleteFile["{temp_filename}"]""").to_python()
    assert result is None
    assert not osp.exists(
        temp_filename
    ), f"temporary filename {temp_filename} should not appear"


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ('Close["abc"]', ("abc is not open.",), "Close[abc]", None),
        (
            "exp = Sin[1]; FilePrint[exp]",
            ("File specification Sin[1] is not a string of one or more characters.",),
            "FilePrint[Sin[1]]",
            None,
        ),
        (
            'FilePrint["somenonexistentpath_h47sdmk^&h4"]',
            ("Cannot open somenonexistentpath_h47sdmk^&h4.",),
            "FilePrint[somenonexistentpath_h47sdmk^&h4]",
            None,
        ),
        (
            'FilePrint[""]',
            ("File specification  is not a string of one or more characters.",),
            "FilePrint[]",
            None,
        ),
        (
            'Get["SomeTypoPackage`"]',
            ("Cannot open SomeTypoPackage`.",),
            "$Failed",
            None,
        ),
        (
            "OpenRead[]",
            ("OpenRead called with 0 arguments; 1 argument is expected.",),
            "OpenRead[]",
            None,
        ),
        (
            "OpenRead[y]",
            ("File specification y is not a string of one or more characters.",),
            "OpenRead[y]",
            None,
        ),
        (
            'OpenRead[""]',
            ("File specification  is not a string of one or more characters.",),
            "OpenRead[]",
            None,
        ),
        (
            'fd=OpenRead["ExampleData/EinsteinSzilLetter.txt", BinaryFormat -> True, CharacterEncoding->"UTF8"]//Head',
            None,
            "InputStream",
            None,
        ),
        (
            "Close[fd]; fd=.;fd=OpenWrite[BinaryFormat -> True]//Head",
            None,
            "OutputStream",
            None,
        ),
        (
            'DeleteFile[Close[fd]];fd=.;appendFile = OpenAppend["MathicsNonExampleFile"]//{#1[[0]],#1[[1]]}&',
            None,
            "{OutputStream, MathicsNonExampleFile}",
            None,
        ),
        (
            "Close[appendFile]",
            None,
            "Close[{OutputStream, MathicsNonExampleFile}]",
            None,
        ),
        ## writing to dir
        ("x >>> /var/", ("Cannot open /var/.",), "x >>> /var/", None),
        ## writing to read only file
        (
            "x >>> /proc/uptime",
            ("Cannot open /proc/uptime.",),
            "x >>> /proc/uptime",
            None,
        ),
        ## Malformed InputString
        (
            "Read[InputStream[String], {Word, Number}]",
            None,
            "Read[InputStream[String], {Word, Number}]",
            None,
        ),
        ## Correctly formed InputString but not open
        (
            "Read[InputStream[String, -1], {Word, Number}]",
            ("InputStream[String, -1] is not open.",),
            "Read[InputStream[String, -1], {Word, Number}]",
            None,
        ),
        ('stream = StringToStream[""];Read[stream, Word]', None, "EndOfFile", None),
        ("Read[stream, Word]", None, "EndOfFile", None),
        ("Close[stream];", None, "Null", None),
        (
            'stream = StringToStream["123xyz 321"]; Read[stream, Number]',
            None,
            "123",
            None,
        ),
        ("Quiet[Read[stream, Number]]", None, "$Failed", None),
        ## Real
        ('stream = StringToStream["123, 4abc"];Read[stream, Real]', None, "123.", None),
        ("Read[stream, Real]", None, "4.", None),
        ("Quiet[Read[stream, Number]]", None, "$Failed", None),
        ("Close[stream];", None, "Null", None),
        (
            'stream = StringToStream["1.523E-19"]; Read[stream, Real]',
            None,
            "1.523×10^-19",
            None,
        ),
        ("Close[stream];", None, "Null", None),
        (
            'stream = StringToStream["-1.523e19"]; Read[stream, Real]',
            None,
            "-1.523×10^19",
            None,
        ),
        ("Close[stream];", None, "Null", None),
        (
            'stream = StringToStream["3*^10"]; Read[stream, Real]',
            None,
            "3.×10^10",
            None,
        ),
        ("Close[stream];", None, "Null", None),
        (
            'stream = StringToStream["3.*^10"]; Read[stream, Real]',
            None,
            "3.×10^10",
            None,
        ),
        ("Close[stream];", None, "Null", None),
        ## Expression
        (
            'stream = StringToStream["x + y Sin[z]"]; Read[stream, Expression]',
            None,
            "x + y Sin[z]",
            None,
        ),
        ("Close[stream];", None, "Null", None),
        ## ('stream = Quiet[StringToStream["Sin[1 123"]; Read[stream, Expression]]', None,'$Failed', None),
        (
            'stream = StringToStream["123 abc"]; Quiet[Read[stream, {Word, Number}]]',
            None,
            "$Failed",
            None,
        ),
        ("Close[stream];", None, "Null", None),
        (
            'stream = StringToStream["123 123"];  Read[stream, {Real, Number}]',
            None,
            "{123., 123}",
            None,
        ),
        ("Close[stream];", None, "Null", None),
        (
            "Quiet[Read[stream, {Real}]]//{#1[[0]],#1[[1]][[0]],#1[[1]][[1]],#1[[2]]}&",
            None,
            "{Read, InputStream, String, {Real}}",
            None,
        ),
        (
            r'stream = StringToStream["\"abc123\""];ReadList[stream, "Invalid"]//{#1[[0]],#1[[2]]}&',
            ("Invalid is not a valid format specification.",),
            "{ReadList, Invalid}",
            None,
        ),
        ("Close[stream];", None, "Null", None),
        (
            'ReadList[StringToStream["a 1 b 2"], {Word, Number}, 1]',
            None,
            "{{a, 1}}",
            None,
        ),
        ('stream = StringToStream["Mathics is cool!"];', None, "Null", None),
        ("SetStreamPosition[stream, -5]", ("Invalid I/O Seek.",), "0", None),
        (
            '(strm = StringToStream["abc 123"])//{#1[[0]],#1[[1]]}&',
            None,
            "{InputStream, String}",
            None,
        ),
        ("Read[strm, Word]", None, "abc", None),
        ("Read[strm, Number]", None, "123", None),
        ("Close[strm]", None, "String", None),
        ("(low=OpenWrite[])//Head", None, "OutputStream", None),
        ('Streams["some_nonexistent_name"]', None, "{}", None),
        (
            "stream = OpenWrite[]; WriteString[stream, 100, 1 + x + y, Sin[x  + y]]",
            None,
            "Null",
            None,
        ),
        ("(pathname = Close[stream])//Head", None, "String", None),
        ("FilePrint[pathname]", ("1001 + x + ySin[x + y]",), "Null", None),
        ("DeleteFile[pathname];", None, "Null", None),
        (
            "stream = OpenWrite[];WriteString[stream];(pathname = Close[stream])//Head",
            None,
            "String",
            None,
        ),
        ("FilePrint[pathname]", None, "Null", None),
        ("DeleteFile[pathname];Clear[pathname];", None, "Null", None),
    ],
)
def test_private_doctests_files(str_expr, msgs, str_expected, fail_msg):
    """Grab-bag tests from mathics.builtin.files_io.files. These need to be split out."""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "Hold[<< ~/some_example/dir/] // FullForm",
            None,
            'Hold[Get["~/some_example/dir/"]]',
            None,
        )
    ],
)
def test_get_operator_parse(str_expr, msgs, str_expected, fail_msg):
    """
    Check that << is canonicalized to "Get"
    """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


def test_open_read():
    """ """
    new_temp_file = NamedTemporaryFile(mode="r", delete=True)
    name = canonic_filename(new_temp_file.name)
    os.unlink(name)
    check_evaluation(
        str_expr=f'OpenRead["{name}"]',
        str_expected=f"OpenRead[{name}]",
        to_string_expr=True,
        hold_expected=True,
        failure_message=None,
        expected_messages=(f"Cannot open {name}.",),
    )


# rocky: I don't understand what these are supposed to test.
# (
#     r"Hold[<<`/.\-_:$*~?] // FullForm",
#     None,
#     r'Hold[Get["`/.\\\\-_:$*~?"]]',
#     None,
# ),

# (
#     "Streams[low[[1]]]//{#1[[0]],#1[[1]][[0]]}&",
#     None,
#     "{List, OutputStream}",
#     None,
# ),


# (
#     "WriteString[pathname, abc];(laststrm=Streams[pathname][[1]])//Head",
#     None,
#     "OutputStream",
#     None,
# ),

# (
#     "WriteString[pathname, abc];(laststrm=Streams[pathname][[1]])//Head",
#     None,
#     "OutputStream",
#     None,
# ),
# ("Close[laststrm];FilePrint[pathname]", ("abc",), "Null", None),

# I do not know what this is it supposed to test with this...
# def test_Inputget_and_put():
#    stream = Expression('Plus', Symbol('x'), Integer(2))

# TODO: add these Unix-specific test. Be sure not to test
# sys.platform for not Windows and to test for applicability
# ## writing to dir
# S> x >> /var/
#  : Cannot open /var/.
#  = x >> /var/

# ## writing to read only file
# S> x >> /proc/uptime
#  : Cannot open /proc/uptime.
#  = x >> /proc/uptime

# ## writing to full file
# S> x >> /dev/full
#  : No space left on device.

# #> WriteString[OpenWrite["/dev/zero"], "abc"]   (* Null *)
#     ## Return $Failed on special files
#     #> FilePrint["/dev/zero"]
#      = $Failed
#     #> FilePrint["/dev/random"]
#      = $Failed
#     #> FilePrint["/dev/null"]
#      = $Failed
