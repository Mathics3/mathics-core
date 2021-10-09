# -*- coding: utf-8 -*-
import subprocess

import os.path as osp
import re
import pytest
import sys


def get_testdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires Python 3.7 or higher")
def test_cli():
    script_file = osp.join(get_testdir(), "data", "script.m")

    # asserts output contains 'Hello' and '2'
    result = subprocess.run(
        ["mathics", "-e", "Print[1+1];", "-script", script_file],
        capture_output=True,
    )

    assert re.match(r"Hello\s+2", result.stdout.decode("utf-8"))
    assert result.returncode == 0

    result = subprocess.run(
        ["mathics", "--execute", "2+3", "---trace-builtins"],
        capture_output=False,
    )
    assert result.returncode == 0


if __name__ == "__main__":
    test_cli()
