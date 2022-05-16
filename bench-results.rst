+--------------------------+-------------+-------------+-------------+-------------+
| Test                     | Current 1st | Current 2nd | 4.0.0 1st   | 4.0.0 2nd   |
+==========================+=============+=============+=============+=============+
| load_combinatorica       |             | 1207.00 ms  |  1295.00 ms |  1261.00 ms |
+--------------------------+-------------+-------------+-------------+-------------+
| permutations_1_1         |  4288.00 ms |  4291.00 ms | 4365.00 ms  |  4266.00 ms |
+--------------------------+-------------+-------------+-------------+-------------+
| permutations_groups_1_2  | 31758.00 ms | 31581.00 ms | 34133.00 ms | 33578.00 ms |
+--------------------------+-------------+-------------+-------------+-------------+
| inv_and_invn_vectors_1_3 |  2950.00 ms |  2935.00 ms |  3091.00 ms |  3008.00 ms |
+--------------------------+-------------+-------------+-------------+-------------+
| classes_of_permutes_1_4  |  1643.00 ms |  1639.00 ms |  1947.00 ms |  1900.00 ms |
+--------------------------+-------------+-------------+-------------+-------------+
| combinations_1_5         |  2358.00 ms |  2336.00 ms |  2497.00 ms |  2440.00 ms |
+--------------------------+-------------+-------------+-------------+-------------+
| 2_1_to_2_3               |   384.00 ms |   384.00 ms |   364.00 ms |   359.00 ms |
+--------------------------+-------------+-------------+-------------+-------------+
| combinatorica_rest       |   491.00 ms |   487.00 ms |   495.00 ms |   483.00 ms |
+--------------------------+-------------+-------------+-------------+-------------+


Current
------

::

    test_permutations_1_1  4288.00 ms
    test_permutations_groups_1_2  31758.00 ms
    test_inversions_and_inversion_vectors_1_3  2950.00 ms
    test_special_classes_of_permutations_1_4  1643.00 ms
    test_combinations_1_5  2358.00 ms
    test_2_1_to_2_3  384.00 ms

    load_combinatorica  1207.00 ms
    test_combinatorica_rest  491.00 ms
    test_permutations_1_1  4291.00 ms
    test_permutations_groups_1_2  31581.00 ms
    test_inversions_and_inversion_vectors_1_3  2935.00 ms
    test_special_classes_of_permutations_1_4  1639.00 ms
    test_combinations_1_5  2336.00 ms
    test_2_1_to_2_3  384.00 ms
    test_combinatorica_rest  487.00 ms


V4.0.0
------

::

    load_combinatorica  1295.00 ms
    test_permutations_1_1  4365.00 ms
    test_permutations_groups_1_2  34133.00 ms
    test_inversions_and_inversion_vectors_1_3  3091.00 mss
    test_special_classes_of_permutations_1_4  1947.00 ms
    test_combinations_1_5  2497.00 ms
    test_2_1_to_2_3  364.00 ms
    test_combinatorica_rest  495.00 ms

    load_combinatorica  1261.00 ms
    test_permutations_1_1  4266.00 ms
    test_permutations_groups_1_2  33578.00 ms
    test_inversions_and_inversion_vectors_1_3  3008.00 ms
    test_special_classes_of_permutations_1_4  1900.00 ms
    test_combinations_1_5  2440.00 ms
    test_2_1_to_2_3  359.00 ms
    test_combinatorica_rest  483.00 ms
