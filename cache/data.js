window.BENCHMARK_DATA = {
  "lastUpdate": 1787843918580,
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
          "id": "638badc810f575673e5d1f2f97887b1f254734e2",
          "message": "Add check benchmarks (#1915)\n\nBetter choice of regression benchmarks.",
          "timestamp": "2026-08-27T12:16:50-03:00",
          "tree_id": "3e548daf935c9b741c13a8a3e655cb5c8b45a799",
          "url": "https://github.com/Mathics3/mathics-core/commit/638badc810f575673e5d1f2f97887b1f254734e2"
        },
        "date": 1787843917993,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 8031.576947911872,
            "unit": "iter/sec",
            "range": "stddev: 0.000039069075712196076",
            "extra": "mean: 124.5085500002574 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 7809.184147232104,
            "unit": "iter/sec",
            "range": "stddev: 0.00003551202927091644",
            "extra": "mean: 128.05434999947352 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 2343.707520294035,
            "unit": "iter/sec",
            "range": "stddev: 0.0006567576718603115",
            "extra": "mean: 426.6744000013034 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 4195.5046426422205,
            "unit": "iter/sec",
            "range": "stddev: 0.00006574618426434551",
            "extra": "mean: 238.35034999990512 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 1434.0674922389912,
            "unit": "iter/sec",
            "range": "stddev: 0.00008623127207863407",
            "extra": "mean: 697.3172499982638 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 7634.511503979455,
            "unit": "iter/sec",
            "range": "stddev: 0.000027812956909777376",
            "extra": "mean: 130.9841499981701 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 7450.973525627067,
            "unit": "iter/sec",
            "range": "stddev: 0.00003581912031829619",
            "extra": "mean: 134.21064999903365 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 1919.2833856492748,
            "unit": "iter/sec",
            "range": "stddev: 0.00005475426020693402",
            "extra": "mean: 521.0277999992741 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 1732.4750190083384,
            "unit": "iter/sec",
            "range": "stddev: 0.000030254458080678812",
            "extra": "mean: 577.2089000004144 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 1641.433322554747,
            "unit": "iter/sec",
            "range": "stddev: 0.00008028874259010987",
            "extra": "mean: 609.2236500009562 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 2095.2169235694596,
            "unit": "iter/sec",
            "range": "stddev: 0.00004682882911979891",
            "extra": "mean: 477.2775500001103 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 2773.580810714716,
            "unit": "iter/sec",
            "range": "stddev: 0.000029141541493343313",
            "extra": "mean: 360.54474999858144 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 2257.510624970445,
            "unit": "iter/sec",
            "range": "stddev: 0.00003159419669973701",
            "extra": "mean: 442.9658000006498 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 4.7565175493808685,
            "unit": "iter/sec",
            "range": "stddev: 0.04982126886108074",
            "extra": "mean: 210.2378451500016 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 5.158210688431944,
            "unit": "iter/sec",
            "range": "stddev: 0.001287314572466728",
            "extra": "mean: 193.86567560000003 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 5.090166473380434,
            "unit": "iter/sec",
            "range": "stddev: 0.008535592896751548",
            "extra": "mean: 196.45722889999888 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 4177.540456334154,
            "unit": "iter/sec",
            "range": "stddev: 0.00004080655263519952",
            "extra": "mean: 239.37530000068818 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 4311.794482594012,
            "unit": "iter/sec",
            "range": "stddev: 0.00002492029914442779",
            "extra": "mean: 231.9220000018163 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 250.74137643045253,
            "unit": "iter/sec",
            "range": "stddev: 0.0003213984212730089",
            "extra": "mean: 3.988173050000654 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 70.5253748659106,
            "unit": "iter/sec",
            "range": "stddev: 0.0005031836705733415",
            "extra": "mean: 14.179293649998925 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 25.240491306516923,
            "unit": "iter/sec",
            "range": "stddev: 0.001178295198810306",
            "extra": "mean: 39.61888014999957 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 128.2541007180742,
            "unit": "iter/sec",
            "range": "stddev: 0.0004334459921474152",
            "extra": "mean: 7.797021649999181 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 4030.447613442297,
            "unit": "iter/sec",
            "range": "stddev: 0.00003009989309531023",
            "extra": "mean: 248.1114000005391 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x]]",
            "value": 9752.51529570775,
            "unit": "iter/sec",
            "range": "stddev: 0.000017270433620095897",
            "extra": "mean: 102.53764999887949 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 1587.5196822699586,
            "unit": "iter/sec",
            "range": "stddev: 0.0000567635758596688",
            "extra": "mean: 629.9134499990089 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 1011.716639819627,
            "unit": "iter/sec",
            "range": "stddev: 0.00011416039540081362",
            "extra": "mean: 988.4190500002887 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 1669.6402960386629,
            "unit": "iter/sec",
            "range": "stddev: 0.000057800000878545076",
            "extra": "mean: 598.9313999982926 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 1575.640099853423,
            "unit": "iter/sec",
            "range": "stddev: 0.00007994557852337906",
            "extra": "mean: 634.6626999992111 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 854.0229648481705,
            "unit": "iter/sec",
            "range": "stddev: 0.00008305937730719496",
            "extra": "mean: 1.1709287000002178 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 663.1740604775606,
            "unit": "iter/sec",
            "range": "stddev: 0.00008989038704402256",
            "extra": "mean: 1.5078997499990976 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 1054.5925104645069,
            "unit": "iter/sec",
            "range": "stddev: 0.000052518196583965924",
            "extra": "mean: 948.2335499988892 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 1182.771420316748,
            "unit": "iter/sec",
            "range": "stddev: 0.00007908112297213009",
            "extra": "mean: 845.4718999992394 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 862.7443604773968,
            "unit": "iter/sec",
            "range": "stddev: 0.000045343078507911566",
            "extra": "mean: 1.1590918999999644 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 661.4365774090448,
            "unit": "iter/sec",
            "range": "stddev: 0.00007874285195406537",
            "extra": "mean: 1.5118607500014036 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 1052.7124161804254,
            "unit": "iter/sec",
            "range": "stddev: 0.00004790795817485465",
            "extra": "mean: 949.9270499993884 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 1162.1765684407096,
            "unit": "iter/sec",
            "range": "stddev: 0.00007209566480721527",
            "extra": "mean: 860.454449999537 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 866.5487611533912,
            "unit": "iter/sec",
            "range": "stddev: 0.00004948247797783699",
            "extra": "mean: 1.1540031500004488 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 663.9671973646658,
            "unit": "iter/sec",
            "range": "stddev: 0.00007858587445486047",
            "extra": "mean: 1.5060984999998084 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 1060.9737362328847,
            "unit": "iter/sec",
            "range": "stddev: 0.00005521741963336612",
            "extra": "mean: 942.5303999989865 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 1181.52089504896,
            "unit": "iter/sec",
            "range": "stddev: 0.00007121586657436325",
            "extra": "mean: 846.3667500002714 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 3337.188898902684,
            "unit": "iter/sec",
            "range": "stddev: 0.000051501707066746306",
            "extra": "mean: 299.6534000004658 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 940.599318845998,
            "unit": "iter/sec",
            "range": "stddev: 0.0002829602114261252",
            "extra": "mean: 1.0631519500002184 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 31.25454748782347,
            "unit": "iter/sec",
            "range": "stddev: 0.0022537620773845943",
            "extra": "mean: 31.995344050000796 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 23.88719552825145,
            "unit": "iter/sec",
            "range": "stddev: 0.0014770420758533017",
            "extra": "mean: 41.863432600001005 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 23.673076732577577,
            "unit": "iter/sec",
            "range": "stddev: 0.00020255158720501617",
            "extra": "mean: 42.24207994999887 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 954.5472291361293,
            "unit": "iter/sec",
            "range": "stddev: 0.00005652846133816958",
            "extra": "mean: 1.0476170999993428 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 954.2279286963108,
            "unit": "iter/sec",
            "range": "stddev: 0.00004016494636211877",
            "extra": "mean: 1.0479676499997481 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 6.624971250730199,
            "unit": "iter/sec",
            "range": "stddev: 0.005406043827760242",
            "extra": "mean: 150.94405125000065 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 13.61573632189843,
            "unit": "iter/sec",
            "range": "stddev: 0.00014527438108742331",
            "extra": "mean: 73.44443050000038 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 926.2340273840274,
            "unit": "iter/sec",
            "range": "stddev: 0.00008527693426108337",
            "extra": "mean: 1.0796407499995553 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 950.945974903658,
            "unit": "iter/sec",
            "range": "stddev: 0.000024277843331893652",
            "extra": "mean: 1.051584450001286 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 2599.5771267876544,
            "unit": "iter/sec",
            "range": "stddev: 0.00004951154184599827",
            "extra": "mean: 384.67795000016736 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 1153.691958479119,
            "unit": "iter/sec",
            "range": "stddev: 0.000028372473288344136",
            "extra": "mean: 866.7824999996299 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 5704.807583976223,
            "unit": "iter/sec",
            "range": "stddev: 0.000021643050950327324",
            "extra": "mean: 175.29074999984573 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 5786.0626479461625,
            "unit": "iter/sec",
            "range": "stddev: 0.000018891904483748975",
            "extra": "mean: 172.82910000204765 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 3098.346954453075,
            "unit": "iter/sec",
            "range": "stddev: 0.00004542688594629231",
            "extra": "mean: 322.7527499987559 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 1809.478064189191,
            "unit": "iter/sec",
            "range": "stddev: 0.00003245052537200445",
            "extra": "mean: 552.6455500017846 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 1143.7980638234026,
            "unit": "iter/sec",
            "range": "stddev: 0.00015359154387525079",
            "extra": "mean: 874.2802000007543 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 235.79402594845354,
            "unit": "iter/sec",
            "range": "stddev: 0.00007586616829368062",
            "extra": "mean: 4.240989550000762 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 419.13254567971774,
            "unit": "iter/sec",
            "range": "stddev: 0.00014712256538079176",
            "extra": "mean: 2.3858801000010033 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 331.31124143343084,
            "unit": "iter/sec",
            "range": "stddev: 0.00007888336762468202",
            "extra": "mean: 3.0183099000005598 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 338.533879505912,
            "unit": "iter/sec",
            "range": "stddev: 0.00004428094645638521",
            "extra": "mean: 2.9539140999993663 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 1.5878995117028742,
            "unit": "iter/sec",
            "range": "stddev: 0.05457018372102613",
            "extra": "mean: 629.762773166668 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 96.00619355156878,
            "unit": "iter/sec",
            "range": "stddev: 0.0010913316382286271",
            "extra": "mean: 10.41599466666554 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 17.697633715762095,
            "unit": "iter/sec",
            "range": "stddev: 0.0005271680607582914",
            "extra": "mean: 56.504729166666344 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 18.529432068058554,
            "unit": "iter/sec",
            "range": "stddev: 0.000222612420151923",
            "extra": "mean: 53.968194833333406 msec\nrounds: 3"
          }
        ]
      }
    ]
  }
}