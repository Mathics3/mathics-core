# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.file_operations
"""
import os
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            'FileDate["MathicsNonExistantExample"]',
            ("File not found during FileDate[MathicsNonExistantExample].",),
            "FileDate[MathicsNonExistantExample]",
            None,
        ),
        (
            'FileDate["MathicsNonExistantExample", "Modification"]',
            (
                "File not found during FileDate[MathicsNonExistantExample, Modification].",
            ),
            "FileDate[MathicsNonExistantExample, Modification]",
            None,
        ),
        (
            'FileDate["ExampleData/sunflowers.jpg", "Fail"]',
            (
                'Date type Fail should be "Access", "Modification", "Creation" (Windows only), "Change" (Macintosh and Unix only), or "Rules".',
            ),
            "FileDate[ExampleData/sunflowers.jpg, Fail]",
            None,
        ),
        ('FileHash["ExampleData/sunflowers.jpg", "CRC32"]', None, "933095683", None),
        (
            'FileHash["ExampleData/sunflowers.jpg", "SHA"]',
            None,
            "851696818771101405642332645949480848295550938123",
            None,
        ),
        (
            'FileHash["ExampleData/sunflowers.jpg", "SHA224"]',
            None,
            "8723805623766373862936267623913366865806344065103917676078120867011",
            None,
        ),
        (
            'FileHash["ExampleData/sunflowers.jpg", "SHA384"]',
            None,
            "28288410602533803613059815846847184383722061845493818218404754864571944356226472174056863474016709057507799332611860",
            None,
        ),
        (
            'FileHash["ExampleData/sunflowers.jpg", "SHA512"]',
            None,
            "10111462070211820348006107532340854103555369343736736045463376555356986226454343186097958657445421102793096729074874292511750542388324853755795387877480102",
            None,
        ),
        (
            'FileHash["ExampleData/sunflowers.jpg", xyzsymbol]',
            None,
            "FileHash[ExampleData/sunflowers.jpg, xyzsymbol]",
            None,
        ),
        (
            'FileHash["ExampleData/sunflowers.jpg", "xyzstr"]',
            None,
            "FileHash[ExampleData/sunflowers.jpg, xyzstr, Integer]",
            None,
        ),
        ("FileHash[xyzsymbol]", None, "FileHash[xyzsymbol]", None),
        (
            "FileType[x]",
            ("File specification x is not a string of one or more characters.",),
            "FileType[x]",
            None,
        ),
        (
            'tmpfilename = $TemporaryDirectory <> "/tmp0";Close[OpenWrite[tmpfilename]];',
            None,
            "Null",
            None,
        ),
        (
            'SetFileDate[tmpfilename, {2002, 1, 1, 0, 0, 0.}];FileDate[tmpfilename, "Access"]',
            None,
            "{2002, 1, 1, 0, 0, 0.}",
            None,
        ),
        ("SetFileDate[tmpfilename]", None, "Null", None),
        ('FileDate[tmpfilename, "Access"]//Length', None, "6", None),
        (
            'DeleteFile[tmpfilename];SetFileDate["MathicsNonExample"]',
            ("File not found during SetFileDate[MathicsNonExample].",),
            "$Failed",
            None,
        ),
    ],
)
@pytest.mark.skipif(
    os.getenv("MATHICS3_SANDBOX"),
    reason="Files module is disabled in sandbox mode",
)
def test_private_doctests_file_properties(str_expr, msgs, str_expected, fail_msg):
    """file_opertions.file_properties"""
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
        ('FindList["ExampleData/EinsteinSzilLetter.txt", "project"]', None, "{}", None),
        (
            'FindList["ExampleData/EinsteinSzilLetter.txt", "uranium", 0]',
            None,
            "$Failed",
            None,
        ),
    ],
)
def test_private_doctests_file_utilities(str_expr, msgs, str_expected, fail_msg):
    """file_opertions.file_utilities"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
