# -*- coding: utf-8 -*-

import pytest
from test.helper import check_evaluation
from mathics.builtin.base import check_requires_list

# FIXME: come up with an example that doesn't require skimage.
@pytest.mark.skipif(
    not check_requires_list(["skimage"]),
    reason="Right now need scikit-mmage for this to work",
)
def test_impossible_elements_sort():
    # There was a bug in elements.sort not being able to sort elements due to
    # incompatible arguments, here it is between a list and an integer.
    check_evaluation(
        'Import["ExampleData/Einstein.jpg"] 5', '5 Import["ExampleData/Einstein.jpg"]'
    )
