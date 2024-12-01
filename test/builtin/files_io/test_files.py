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


@pytest.mark.skipif(
    sys.platform in ("emscripten",),
    reason="Pyodide has restricted filesystem access",
)
@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (None, None, None, None),  # Reset the session and set the working
        # directory as the temporary directory
        ('Close["abc"]', ("abc is not open.",), "Close[abc]", ""),
        (
            "exp = Sin[1]; FilePrint[exp]",
            ("File specification Sin[1] is not a string of one or more characters.",),
            "FilePrint[Sin[1]]",
            "",
        ),
        (
            'FilePrint["somenonexistentpath_h47sdmk^&h4"]',
            ("Cannot open somenonexistentpath_h47sdmk^&h4.",),
            "FilePrint[somenonexistentpath_h47sdmk^&h4]",
            "",
        ),
        (
            'FilePrint[""]',
            ("File specification  is not a string of one or more characters.",),
            "FilePrint[]",
            "",
        ),
        (
            'Get["SomeTypoPackage`"]',
            ("Cannot open SomeTypoPackage`.",),
            "$Failed",
            "",
        ),
        (
            "OpenRead[]",
            ("OpenRead called with 0 arguments; 1 argument is expected.",),
            "OpenRead[]",
            "",
        ),
        (
            "OpenRead[y]",
            ("File specification y is not a string of one or more characters.",),
            "OpenRead[y]",
            "",
        ),
        (
            'OpenRead[""]',
            ("File specification  is not a string of one or more characters.",),
            "OpenRead[]",
            "",
        ),
        (
            'Close[OpenRead["https://raw.githubusercontent.com/Mathics3/mathics-core/master/README.rst"]];',
            None,
            "Null",
            "",
        ),
        (
            'fd=OpenRead["ExampleData/EinsteinSzilLetter.txt", BinaryFormat -> True, CharacterEncoding->"UTF8"]//Head',
            None,
            "InputStream",
            "",
        ),
        (
            "Close[fd]; fd=.;fd=OpenWrite[BinaryFormat -> True]//Head",
            None,
            "OutputStream",
            "",
        ),
        (
            'DeleteFile[Close[fd]];fd=.;appendFile = OpenAppend["MathicsNonExampleFile"]//{#1[[0]],#1[[1]]}&',
            None,
            "{OutputStream, MathicsNonExampleFile}",
            "",
        ),
        (
            "Close[appendFile]",
            None,
            "Close[{OutputStream, MathicsNonExampleFile}]",
            "",
        ),
        (
            "Delete[MathicsNonExampleFile]",
            None,
            "Delete[MathicsNonExampleFile]",
            "",
        ),
        ## writing to dir
        ("x >>> /var/", ("Cannot open /var/.",), "x >>> /var/", ""),
        ## writing to read only file
        (
            "x >>> /proc/uptime",
            ("Cannot open /proc/uptime.",),
            "x >>> /proc/uptime",
            "",
        ),
        ## Malformed InputString
        (
            "Read[InputStream[String], {Word, Number}]",
            None,
            "Read[InputStream[String], {Word, Number}]",
            "",
        ),
        ## Correctly formed InputString but not open
        (
            "Read[InputStream[String, -1], {Word, Number}]",
            (
                "Positive machine-sized integer expected at position 2 "
                "of InputStream[String, -1]",
            ),
            "Read[InputStream[String, -1], {Word, Number}]",
            "",
        ),
        ('stream = StringToStream[""];Read[stream, Word]', None, "EndOfFile", ""),
        ("Read[stream, Word]", None, "EndOfFile", ""),
        ("Close[stream];", None, "Null", ""),
        (
            'stream = StringToStream["123xyz 321"]; Read[stream, Number]',
            None,
            "123",
            "",
        ),
        ("Quiet[Read[stream, Number]]", None, "$Failed", ""),
        ## Real
        ('stream = StringToStream["123, 4abc"];Read[stream, Real]', None, "123.", ""),
        ("Read[stream, Real]", None, "4.", ""),
        ("Quiet[Read[stream, Number]]", None, "$Failed", ""),
        ("Close[stream];", None, "Null", ""),
        (
            'stream = StringToStream["1.523E-19"]; Read[stream, Real]',
            None,
            "1.523×10^-19",
            "",
        ),
        ("Close[stream];", None, "Null", ""),
        (
            'stream = StringToStream["-1.523e19"]; Read[stream, Real]',
            None,
            "-1.523×10^19",
            "",
        ),
        ("Close[stream];", None, "Null", ""),
        (
            'stream = StringToStream["3*^10"]; Read[stream, Real]',
            None,
            "3.×10^10",
            "",
        ),
        ("Close[stream];", None, "Null", ""),
        (
            'stream = StringToStream["3.*^10"]; Read[stream, Real]',
            None,
            "3.×10^10",
            "",
        ),
        ("Close[stream];", None, "Null", ""),
        ## Expression
        (
            'stream = StringToStream["x + y Sin[z]"]; Read[stream, Expression]',
            None,
            "x + y Sin[z]",
            "",
        ),
        ("Close[stream];", None, "Null", ""),
        ## ('stream = Quiet[StringToStream["Sin[1 123"]; Read[stream, Expression]]', None,'$Failed', ""),
        (
            'stream = StringToStream["123 abc"]; Quiet[Read[stream, {Word, Number}]]',
            None,
            "$Failed",
            "",
        ),
        ("Close[stream];", None, "Null", ""),
        (
            'stream = StringToStream["123 123"];  Read[stream, {Real, Number}]',
            None,
            "{123., 123}",
            "",
        ),
        ("Close[stream];", None, "Null", ""),
        # Rocky: I don't know what this is supposed to check, but WMA reports:
        #    Part::partd: Part specification of streapm[[1]] is longer than depth of object.
        # and partd testing should be done somewhere else.
        # (
        #     "Quiet[Read[stream, {Real}]]//{#1[[0]],#1[[1]][[0]],#1[[1]][[1]],#1[[2]]}&",
        #     None,
        #     "{Read, InputStream, String, {Real}}",
        #     "",
        # ),
        ("Close[stream];", None, "Null", ""),
        (
            'ReadList[StringToStream["a 1 b 2"], {Word, Number}, 1]',
            None,
            "{{a, 1}}",
            "",
        ),
        ('stream = StringToStream["Mathics is cool!"];', None, "Null", ""),
        ("SetStreamPosition[stream, -5]", ("Invalid I/O Seek.",), "0", ""),
        (
            '(strm = StringToStream["abc 123"])//{#1[[0]],#1[[1]]}&',
            None,
            "{InputStream, String}",
            "",
        ),
        ("Read[strm, Word]", None, "abc", ""),
        ("Read[strm, Number]", None, "123", ""),
        ("Close[strm]", None, "String", ""),
        ('Streams["some_nonexistent_name"]', None, "{}", ""),
        (
            "stream = OpenWrite[]; WriteString[stream, 100, 1 + x + y, Sin[x  + y]]",
            None,
            "Null",
            "",
        ),
        ("(pathname = Close[stream])//Head", None, "String", ""),
        ("FilePrint[pathname]", ("1001 + x + ySin[x + y]",), "Null", ""),
        ("DeleteFile[pathname];", None, "Null", ""),
        (
            "stream = OpenWrite[];WriteString[stream];(pathname = Close[stream])//Head",
            None,
            "String",
            "",
        ),
        ("FilePrint[pathname]", None, "Null", ""),
        ("DeleteFile[pathname];Clear[pathname];", None, "Null", ""),
        ('tmpfilename = $TemporaryDirectory <> "/tmp0";', None, "Null", ""),
        ("Close[OpenWrite[tmpfilename]];", None, "Null", ""),
        (
            'SetFileDate[tmpfilename, {2002, 1, 1, 0, 0, 0.}, "Access"];',
            None,
            "Null",
            "",
        ),
        ('FileDate[tmpfilename, "Access"]', None, "{2002, 1, 1, 0, 0, 0.}", ""),
        ("DeleteFile[tmpfilename]", None, "Null", ""),
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
            'We expect "<<" to get parsed as "Get[...]',
        ),
        # (
        #     r"Hold[<<`/.\-_:$*~?] // FullForm",
        #     None,
        #     r'Hold[Get["`/.\\\\-_:$*~?"]]',
        #     (
        #         'We expect "<<" to get parse as "Get[...]" '
        #         "even when there are weird filename characters",
        #     ),
        # ),
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
    """
    Check OpenRead[] on a non-existent file name"""
    # Below, we set "delete=False" because `os.unlink()` is used
    # to delete the file.
    new_temp_file = NamedTemporaryFile(mode="r", delete=False)
    name = canonic_filename(new_temp_file.name)
    try:
        os.unlink(name)
    except PermissionError:
        # This can happen in MS Windows
        pytest.mark.skip("Something went wrong in trying to set up test.")
        return
    check_evaluation(
        str_expr=f'OpenRead["{name}"]',
        str_expected=f"OpenRead[{name}]",
        to_string_expr=True,
        hold_expected=True,
        failure_message="",
        expected_messages=(f"Cannot open {name}.",),
    )


def test_streams():
    """
    Test Streams[] and Streams[name]
    """
    # Save original Streams[] count. Then add a new OutputStream,
    # See that this is indeed a new OutputStream, and that
    # See that Streams[] count is now one larger.
    # See that we can find new stream by name in Streams[]
    # Finally Close new stream.
    orig_streams_count = evaluate("Length[Streams[]]").to_python()
    check_evaluation(
        str_expr="(newStream = OpenWrite[]) // Head",
        str_expected="OutputStream",
        failure_message="Expecting Head[] of a new OpenWrite stream to be an 'OutputStream'",
    )
    new_streams_count = evaluate("Length[Streams[]]").to_python()
    assert (
        orig_streams_count + 1 == new_streams_count
    ), "should have added one more stream listed"
    check_evaluation(
        str_expr="Length[Streams[newStream]] == 1",
        str_expected="True",
        to_string_expr=False,
        to_string_expected=False,
        failure_message="Expecting to find new stream in list of existing streams",
    )
    check_evaluation(
        str_expr="Streams[newStream][[1]] == newStream",
        str_expected="True",
        to_string_expr=False,
        to_string_expected=False,
        failure_message="Expecting stream found in list to be the one we just added",
    )
    evaluate("Close[newStream]")


def test_write_string():
    """
    Check OpenWrite[] and WriteString[] using a path name.
    """
    # 1. Create a temporary file name in Python.
    # 2. Open that for writing in Mathics3 using OpenWrite[].
    # 3. Write some data to that using WriteString[] and
    #    close the stream using Close[]
    # 4. Then back in Python, see that the file was written and
    #    that it has the data that was written via WriteString[].
    # 5. Finally, remove the file.

    # 1. Create temporary file name
    tempfile = NamedTemporaryFile(mode="r", delete=False)
    tempfile_path = tempfile.name

    # 2. Open that for writing in Mathics3 using OpenWrite[].
    check_evaluation(
        str_expr=f'stream = OpenWrite["{tempfile_path}"];',
        to_string_expr=False,
        to_string_expected=False,
    )

    # 3. Write some data to that using WriteString[] and
    #    close the stream using Close[]
    text = "testing\n"
    check_evaluation(
        str_expr=f'WriteString["{tempfile_path}", "{text}"];',
        to_string_expr=False,
        to_string_expected=False,
    )
    check_evaluation(
        str_expr="Close[stream];",
    )

    # 4. Back in Python, see that the file was written and
    #    that it has the data that was written via WriteString[].

    assert osp.exists(tempfile_path)
    assert open(tempfile_path, "r").read() == text

    # 5. Finally, remove the file.
    try:
        os.unlink(tempfile_path)
    except PermissionError:
        # This can happen in MS Windows
        pass


# rocky: I don't understand what these are supposed to test.

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
# ("Close[laststrm];FilePrint[pathname]", ("abc",), "Null", ""),

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
