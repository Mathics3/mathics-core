# -*- coding: utf-8 -*-
"""
Test mathics.core.streams
"""

import os.path as osp
from os import chdir

from mathics.core.streams import path_search


def get_datadir():
    dirname = osp.normcase(osp.join(osp.dirname(osp.abspath(__file__)), "..", "data"))
    return osp.realpath(dirname)


def test_path_search():
    """
    Test mathics.core.path_search()
    """

    chdir(get_datadir())
    for expect_find, expect_temporary, filename, assert_msg in (
        (True, False, "fortytwo`", "should find with .m extension"),
        (False, False, "fortytwo", "should not find without backtick (`) added"),
        (True, False, "recursive-gcd`", "should find with .wl extension"),
    ):
        resolved_file, is_temporary = path_search(filename)
        assert expect_find == bool(resolved_file), assert_msg
        assert expect_temporary == is_temporary
