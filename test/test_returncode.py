# -*- coding: utf-8 -*-
import os.path as osp
import subprocess
import sys

import pytest


def get_testdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


@pytest.mark.skipif(
    sys.platform in ("emscripten",),
    reason="Pyodide does not support processes",
)
def test_returncode():
    assert subprocess.run(["mathics", "-c", "Quit[5]"]).returncode == 5
    assert subprocess.run(["mathics", "-code", "1 + 2'"]).returncode == 0
    assert subprocess.run(["mathics", "---code", "Quit[0]"]).returncode == 0

    gcd_file = osp.join(get_testdir(), "data", "recursive-gcd.wl")
    assert subprocess.run(["mathics", "-f", gcd_file]).returncode == 0


if __name__ == "__main__":
    test_returncode()
