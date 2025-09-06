# -*- coding: utf-8 -*-
import os.path as osp
import re
import subprocess
import sys

import pytest

from mathics import version_string


def get_testdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


@pytest.mark.skipif(
    sys.platform in ("emscripten",),
    reason="Pyodide does not support processes",
)
def test_cli():
    script_file = osp.join(get_testdir(), "data", "script.m")

    # asserts output contains 'Hello' and '2'
    result = subprocess.run(
        ["mathics", "-c", "Print[1+1];", "-f", script_file],
        capture_output=True,
    )

    assert re.match(r"Hello\s+2", result.stdout.decode("utf-8"))
    assert result.returncode == 0

    result = subprocess.run(
        ["mathics", "-ecode", "2+3", "---trace-builtins"],
        capture_output=False,
    )
    assert result.returncode == 0


def test_version_option():
    """
    Check that --version works and returns
    software version information.
    """
    result = subprocess.run(
        ["mathics", "--version"],
        capture_output=True,
    )
    assert result.stdout.decode("utf-8").index(version_string) == 0
    assert result.returncode == 0


if __name__ == "__main__":
    test_cli()
