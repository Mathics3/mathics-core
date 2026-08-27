window.BENCHMARK_DATA = {
  "lastUpdate": 1787830540318,
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
          "id": "11107cf3c2b09a872788c6a3f232a8365f7d949a",
          "message": "Revise Unevaluated[]",
          "timestamp": "2026-08-26T23:05:55Z",
          "url": "https://github.com/Mathics3/mathics-core/pull/1463/commits/11107cf3c2b09a872788c6a3f232a8365f7d949a"
        },
        "date": 1787793200684,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=3]",
            "value": 1488.7860170947229,
            "unit": "iter/sec",
            "range": "stddev: 0.0001308452035583043",
            "extra": "mean: 671.6881999949464 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=5]",
            "value": 1319.791567962028,
            "unit": "iter/sec",
            "range": "stddev: 0.00002086919840474699",
            "extra": "mean: 757.6953999972602 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=7]",
            "value": 993.3532745706831,
            "unit": "iter/sec",
            "range": "stddev: 0.00015459240897988414",
            "extra": "mean: 1.0066911999984995 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=9]",
            "value": 828.7849614672862,
            "unit": "iter/sec",
            "range": "stddev: 0.0001417851666471309",
            "extra": "mean: 1.2065855999964015 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=11]",
            "value": 655.9624096804085,
            "unit": "iter/sec",
            "range": "stddev: 0.00015810020296261142",
            "extra": "mean: 1.5244776000002958 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=4]",
            "value": 2084.4876183443575,
            "unit": "iter/sec",
            "range": "stddev: 0.000016744755120485446",
            "extra": "mean: 479.7342000017579 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=6]",
            "value": 2075.1589364210954,
            "unit": "iter/sec",
            "range": "stddev: 0.000028844170040576617",
            "extra": "mean: 481.8908000004285 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=8]",
            "value": 2123.5290844804613,
            "unit": "iter/sec",
            "range": "stddev: 0.000017837746654726557",
            "extra": "mean: 470.9142000024258 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=10]",
            "value": 2040.2816894516322,
            "unit": "iter/sec",
            "range": "stddev: 0.000032435678508201843",
            "extra": "mean: 490.1283999998896 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=3]",
            "value": 709.0455301757,
            "unit": "iter/sec",
            "range": "stddev: 0.00013862203289746958",
            "extra": "mean: 1.4103466666692082 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=4]",
            "value": 181.22826733279368,
            "unit": "iter/sec",
            "range": "stddev: 0.0001616213814867379",
            "extra": "mean: 5.517902999997659 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=5]",
            "value": 26.07389735356884,
            "unit": "iter/sec",
            "range": "stddev: 0.0014981448856669808",
            "extra": "mean: 38.352532666664274 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=6]",
            "value": 3.248505988002981,
            "unit": "iter/sec",
            "range": "stddev: 0.0018704372126017697",
            "extra": "mean: 307.83381766667145 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_leading_blanks_benchmark",
            "value": 35.42131669963796,
            "unit": "iter/sec",
            "range": "stddev: 0.04253291410121493",
            "extra": "mean: 28.231587450000717 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3000, b___}]-System`True]",
            "value": 1.0186038696427617,
            "unit": "iter/sec",
            "range": "stddev: 0.008724957153457408",
            "extra": "mean: 981.7359130500001 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3001, b___}]-System`False]",
            "value": 468.351290351065,
            "unit": "iter/sec",
            "range": "stddev: 0.0001732508127826809",
            "extra": "mean: 2.1351494500002843 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_functionapplyrule_hot_path_benchmark",
            "value": 3.1024676769777617,
            "unit": "iter/sec",
            "range": "stddev: 0.003304356609408453",
            "extra": "mean: 322.32406719999744 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_strip_context_call_cost_benchmark",
            "value": 757734.9971175097,
            "unit": "iter/sec",
            "range": "stddev: 2.96886252303619e-7",
            "extra": "mean: 1.3197225993310162 usec\nrounds: 189466"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_benchmark",
            "value": 1456.057636588534,
            "unit": "iter/sec",
            "range": "stddev: 0.0004929958461285546",
            "extra": "mean: 686.7859999985626 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_pattern_precedence_repeated_access_benchmark",
            "value": 12937.246591695592,
            "unit": "iter/sec",
            "range": "stddev: 0.000009463574376216733",
            "extra": "mean: 77.2961999999211 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=10]",
            "value": 7644.386015362796,
            "unit": "iter/sec",
            "range": "stddev: 0.00000589139036201033",
            "extra": "mean: 130.81495335142895 usec\nrounds: 4073"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=100]",
            "value": 785.9403487585644,
            "unit": "iter/sec",
            "range": "stddev: 0.000012527751978590962",
            "extra": "mean: 1.272361193288466 msec\nrounds: 745"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=1000]",
            "value": 79.18347198457376,
            "unit": "iter/sec",
            "range": "stddev: 0.00013507608507845872",
            "extra": "mean: 12.628898113924791 msec\nrounds: 79"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=5000]",
            "value": 15.572208767590576,
            "unit": "iter/sec",
            "range": "stddev: 0.0009039125485853565",
            "extra": "mean: 64.21696593749982 msec\nrounds: 16"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=10]",
            "value": 7399.00043134964,
            "unit": "iter/sec",
            "range": "stddev: 0.000016605594559593932",
            "extra": "mean: 135.15339122876514 usec\nrounds: 4606"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=100]",
            "value": 783.0177452265693,
            "unit": "iter/sec",
            "range": "stddev: 0.00001651809868056019",
            "extra": "mean: 1.2771102648646182 msec\nrounds: 740"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=1000]",
            "value": 78.53635216307391,
            "unit": "iter/sec",
            "range": "stddev: 0.00007747215001173897",
            "extra": "mean: 12.732957063292002 msec\nrounds: 79"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=5000]",
            "value": 15.851448797502806,
            "unit": "iter/sec",
            "range": "stddev: 0.00023081424027309718",
            "extra": "mean: 63.08571618750314 msec\nrounds: 16"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=10]",
            "value": 51308.51151114866,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014543069875416825",
            "extra": "mean: 19.489943686686626 usec\nrounds: 27933"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=100]",
            "value": 5242.371757739117,
            "unit": "iter/sec",
            "range": "stddev: 0.000008523873205805023",
            "extra": "mean: 190.7533548195504 usec\nrounds: 4980"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=1000]",
            "value": 524.254216496679,
            "unit": "iter/sec",
            "range": "stddev: 0.000035923496346297845",
            "extra": "mean: 1.9074715444016554 msec\nrounds: 518"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=5000]",
            "value": 105.91267648100995,
            "unit": "iter/sec",
            "range": "stddev: 0.00007095982105983993",
            "extra": "mean: 9.44174043396306 msec\nrounds: 106"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=10]",
            "value": 43275.69443213516,
            "unit": "iter/sec",
            "range": "stddev: 0.000001529238254944969",
            "extra": "mean: 23.107659232787068 usec\nrounds: 28832"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=100]",
            "value": 4320.263207625635,
            "unit": "iter/sec",
            "range": "stddev: 0.0000071096911457537274",
            "extra": "mean: 231.46737870852735 usec\nrounds: 4180"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=1000]",
            "value": 433.3815495741122,
            "unit": "iter/sec",
            "range": "stddev: 0.00003717983318855727",
            "extra": "mean: 2.30743556337991 msec\nrounds: 426"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=5000]",
            "value": 87.70842762881838,
            "unit": "iter/sec",
            "range": "stddev: 0.0000658162359514852",
            "extra": "mean: 11.401412920454973 msec\nrounds: 88"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=10]",
            "value": 63570.10032580737,
            "unit": "iter/sec",
            "range": "stddev: 0.0000053622932785697794",
            "extra": "mean: 15.73066575127038 usec\nrounds: 36775"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=100]",
            "value": 6974.434417670451,
            "unit": "iter/sec",
            "range": "stddev: 0.000004526660568662365",
            "extra": "mean: 143.3808019567001 usec\nrounds: 6746"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=1000]",
            "value": 687.9361406128456,
            "unit": "iter/sec",
            "range": "stddev: 0.00014778578746453845",
            "extra": "mean: 1.45362329577445 msec\nrounds: 710"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=5000]",
            "value": 139.77692479136985,
            "unit": "iter/sec",
            "range": "stddev: 0.000053881836237300476",
            "extra": "mean: 7.154256695034561 msec\nrounds: 141"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=4]",
            "value": 1971.3830099480729,
            "unit": "iter/sec",
            "range": "stddev: 0.00003269357535082131",
            "extra": "mean: 507.25810000074034 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=6]",
            "value": 1615.5529932884122,
            "unit": "iter/sec",
            "range": "stddev: 0.00040016768863210684",
            "extra": "mean: 618.9831000000368 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=8]",
            "value": 1924.8370384804807,
            "unit": "iter/sec",
            "range": "stddev: 0.00010202184091733027",
            "extra": "mean: 519.5245000010118 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=10]",
            "value": 2032.198973420688,
            "unit": "iter/sec",
            "range": "stddev: 0.000019777802980857798",
            "extra": "mean: 492.07779999846935 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=12]",
            "value": 1904.7829480760854,
            "unit": "iter/sec",
            "range": "stddev: 0.0001107005773895252",
            "extra": "mean: 524.9942000006058 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=4]",
            "value": 1730.8680233807067,
            "unit": "iter/sec",
            "range": "stddev: 0.000014109838657042502",
            "extra": "mean: 577.7448000031882 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=6]",
            "value": 1536.5661250463622,
            "unit": "iter/sec",
            "range": "stddev: 0.00001857806356873446",
            "extra": "mean: 650.8018000005222 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=8]",
            "value": 1303.6470307997545,
            "unit": "iter/sec",
            "range": "stddev: 0.0001068584128537411",
            "extra": "mean: 767.0787999927597 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=10]",
            "value": 1172.3407764761887,
            "unit": "iter/sec",
            "range": "stddev: 0.00010819719463373896",
            "extra": "mean: 852.9943000070261 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=12]",
            "value": 1056.6642546590003,
            "unit": "iter/sec",
            "range": "stddev: 0.0001363997596266633",
            "extra": "mean: 946.3743999958751 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=100]",
            "value": 2092.958763499044,
            "unit": "iter/sec",
            "range": "stddev: 0.000020754351753710925",
            "extra": "mean: 477.792499995644 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=300]",
            "value": 1556.2543137123205,
            "unit": "iter/sec",
            "range": "stddev: 0.000016140743232458547",
            "extra": "mean: 642.5685000124304 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=1000]",
            "value": 805.6797846653858,
            "unit": "iter/sec",
            "range": "stddev: 0.000030387126789931407",
            "extra": "mean: 1.2411878999984083 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=2000]",
            "value": 480.11823199515936,
            "unit": "iter/sec",
            "range": "stddev: 0.00002396762316410957",
            "extra": "mean: 2.082820300000776 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=100]",
            "value": 599.1934496642235,
            "unit": "iter/sec",
            "range": "stddev: 0.00003329315150473894",
            "extra": "mean: 1.668910100002563 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=300]",
            "value": 113.31064317912264,
            "unit": "iter/sec",
            "range": "stddev: 0.00007063256806277752",
            "extra": "mean: 8.825296300005903 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=1000]",
            "value": 12.173808092548846,
            "unit": "iter/sec",
            "range": "stddev: 0.00037301159839629716",
            "extra": "mean: 82.14356530000373 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=2000]",
            "value": 3.137322234063359,
            "unit": "iter/sec",
            "range": "stddev: 0.002356055380067824",
            "extra": "mean: 318.7431590999921 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=100]",
            "value": 417.7978369013429,
            "unit": "iter/sec",
            "range": "stddev: 0.000036304085821634565",
            "extra": "mean: 2.39350210000282 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=300]",
            "value": 78.1919646981202,
            "unit": "iter/sec",
            "range": "stddev: 0.00005245127442438013",
            "extra": "mean: 12.789037900003564 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=1000]",
            "value": 8.584320523612341,
            "unit": "iter/sec",
            "range": "stddev: 0.0016037790488133848",
            "extra": "mean: 116.49145639999858 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=2000]",
            "value": 2.243709247931018,
            "unit": "iter/sec",
            "range": "stddev: 0.010148218875464902",
            "extra": "mean: 445.69054610000194 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=100]",
            "value": 2414.876800248666,
            "unit": "iter/sec",
            "range": "stddev: 0.000020213241850750196",
            "extra": "mean: 414.09979999684765 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=300]",
            "value": 1905.4544013269442,
            "unit": "iter/sec",
            "range": "stddev: 0.000014838427721074915",
            "extra": "mean: 524.8092000016413 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=1000]",
            "value": 1075.2120506287617,
            "unit": "iter/sec",
            "range": "stddev: 0.000016446512819736496",
            "extra": "mean: 930.0491000033162 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=2000]",
            "value": 660.9040678561984,
            "unit": "iter/sec",
            "range": "stddev: 0.000018755371151916586",
            "extra": "mean: 1.5130789000039613 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=30]",
            "value": 1320.334551652687,
            "unit": "iter/sec",
            "range": "stddev: 0.00002297207280147043",
            "extra": "mean: 757.3837999984789 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=60]",
            "value": 830.3645034494309,
            "unit": "iter/sec",
            "range": "stddev: 0.00001799547015017952",
            "extra": "mean: 1.204290399994079 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=100]",
            "value": 482.6182852785447,
            "unit": "iter/sec",
            "range": "stddev: 0.00009652555124457837",
            "extra": "mean: 2.072030899995525 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=150]",
            "value": 286.56340583568476,
            "unit": "iter/sec",
            "range": "stddev: 0.000018330704785767418",
            "extra": "mean: 3.4896291000023894 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=30]",
            "value": 2279.032942510329,
            "unit": "iter/sec",
            "range": "stddev: 0.00002058310221697063",
            "extra": "mean: 438.782599999854 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=60]",
            "value": 2169.28303892382,
            "unit": "iter/sec",
            "range": "stddev: 0.000014378576870898173",
            "extra": "mean: 460.9818000034238 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=100]",
            "value": 2098.562337891957,
            "unit": "iter/sec",
            "range": "stddev: 0.000012195621502051837",
            "extra": "mean: 476.51670000163904 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=150]",
            "value": 1900.2097261693261,
            "unit": "iter/sec",
            "range": "stddev: 0.000030419846074468503",
            "extra": "mean: 526.2576999939483 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-present]",
            "value": 1202.296482463603,
            "unit": "iter/sec",
            "range": "stddev: 0.00004855350280574298",
            "extra": "mean: 831.7416000011235 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-empty]",
            "value": 1182.2128044563299,
            "unit": "iter/sec",
            "range": "stddev: 0.00007255175111879633",
            "extra": "mean: 845.8713999971224 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[oneidentity-atom]",
            "value": 1312.9572866092335,
            "unit": "iter/sec",
            "range": "stddev: 0.000034258647067122895",
            "extra": "mean: 761.6394000010018 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-present]",
            "value": 864.0170632973235,
            "unit": "iter/sec",
            "range": "stddev: 0.00013202056885518496",
            "extra": "mean: 1.157384550003826 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient2]",
            "value": 1030.4755412746033,
            "unit": "iter/sec",
            "range": "stddev: 0.00002542585154838398",
            "extra": "mean: 970.4257500018798 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient]",
            "value": 969.3149303709037,
            "unit": "iter/sec",
            "range": "stddev: 0.00006247790369970878",
            "extra": "mean: 1.0316564500016057 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[F[__Real]:=1;-None]",
            "value": 3488.5773511926195,
            "unit": "iter/sec",
            "range": "stddev: 0.00003852108026726051",
            "extra": "mean: 286.64979999888374 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[uniformTable=Table[1./(1.+i^2),{i,0,1000}];-None]",
            "value": 1.2415236012024145,
            "unit": "iter/sec",
            "range": "stddev: 0.025906244131107346",
            "extra": "mean: 805.461933250001 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[nonuniformTable=Table[If[i==0,1,1./(1.+i^2)],{i, 0,1000}];-None]",
            "value": 0.6128233706038224,
            "unit": "iter/sec",
            "range": "stddev: 0.030406175404843555",
            "extra": "mean: 1.6317915536 sec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@uniformTable-2.075674547634748]",
            "value": 205.9796107581378,
            "unit": "iter/sec",
            "range": "stddev: 0.00009345957581376688",
            "extra": "mean: 4.854849449998255 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[uniformTable,{__Real}]-System`True]",
            "value": 988.9830257873544,
            "unit": "iter/sec",
            "range": "stddev: 0.000118320287910051",
            "extra": "mean: 1.0111397000002853 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@uniformTable]-0]",
            "value": 495.57811752004164,
            "unit": "iter/sec",
            "range": "stddev: 0.00003106871342288367",
            "extra": "mean: 2.0178453500008686 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@nonuniformTable-2.075674547634748]",
            "value": 207.5541857302082,
            "unit": "iter/sec",
            "range": "stddev: 0.000037145532188691984",
            "extra": "mean: 4.81801895000018 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[nonuniformTable,{__Real}]-System`False]",
            "value": 98.58728706188181,
            "unit": "iter/sec",
            "range": "stddev: 0.00035663453763822624",
            "extra": "mean: 10.143295649999118 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@nonuniformTable]-1001]",
            "value": 87.15464812713554,
            "unit": "iter/sec",
            "range": "stddev: 0.00009046325734420255",
            "extra": "mean: 11.47385734999773 msec\nrounds: 10"
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
          "id": "90cf764f81335367c1b4e9b7983baa63b7d79833",
          "message": "Pretty print",
          "timestamp": "2026-08-26T23:05:55Z",
          "url": "https://github.com/Mathics3/mathics-core/pull/1162/commits/90cf764f81335367c1b4e9b7983baa63b7d79833"
        },
        "date": 1787793554279,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=3]",
            "value": 1071.1493840131366,
            "unit": "iter/sec",
            "range": "stddev: 0.0001396467741946731",
            "extra": "mean: 933.5765999821888 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=5]",
            "value": 889.6290603133881,
            "unit": "iter/sec",
            "range": "stddev: 0.000032734511022797424",
            "extra": "mean: 1.124063999941427 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=7]",
            "value": 685.8036047821158,
            "unit": "iter/sec",
            "range": "stddev: 0.00018380370732173118",
            "extra": "mean: 1.4581433999865112 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=9]",
            "value": 564.8800940475861,
            "unit": "iter/sec",
            "range": "stddev: 0.00017290232788893625",
            "extra": "mean: 1.770287199951781 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=11]",
            "value": 434.35271281151756,
            "unit": "iter/sec",
            "range": "stddev: 0.00022144598453726307",
            "extra": "mean: 2.302276400041592 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=4]",
            "value": 1487.381649171496,
            "unit": "iter/sec",
            "range": "stddev: 0.00004000321292348555",
            "extra": "mean: 672.3223999415495 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=6]",
            "value": 1529.38966928181,
            "unit": "iter/sec",
            "range": "stddev: 0.000019204690529987426",
            "extra": "mean: 653.8556001032703 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=8]",
            "value": 1520.415839835647,
            "unit": "iter/sec",
            "range": "stddev: 0.00001375654323073455",
            "extra": "mean: 657.7147999905719 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=10]",
            "value": 1493.8911799820655,
            "unit": "iter/sec",
            "range": "stddev: 0.000015393127519610804",
            "extra": "mean: 669.3928000913729 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=3]",
            "value": 500.0072501160698,
            "unit": "iter/sec",
            "range": "stddev: 0.00006599100091333207",
            "extra": "mean: 1.9999709999562278 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=4]",
            "value": 114.95294056605488,
            "unit": "iter/sec",
            "range": "stddev: 0.00019718394612353718",
            "extra": "mean: 8.699211999934656 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=5]",
            "value": 16.49105688336866,
            "unit": "iter/sec",
            "range": "stddev: 0.002548120461168035",
            "extra": "mean: 60.638927333305524 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=6]",
            "value": 2.009063345496612,
            "unit": "iter/sec",
            "range": "stddev: 0.0007365444892242935",
            "extra": "mean: 497.7443853333625 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_leading_blanks_benchmark",
            "value": 24.73869319293795,
            "unit": "iter/sec",
            "range": "stddev: 0.055359696954379846",
            "extra": "mean: 40.422507050027434 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3000, b___}]-System`True]",
            "value": 0.6704533134771515,
            "unit": "iter/sec",
            "range": "stddev: 0.009384368005040146",
            "extra": "mean: 1.4915281644500056 sec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3001, b___}]-System`False]",
            "value": 304.71032803850466,
            "unit": "iter/sec",
            "range": "stddev: 0.000024038523929241808",
            "extra": "mean: 3.2818054000244956 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_functionapplyrule_hot_path_benchmark",
            "value": 2.149976650479764,
            "unit": "iter/sec",
            "range": "stddev: 0.006105446027465843",
            "extra": "mean: 465.12133039996115 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_strip_context_call_cost_benchmark",
            "value": 532281.2012560499,
            "unit": "iter/sec",
            "range": "stddev: 5.114884637233973e-7",
            "extra": "mean: 1.878706213257675 usec\nrounds: 148744"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_benchmark",
            "value": 1228.2936710266297,
            "unit": "iter/sec",
            "range": "stddev: 0.0003723826104661892",
            "extra": "mean: 814.1375499917558 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_pattern_precedence_repeated_access_benchmark",
            "value": 10212.439158397767,
            "unit": "iter/sec",
            "range": "stddev: 0.00000406485179233441",
            "extra": "mean: 97.91980000954936 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=10]",
            "value": 4840.1122388022695,
            "unit": "iter/sec",
            "range": "stddev: 0.000009149153798856202",
            "extra": "mean: 206.60677907078025 usec\nrounds: 3612"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=100]",
            "value": 512.3374918187573,
            "unit": "iter/sec",
            "range": "stddev: 0.00003728734139466469",
            "extra": "mean: 1.9518384189493525 msec\nrounds: 475"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=1000]",
            "value": 50.881604133700314,
            "unit": "iter/sec",
            "range": "stddev: 0.00019704314389202258",
            "extra": "mean: 19.653468419987803 msec\nrounds: 50"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=5000]",
            "value": 10.33860924655988,
            "unit": "iter/sec",
            "range": "stddev: 0.0019397741571019439",
            "extra": "mean: 96.72480854547675 msec\nrounds: 11"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=10]",
            "value": 4871.208366170652,
            "unit": "iter/sec",
            "range": "stddev: 0.00000893435656554904",
            "extra": "mean: 205.2878720903739 usec\nrounds: 3268"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=100]",
            "value": 521.3848985123985,
            "unit": "iter/sec",
            "range": "stddev: 0.00004062416866103663",
            "extra": "mean: 1.9179688611104257 msec\nrounds: 468"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=1000]",
            "value": 51.029987012576335,
            "unit": "iter/sec",
            "range": "stddev: 0.00033107862848192655",
            "extra": "mean: 19.596320879986706 msec\nrounds: 50"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=5000]",
            "value": 10.268729342221524,
            "unit": "iter/sec",
            "range": "stddev: 0.001743346486800647",
            "extra": "mean: 97.38303218182409 msec\nrounds: 11"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=10]",
            "value": 35216.30123261743,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021288769354389125",
            "extra": "mean: 28.39594065812333 usec\nrounds: 22716"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=100]",
            "value": 3571.3972494512795,
            "unit": "iter/sec",
            "range": "stddev: 0.000012633467695616882",
            "extra": "mean: 280.00245566455624 usec\nrounds: 3406"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=1000]",
            "value": 359.27274870452254,
            "unit": "iter/sec",
            "range": "stddev: 0.00003640533452299025",
            "extra": "mean: 2.783400643677631 msec\nrounds: 348"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=5000]",
            "value": 71.98327913165022,
            "unit": "iter/sec",
            "range": "stddev: 0.00011145081777057395",
            "extra": "mean: 13.892115114276748 msec\nrounds: 70"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=10]",
            "value": 28929.49885754414,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024986526920165894",
            "extra": "mean: 34.56679304830831 usec\nrounds: 21121"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=100]",
            "value": 2904.5470394311287,
            "unit": "iter/sec",
            "range": "stddev: 0.000011880596371962154",
            "extra": "mean: 344.2877620587117 usec\nrounds: 2757"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=1000]",
            "value": 297.1930205417035,
            "unit": "iter/sec",
            "range": "stddev: 0.0000347083854350222",
            "extra": "mean: 3.3648165699761963 msec\nrounds: 293"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=5000]",
            "value": 59.82028353734435,
            "unit": "iter/sec",
            "range": "stddev: 0.0010331251205664168",
            "extra": "mean: 16.71673788332555 msec\nrounds: 60"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=10]",
            "value": 47900.884614175,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018751024460420633",
            "extra": "mean: 20.876441177540936 usec\nrounds: 27175"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=100]",
            "value": 4912.19859526488,
            "unit": "iter/sec",
            "range": "stddev: 0.000005891151365984571",
            "extra": "mean: 203.57483123014433 usec\nrounds: 4598"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=1000]",
            "value": 491.8468671731425,
            "unit": "iter/sec",
            "range": "stddev: 0.000024375636268344293",
            "extra": "mean: 2.0331531351362147 msec\nrounds: 481"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=5000]",
            "value": 97.98101165784908,
            "unit": "iter/sec",
            "range": "stddev: 0.000048407348068649",
            "extra": "mean: 10.206059144316784 msec\nrounds: 97"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=4]",
            "value": 1348.1049688038672,
            "unit": "iter/sec",
            "range": "stddev: 0.0000379740827160712",
            "extra": "mean: 741.7820000227948 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=6]",
            "value": 57.27288459101047,
            "unit": "iter/sec",
            "range": "stddev: 0.052829514048921916",
            "extra": "mean: 17.460269499974856 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=8]",
            "value": 1298.662507452802,
            "unit": "iter/sec",
            "range": "stddev: 0.00010397065279629633",
            "extra": "mean: 770.0230000182273 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=10]",
            "value": 1391.159957486857,
            "unit": "iter/sec",
            "range": "stddev: 0.000017166975558641348",
            "extra": "mean: 718.8246000168874 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=12]",
            "value": 1299.1138095064414,
            "unit": "iter/sec",
            "range": "stddev: 0.00011174985343379902",
            "extra": "mean: 769.755500004976 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=4]",
            "value": 1101.0332315894289,
            "unit": "iter/sec",
            "range": "stddev: 0.00011387646617462781",
            "extra": "mean: 908.237800013012 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=6]",
            "value": 766.8776935092071,
            "unit": "iter/sec",
            "range": "stddev: 0.00039340122714096834",
            "extra": "mean: 1.303988900008335 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=8]",
            "value": 855.1391683410718,
            "unit": "iter/sec",
            "range": "stddev: 0.00013283350346074343",
            "extra": "mean: 1.169400300000234 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=10]",
            "value": 750.0384957286614,
            "unit": "iter/sec",
            "range": "stddev: 0.0001400139217057392",
            "extra": "mean: 1.3332648999949015 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=12]",
            "value": 697.8922259114946,
            "unit": "iter/sec",
            "range": "stddev: 0.00010709230434587356",
            "extra": "mean: 1.432885999975042 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=100]",
            "value": 1440.3120291887794,
            "unit": "iter/sec",
            "range": "stddev: 0.000019029640969470748",
            "extra": "mean: 694.2940000044473 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=300]",
            "value": 1030.5981499157544,
            "unit": "iter/sec",
            "range": "stddev: 0.000013277216999397663",
            "extra": "mean: 970.3102999765179 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=1000]",
            "value": 522.326425186307,
            "unit": "iter/sec",
            "range": "stddev: 0.000021947639228805754",
            "extra": "mean: 1.914511599989055 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=2000]",
            "value": 310.95867502830424,
            "unit": "iter/sec",
            "range": "stddev: 0.000042668428683861946",
            "extra": "mean: 3.2158613999399677 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=100]",
            "value": 373.2911663659443,
            "unit": "iter/sec",
            "range": "stddev: 0.00002007018566392978",
            "extra": "mean: 2.678873999980169 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=300]",
            "value": 67.22178144895754,
            "unit": "iter/sec",
            "range": "stddev: 0.00012307815341901565",
            "extra": "mean: 14.876130600009674 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=1000]",
            "value": 7.5229727684098995,
            "unit": "iter/sec",
            "range": "stddev: 0.0006323454341728561",
            "extra": "mean: 132.92617570000402 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=2000]",
            "value": 2.0847672870897087,
            "unit": "iter/sec",
            "range": "stddev: 0.003059402222316694",
            "extra": "mean: 479.6698442999741 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=100]",
            "value": 262.6952607298852,
            "unit": "iter/sec",
            "range": "stddev: 0.0000655382649982556",
            "extra": "mean: 3.8066922000098202 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=300]",
            "value": 47.49645858100445,
            "unit": "iter/sec",
            "range": "stddev: 0.0002173858393236407",
            "extra": "mean: 21.054201299966735 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=1000]",
            "value": 5.621736062907763,
            "unit": "iter/sec",
            "range": "stddev: 0.0008979337441516396",
            "extra": "mean: 177.88099419999526 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=2000]",
            "value": 1.5198605088682142,
            "unit": "iter/sec",
            "range": "stddev: 0.003711616197959547",
            "extra": "mean: 657.9551177000212 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=100]",
            "value": 1640.2173419631483,
            "unit": "iter/sec",
            "range": "stddev: 0.00003107408164181056",
            "extra": "mean: 609.6752999837918 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=300]",
            "value": 1256.7204698396897,
            "unit": "iter/sec",
            "range": "stddev: 0.00001666940692797309",
            "extra": "mean: 795.7218999763427 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=1000]",
            "value": 684.8329096823023,
            "unit": "iter/sec",
            "range": "stddev: 0.000038263707741485334",
            "extra": "mean: 1.4602101999798833 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=2000]",
            "value": 428.22242729143136,
            "unit": "iter/sec",
            "range": "stddev: 0.000018368602447607362",
            "extra": "mean: 2.335235000009561 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=30]",
            "value": 859.9114033030986,
            "unit": "iter/sec",
            "range": "stddev: 0.000024883840911586914",
            "extra": "mean: 1.1629105000338313 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=60]",
            "value": 523.889299664117,
            "unit": "iter/sec",
            "range": "stddev: 0.000016924891407931474",
            "extra": "mean: 1.9088002000444249 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=100]",
            "value": 302.1913648544599,
            "unit": "iter/sec",
            "range": "stddev: 0.000024177791872838412",
            "extra": "mean: 3.3091614000340996 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=150]",
            "value": 170.9483939960532,
            "unit": "iter/sec",
            "range": "stddev: 0.00012304789067537868",
            "extra": "mean: 5.849718600006781 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=30]",
            "value": 1508.2150968151868,
            "unit": "iter/sec",
            "range": "stddev: 0.00004034819631581197",
            "extra": "mean: 663.0353999980798 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=60]",
            "value": 1479.3186080460405,
            "unit": "iter/sec",
            "range": "stddev: 0.000016884617614767735",
            "extra": "mean: 675.9869000234175 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=100]",
            "value": 1384.3455436791728,
            "unit": "iter/sec",
            "range": "stddev: 0.000017893319923863104",
            "extra": "mean: 722.3630000225967 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=150]",
            "value": 1309.2319442732248,
            "unit": "iter/sec",
            "range": "stddev: 0.000014469913999211636",
            "extra": "mean: 763.8066000254184 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-present]",
            "value": 823.7499296208722,
            "unit": "iter/sec",
            "range": "stddev: 0.00004879067671905067",
            "extra": "mean: 1.21396064999999 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-empty]",
            "value": 798.6132559810317,
            "unit": "iter/sec",
            "range": "stddev: 0.00008945013295975611",
            "extra": "mean: 1.2521705500262215 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[oneidentity-atom]",
            "value": 892.7900241609082,
            "unit": "iter/sec",
            "range": "stddev: 0.00003189004018672009",
            "extra": "mean: 1.12008420002212 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-present]",
            "value": 579.1773018226484,
            "unit": "iter/sec",
            "range": "stddev: 0.00018196855837503297",
            "extra": "mean: 1.72658699996191 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient2]",
            "value": 687.8579182709212,
            "unit": "iter/sec",
            "range": "stddev: 0.000038466677331458005",
            "extra": "mean: 1.4537885999970968 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient]",
            "value": 654.1500291720523,
            "unit": "iter/sec",
            "range": "stddev: 0.00008205862489229536",
            "extra": "mean: 1.5287013000147454 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[F[__Real]:=1;-None]",
            "value": 2358.538404326937,
            "unit": "iter/sec",
            "range": "stddev: 0.00003760109760159334",
            "extra": "mean: 423.99139999815816 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[uniformTable=Table[1./(1.+i^2),{i,0,1000}];-None]",
            "value": 0.8838877911905456,
            "unit": "iter/sec",
            "range": "stddev: 0.03784519073406531",
            "extra": "mean: 1.1313653271000135 sec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[nonuniformTable=Table[If[i==0,1,1./(1.+i^2)],{i, 0,1000}];-None]",
            "value": 0.440210944071278,
            "unit": "iter/sec",
            "range": "stddev: 0.050983469334072745",
            "extra": "mean: 2.2716382076999935 sec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@uniformTable-2.075674547634748]",
            "value": 135.1944398203771,
            "unit": "iter/sec",
            "range": "stddev: 0.00009045592861755487",
            "extra": "mean: 7.396753900002295 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[uniformTable,{__Real}]-System`True]",
            "value": 657.6627160338596,
            "unit": "iter/sec",
            "range": "stddev: 0.0001195450298578684",
            "extra": "mean: 1.52053624999553 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@uniformTable]-0]",
            "value": 316.8836847206561,
            "unit": "iter/sec",
            "range": "stddev: 0.000019505555665841485",
            "extra": "mean: 3.1557320500155583 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@nonuniformTable-2.075674547634748]",
            "value": 134.80046383813365,
            "unit": "iter/sec",
            "range": "stddev: 0.00004518833388496668",
            "extra": "mean: 7.418372099971293 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[nonuniformTable,{__Real}]-System`False]",
            "value": 86.35398977895642,
            "unit": "iter/sec",
            "range": "stddev: 0.00005465936828800034",
            "extra": "mean: 11.580240850014434 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@nonuniformTable]-1001]",
            "value": 71.09972529600608,
            "unit": "iter/sec",
            "range": "stddev: 0.000357143130325304",
            "extra": "mean: 14.064751949979382 msec\nrounds: 10"
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
          "id": "1b403c85af2bac9b96efba1f6f35a3890a476c9f",
          "message": "add check_benchmarks.py.",
          "timestamp": "2026-08-26T23:05:55Z",
          "url": "https://github.com/Mathics3/mathics-core/pull/1911/commits/1b403c85af2bac9b96efba1f6f35a3890a476c9f"
        },
        "date": 1787829856951,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=3]",
            "value": 1220.2172426201319,
            "unit": "iter/sec",
            "range": "stddev: 0.00009895347733614339",
            "extra": "mean: 819.5261999844661 usec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=5]",
            "value": 864.766091438831,
            "unit": "iter/sec",
            "range": "stddev: 0.00014930341212252647",
            "extra": "mean: 1.1563820666651736 msec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=7]",
            "value": 699.7630322469488,
            "unit": "iter/sec",
            "range": "stddev: 0.00015611482101801687",
            "extra": "mean: 1.4290551999996146 msec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=9]",
            "value": 540.3836832195879,
            "unit": "iter/sec",
            "range": "stddev: 0.0005630059195931455",
            "extra": "mean: 1.8505370000108694 msec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=11]",
            "value": 442.90327228904147,
            "unit": "iter/sec",
            "range": "stddev: 0.0001560931799167784",
            "extra": "mean: 2.2578293333253896 msec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=4]",
            "value": 1366.181062209532,
            "unit": "iter/sec",
            "range": "stddev: 0.00018912366316355326",
            "extra": "mean: 731.9673999745646 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=6]",
            "value": 1521.2559001113602,
            "unit": "iter/sec",
            "range": "stddev: 0.000019709501106668415",
            "extra": "mean: 657.3516000344171 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=8]",
            "value": 1495.001611597923,
            "unit": "iter/sec",
            "range": "stddev: 0.000027307666795680887",
            "extra": "mean: 668.8956000061808 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=10]",
            "value": 1514.4140414449998,
            "unit": "iter/sec",
            "range": "stddev: 0.000023730971284428765",
            "extra": "mean: 660.321399982422 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=3]",
            "value": 507.40910315102155,
            "unit": "iter/sec",
            "range": "stddev: 0.00009587078061659822",
            "extra": "mean: 1.9707963333530643 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=4]",
            "value": 116.2644601013306,
            "unit": "iter/sec",
            "range": "stddev: 0.0002942215370895192",
            "extra": "mean: 8.601080666683933 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=5]",
            "value": 17.014170223313425,
            "unit": "iter/sec",
            "range": "stddev: 0.0003625135651840716",
            "extra": "mean: 58.774538333333716 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=6]",
            "value": 1.8208804291916403,
            "unit": "iter/sec",
            "range": "stddev: 0.14736096971197482",
            "extra": "mean: 549.1848800000222 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_leading_blanks_benchmark",
            "value": 35.71803929751625,
            "unit": "iter/sec",
            "range": "stddev: 0.00221301518303304",
            "extra": "mean: 27.997057500004985 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3000, b___}]-System`True]",
            "value": 0.6979750387993772,
            "unit": "iter/sec",
            "range": "stddev: 0.009688585527390204",
            "extra": "mean: 1.4327159918500114 sec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3001, b___}]-System`False]",
            "value": 310.15858858318006,
            "unit": "iter/sec",
            "range": "stddev: 0.00006258337607946997",
            "extra": "mean: 3.2241570500048056 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_functionapplyrule_hot_path_benchmark",
            "value": 2.167707791429069,
            "unit": "iter/sec",
            "range": "stddev: 0.0033517082680065845",
            "extra": "mean: 461.316789999978 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_strip_context_call_cost_benchmark",
            "value": 545294.8875410671,
            "unit": "iter/sec",
            "range": "stddev: 4.6453740336404873e-7",
            "extra": "mean: 1.8338701184406179 usec\nrounds: 143823"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_benchmark",
            "value": 1216.2904099302684,
            "unit": "iter/sec",
            "range": "stddev: 0.0003978314500174551",
            "extra": "mean: 822.1720666673112 usec\nrounds: 30"
          },
          {
            "name": "test/timings/test_patterns.py::test_pattern_precedence_repeated_access_benchmark",
            "value": 10277.547922223835,
            "unit": "iter/sec",
            "range": "stddev: 0.000002999099484299821",
            "extra": "mean: 97.29947333426026 usec\nrounds: 30"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=10]",
            "value": 4805.442974188585,
            "unit": "iter/sec",
            "range": "stddev: 0.000012706211501684447",
            "extra": "mean: 208.0973607160229 usec\nrounds: 3518"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=100]",
            "value": 497.0342714349326,
            "unit": "iter/sec",
            "range": "stddev: 0.00017812131401631393",
            "extra": "mean: 2.0119336984812146 msec\nrounds: 461"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=1000]",
            "value": 49.93521374799041,
            "unit": "iter/sec",
            "range": "stddev: 0.0004449298696435876",
            "extra": "mean: 20.025948122435825 msec\nrounds: 49"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=5000]",
            "value": 10.20015982259361,
            "unit": "iter/sec",
            "range": "stddev: 0.000860777859395051",
            "extra": "mean: 98.03767954546898 msec\nrounds: 11"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=10]",
            "value": 4802.938182073958,
            "unit": "iter/sec",
            "range": "stddev: 0.000013524328017494107",
            "extra": "mean: 208.20588608287892 usec\nrounds: 3643"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=100]",
            "value": 502.93399338041263,
            "unit": "iter/sec",
            "range": "stddev: 0.00003853782379192732",
            "extra": "mean: 1.9883324912651372 msec\nrounds: 458"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=1000]",
            "value": 52.014189083790306,
            "unit": "iter/sec",
            "range": "stddev: 0.00022040506423498952",
            "extra": "mean: 19.225523220002287 msec\nrounds: 50"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=5000]",
            "value": 10.37925710148433,
            "unit": "iter/sec",
            "range": "stddev: 0.0007197016262052559",
            "extra": "mean: 96.34600918181232 msec\nrounds: 11"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=10]",
            "value": 34920.88308960168,
            "unit": "iter/sec",
            "range": "stddev: 0.000002152812756054059",
            "extra": "mean: 28.636160129002235 usec\nrounds: 21976"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=100]",
            "value": 3607.7672298775087,
            "unit": "iter/sec",
            "range": "stddev: 0.000008777238938052275",
            "extra": "mean: 277.179744779142 usec\nrounds: 3209"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=1000]",
            "value": 363.55827485612895,
            "unit": "iter/sec",
            "range": "stddev: 0.00002693805658989076",
            "extra": "mean: 2.750590673244146 msec\nrounds: 355"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=5000]",
            "value": 73.05658243061663,
            "unit": "iter/sec",
            "range": "stddev: 0.00005445879076048148",
            "extra": "mean: 13.688020527783666 msec\nrounds: 72"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=10]",
            "value": 28648.980634492018,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031735423750740924",
            "extra": "mean: 34.90525588879233 usec\nrounds: 20079"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=100]",
            "value": 2845.787181762623,
            "unit": "iter/sec",
            "range": "stddev: 0.00003168094443372059",
            "extra": "mean: 351.39662108556564 usec\nrounds: 2618"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=1000]",
            "value": 292.8783063035813,
            "unit": "iter/sec",
            "range": "stddev: 0.00003231066972553857",
            "extra": "mean: 3.4143874041782247 msec\nrounds: 287"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=5000]",
            "value": 59.44801732006404,
            "unit": "iter/sec",
            "range": "stddev: 0.00012059612330023598",
            "extra": "mean: 16.82141886441845 msec\nrounds: 59"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=10]",
            "value": 48523.053702220044,
            "unit": "iter/sec",
            "range": "stddev: 0.000001828324437762118",
            "extra": "mean: 20.60876065502546 usec\nrounds: 28649"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=100]",
            "value": 4912.6368974838815,
            "unit": "iter/sec",
            "range": "stddev: 0.00000972690064375294",
            "extra": "mean: 203.55666841817123 usec\nrounds: 4376"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=1000]",
            "value": 492.65017050401804,
            "unit": "iter/sec",
            "range": "stddev: 0.00003559077129343308",
            "extra": "mean: 2.0298379253110275 msec\nrounds: 482"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=5000]",
            "value": 98.83187261568679,
            "unit": "iter/sec",
            "range": "stddev: 0.0004265632625640144",
            "extra": "mean: 10.118193387760195 msec\nrounds: 98"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=4]",
            "value": 1345.770223980839,
            "unit": "iter/sec",
            "range": "stddev: 0.00016415597587594608",
            "extra": "mean: 743.0689000102575 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=6]",
            "value": 1326.890307850765,
            "unit": "iter/sec",
            "range": "stddev: 0.0002206979627955994",
            "extra": "mean: 753.6417999915557 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=8]",
            "value": 1397.4769671216516,
            "unit": "iter/sec",
            "range": "stddev: 0.00008278902560071886",
            "extra": "mean: 715.5753000063214 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=10]",
            "value": 1320.126000754883,
            "unit": "iter/sec",
            "range": "stddev: 0.00012461630329880518",
            "extra": "mean: 757.5034499950561 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=12]",
            "value": 1379.4281194475213,
            "unit": "iter/sec",
            "range": "stddev: 0.00008495479679618524",
            "extra": "mean: 724.938100000827 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=4]",
            "value": 1140.5897156847675,
            "unit": "iter/sec",
            "range": "stddev: 0.00007469809487265294",
            "extra": "mean: 876.7394499955117 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=6]",
            "value": 978.9114573141889,
            "unit": "iter/sec",
            "range": "stddev: 0.00010494272409956765",
            "extra": "mean: 1.0215428499975587 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=8]",
            "value": 866.8183078734057,
            "unit": "iter/sec",
            "range": "stddev: 0.00010602198495866574",
            "extra": "mean: 1.1536442999840801 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=10]",
            "value": 782.2966885270918,
            "unit": "iter/sec",
            "range": "stddev: 0.00014590889838723926",
            "extra": "mean: 1.2782873999924504 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=12]",
            "value": 721.6008917911084,
            "unit": "iter/sec",
            "range": "stddev: 0.00002509170759943176",
            "extra": "mean: 1.3858075999849007 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=100]",
            "value": 1454.9416219594818,
            "unit": "iter/sec",
            "range": "stddev: 0.000019891602439014263",
            "extra": "mean: 687.3127999824646 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=300]",
            "value": 1029.969856934296,
            "unit": "iter/sec",
            "range": "stddev: 0.00001002481888846647",
            "extra": "mean: 970.9021999697143 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=1000]",
            "value": 511.0695361745049,
            "unit": "iter/sec",
            "range": "stddev: 0.00002262816290815285",
            "extra": "mean: 1.9566808999911698 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=2000]",
            "value": 307.0317548534618,
            "unit": "iter/sec",
            "range": "stddev: 0.000022144841001363886",
            "extra": "mean: 3.2569920999776514 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=100]",
            "value": 367.61944681891214,
            "unit": "iter/sec",
            "range": "stddev: 0.00009102226048189324",
            "extra": "mean: 2.7202042999988407 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=300]",
            "value": 66.7651167272879,
            "unit": "iter/sec",
            "range": "stddev: 0.0002552265306187211",
            "extra": "mean: 14.977881400022852 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=1000]",
            "value": 7.471227585332694,
            "unit": "iter/sec",
            "range": "stddev: 0.003758844010369432",
            "extra": "mean: 133.8468127999704 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=2000]",
            "value": 2.0770775893188924,
            "unit": "iter/sec",
            "range": "stddev: 0.002692694070652654",
            "extra": "mean: 481.44566440000744 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=100]",
            "value": 261.89459104044636,
            "unit": "iter/sec",
            "range": "stddev: 0.00003937348515420716",
            "extra": "mean: 3.8183301000117353 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=300]",
            "value": 47.43822642774482,
            "unit": "iter/sec",
            "range": "stddev: 0.00007963513913781538",
            "extra": "mean: 21.08004610001899 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=1000]",
            "value": 5.561018851857791,
            "unit": "iter/sec",
            "range": "stddev: 0.0031791306085261913",
            "extra": "mean: 179.82316310003625 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=2000]",
            "value": 1.5192751746464435,
            "unit": "iter/sec",
            "range": "stddev: 0.006269947785298418",
            "extra": "mean: 658.2086094000147 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=100]",
            "value": 1659.8579294310382,
            "unit": "iter/sec",
            "range": "stddev: 0.000024299153559778865",
            "extra": "mean: 602.4612000032903 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=300]",
            "value": 1248.9284194013946,
            "unit": "iter/sec",
            "range": "stddev: 0.000013790200728198405",
            "extra": "mean: 800.6864000094538 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=1000]",
            "value": 678.7743724210434,
            "unit": "iter/sec",
            "range": "stddev: 0.000013223559359493406",
            "extra": "mean: 1.4732435999803783 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=2000]",
            "value": 418.3597511499435,
            "unit": "iter/sec",
            "range": "stddev: 0.000026299196050179146",
            "extra": "mean: 2.3902872999883584 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=30]",
            "value": 875.2751317773442,
            "unit": "iter/sec",
            "range": "stddev: 0.000025748554570492072",
            "extra": "mean: 1.1424979000253188 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=60]",
            "value": 533.3847658458186,
            "unit": "iter/sec",
            "range": "stddev: 0.000019339203432976918",
            "extra": "mean: 1.8748192000089148 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=100]",
            "value": 304.22733618750453,
            "unit": "iter/sec",
            "range": "stddev: 0.000043576010063158515",
            "extra": "mean: 3.2870156000171846 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=150]",
            "value": 171.59980940672457,
            "unit": "iter/sec",
            "range": "stddev: 0.00014630791683784158",
            "extra": "mean: 5.827512300027138 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=30]",
            "value": 1588.7173109694086,
            "unit": "iter/sec",
            "range": "stddev: 0.000019444967016039576",
            "extra": "mean: 629.438599992227 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=60]",
            "value": 1526.3710360660014,
            "unit": "iter/sec",
            "range": "stddev: 0.000011920127381505032",
            "extra": "mean: 655.1487000024281 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=100]",
            "value": 1430.268748944949,
            "unit": "iter/sec",
            "range": "stddev: 0.000014560814576927989",
            "extra": "mean: 699.1692999918087 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=150]",
            "value": 1336.5410317926228,
            "unit": "iter/sec",
            "range": "stddev: 0.000018746815033349892",
            "extra": "mean: 748.2000000095468 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-present]",
            "value": 852.1491051339408,
            "unit": "iter/sec",
            "range": "stddev: 0.00005002975188453599",
            "extra": "mean: 1.1735035499953028 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-empty]",
            "value": 819.3504017993762,
            "unit": "iter/sec",
            "range": "stddev: 0.00008015511072469454",
            "extra": "mean: 1.220479049993628 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[oneidentity-atom]",
            "value": 920.8429156670524,
            "unit": "iter/sec",
            "range": "stddev: 0.00002733685909603428",
            "extra": "mean: 1.085961549995318 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-present]",
            "value": 605.5518874223267,
            "unit": "iter/sec",
            "range": "stddev: 0.00007741582267045533",
            "extra": "mean: 1.6513861500072835 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient2]",
            "value": 700.839262023708,
            "unit": "iter/sec",
            "range": "stddev: 0.00004365986973439054",
            "extra": "mean: 1.4268607000019529 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient]",
            "value": 669.4914743620654,
            "unit": "iter/sec",
            "range": "stddev: 0.00007091674600109798",
            "extra": "mean: 1.4936709999972209 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[F[__Real]:=1;-None]",
            "value": 2567.969003540817,
            "unit": "iter/sec",
            "range": "stddev: 0.000036579613264365095",
            "extra": "mean: 389.4128000069941 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[uniformTable=Table[1./(1.+i^2),{i,0,1000}];-None]",
            "value": 0.8979297803654062,
            "unit": "iter/sec",
            "range": "stddev: 0.040265339354724636",
            "extra": "mean: 1.1136728304000088 sec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[nonuniformTable=Table[If[i==0,1,1./(1.+i^2)],{i, 0,1000}];-None]",
            "value": 0.45285223144787895,
            "unit": "iter/sec",
            "range": "stddev: 0.05048207469894993",
            "extra": "mean: 2.2082258417999983 sec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@uniformTable-2.075674547634748]",
            "value": 136.45504635855184,
            "unit": "iter/sec",
            "range": "stddev: 0.00005989673118350607",
            "extra": "mean: 7.328420800007507 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[uniformTable,{__Real}]-System`True]",
            "value": 650.6786252713382,
            "unit": "iter/sec",
            "range": "stddev: 0.00020760574233684987",
            "extra": "mean: 1.536857000002101 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@uniformTable]-0]",
            "value": 317.7855785673631,
            "unit": "iter/sec",
            "range": "stddev: 0.00002735801195483779",
            "extra": "mean: 3.146775899989507 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@nonuniformTable-2.075674547634748]",
            "value": 135.9136346592407,
            "unit": "iter/sec",
            "range": "stddev: 0.00003067401506380293",
            "extra": "mean: 7.357613550010456 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[nonuniformTable,{__Real}]-System`False]",
            "value": 85.84246678944355,
            "unit": "iter/sec",
            "range": "stddev: 0.0000765794585024509",
            "extra": "mean: 11.649245849991985 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@nonuniformTable]-1001]",
            "value": 71.79721551370415,
            "unit": "iter/sec",
            "range": "stddev: 0.00006841513309746233",
            "extra": "mean: 13.928116750003028 msec\nrounds: 10"
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
          "id": "c3270a81563741129a70d0d0280f61f35b81a539",
          "message": "add check_benchmarks.py.",
          "timestamp": "2026-08-26T23:05:55Z",
          "url": "https://github.com/Mathics3/mathics-core/pull/1911/commits/c3270a81563741129a70d0d0280f61f35b81a539"
        },
        "date": 1787830539742,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=3]",
            "value": 1436.008997842589,
            "unit": "iter/sec",
            "range": "stddev: 0.00008981931952241142",
            "extra": "mean: 696.3744666658537 usec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=5]",
            "value": 1032.2379614026133,
            "unit": "iter/sec",
            "range": "stddev: 0.0001464786903945956",
            "extra": "mean: 968.7688666682941 usec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=7]",
            "value": 804.9114192291369,
            "unit": "iter/sec",
            "range": "stddev: 0.0001585328358400729",
            "extra": "mean: 1.2423727333346808 msec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=9]",
            "value": 611.1162535409741,
            "unit": "iter/sec",
            "range": "stddev: 0.0006089548448570764",
            "extra": "mean: 1.636349866667312 msec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=11]",
            "value": 506.74499547911,
            "unit": "iter/sec",
            "range": "stddev: 0.00015815925560711962",
            "extra": "mean: 1.9733791333341817 msec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=4]",
            "value": 1551.119629172971,
            "unit": "iter/sec",
            "range": "stddev: 0.00018417938583658311",
            "extra": "mean: 644.6955999990678 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=6]",
            "value": 1794.629105803669,
            "unit": "iter/sec",
            "range": "stddev: 0.00001777698287028579",
            "extra": "mean: 557.218199998033 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=8]",
            "value": 1815.5001594142695,
            "unit": "iter/sec",
            "range": "stddev: 0.000017845133757534036",
            "extra": "mean: 550.812399995948 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=10]",
            "value": 1805.2522731727295,
            "unit": "iter/sec",
            "range": "stddev: 0.00003086125895865967",
            "extra": "mean: 553.9392000002863 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=3]",
            "value": 606.0870534951359,
            "unit": "iter/sec",
            "range": "stddev: 0.00009998848051990909",
            "extra": "mean: 1.6499280000014476 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=4]",
            "value": 135.7279115039235,
            "unit": "iter/sec",
            "range": "stddev: 0.00029794937471362427",
            "extra": "mean: 7.3676813333349855 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=5]",
            "value": 19.13829251063194,
            "unit": "iter/sec",
            "range": "stddev: 0.00023503589121721255",
            "extra": "mean: 52.25126533333461 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=6]",
            "value": 1.920150266965988,
            "unit": "iter/sec",
            "range": "stddev: 0.17317092648351232",
            "extra": "mean: 520.7925739999979 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_leading_blanks_benchmark",
            "value": 38.00925948511921,
            "unit": "iter/sec",
            "range": "stddev: 0.002412945740651596",
            "extra": "mean: 26.309378649997228 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3000, b___}]-System`True]",
            "value": 0.7843522528420979,
            "unit": "iter/sec",
            "range": "stddev: 0.025554402546063375",
            "extra": "mean: 1.2749373720499981 sec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3001, b___}]-System`False]",
            "value": 360.07485668197955,
            "unit": "iter/sec",
            "range": "stddev: 0.000035225236812589634",
            "extra": "mean: 2.7772003000009704 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_functionapplyrule_hot_path_benchmark",
            "value": 2.747360581155518,
            "unit": "iter/sec",
            "range": "stddev: 0.0031164456162940573",
            "extra": "mean: 363.98571300000526 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_strip_context_call_cost_benchmark",
            "value": 560451.595791347,
            "unit": "iter/sec",
            "range": "stddev: 4.0682382716124495e-7",
            "extra": "mean: 1.7842754084552461 usec\nrounds: 144509"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_benchmark",
            "value": 1402.2296760620743,
            "unit": "iter/sec",
            "range": "stddev: 0.0004708147920490266",
            "extra": "mean: 713.1499333321282 usec\nrounds: 30"
          },
          {
            "name": "test/timings/test_patterns.py::test_pattern_precedence_repeated_access_benchmark",
            "value": 10019.219534869171,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010319494958922496",
            "extra": "mean: 99.80817333323937 usec\nrounds: 30"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=10]",
            "value": 5662.609139519192,
            "unit": "iter/sec",
            "range": "stddev: 0.000006244106983855105",
            "extra": "mean: 176.59703775438567 usec\nrounds: 4079"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=100]",
            "value": 577.5015567998028,
            "unit": "iter/sec",
            "range": "stddev: 0.00001978466462356893",
            "extra": "mean: 1.7315970636364206 msec\nrounds: 550"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=1000]",
            "value": 57.53807208897247,
            "unit": "iter/sec",
            "range": "stddev: 0.00007472583740064842",
            "extra": "mean: 17.37979677966402 msec\nrounds: 59"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=5000]",
            "value": 11.719229881863425,
            "unit": "iter/sec",
            "range": "stddev: 0.0002594691305833823",
            "extra": "mean: 85.32983908333354 msec\nrounds: 12"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=10]",
            "value": 5758.82684730961,
            "unit": "iter/sec",
            "range": "stddev: 0.000005231867126845092",
            "extra": "mean: 173.64647809599913 usec\nrounds: 4223"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=100]",
            "value": 578.2429297787459,
            "unit": "iter/sec",
            "range": "stddev: 0.000023367259502013975",
            "extra": "mean: 1.7293769599269149 msec\nrounds: 549"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=1000]",
            "value": 58.61772596455529,
            "unit": "iter/sec",
            "range": "stddev: 0.00007832289200155389",
            "extra": "mean: 17.059686017241194 msec\nrounds: 58"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=5000]",
            "value": 11.86841229749097,
            "unit": "iter/sec",
            "range": "stddev: 0.0006503196097276949",
            "extra": "mean: 84.25726836363818 msec\nrounds: 11"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=10]",
            "value": 36024.007177939275,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020593576350520314",
            "extra": "mean: 27.75926606555835 usec\nrounds: 22735"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=100]",
            "value": 3665.912275738426,
            "unit": "iter/sec",
            "range": "stddev: 0.000011572808775920907",
            "extra": "mean: 272.7833959961766 usec\nrounds: 3447"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=1000]",
            "value": 367.22613150809434,
            "unit": "iter/sec",
            "range": "stddev: 0.00003320657689823539",
            "extra": "mean: 2.7231177582414454 msec\nrounds: 364"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=5000]",
            "value": 73.46982845904965,
            "unit": "iter/sec",
            "range": "stddev: 0.00008299386852032774",
            "extra": "mean: 13.611029465753772 msec\nrounds: 73"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=10]",
            "value": 29375.171660397584,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020259155468615606",
            "extra": "mean: 34.042354256202 usec\nrounds: 21428"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=100]",
            "value": 2958.80538200337,
            "unit": "iter/sec",
            "range": "stddev: 0.00000763787722476038",
            "extra": "mean: 337.9742399018189 usec\nrounds: 2847"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=1000]",
            "value": 297.2456253052001,
            "unit": "iter/sec",
            "range": "stddev: 0.00003790949618217547",
            "extra": "mean: 3.3642210847451137 msec\nrounds: 295"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=5000]",
            "value": 60.49859658229659,
            "unit": "iter/sec",
            "range": "stddev: 0.00006404309106311172",
            "extra": "mean: 16.529309049999103 msec\nrounds: 60"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=10]",
            "value": 49710.80450870714,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015270847266699042",
            "extra": "mean: 20.11635116114132 usec\nrounds: 31262"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=100]",
            "value": 5137.868279370083,
            "unit": "iter/sec",
            "range": "stddev: 0.000006187608006820888",
            "extra": "mean: 194.63324974975862 usec\nrounds: 4993"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=1000]",
            "value": 515.1428410601715,
            "unit": "iter/sec",
            "range": "stddev: 0.00001886619224236638",
            "extra": "mean: 1.9412091565554621 msec\nrounds: 511"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=5000]",
            "value": 102.46566494859108,
            "unit": "iter/sec",
            "range": "stddev: 0.000057024669500983754",
            "extra": "mean: 9.759366715686845 msec\nrounds: 102"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=4]",
            "value": 1612.9427689098904,
            "unit": "iter/sec",
            "range": "stddev: 0.00019927418203954966",
            "extra": "mean: 619.9848000036923 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=6]",
            "value": 1595.4547409008455,
            "unit": "iter/sec",
            "range": "stddev: 0.00022554782494531094",
            "extra": "mean: 626.7805499987844 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=8]",
            "value": 1666.4625250032275,
            "unit": "iter/sec",
            "range": "stddev: 0.0000817028223168773",
            "extra": "mean: 600.0735000014856 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=10]",
            "value": 1613.3159224177307,
            "unit": "iter/sec",
            "range": "stddev: 0.00011661534772992356",
            "extra": "mean: 619.8414000039065 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=12]",
            "value": 1654.1670908872586,
            "unit": "iter/sec",
            "range": "stddev: 0.00010213494367661921",
            "extra": "mean: 604.5338500015873 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=4]",
            "value": 1397.4497241297431,
            "unit": "iter/sec",
            "range": "stddev: 0.000074052197602901",
            "extra": "mean: 715.589249998061 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=6]",
            "value": 1189.2912175159827,
            "unit": "iter/sec",
            "range": "stddev: 0.0001157408072910306",
            "extra": "mean: 840.8369500017443 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=8]",
            "value": 1061.9750590880726,
            "unit": "iter/sec",
            "range": "stddev: 0.00010860571266623718",
            "extra": "mean: 941.641700002549 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=10]",
            "value": 954.6342984548085,
            "unit": "iter/sec",
            "range": "stddev: 0.00014452754786764744",
            "extra": "mean: 1.0475215499994306 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=12]",
            "value": 895.8157342852434,
            "unit": "iter/sec",
            "range": "stddev: 0.000019567704655419265",
            "extra": "mean: 1.1163010000018403 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=100]",
            "value": 1678.1409554579386,
            "unit": "iter/sec",
            "range": "stddev: 0.00003152548256106016",
            "extra": "mean: 595.8974999970224 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=300]",
            "value": 1177.3989326735102,
            "unit": "iter/sec",
            "range": "stddev: 0.00003607929663535589",
            "extra": "mean: 849.3297999933702 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=1000]",
            "value": 585.1226823795267,
            "unit": "iter/sec",
            "range": "stddev: 0.000039711592285257914",
            "extra": "mean: 1.7090433000021221 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=2000]",
            "value": 352.7708918851886,
            "unit": "iter/sec",
            "range": "stddev: 0.000028084009556243455",
            "extra": "mean: 2.8347010000061346 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=100]",
            "value": 427.6636635683231,
            "unit": "iter/sec",
            "range": "stddev: 0.000029892714909505365",
            "extra": "mean: 2.3382861000072808 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=300]",
            "value": 76.10340693488071,
            "unit": "iter/sec",
            "range": "stddev: 0.00017569748608593707",
            "extra": "mean: 13.140016200006244 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=1000]",
            "value": 8.605551303457164,
            "unit": "iter/sec",
            "range": "stddev: 0.00038434917150800043",
            "extra": "mean: 116.20405999999832 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=2000]",
            "value": 2.3317456975095343,
            "unit": "iter/sec",
            "range": "stddev: 0.0023341980700257096",
            "extra": "mean: 428.86323369999957 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=100]",
            "value": 300.34132890967504,
            "unit": "iter/sec",
            "range": "stddev: 0.00004789534866173605",
            "extra": "mean: 3.3295451000043386 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=300]",
            "value": 54.138506026489786,
            "unit": "iter/sec",
            "range": "stddev: 0.00009021325130291535",
            "extra": "mean: 18.47114139999917 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=1000]",
            "value": 6.338104059329527,
            "unit": "iter/sec",
            "range": "stddev: 0.0007009825291325674",
            "extra": "mean: 157.77588860000265 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=2000]",
            "value": 1.704839963614991,
            "unit": "iter/sec",
            "range": "stddev: 0.004376379889166994",
            "extra": "mean: 586.565320699998 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=100]",
            "value": 1929.5118450608156,
            "unit": "iter/sec",
            "range": "stddev: 0.00003173490401133765",
            "extra": "mean: 518.2658000052243 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=300]",
            "value": 1459.9748621499448,
            "unit": "iter/sec",
            "range": "stddev: 0.000020368913719223732",
            "extra": "mean: 684.9433000013505 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=1000]",
            "value": 784.2957635815745,
            "unit": "iter/sec",
            "range": "stddev: 0.000029692637109186876",
            "extra": "mean: 1.2750291999964247 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=2000]",
            "value": 487.16078020697864,
            "unit": "iter/sec",
            "range": "stddev: 0.000018611114730738038",
            "extra": "mean: 2.0527103999938845 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=30]",
            "value": 1045.5954917199906,
            "unit": "iter/sec",
            "range": "stddev: 0.00004016898322468952",
            "extra": "mean: 956.392800006256 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=60]",
            "value": 619.6082080971244,
            "unit": "iter/sec",
            "range": "stddev: 0.000017043840066787183",
            "extra": "mean: 1.6139231000039445 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=100]",
            "value": 351.7809738482843,
            "unit": "iter/sec",
            "range": "stddev: 0.000030049027241523896",
            "extra": "mean: 2.8426779000028546 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=150]",
            "value": 196.77498782133725,
            "unit": "iter/sec",
            "range": "stddev: 0.00015356180459674289",
            "extra": "mean: 5.081946699993978 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=30]",
            "value": 1965.8682030796144,
            "unit": "iter/sec",
            "range": "stddev: 0.000023262037811109128",
            "extra": "mean: 508.68110000124034 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=60]",
            "value": 1858.405829731334,
            "unit": "iter/sec",
            "range": "stddev: 0.000018260835487918573",
            "extra": "mean: 538.095600003885 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=100]",
            "value": 1707.6470655560977,
            "unit": "iter/sec",
            "range": "stddev: 0.00001868566579205551",
            "extra": "mean: 585.6010999991668 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=150]",
            "value": 1562.0970277951492,
            "unit": "iter/sec",
            "range": "stddev: 0.000027154832288348488",
            "extra": "mean: 640.1650999947606 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-present]",
            "value": 1034.9489317388704,
            "unit": "iter/sec",
            "range": "stddev: 0.00006105929365740381",
            "extra": "mean: 966.2312499997938 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-empty]",
            "value": 990.0533302101684,
            "unit": "iter/sec",
            "range": "stddev: 0.0000941859584093748",
            "extra": "mean: 1.0100466000025676 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[oneidentity-atom]",
            "value": 1101.4655770474287,
            "unit": "iter/sec",
            "range": "stddev: 0.00003935240434601476",
            "extra": "mean: 907.8813000044761 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-present]",
            "value": 723.656837730513,
            "unit": "iter/sec",
            "range": "stddev: 0.00008203062611051285",
            "extra": "mean: 1.381870449999667 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient2]",
            "value": 857.70454333524,
            "unit": "iter/sec",
            "range": "stddev: 0.000036708271204261226",
            "extra": "mean: 1.165902650009798 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient]",
            "value": 808.64558576298,
            "unit": "iter/sec",
            "range": "stddev: 0.00009186373735912176",
            "extra": "mean: 1.2366356999976347 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[F[__Real]:=1;-None]",
            "value": 3117.604943623723,
            "unit": "iter/sec",
            "range": "stddev: 0.00004806980131996305",
            "extra": "mean: 320.75905000255034 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[uniformTable=Table[1./(1.+i^2),{i,0,1000}];-None]",
            "value": 1.1162188461368763,
            "unit": "iter/sec",
            "range": "stddev: 0.0442867965334982",
            "extra": "mean: 895.8816664499991 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[nonuniformTable=Table[If[i==0,1,1./(1.+i^2)],{i, 0,1000}];-None]",
            "value": 0.5515363742875331,
            "unit": "iter/sec",
            "range": "stddev: 0.04978527042778727",
            "extra": "mean: 1.8131170429000008 sec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@uniformTable-2.075674547634748]",
            "value": 142.40372836888068,
            "unit": "iter/sec",
            "range": "stddev: 0.00009772396711137388",
            "extra": "mean: 7.0222880499983376 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[uniformTable,{__Real}]-System`True]",
            "value": 717.7909953409368,
            "unit": "iter/sec",
            "range": "stddev: 0.00020709576638185402",
            "extra": "mean: 1.393163199999492 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@uniformTable]-0]",
            "value": 347.1095201000053,
            "unit": "iter/sec",
            "range": "stddev: 0.0000443399864214632",
            "extra": "mean: 2.880935099999249 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@nonuniformTable-2.075674547634748]",
            "value": 142.78694573490623,
            "unit": "iter/sec",
            "range": "stddev: 0.00007128416080806282",
            "extra": "mean: 7.003441349999662 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[nonuniformTable,{__Real}]-System`False]",
            "value": 84.78727290804522,
            "unit": "iter/sec",
            "range": "stddev: 0.000047640084443228924",
            "extra": "mean: 11.794222950000233 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@nonuniformTable]-1001]",
            "value": 72.0787695534128,
            "unit": "iter/sec",
            "range": "stddev: 0.00007481961964221925",
            "extra": "mean: 13.873710750000612 msec\nrounds: 10"
          }
        ]
      }
    ]
  }
}