To get results:

```
pytest -s test/package/test_combinatorica_benched.py
```

These results are for 3.8.13:


+--------------------------+-------------+-------------+-------------+-------------+
| Test                     | Current 1st | Current 2nd | 4.0.0 1st   | 4.0.0 2nd   |
+==========================+=============+=============+=============+=============+
| load_combinatorica       |             | 1207.00 ms  |  1295.00 ms |  1261.00 ms |
|                          |             | 1139.00 ms  |             |             |
|                          |             |  938.92 ms  |             |             |
|                          |             |  935.36 ms  |             |             |
|                          | cython      | 1017.00 ms  |             |             |
|                          | pyston 2.3  | 1021.00 ms  |             |             |
|                          |             | 350.53 mss  |             |             |
+--------------------------+-------------+-------------+-------------+-------------+
| permutations_1_1         |  4288.00 ms | 4291.00 ms  | 4365.00 ms  |  4266.00 ms |
|                          |             | 4075.00 ms  |             |             |
|                          |             | 3631.77 ms  |             |             |
|                          |             | 4017.77 ms  |             |             |
|                          | pyston 2.3  | 3810.00 ms  |             |             |
|                          |             | 1975.42 ms  |             |             |
|                          | cython      | 3759.00 ms  |             |             |
+--------------------------+-------------+-------------+-------------+-------------+
| permutations_groups_1_2  | 31758.00 ms | 31581.00 ms | 34133.00 ms | 33578.00 ms |
|                          |             | 29727.00 ms |             |             |
|                          |             | 29592.86 ms |             |             |
|                          | pyston 2.3  | 28219.00 ms |             |             |
|                          |             | 13086.08 ms |             |             |
|                          | cython      | 27951.00 ms |             |             |
+--------------------------+-------------+-------------+-------------+-------------+
| inv_and_invn_vectors_1_3 |  2950.00 ms |  2935.00 ms |  3091.00 ms |  3008.00 ms |
|                          |             |  2750.00 ms |             |             |
|                          |             |  2712.00 ms |             |             |
|                          | pyston 2.3  |  2622.00 ms |             |             |
|                          |             |  1203.59 ms |             |             |
|                          | cython      |  2608.00 ms |             |             |
+--------------------------+-------------+-------------+-------------+-------------+
| classes_of_permutes_1_4  |  1643.00 ms |  1639.00 ms |  1947.00 ms |  1900.00 ms |
|                          |             |  1557.00 ms |             |             |
|                          |             |  1397.00 ms |             |             |
|                          |             |  1451.51 ms |             |             |
|                          | pyston 2.3  |  1437.00 ms |             |             |
|                          |             |   634.27 ms |             |             |
|                          | cython      |  1421.00    |             |             |
+--------------------------+-------------+-------------+-------------+-------------+
| combinations_1_5         |  2358.00 ms |  2336.00 ms |  2497.00 ms |  2440.00 ms |
|                          |             |  2270.00 ms |             |             |
|                          |             |  2122.98 ms |             |             |
|                          |             |  2253.06 ms |             |             |
|                          | pyston 2.3  |  2050.00 ms |             |             |
|                          |             |   949.64 ms |             |             |
|                          | cython      |  2022.00 ms |             |             |
+--------------------------+-------------+-------------+-------------+-------------+
| 2_1_to_2_3               |   384.00 ms |   384.00 ms |   364.00 ms |   359.00 ms |
|                          |             |   364.00 ms |             |             |
|                          |             |   340.00 ms |             |             |
|                          |             |   345.46 ms |             |             |
|                          | pyston 2.3  |   366.00 ms |             |             |
|                          |             |   148.52 ms |             |             |
|                          | cython      |   340.00 ms |             |             |
+--------------------------+-------------+-------------+-------------+-------------+
| combinatorica_rest       |   491.00 ms |   487.00 ms |   495.00 ms |   483.00 ms |
|                          |             |   469.00 ms |             |             |
|                          |             |   425.00 ms |             |             |
|                          |             |   440.00 ms |             |             |
|                          | pyston 2.3  |   629.00 ms |             |             |
|                          |             |   348.63 ms |             |             |
|                          | cython      |   418.00 ms |             |             |
|                          | cython      |   348.00 ms |             |             |
+--------------------------+-------------+-------------+-------------+-------------+


Current
-------

1415ca473493d747597fcde9427bb410e120e601
++++++++++++++++++++++++++++++++++++++++

(Some small changes and runs with Cython and Python 2.3.3)

pyston 2.3.3

::

   load_combinatorica  1021.00 ms
   test_permutations_1_1  3810.00 ms
   test_permutations_groups_1_2  28219.00 ms
   test_inversions_and_inversion_vectors_1_3  2622.00 ms
   test_special_classes_of_permutations_1_4  1437.00 ms
   test_combinations_1_5  2050.00 ms
   test_2_1_to_2_3  346.00 ms
   test_combinatorica_rest  629.00 ms

Cython

::

   load_combinatorica  1017.00 ms
   test_permutations_1_1  3759.00 ms
   test_permutations_groups_1_2  27951.00 ms
   test_inversions_and_inversion_vectors_1_3  2608.00 ms
   test_special_classes_of_permutations_1_4  1421.00 ms
   test_combinations_1_5  2022.00 ms
   test_2_1_to_2_3  340.00 ms
   test_combinatorica_rest  418.00 ms


5a42af1c7e2addbdf3b887b1b81b7d417fee871a
++++++++++++++++++++++++++++++++++++++++

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


443c4223e0644ff7e68cf8aa3d858a692196004c
++++++++++++++++++++++++++++++++++++++++

::
    load_combinatorica  1139.00 ms
    test_permutations_1_1  4075.00 ms
    test_permutations_groups_1_2  29727.00 ms
    test_inversions_and_inversion_vectors_1_3  2750.00 ms
    test_special_classes_of_permutations_1_4  1557.00 ms
    test_combinations_1_5  2270.00 ms
    test_2_1_to_2_3  364.00 ms
    test_combinatorica_rest  469.00 ms



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


Specific Expressions
---------------------

F[a,a,a,a,a,a,a]
++++++++++++++++

::

    Timing[Do[F[a,a,a,a,a,a,a,a,a,a,a];,{1000}]][[1]]


4.1.0:

::
    Out[1]= 0.297307
    Out[2]= 0.299373
    Out[3]= 0.308271
    Out[4]= 0.307523

    Out[1]  0.0912786 # using Pyston at 1415ca473493d747597fcde9427bb410e120e601

4.0.0:

::

    Out[1]= 0.112872
    Out[2]= 0.11084

Do[1;,{1000}]
+++++++++++++

::

    Timing[Do[1;,{1000}]][[1]]

4.1.0

::
    Out[1]= 0.115065
    Out[2]= 0.114487
    Out[3]= 0.112977

    Out[1]= 0.0912786  Pyston
    Out[1]= 0.11       Cython

4.0.0

::
    Out[1]= 0.297194
    Out[2]= 0.302619
    Out[3]= 0.296671
    Out[4]= 0.294125
