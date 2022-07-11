# -*- coding: utf-8 -*-
"""
Unit tests from builtins/files_io/files.py
"""
import os.path as osp
import pytest
import sys
from test.helper import check_evaluation, evaluate


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


@pytest.mark.skipif(
    sys.platform in ("win32",), reason="POSIX pathname tests do not work on Windows"
)
def test_get_and_put():
    temp_filename = evaluate('$TemporaryDirectory<>"/testfile"').to_python()
    temp_filename_strip = temp_filename[1:-1]
    check_evaluation(f"40! >> {temp_filename_strip}", "Null")
    check_evaluation(f"<< {temp_filename_strip}", "40!")
    check_evaluation(f"DeleteFile[{temp_filename}]", "Null")


@pytest.mark.skipif(
    sys.platform in ("win32",), reason="$Path does not work on Windows?"
)
def test_get_path_search():
    # Check that AppendTo[$Path] works in conjunction with Get[]
    dirname = osp.join(osp.dirname(osp.abspath(__file__)), "..", "..", "data")
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
