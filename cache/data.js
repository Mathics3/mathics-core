window.BENCHMARK_DATA = {
  "lastUpdate": 1787834555482,
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
          "id": "f0b96adf7b771f22bacec654fa7b0a8a1d0fff1b",
          "message": "Just store benchmarks from the branch master (#1913)",
          "timestamp": "2026-08-27T09:39:13-03:00",
          "tree_id": "d09d9f4376c0fe51269b71b4276d497950e5645b",
          "url": "https://github.com/Mathics3/mathics-core/commit/f0b96adf7b771f22bacec654fa7b0a8a1d0fff1b"
        },
        "date": 1787834554645,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=3]",
            "value": 1980.01818448626,
            "unit": "iter/sec",
            "range": "stddev: 0.00007492858937952263",
            "extra": "mean: 505.0458666668571 usec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=5]",
            "value": 1538.3338962066564,
            "unit": "iter/sec",
            "range": "stddev: 0.00010345090673828841",
            "extra": "mean: 650.0539333273991 usec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=7]",
            "value": 1217.1536877297394,
            "unit": "iter/sec",
            "range": "stddev: 0.00012786208340492483",
            "extra": "mean: 821.588933329546 usec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=9]",
            "value": 930.428049004511,
            "unit": "iter/sec",
            "range": "stddev: 0.0003893141185298414",
            "extra": "mean: 1.0747741333356466 msec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_plus_match_benchmark[n=11]",
            "value": 775.9417100184579,
            "unit": "iter/sec",
            "range": "stddev: 0.0001321112603527803",
            "extra": "mean: 1.288756599997972 msec\nrounds: 15"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=4]",
            "value": 2220.0170053440033,
            "unit": "iter/sec",
            "range": "stddev: 0.00013389870333830196",
            "extra": "mean: 450.4469999972116 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=6]",
            "value": 2623.9033395933648,
            "unit": "iter/sec",
            "range": "stddev: 0.000012327784768392095",
            "extra": "mean: 381.11160000084965 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=8]",
            "value": 2596.1712705230293,
            "unit": "iter/sec",
            "range": "stddev: 0.000019933725113476926",
            "extra": "mean: 385.1825999902303 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_blank_sequence_wrapping_benchmark[n=10]",
            "value": 2514.3266331679274,
            "unit": "iter/sec",
            "range": "stddev: 0.00003642065615485576",
            "extra": "mean: 397.7207999980692 usec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=3]",
            "value": 913.4633536663504,
            "unit": "iter/sec",
            "range": "stddev: 0.00007568695550153122",
            "extra": "mean: 1.094734666679642 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=4]",
            "value": 200.26144799606845,
            "unit": "iter/sec",
            "range": "stddev: 0.0003655027414359663",
            "extra": "mean: 4.993472333325144 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=5]",
            "value": 31.124529564406213,
            "unit": "iter/sec",
            "range": "stddev: 0.000199156268152496",
            "extra": "mean: 32.12899966666782 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_exhaustive_failure_benchmark[n=6]",
            "value": 3.1617272894746584,
            "unit": "iter/sec",
            "range": "stddev: 0.09980691267551176",
            "extra": "mean: 316.2828126666663 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_patterns.py::test_leading_blanks_benchmark",
            "value": 63.26881636031557,
            "unit": "iter/sec",
            "range": "stddev: 0.0012726362490331359",
            "extra": "mean: 15.805574649998277 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3000, b___}]-System`True]",
            "value": 1.2181018635634537,
            "unit": "iter/sec",
            "range": "stddev: 0.023174037032565695",
            "extra": "mean: 820.9494049000015 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_backtracking_benchmark[MatchQ[bigList, {a___, 3001, b___}]-System`False]",
            "value": 565.6793779619542,
            "unit": "iter/sec",
            "range": "stddev: 0.00005965187997174017",
            "extra": "mean: 1.7677858500036336 msec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_functionapplyrule_hot_path_benchmark",
            "value": 3.7423930257517,
            "unit": "iter/sec",
            "range": "stddev: 0.0020164533489468975",
            "extra": "mean: 267.2087066000074 msec\nrounds: 5"
          },
          {
            "name": "test/timings/test_patterns.py::test_strip_context_call_cost_benchmark",
            "value": 883116.699743092,
            "unit": "iter/sec",
            "range": "stddev: 3.7342705564264314e-7",
            "extra": "mean: 1.1323531763026455 usec\nrounds: 166390"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_benchmark",
            "value": 1940.142842378534,
            "unit": "iter/sec",
            "range": "stddev: 0.0004180113263434241",
            "extra": "mean: 515.4259666644141 usec\nrounds: 30"
          },
          {
            "name": "test/timings/test_patterns.py::test_pattern_precedence_repeated_access_benchmark",
            "value": 19594.907936562755,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010615990490214716",
            "extra": "mean: 51.03366666673992 usec\nrounds: 30"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=10]",
            "value": 8728.14156188598,
            "unit": "iter/sec",
            "range": "stddev: 0.00001104397403058069",
            "extra": "mean: 114.5719272435723 usec\nrounds: 6240"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=100]",
            "value": 938.5697360744017,
            "unit": "iter/sec",
            "range": "stddev: 0.00003319841777950409",
            "extra": "mean: 1.065450931949428 msec\nrounds: 867"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=1000]",
            "value": 94.94991259180654,
            "unit": "iter/sec",
            "range": "stddev: 0.00009437441649712423",
            "extra": "mean: 10.53186856842133 msec\nrounds: 95"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_benchmark[n=5000]",
            "value": 18.990467070389837,
            "unit": "iter/sec",
            "range": "stddev: 0.0001577601152134147",
            "extra": "mean: 52.657999210520316 msec\nrounds: 19"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=10]",
            "value": 8436.211172407879,
            "unit": "iter/sec",
            "range": "stddev: 0.000017545733053301924",
            "extra": "mean: 118.53662498049799 usec\nrounds: 6301"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=100]",
            "value": 932.6942418134838,
            "unit": "iter/sec",
            "range": "stddev: 0.000025383468157325854",
            "extra": "mean: 1.0721627251130554 msec\nrounds: 884"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=1000]",
            "value": 95.90287802881434,
            "unit": "iter/sec",
            "range": "stddev: 0.00006726851866857923",
            "extra": "mean: 10.42721574736836 msec\nrounds: 95"
          },
          {
            "name": "test/timings/test_patterns.py::test_get_match_candidates_count_benchmark[n=5000]",
            "value": 17.17119642346343,
            "unit": "iter/sec",
            "range": "stddev: 0.0031620398274103743",
            "extra": "mean: 58.2370602105255 msec\nrounds: 19"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=10]",
            "value": 62022.409912876945,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012961719774091625",
            "extra": "mean: 16.123204522441206 usec\nrounds: 31576"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=100]",
            "value": 6382.4595583525015,
            "unit": "iter/sec",
            "range": "stddev: 0.000005031034939990409",
            "extra": "mean: 156.67941032095297 usec\nrounds: 5542"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=1000]",
            "value": 642.4972941298677,
            "unit": "iter/sec",
            "range": "stddev: 0.000038616099660408673",
            "extra": "mean: 1.5564267883093537 msec\nrounds: 633"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[blank-n=5000]",
            "value": 116.20546992652525,
            "unit": "iter/sec",
            "range": "stddev: 0.0004406830780901989",
            "extra": "mean: 8.60544689189143 msec\nrounds: 111"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=10]",
            "value": 47452.813225220816,
            "unit": "iter/sec",
            "range": "stddev: 0.000002154926690243965",
            "extra": "mean: 21.073566181498958 usec\nrounds: 30983"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=100]",
            "value": 4503.108431419729,
            "unit": "iter/sec",
            "range": "stddev: 0.000021857786272912692",
            "extra": "mean: 222.06882539684315 usec\nrounds: 4221"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=1000]",
            "value": 481.31545046303967,
            "unit": "iter/sec",
            "range": "stddev: 0.00013334622258640285",
            "extra": "mean: 2.0776395169487505 msec\nrounds: 472"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[integer-n=5000]",
            "value": 105.36985188355537,
            "unit": "iter/sec",
            "range": "stddev: 0.0005468316155437291",
            "extra": "mean: 9.490380617646723 msec\nrounds: 102"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=10]",
            "value": 85694.19646686221,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010411910445696421",
            "extra": "mean: 11.669401677471802 usec\nrounds: 45305"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=100]",
            "value": 8248.056624453237,
            "unit": "iter/sec",
            "range": "stddev: 0.000013802922245212816",
            "extra": "mean: 121.24068074839265 usec\nrounds: 8285"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=1000]",
            "value": 865.1418466831185,
            "unit": "iter/sec",
            "range": "stddev: 0.00005650009220730731",
            "extra": "mean: 1.1558798176667981 msec\nrounds: 883"
          },
          {
            "name": "test/timings/test_patterns.py::test_does_match_scaling_benchmark[expr-n=5000]",
            "value": 171.91572354429923,
            "unit": "iter/sec",
            "range": "stddev: 0.00030322679087795343",
            "extra": "mean: 5.816803602273879 msec\nrounds: 176"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=4]",
            "value": 2117.242964309575,
            "unit": "iter/sec",
            "range": "stddev: 0.0003593858254193962",
            "extra": "mean: 472.3123500028237 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=6]",
            "value": 2279.6446991204825,
            "unit": "iter/sec",
            "range": "stddev: 0.00022235421278417666",
            "extra": "mean: 438.66485000307875 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=8]",
            "value": 2484.1032914879474,
            "unit": "iter/sec",
            "range": "stddev: 0.00005787653212602699",
            "extra": "mean: 402.55975000178523 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=10]",
            "value": 2408.436947335359,
            "unit": "iter/sec",
            "range": "stddev: 0.00008316683950303124",
            "extra": "mean: 415.2070499941374 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[match-n=12]",
            "value": 2493.162501832391,
            "unit": "iter/sec",
            "range": "stddev: 0.00005542348072310272",
            "extra": "mean: 401.0970000010161 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=4]",
            "value": 2104.02931079146,
            "unit": "iter/sec",
            "range": "stddev: 0.00005447068969630101",
            "extra": "mean: 475.278550004532 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=6]",
            "value": 1809.3459594459798,
            "unit": "iter/sec",
            "range": "stddev: 0.00007878292150177298",
            "extra": "mean: 552.6858999957085 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=8]",
            "value": 1617.6247332140758,
            "unit": "iter/sec",
            "range": "stddev: 0.00008161233527055339",
            "extra": "mean: 618.1903500035446 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=10]",
            "value": 1440.0660356695025,
            "unit": "iter/sec",
            "range": "stddev: 0.00010688145890709931",
            "extra": "mean: 694.4125999993389 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_orderless_repeated_names_scaling_benchmark[fail-n=12]",
            "value": 1371.408196223987,
            "unit": "iter/sec",
            "range": "stddev: 0.000012999097989046046",
            "extra": "mean: 729.1774999984568 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=100]",
            "value": 2587.9709557154006,
            "unit": "iter/sec",
            "range": "stddev: 0.000015043064448642307",
            "extra": "mean: 386.4031000006207 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=300]",
            "value": 1904.5874082706748,
            "unit": "iter/sec",
            "range": "stddev: 0.00001816420956372795",
            "extra": "mean: 525.0481000018681 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=1000]",
            "value": 964.8882008179412,
            "unit": "iter/sec",
            "range": "stddev: 0.000022478764969892305",
            "extra": "mean: 1.0363894999983359 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-first-n=2000]",
            "value": 572.8770993582585,
            "unit": "iter/sec",
            "range": "stddev: 0.00002216841206921303",
            "extra": "mean: 1.7455750999999964 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=100]",
            "value": 690.9165955178429,
            "unit": "iter/sec",
            "range": "stddev: 0.000019400247231750227",
            "extra": "mean: 1.4473527000035347 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=300]",
            "value": 124.7678335748738,
            "unit": "iter/sec",
            "range": "stddev: 0.00011267158915909",
            "extra": "mean: 8.014886300000512 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=1000]",
            "value": 14.03067243898803,
            "unit": "iter/sec",
            "range": "stddev: 0.00023900224696054377",
            "extra": "mean: 71.27242150000086 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-middle-n=2000]",
            "value": 3.7960429071634474,
            "unit": "iter/sec",
            "range": "stddev: 0.0018318368558369043",
            "extra": "mean: 263.4322172999987 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=100]",
            "value": 482.786559049949,
            "unit": "iter/sec",
            "range": "stddev: 0.000022636845285729393",
            "extra": "mean: 2.071308699993324 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=300]",
            "value": 87.21362827369843,
            "unit": "iter/sec",
            "range": "stddev: 0.00006316026386288106",
            "extra": "mean: 11.46609789999502 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=1000]",
            "value": 10.174190784112353,
            "unit": "iter/sec",
            "range": "stddev: 0.00036959399195109075",
            "extra": "mean: 98.28791509999633 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-last-n=2000]",
            "value": 2.705409748858884,
            "unit": "iter/sec",
            "range": "stddev: 0.008696527963750639",
            "extra": "mean: 369.6297761999972 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=100]",
            "value": 2970.7132237486658,
            "unit": "iter/sec",
            "range": "stddev: 0.000025475565242925517",
            "extra": "mean: 336.61949999270746 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=300]",
            "value": 2293.9636411136394,
            "unit": "iter/sec",
            "range": "stddev: 0.000017445575380100444",
            "extra": "mean: 435.9267000040745 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=1000]",
            "value": 1285.728961388317,
            "unit": "iter/sec",
            "range": "stddev: 0.000017302392775199244",
            "extra": "mean: 777.7689000022292 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_blank_sequence_position_scaling_benchmark[literal-absent-n=2000]",
            "value": 783.6012936297171,
            "unit": "iter/sec",
            "range": "stddev: 0.00002523245925588779",
            "extra": "mean: 1.2761592000032351 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=30]",
            "value": 1611.367748281591,
            "unit": "iter/sec",
            "range": "stddev: 0.00001969619444040272",
            "extra": "mean: 620.5907999998317 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=60]",
            "value": 985.8197712473258,
            "unit": "iter/sec",
            "range": "stddev: 0.000012904416136525399",
            "extra": "mean: 1.0143841999990855 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=100]",
            "value": 564.2811923800124,
            "unit": "iter/sec",
            "range": "stddev: 0.000028045174895608677",
            "extra": "mean: 1.7721660999939104 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[match-n=150]",
            "value": 319.4952282106117,
            "unit": "iter/sec",
            "range": "stddev: 0.00007535327495635155",
            "extra": "mean: 3.1299372000034964 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=30]",
            "value": 2896.2882617840737,
            "unit": "iter/sec",
            "range": "stddev: 0.000013250650618427676",
            "extra": "mean: 345.26949999929 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=60]",
            "value": 2767.6711652671365,
            "unit": "iter/sec",
            "range": "stddev: 0.000013774871341944692",
            "extra": "mean: 361.3145999963763 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=100]",
            "value": 2616.139593003909,
            "unit": "iter/sec",
            "range": "stddev: 0.000010397320781817171",
            "extra": "mean: 382.242600002769 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_multiple_blank_sequences_benchmark[fail-n=150]",
            "value": 2454.302724029812,
            "unit": "iter/sec",
            "range": "stddev: 0.000014042240466973413",
            "extra": "mean: 407.44769999605523 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-present]",
            "value": 1523.6351618997905,
            "unit": "iter/sec",
            "range": "stddev: 0.00004785834135653744",
            "extra": "mean: 656.325100001709 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[optional-empty]",
            "value": 1481.0146875912585,
            "unit": "iter/sec",
            "range": "stddev: 0.00007032363441829414",
            "extra": "mean: 675.2127500007532 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[oneidentity-atom]",
            "value": 1653.8884488658973,
            "unit": "iter/sec",
            "range": "stddev: 0.00003095054463003854",
            "extra": "mean: 604.6356999988234 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-present]",
            "value": 1099.7944704107126,
            "unit": "iter/sec",
            "range": "stddev: 0.00005891368608012325",
            "extra": "mean: 909.26079999889 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient2]",
            "value": 1283.2621550652912,
            "unit": "iter/sec",
            "range": "stddev: 0.00003418928807950314",
            "extra": "mean: 779.2639999962603 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_patterns.py::test_one_identity_optional_benchmark[multiple-optionals-insufficient]",
            "value": 1212.196221355784,
            "unit": "iter/sec",
            "range": "stddev: 0.00005859121411430392",
            "extra": "mean: 824.9489499988272 usec\nrounds: 20"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[F[__Real]:=1;-None]",
            "value": 4315.853121204455,
            "unit": "iter/sec",
            "range": "stddev: 0.00003882656194886356",
            "extra": "mean: 231.7038999976262 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[uniformTable=Table[1./(1.+i^2),{i,0,1000}];-None]",
            "value": 1.4731222769465915,
            "unit": "iter/sec",
            "range": "stddev: 0.037652877218365716",
            "extra": "mean: 678.8302747499998 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[nonuniformTable=Table[If[i==0,1,1./(1.+i^2)],{i, 0,1000}];-None]",
            "value": 0.7531015131365423,
            "unit": "iter/sec",
            "range": "stddev: 0.04737046808076894",
            "extra": "mean: 1.327842239800006 sec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@uniformTable-2.075674547634748]",
            "value": 250.5096807334245,
            "unit": "iter/sec",
            "range": "stddev: 0.00006930609708390533",
            "extra": "mean: 3.9918617000040513 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[uniformTable,{__Real}]-System`True]",
            "value": 1181.81154218468,
            "unit": "iter/sec",
            "range": "stddev: 0.00014615677534243393",
            "extra": "mean: 846.1586000009902 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@uniformTable]-0]",
            "value": 592.5391323958584,
            "unit": "iter/sec",
            "range": "stddev: 0.00003607158829909123",
            "extra": "mean: 1.6876522499984503 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Plus@@nonuniformTable-2.075674547634748]",
            "value": 250.83921394542207,
            "unit": "iter/sec",
            "range": "stddev: 0.000025992973647691024",
            "extra": "mean: 3.9866174999957598 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[MatchQ[nonuniformTable,{__Real}]-System`False]",
            "value": 127.08181215088135,
            "unit": "iter/sec",
            "range": "stddev: 0.00002344210244126536",
            "extra": "mean: 7.868946649995222 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_uniform_tables.py::test_evaluate_benchmark[Length[F@@nonuniformTable]-1001]",
            "value": 110.80315651378119,
            "unit": "iter/sec",
            "range": "stddev: 0.0000222925963044684",
            "extra": "mean: 9.025013650000346 msec\nrounds: 10"
          }
        ]
      }
    ]
  }
}