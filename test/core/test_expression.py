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
        r'Sort[{Import["ExampleData/Einstein.jpg"], 5}]',
        r'{5, Import["ExampleData/Einstein.jpg"]}',
    )
    check_evaluation(
        r"Sort[Table[IntegerDigits[2^n], {n, 10}]]",
        r"{{2}, {4}, {8}, {1, 6}, {3, 2}, {6, 4}, {1, 2, 8}, {2, 5, 6}, {5, 1, 2}, {1, 0, 2, 4}}",
    )
    check_evaluation(
        r"SortBy[Table[IntegerDigits[2^n], {n, 10}], First]",
        r"{{1, 6}, {1, 2, 8}, {1, 0, 2, 4}, {2}, {2, 5, 6}, {3, 2}, {4}, {5, 1, 2}, {6, 4}, {8}}",
    )
