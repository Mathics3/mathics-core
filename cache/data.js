window.BENCHMARK_DATA = {
  "lastUpdate": 1787784963167,
  "repoUrl": "https://github.com/Mathics3/mathics-core",
  "entries": {
    "Mathics3 Core Benchmarks": [
      {
        "commit": {
          "author": {
            "email": "matera@fisica.unlp.edu.ar",
            "name": "Juan Mauricio Matera",
            "username": "mmatera"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a9f9f6e4da9ab4ee6978cf2f811a7d67024fc81e",
          "message": "Update benchmark.yml",
          "timestamp": "2026-08-26T19:52:25-03:00",
          "tree_id": "fe7eec415a018c92672494bb33deda7360552314",
          "url": "https://github.com/Mathics3/mathics-core/commit/a9f9f6e4da9ab4ee6978cf2f811a7d67024fc81e"
        },
        "date": 1787784962024,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=3]",
            "value": 1258.459047090621,
            "unit": "iter/sec",
            "range": "stddev: 0.00019985362178550587",
            "extra": "mean: 794.6226000058232 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=5]",
            "value": 1107.1774327172782,
            "unit": "iter/sec",
            "range": "stddev: 0.000045518877481720674",
            "extra": "mean: 903.1975999960196 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=7]",
            "value": 839.9453833853439,
            "unit": "iter/sec",
            "range": "stddev: 0.00019890348849199672",
            "extra": "mean: 1.1905536000085704 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=9]",
            "value": 666.6081829114668,
            "unit": "iter/sec",
            "range": "stddev: 0.00014731801815756507",
            "extra": "mean: 1.5001315999938925 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=11]",
            "value": 558.7259528527621,
            "unit": "iter/sec",
            "range": "stddev: 0.00018920185704278335",
            "extra": "mean: 1.7897862000040732 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=4]",
            "value": 1863.9328984214205,
            "unit": "iter/sec",
            "range": "stddev: 0.00003584355723769143",
            "extra": "mean: 536.4999999983411 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=6]",
            "value": 1834.85834523349,
            "unit": "iter/sec",
            "range": "stddev: 0.00002868580595929769",
            "extra": "mean: 545.0012000096649 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=8]",
            "value": 1882.228226917277,
            "unit": "iter/sec",
            "range": "stddev: 0.00001890589902222772",
            "extra": "mean: 531.2852000088242 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=10]",
            "value": 1817.9319351540428,
            "unit": "iter/sec",
            "range": "stddev: 0.000034399401982942966",
            "extra": "mean: 550.0756000060392 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=3]",
            "value": 650.620344810033,
            "unit": "iter/sec",
            "range": "stddev: 0.00007517927565841064",
            "extra": "mean: 1.5369946666699736 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=4]",
            "value": 158.93187607618853,
            "unit": "iter/sec",
            "range": "stddev: 0.0002626697925314476",
            "extra": "mean: 6.29200400000703 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=5]",
            "value": 22.13372715431325,
            "unit": "iter/sec",
            "range": "stddev: 0.001708999033229482",
            "extra": "mean: 45.17991900000121 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=6]",
            "value": 2.844642819298861,
            "unit": "iter/sec",
            "range": "stddev: 0.006460385166463703",
            "extra": "mean: 351.5379833333441 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_leading_blanks_benchmark",
            "value": 27.398352717605135,
            "unit": "iter/sec",
            "range": "stddev: 0.06792347656503267",
            "extra": "mean: 36.49854465000146 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3000, b___}]-System`True]",
            "value": 0.9067955636540441,
            "unit": "iter/sec",
            "range": "stddev: 0.00884439132950846",
            "extra": "mean: 1.1027843982500058 sec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3001, b___}]-System`False]",
            "value": 415.471761227787,
            "unit": "iter/sec",
            "range": "stddev: 0.000053909128526278685",
            "extra": "mean: 2.4069024499880243 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_functionapplyrule_hot_path_benchmark",
            "value": 2.7227830525741092,
            "unit": "iter/sec",
            "range": "stddev: 0.004212473563783042",
            "extra": "mean: 367.27127380002 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_strip_context_call_cost_benchmark",
            "value": 666100.2635764186,
            "unit": "iter/sec",
            "range": "stddev: 3.132477557241667e-7",
            "extra": "mean: 1.5012754906157977 usec\nrounds: 144593"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_benchmark",
            "value": 1441.0012999315704,
            "unit": "iter/sec",
            "range": "stddev: 0.0005594870450283755",
            "extra": "mean: 693.9618999979302 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_pattern_precedence_repeated_access_benchmark",
            "value": 13390.923230227108,
            "unit": "iter/sec",
            "range": "stddev: 0.000005178030994405317",
            "extra": "mean: 74.67745000155901 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=10]",
            "value": 6813.4700442236035,
            "unit": "iter/sec",
            "range": "stddev: 0.00000871082684711121",
            "extra": "mean: 146.76809225099487 usec\nrounds: 4607"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=100]",
            "value": 705.7281774903446,
            "unit": "iter/sec",
            "range": "stddev: 0.00010741637968753998",
            "extra": "mean: 1.4169761558283274 msec\nrounds: 738"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=1000]",
            "value": 71.19665641406279,
            "unit": "iter/sec",
            "range": "stddev: 0.00019661587929467624",
            "extra": "mean: 14.045603408455564 msec\nrounds: 71"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=5000]",
            "value": 13.900610475706696,
            "unit": "iter/sec",
            "range": "stddev: 0.00035584172387763895",
            "extra": "mean: 71.93928653332478 msec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=10]",
            "value": 6598.782759808886,
            "unit": "iter/sec",
            "range": "stddev: 0.00000710905897412322",
            "extra": "mean: 151.5431006595165 usec\nrounds: 4401"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=100]",
            "value": 706.220833906621,
            "unit": "iter/sec",
            "range": "stddev: 0.00004099388969949503",
            "extra": "mean: 1.4159876797577222 msec\nrounds: 662"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=1000]",
            "value": 71.84744426939608,
            "unit": "iter/sec",
            "range": "stddev: 0.0002541353532280717",
            "extra": "mean: 13.918379563376579 msec\nrounds: 71"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=5000]",
            "value": 14.128373133545086,
            "unit": "iter/sec",
            "range": "stddev: 0.0004322678458037149",
            "extra": "mean: 70.77955759999668 msec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=10]",
            "value": 46368.636021659695,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018535088505774804",
            "extra": "mean: 21.56630183240414 usec\nrounds: 22867"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=100]",
            "value": 4720.482351364922,
            "unit": "iter/sec",
            "range": "stddev: 0.000009812319091893315",
            "extra": "mean: 211.8427579145278 usec\nrounds: 4296"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=1000]",
            "value": 473.30689147752634,
            "unit": "iter/sec",
            "range": "stddev: 0.000035883827928103234",
            "extra": "mean: 2.1127940835137453 msec\nrounds: 467"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=5000]",
            "value": 94.63825248846045,
            "unit": "iter/sec",
            "range": "stddev: 0.0002888122168081705",
            "extra": "mean: 10.566551829789264 msec\nrounds: 94"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=10]",
            "value": 38151.14885512895,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020336209004824906",
            "extra": "mean: 26.21153045213113 usec\nrounds: 23693"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=100]",
            "value": 3835.121874007075,
            "unit": "iter/sec",
            "range": "stddev: 0.000008564685639367955",
            "extra": "mean: 260.74790654701246 usec\nrounds: 3574"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=1000]",
            "value": 388.31491825482135,
            "unit": "iter/sec",
            "range": "stddev: 0.00005205294631200678",
            "extra": "mean: 2.575229415584226 msec\nrounds: 385"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=5000]",
            "value": 79.08236265449071,
            "unit": "iter/sec",
            "range": "stddev: 0.00021154192230674477",
            "extra": "mean: 12.645044564095542 msec\nrounds: 78"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=10]",
            "value": 62524.93076978792,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014924219497443067",
            "extra": "mean: 15.993620267760468 usec\nrounds: 35870"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=100]",
            "value": 6290.318896825617,
            "unit": "iter/sec",
            "range": "stddev: 0.00001971167083385813",
            "extra": "mean: 158.9744520750205 usec\nrounds: 6145"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=1000]",
            "value": 659.9499976192731,
            "unit": "iter/sec",
            "range": "stddev: 0.00005779845466023601",
            "extra": "mean: 1.5152663135198656 msec\nrounds: 673"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=5000]",
            "value": 131.43970038382798,
            "unit": "iter/sec",
            "range": "stddev: 0.00017582456581270533",
            "extra": "mean: 7.6080514264702135 msec\nrounds: 136"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=4]",
            "value": 1752.680637435334,
            "unit": "iter/sec",
            "range": "stddev: 0.00003431889721054904",
            "extra": "mean: 570.5545999887818 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=6]",
            "value": 1416.074971545377,
            "unit": "iter/sec",
            "range": "stddev: 0.0003944623929372111",
            "extra": "mean: 706.1772999975346 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=8]",
            "value": 1668.3522585762294,
            "unit": "iter/sec",
            "range": "stddev: 0.0001183872357918619",
            "extra": "mean: 599.3937999960508 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=10]",
            "value": 1799.6752665873119,
            "unit": "iter/sec",
            "range": "stddev: 0.00002589187046016107",
            "extra": "mean: 555.6558000023415 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=12]",
            "value": 1687.1557674896126,
            "unit": "iter/sec",
            "range": "stddev: 0.00012581302100062548",
            "extra": "mean: 592.7135000035832 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=4]",
            "value": 1525.4918071052107,
            "unit": "iter/sec",
            "range": "stddev: 0.000012299804055697864",
            "extra": "mean: 655.5263000052491 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=6]",
            "value": 1279.1031133639672,
            "unit": "iter/sec",
            "range": "stddev: 0.00007440007371289518",
            "extra": "mean: 781.7977999991399 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=8]",
            "value": 1155.7122290303976,
            "unit": "iter/sec",
            "range": "stddev: 0.00012133692859107333",
            "extra": "mean: 865.2673000085542 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=10]",
            "value": 1039.4512279550609,
            "unit": "iter/sec",
            "range": "stddev: 0.0001178817304366131",
            "extra": "mean: 962.0461000054092 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=12]",
            "value": 929.2289044859058,
            "unit": "iter/sec",
            "range": "stddev: 0.00015233150370531041",
            "extra": "mean: 1.0761610999963978 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=100]",
            "value": 1841.9907204230913,
            "unit": "iter/sec",
            "range": "stddev: 0.000018254471637399594",
            "extra": "mean: 542.890899998838 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=300]",
            "value": 1363.2456698175847,
            "unit": "iter/sec",
            "range": "stddev: 0.000022618539434690987",
            "extra": "mean: 733.5435000015877 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=1000]",
            "value": 719.9782221028088,
            "unit": "iter/sec",
            "range": "stddev: 0.00005980512468859397",
            "extra": "mean: 1.3889308999921468 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=2000]",
            "value": 414.18689521016154,
            "unit": "iter/sec",
            "range": "stddev: 0.00007286856784191728",
            "extra": "mean: 2.414368999995986 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=100]",
            "value": 507.99717085782805,
            "unit": "iter/sec",
            "range": "stddev: 0.00007588752087836088",
            "extra": "mean: 1.9685149000167714 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=300]",
            "value": 88.0404931330783,
            "unit": "iter/sec",
            "range": "stddev: 0.0006007006838240002",
            "extra": "mean: 11.358409800004665 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=1000]",
            "value": 10.188888108260928,
            "unit": "iter/sec",
            "range": "stddev: 0.004279797157935799",
            "extra": "mean: 98.14613620000614 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=2000]",
            "value": 2.7838022909227185,
            "unit": "iter/sec",
            "range": "stddev: 0.0025054567639866705",
            "extra": "mean: 359.2209128000036 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=100]",
            "value": 350.23090022671965,
            "unit": "iter/sec",
            "range": "stddev: 0.00005057850216251649",
            "extra": "mean: 2.855259200009641 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=300]",
            "value": 61.49606293591921,
            "unit": "iter/sec",
            "range": "stddev: 0.00010345955914982335",
            "extra": "mean: 16.26120360000982 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=1000]",
            "value": 7.38591922434446,
            "unit": "iter/sec",
            "range": "stddev: 0.000621936471582009",
            "extra": "mean: 135.39276150000887 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=2000]",
            "value": 2.0065437734613183,
            "unit": "iter/sec",
            "range": "stddev: 0.0038777867946879277",
            "extra": "mean: 498.36939180000286 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=100]",
            "value": 2148.2143290661634,
            "unit": "iter/sec",
            "range": "stddev: 0.000025462111374891678",
            "extra": "mean: 465.5028999991373 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=300]",
            "value": 1649.8655359558766,
            "unit": "iter/sec",
            "range": "stddev: 0.000020309124238822953",
            "extra": "mean: 606.1100000010811 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=1000]",
            "value": 910.7765080187595,
            "unit": "iter/sec",
            "range": "stddev: 0.000023378927778728178",
            "extra": "mean: 1.0979641999938394 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=2000]",
            "value": 548.0452349975413,
            "unit": "iter/sec",
            "range": "stddev: 0.00018422825342803993",
            "extra": "mean: 1.8246668999950089 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=30]",
            "value": 1155.487345852091,
            "unit": "iter/sec",
            "range": "stddev: 0.00002404993100807893",
            "extra": "mean: 865.4357000011714 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=60]",
            "value": 716.2855836344069,
            "unit": "iter/sec",
            "range": "stddev: 0.0000262172144088278",
            "extra": "mean: 1.3960912000015924 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=100]",
            "value": 410.6370940072679,
            "unit": "iter/sec",
            "range": "stddev: 0.00001808852629045687",
            "extra": "mean: 2.4352402999966216 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=150]",
            "value": 235.56936798314146,
            "unit": "iter/sec",
            "range": "stddev: 0.000025144271213876835",
            "extra": "mean: 4.245034099983513 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=30]",
            "value": 2040.1372522519428,
            "unit": "iter/sec",
            "range": "stddev: 0.000023188706845496775",
            "extra": "mean: 490.16310000524754 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=60]",
            "value": 1938.1091961393472,
            "unit": "iter/sec",
            "range": "stddev: 0.0000075664656281836805",
            "extra": "mean: 515.9668000089823 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=100]",
            "value": 1839.3811880254798,
            "unit": "iter/sec",
            "range": "stddev: 0.000024818273601552264",
            "extra": "mean: 543.6610999993263 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=150]",
            "value": 1726.8520661031835,
            "unit": "iter/sec",
            "range": "stddev: 0.000015707117468054002",
            "extra": "mean: 579.0884000020924 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-present]",
            "value": 1088.7374950862134,
            "unit": "iter/sec",
            "range": "stddev: 0.00005273685078159013",
            "extra": "mean: 918.4950500127798 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-empty]",
            "value": 1055.465002523688,
            "unit": "iter/sec",
            "range": "stddev: 0.00009468800437297144",
            "extra": "mean: 947.4496999985149 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[oneidentity-atom]",
            "value": 1174.6649899522076,
            "unit": "iter/sec",
            "range": "stddev: 0.00003626856627370183",
            "extra": "mean: 851.3065499982986 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-present]",
            "value": 766.3392533298525,
            "unit": "iter/sec",
            "range": "stddev: 0.00015439108823932452",
            "extra": "mean: 1.304905099999587 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient2]",
            "value": 918.2153401434554,
            "unit": "iter/sec",
            "range": "stddev: 0.00005168714481565812",
            "extra": "mean: 1.0890691499923832 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient]",
            "value": 858.8331266251838,
            "unit": "iter/sec",
            "range": "stddev: 0.0000889581113436723",
            "extra": "mean: 1.1643705499920998 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[F[__Real]:=1;-None]",
            "value": 3148.3320923425463,
            "unit": "iter/sec",
            "range": "stddev: 0.000041481199821004535",
            "extra": "mean: 317.62850000234266 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[uniformTable=Table[1./(1.+i^2),{i,0,1000}];-None]",
            "value": 1.1033396983481614,
            "unit": "iter/sec",
            "range": "stddev: 0.041074489335353535",
            "extra": "mean: 906.3391822999989 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[nonuniformTable=Table[If[i==0,1,1./(1.+i^2)],{i, 0,1000}];-None]",
            "value": 0.551566122559866,
            "unit": "iter/sec",
            "range": "stddev: 0.045505914023919444",
            "extra": "mean: 1.813019253899992 sec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@uniformTable-2.075674547634748]",
            "value": 182.81920003833116,
            "unit": "iter/sec",
            "range": "stddev: 0.00012636985506619418",
            "extra": "mean: 5.469884999990882 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[uniformTable,{__Real}]-System`True]",
            "value": 928.1135238799308,
            "unit": "iter/sec",
            "range": "stddev: 0.00011594442794428808",
            "extra": "mean: 1.0774543999957586 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@uniformTable]-0]",
            "value": 422.0168824066656,
            "unit": "iter/sec",
            "range": "stddev: 0.00002316839641324912",
            "extra": "mean: 2.3695734499938226 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@nonuniformTable-2.075674547634748]",
            "value": 184.11987102064882,
            "unit": "iter/sec",
            "range": "stddev: 0.00010148981795431194",
            "extra": "mean: 5.43124430001285 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[nonuniformTable,{__Real}]-System`False]",
            "value": 88.63814457821407,
            "unit": "iter/sec",
            "range": "stddev: 0.00013931293495406555",
            "extra": "mean: 11.281824599990387 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@nonuniformTable]-1001]",
            "value": 77.44386847117907,
            "unit": "iter/sec",
            "range": "stddev: 0.0002262696447582335",
            "extra": "mean: 12.912578099997063 msec\nrounds: 10"
          }
        ]
      }
    ]
  }
}