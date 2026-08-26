window.BENCHMARK_DATA = {
  "lastUpdate": 1787785428910,
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
      },
      {
        "commit": {
          "author": {
            "name": "Mathics3",
            "username": "Mathics3"
          },
          "committer": {
            "name": "Mathics3",
            "username": "Mathics3"
          },
          "id": "040a43c5cd8098da214294ef01c64434ab3f2152",
          "message": "Split order and orderless patterns",
          "timestamp": "2026-08-26T22:35:34Z",
          "url": "https://github.com/Mathics3/mathics-core/pull/1910/commits/040a43c5cd8098da214294ef01c64434ab3f2152"
        },
        "date": 1787785428307,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=3]",
            "value": 1091.19510306315,
            "unit": "iter/sec",
            "range": "stddev: 0.0002518246330103603",
            "extra": "mean: 916.4264000020239 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=5]",
            "value": 999.2705325100421,
            "unit": "iter/sec",
            "range": "stddev: 0.00002948766116843941",
            "extra": "mean: 1.0007300000012265 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=7]",
            "value": 763.2533214879398,
            "unit": "iter/sec",
            "range": "stddev: 0.00020989438905752678",
            "extra": "mean: 1.3101809999994884 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=9]",
            "value": 626.1816046871614,
            "unit": "iter/sec",
            "range": "stddev: 0.00019239331389090016",
            "extra": "mean: 1.5969808000022567 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=11]",
            "value": 483.1500455327826,
            "unit": "iter/sec",
            "range": "stddev: 0.00017514431234207111",
            "extra": "mean: 2.069750399996906 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=4]",
            "value": 1536.7214968895535,
            "unit": "iter/sec",
            "range": "stddev: 0.00017398885823595458",
            "extra": "mean: 650.7360000000517 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=6]",
            "value": 1725.3093565936747,
            "unit": "iter/sec",
            "range": "stddev: 0.00001812471847282354",
            "extra": "mean: 579.6062000001712 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=8]",
            "value": 1711.4162071754724,
            "unit": "iter/sec",
            "range": "stddev: 0.000023216897110231834",
            "extra": "mean: 584.3114000015248 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=10]",
            "value": 1504.0968590218868,
            "unit": "iter/sec",
            "range": "stddev: 0.00018549302709039696",
            "extra": "mean: 664.8508000012043 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=3]",
            "value": 545.2456667951554,
            "unit": "iter/sec",
            "range": "stddev: 0.000080280033480662",
            "extra": "mean: 1.8340356666707673 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=4]",
            "value": 123.0116448973999,
            "unit": "iter/sec",
            "range": "stddev: 0.0002877319983781358",
            "extra": "mean: 8.129311666664307 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=5]",
            "value": 17.59904015304421,
            "unit": "iter/sec",
            "range": "stddev: 0.0003061414885040055",
            "extra": "mean: 56.82128066666318 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=6]",
            "value": 2.2066714278152606,
            "unit": "iter/sec",
            "range": "stddev: 0.002034286554752355",
            "extra": "mean: 453.1712276666677 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_leading_blanks_benchmark",
            "value": 36.04902615646769,
            "unit": "iter/sec",
            "range": "stddev: 0.0022390756630021936",
            "extra": "mean: 27.74000039999933 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3000, b___}]-System`True]",
            "value": 52.899956295638006,
            "unit": "iter/sec",
            "range": "stddev: 0.05758657414067146",
            "extra": "mean: 18.903607300001823 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3001, b___}]-System`False]",
            "value": 349.297321198851,
            "unit": "iter/sec",
            "range": "stddev: 0.000026832034590112685",
            "extra": "mean: 2.8628905499985535 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_functionapplyrule_hot_path_benchmark",
            "value": 2.4600393689546873,
            "unit": "iter/sec",
            "range": "stddev: 0.0015817376592464007",
            "extra": "mean: 406.4975595999982 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_strip_context_call_cost_benchmark",
            "value": 543074.0116932406,
            "unit": "iter/sec",
            "range": "stddev: 4.256814369574985e-7",
            "extra": "mean: 1.841369644778468 usec\nrounds: 137156"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_benchmark",
            "value": 1292.9548699292545,
            "unit": "iter/sec",
            "range": "stddev: 0.0005571735532829672",
            "extra": "mean: 773.4221999989188 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_pattern_precedence_repeated_access_benchmark",
            "value": 9686.135314225057,
            "unit": "iter/sec",
            "range": "stddev: 0.00000443841190921531",
            "extra": "mean: 103.24035000124354 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=10]",
            "value": 5034.2664002043375,
            "unit": "iter/sec",
            "range": "stddev: 0.000010103553082117267",
            "extra": "mean: 198.63867354326158 usec\nrounds: 3587"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=100]",
            "value": 515.4297574189527,
            "unit": "iter/sec",
            "range": "stddev: 0.00008575420181084231",
            "extra": "mean: 1.9401285734986737 msec\nrounds: 483"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=1000]",
            "value": 50.2384644565708,
            "unit": "iter/sec",
            "range": "stddev: 0.0007634143135138203",
            "extra": "mean: 19.905066980390316 msec\nrounds: 51"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=5000]",
            "value": 10.237014278520554,
            "unit": "iter/sec",
            "range": "stddev: 0.0002610697033837018",
            "extra": "mean: 97.68473236363593 msec\nrounds: 11"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=10]",
            "value": 5055.3171632464455,
            "unit": "iter/sec",
            "range": "stddev: 0.000005900130470324255",
            "extra": "mean: 197.81152551026403 usec\nrounds: 3528"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=100]",
            "value": 509.98579679084975,
            "unit": "iter/sec",
            "range": "stddev: 0.00002111830875944995",
            "extra": "mean: 1.9608389219712132 msec\nrounds: 487"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=1000]",
            "value": 49.31881182609934,
            "unit": "iter/sec",
            "range": "stddev: 0.0015198942981939495",
            "extra": "mean: 20.276238680000063 msec\nrounds: 50"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=5000]",
            "value": 10.226047324599115,
            "unit": "iter/sec",
            "range": "stddev: 0.00048614112560160604",
            "extra": "mean: 97.78949463635524 msec\nrounds: 11"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=10]",
            "value": 35273.96669252177,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016859971586287025",
            "extra": "mean: 28.349519313120073 usec\nrounds: 21721"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=100]",
            "value": 3600.8293849354945,
            "unit": "iter/sec",
            "range": "stddev: 0.00000661556511803814",
            "extra": "mean: 277.71379676682847 usec\nrounds: 3464"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=1000]",
            "value": 360.75580493571687,
            "unit": "iter/sec",
            "range": "stddev: 0.000020217249387852003",
            "extra": "mean: 2.771958167598135 msec\nrounds: 358"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=5000]",
            "value": 71.38773254642955,
            "unit": "iter/sec",
            "range": "stddev: 0.00017816242642986667",
            "extra": "mean: 14.008009000000309 msec\nrounds: 71"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=10]",
            "value": 27879.218378645473,
            "unit": "iter/sec",
            "range": "stddev: 0.000005585413684402124",
            "extra": "mean: 35.869011333759836 usec\nrounds: 20205"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=100]",
            "value": 2831.2933891132798,
            "unit": "iter/sec",
            "range": "stddev: 0.000008490186308569627",
            "extra": "mean: 353.1954702557991 usec\nrounds: 2656"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=1000]",
            "value": 285.2737935763869,
            "unit": "iter/sec",
            "range": "stddev: 0.000042058020436464996",
            "extra": "mean: 3.5054043607136776 msec\nrounds: 280"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=5000]",
            "value": 57.63905650454175,
            "unit": "iter/sec",
            "range": "stddev: 0.0003206525077112034",
            "extra": "mean: 17.349347137929012 msec\nrounds: 58"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=10]",
            "value": 48935.15251092044,
            "unit": "iter/sec",
            "range": "stddev: 0.0000025934643093433946",
            "extra": "mean: 20.43520758981672 usec\nrounds: 28802"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=100]",
            "value": 4988.23534489116,
            "unit": "iter/sec",
            "range": "stddev: 0.000007378772286219481",
            "extra": "mean: 200.47169607267585 usec\nrounds: 4863"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=1000]",
            "value": 497.7988721584864,
            "unit": "iter/sec",
            "range": "stddev: 0.000135184530108113",
            "extra": "mean: 2.0088434424608854 msec\nrounds: 504"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=5000]",
            "value": 100.06632865963576,
            "unit": "iter/sec",
            "range": "stddev: 0.00016863674124695577",
            "extra": "mean: 9.993371530611324 msec\nrounds: 98"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=4]",
            "value": 1543.6520089707042,
            "unit": "iter/sec",
            "range": "stddev: 0.000038762309593178844",
            "extra": "mean: 647.814399999902 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=6]",
            "value": 1392.8804586826589,
            "unit": "iter/sec",
            "range": "stddev: 0.0003056699181920123",
            "extra": "mean: 717.9366999991998 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=8]",
            "value": 1389.5388843079793,
            "unit": "iter/sec",
            "range": "stddev: 0.0002976265307933366",
            "extra": "mean: 719.6631999960346 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=10]",
            "value": 1595.6745730078794,
            "unit": "iter/sec",
            "range": "stddev: 0.000019293856842918716",
            "extra": "mean: 626.6942000053177 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=12]",
            "value": 1492.9199020062615,
            "unit": "iter/sec",
            "range": "stddev: 0.00011925661770807585",
            "extra": "mean: 669.8283000019956 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=4]",
            "value": 1237.1722251417161,
            "unit": "iter/sec",
            "range": "stddev: 0.00013244818519483274",
            "extra": "mean: 808.2948999970085 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=6]",
            "value": 1155.7911725796944,
            "unit": "iter/sec",
            "range": "stddev: 0.000012204652281049734",
            "extra": "mean: 865.2081999969141 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=8]",
            "value": 976.7468800571829,
            "unit": "iter/sec",
            "range": "stddev: 0.0001321899990284521",
            "extra": "mean: 1.0238066999932016 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=10]",
            "value": 859.077745681351,
            "unit": "iter/sec",
            "range": "stddev: 0.00016026856493471728",
            "extra": "mean: 1.164038999993977 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=12]",
            "value": 803.413801651547,
            "unit": "iter/sec",
            "range": "stddev: 0.00010756323147936823",
            "extra": "mean: 1.244688600002064 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=100]",
            "value": 1373.6614699194276,
            "unit": "iter/sec",
            "range": "stddev: 0.000023534445310005306",
            "extra": "mean: 727.981400001454 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=300]",
            "value": 845.0925139678498,
            "unit": "iter/sec",
            "range": "stddev: 0.00004899096827262981",
            "extra": "mean: 1.183302399999775 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=1000]",
            "value": 379.93752079469857,
            "unit": "iter/sec",
            "range": "stddev: 0.000047639172179735085",
            "extra": "mean: 2.6320116999983156 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=2000]",
            "value": 216.00863775326965,
            "unit": "iter/sec",
            "range": "stddev: 0.0000455961429834547",
            "extra": "mean: 4.629444500002933 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=100]",
            "value": 1420.3171539842629,
            "unit": "iter/sec",
            "range": "stddev: 0.000026615636182780682",
            "extra": "mean: 704.0680999978122 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=300]",
            "value": 857.6971500523772,
            "unit": "iter/sec",
            "range": "stddev: 0.0001567383245405256",
            "extra": "mean: 1.165912700000149 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=1000]",
            "value": 400.1104785054481,
            "unit": "iter/sec",
            "range": "stddev: 0.00009005722002080473",
            "extra": "mean: 2.4993096999992304 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=2000]",
            "value": 230.04749744687,
            "unit": "iter/sec",
            "range": "stddev: 0.00004199203364192832",
            "extra": "mean: 4.346928399996841 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=100]",
            "value": 1425.5551575079044,
            "unit": "iter/sec",
            "range": "stddev: 0.00003156739536748534",
            "extra": "mean: 701.4811000004784 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=300]",
            "value": 939.6646055115981,
            "unit": "iter/sec",
            "range": "stddev: 0.000039255256604974895",
            "extra": "mean: 1.0642095000008567 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=1000]",
            "value": 434.13896936123234,
            "unit": "iter/sec",
            "range": "stddev: 0.000018768232651449857",
            "extra": "mean: 2.3034098999943353 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=2000]",
            "value": 251.40473021502572,
            "unit": "iter/sec",
            "range": "stddev: 0.000029177576411336927",
            "extra": "mean: 3.9776499000026884 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=100]",
            "value": 1899.83608212479,
            "unit": "iter/sec",
            "range": "stddev: 0.00003202718059579833",
            "extra": "mean: 526.3612000049989 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=300]",
            "value": 1397.369758856153,
            "unit": "iter/sec",
            "range": "stddev: 0.000018254350691952367",
            "extra": "mean: 715.6301999970083 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=1000]",
            "value": 760.3879255854952,
            "unit": "iter/sec",
            "range": "stddev: 0.000014695055356808646",
            "extra": "mean: 1.3151182000029848 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=2000]",
            "value": 468.7233120670727,
            "unit": "iter/sec",
            "range": "stddev: 0.00001592970803570179",
            "extra": "mean: 2.1334547999970255 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=30]",
            "value": 1362.4241776789038,
            "unit": "iter/sec",
            "range": "stddev: 0.0000398244142065002",
            "extra": "mean: 733.9858000051436 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=60]",
            "value": 1221.833977685869,
            "unit": "iter/sec",
            "range": "stddev: 0.00002125430251172224",
            "extra": "mean: 818.4418000013238 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=100]",
            "value": 1057.011612544963,
            "unit": "iter/sec",
            "range": "stddev: 0.000018634580686402834",
            "extra": "mean: 946.063399996433 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=150]",
            "value": 874.0600140115589,
            "unit": "iter/sec",
            "range": "stddev: 0.00012476130290197632",
            "extra": "mean: 1.1440861999972185 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=30]",
            "value": 1754.5829707038183,
            "unit": "iter/sec",
            "range": "stddev: 0.000036533601443539",
            "extra": "mean: 569.9360000051001 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=60]",
            "value": 1739.7918582474615,
            "unit": "iter/sec",
            "range": "stddev: 0.00001632945867123442",
            "extra": "mean: 574.7814000045537 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=100]",
            "value": 1626.5415140515092,
            "unit": "iter/sec",
            "range": "stddev: 0.00002305889453021161",
            "extra": "mean: 614.801400001852 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=150]",
            "value": 1493.500732854511,
            "unit": "iter/sec",
            "range": "stddev: 0.000020031993143615823",
            "extra": "mean: 669.5678000028238 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-present]",
            "value": 950.6015168752051,
            "unit": "iter/sec",
            "range": "stddev: 0.00006779346552220333",
            "extra": "mean: 1.0519654999995964 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-empty]",
            "value": 933.946319661892,
            "unit": "iter/sec",
            "range": "stddev: 0.00010548608106237127",
            "extra": "mean: 1.0707253499987246 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[oneidentity-atom]",
            "value": 1034.0674022710982,
            "unit": "iter/sec",
            "range": "stddev: 0.00004824212658591849",
            "extra": "mean: 967.0549500000902 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-present]",
            "value": 680.3736557687162,
            "unit": "iter/sec",
            "range": "stddev: 0.00008305383488431127",
            "extra": "mean: 1.4697806000000924 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient2]",
            "value": 806.8924104165267,
            "unit": "iter/sec",
            "range": "stddev: 0.00003871695450697905",
            "extra": "mean: 1.239322600002879 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient]",
            "value": 728.616826601728,
            "unit": "iter/sec",
            "range": "stddev: 0.00019236095156633935",
            "extra": "mean: 1.3724635000045282 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[F[__Real]:=1;-None]",
            "value": 2881.7310212209636,
            "unit": "iter/sec",
            "range": "stddev: 0.00004848405705714284",
            "extra": "mean: 347.01365000273654 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[uniformTable=Table[1./(1.+i^2),{i,0,1000}];-None]",
            "value": 1.0412212534726966,
            "unit": "iter/sec",
            "range": "stddev: 0.04631195703074962",
            "extra": "mean: 960.4106684000016 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[nonuniformTable=Table[If[i==0,1,1./(1.+i^2)],{i, 0,1000}];-None]",
            "value": 0.5145868106332833,
            "unit": "iter/sec",
            "range": "stddev: 0.052124702641926715",
            "extra": "mean: 1.9433067061500011 sec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@uniformTable-2.075674547634748]",
            "value": 136.79171328381736,
            "unit": "iter/sec",
            "range": "stddev: 0.00034795234993479317",
            "extra": "mean: 7.310384350002153 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[uniformTable,{__Real}]-System`True]",
            "value": 586.47158432327,
            "unit": "iter/sec",
            "range": "stddev: 0.00035448474212497526",
            "extra": "mean: 1.7051124499985804 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@uniformTable]-0]",
            "value": 343.1056925419253,
            "unit": "iter/sec",
            "range": "stddev: 0.000034434606024910636",
            "extra": "mean: 2.914553800000874 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@nonuniformTable-2.075674547634748]",
            "value": 139.66119200377574,
            "unit": "iter/sec",
            "range": "stddev: 0.000055541819558698124",
            "extra": "mean: 7.160185200001479 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[nonuniformTable,{__Real}]-System`False]",
            "value": 81.35552790777804,
            "unit": "iter/sec",
            "range": "stddev: 0.00005670871041924668",
            "extra": "mean: 12.291727750000803 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@nonuniformTable]-1001]",
            "value": 71.41637733720796,
            "unit": "iter/sec",
            "range": "stddev: 0.000049964080283285856",
            "extra": "mean: 14.002390449998359 msec\nrounds: 10"
          }
        ]
      }
    ]
  }
}