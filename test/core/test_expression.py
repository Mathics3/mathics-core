# -*- coding: utf-8 -*-

import pytest
from test.helper import check_evaluation
from mathics.builtin.base import check_requires_list

# FIXME: come up with an example that doesn't require skimage.
@pytest.mark.skipif(
    not check_requires_list(["skimage"]),
    reason="Right now need scikit-image for this to work",
)
def test_canonical_sort():
    check_evaluation(
        'Sort[{Import["ExampleData/Einstein.jpg"], 5}]',
        '{5, Import["ExampleData/Einstein.jpg"]}',
    )
