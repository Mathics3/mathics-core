window.BENCHMARK_DATA = {
  "lastUpdate": 1787845820861,
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
      },
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
          "id": "dddad5bc1fc35c9f34eb6628918fccaa8b4ef1c4",
          "message": "Update benchmark.yml",
          "timestamp": "2026-08-27T12:29:12-03:00",
          "tree_id": "1cde19d35cff4f1ad8283826b8d97329881822cc",
          "url": "https://github.com/Mathics3/mathics-core/commit/dddad5bc1fc35c9f34eb6628918fccaa8b4ef1c4"
        },
        "date": 1787844681617,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 6509.499149311366,
            "unit": "iter/sec",
            "range": "stddev: 0.000026042988031016736",
            "extra": "mean: 153.62165000141204 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 6652.0742331076835,
            "unit": "iter/sec",
            "range": "stddev: 0.000025997855900559752",
            "extra": "mean: 150.32905000111896 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 3376.578867155647,
            "unit": "iter/sec",
            "range": "stddev: 0.00010090980566245917",
            "extra": "mean: 296.1577500016688 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 2254.7266115642065,
            "unit": "iter/sec",
            "range": "stddev: 0.0005590656166709734",
            "extra": "mean: 443.5127500030944 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 1154.4328721507102,
            "unit": "iter/sec",
            "range": "stddev: 0.00008028961052762313",
            "extra": "mean: 866.226200001563 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 5932.426107174688,
            "unit": "iter/sec",
            "range": "stddev: 0.00002053483307178345",
            "extra": "mean: 168.56510000025082 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 5792.747653734123,
            "unit": "iter/sec",
            "range": "stddev: 0.00004218047500721846",
            "extra": "mean: 172.6296499995783 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 1584.7809052224256,
            "unit": "iter/sec",
            "range": "stddev: 0.000050919900360038984",
            "extra": "mean: 631.0020500023938 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 1443.8626560335317,
            "unit": "iter/sec",
            "range": "stddev: 0.000022436347258730065",
            "extra": "mean: 692.5866499983613 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 1386.690310664588,
            "unit": "iter/sec",
            "range": "stddev: 0.00007873389831518288",
            "extra": "mean: 721.1415499980944 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 1695.4085031640088,
            "unit": "iter/sec",
            "range": "stddev: 0.00004835722543603661",
            "extra": "mean: 589.8283500016532 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 2280.710537124147,
            "unit": "iter/sec",
            "range": "stddev: 0.000019711345827978946",
            "extra": "mean: 438.4598499996173 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 1877.1323049830185,
            "unit": "iter/sec",
            "range": "stddev: 0.000020163631662708687",
            "extra": "mean: 532.7274999984866 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 3.828750004567457,
            "unit": "iter/sec",
            "range": "stddev: 0.039927571667385225",
            "extra": "mean: 261.18184755000016 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 4.042929118350283,
            "unit": "iter/sec",
            "range": "stddev: 0.0034810494528033304",
            "extra": "mean: 247.3454198000013 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 4.0322371497247556,
            "unit": "iter/sec",
            "range": "stddev: 0.0030523604399817256",
            "extra": "mean: 248.00128635000078 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 3398.1121108355946,
            "unit": "iter/sec",
            "range": "stddev: 0.00003175816206157395",
            "extra": "mean: 294.2810500016435 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 3614.0361212399043,
            "unit": "iter/sec",
            "range": "stddev: 0.000015077254382242201",
            "extra": "mean: 276.698949997467 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 204.42015451489408,
            "unit": "iter/sec",
            "range": "stddev: 0.0004812469040555194",
            "extra": "mean: 4.891885549999131 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 59.20824841477739,
            "unit": "iter/sec",
            "range": "stddev: 0.0005773915530457685",
            "extra": "mean: 16.889538649996894 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 21.038468172132866,
            "unit": "iter/sec",
            "range": "stddev: 0.0013314950440870218",
            "extra": "mean: 47.53197770000099 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 108.5615744993491,
            "unit": "iter/sec",
            "range": "stddev: 0.00047286334004788245",
            "extra": "mean: 9.211362349999774 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 3185.6761804710145,
            "unit": "iter/sec",
            "range": "stddev: 0.000034405844502048675",
            "extra": "mean: 313.9051000005111 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x]]",
            "value": 7776.950828895898,
            "unit": "iter/sec",
            "range": "stddev: 0.000010889357592102803",
            "extra": "mean: 128.5850999963145 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 1298.658459842693,
            "unit": "iter/sec",
            "range": "stddev: 0.00004501373509446101",
            "extra": "mean: 770.0253999971096 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 817.8040856254689,
            "unit": "iter/sec",
            "range": "stddev: 0.0001324885364315454",
            "extra": "mean: 1.2227867500016032 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 1399.1061530539228,
            "unit": "iter/sec",
            "range": "stddev: 0.000041097145368817986",
            "extra": "mean: 714.7420499990176 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 1319.95654175377,
            "unit": "iter/sec",
            "range": "stddev: 0.00008759905185683533",
            "extra": "mean: 757.6006999983065 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 704.54118006122,
            "unit": "iter/sec",
            "range": "stddev: 0.00007227744015406359",
            "extra": "mean: 1.4193634500017538 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 549.8854574846725,
            "unit": "iter/sec",
            "range": "stddev: 0.00009426029606271419",
            "extra": "mean: 1.818560549999404 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 894.959498607347,
            "unit": "iter/sec",
            "range": "stddev: 0.00004020589820220544",
            "extra": "mean: 1.1173690000006786 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 986.0921076108145,
            "unit": "iter/sec",
            "range": "stddev: 0.00008258598980155641",
            "extra": "mean: 1.0141040499988208 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 706.6648387597442,
            "unit": "iter/sec",
            "range": "stddev: 0.000038315406182732314",
            "extra": "mean: 1.4150980000010804 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 549.647909290628,
            "unit": "iter/sec",
            "range": "stddev: 0.00008379710673227026",
            "extra": "mean: 1.8193464999995967 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 901.9147017789616,
            "unit": "iter/sec",
            "range": "stddev: 0.00003953103128951228",
            "extra": "mean: 1.1087522999986277 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 991.7236692934393,
            "unit": "iter/sec",
            "range": "stddev: 0.00009337386580520531",
            "extra": "mean: 1.0083453999968128 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 699.1173643256343,
            "unit": "iter/sec",
            "range": "stddev: 0.00004998508396495978",
            "extra": "mean: 1.4303750000038917 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 543.8520704970879,
            "unit": "iter/sec",
            "range": "stddev: 0.0001276336704770205",
            "extra": "mean: 1.8387352999980067 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 885.5094306960324,
            "unit": "iter/sec",
            "range": "stddev: 0.00005930824579778443",
            "extra": "mean: 1.129293450001967 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 994.3918784015237,
            "unit": "iter/sec",
            "range": "stddev: 0.00008833627944780686",
            "extra": "mean: 1.005639750002274 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 2839.670768578999,
            "unit": "iter/sec",
            "range": "stddev: 0.00004404282343789833",
            "extra": "mean: 352.15349999901946 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 847.1493509056286,
            "unit": "iter/sec",
            "range": "stddev: 0.00027708611020630297",
            "extra": "mean: 1.1804294000000937 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 23.682236384438482,
            "unit": "iter/sec",
            "range": "stddev: 0.002291999281523282",
            "extra": "mean: 42.225741850000986 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 18.618893438518963,
            "unit": "iter/sec",
            "range": "stddev: 0.001501563326106453",
            "extra": "mean: 53.708884649996946 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 18.22713782246779,
            "unit": "iter/sec",
            "range": "stddev: 0.0005231078570210961",
            "extra": "mean: 54.86324894999939 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 848.2541593406356,
            "unit": "iter/sec",
            "range": "stddev: 0.000041788927232450475",
            "extra": "mean: 1.1788919499991835 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 840.9746745093934,
            "unit": "iter/sec",
            "range": "stddev: 0.00003233022447327544",
            "extra": "mean: 1.1890964500011592 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 5.398988576156057,
            "unit": "iter/sec",
            "range": "stddev: 0.005624313902518907",
            "extra": "mean: 185.21987699999443 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 10.92120524608178,
            "unit": "iter/sec",
            "range": "stddev: 0.0005364875717450341",
            "extra": "mean: 91.5649854999998 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 869.3064664333381,
            "unit": "iter/sec",
            "range": "stddev: 0.00010632103378030077",
            "extra": "mean: 1.1503422999979307 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 882.5732729993763,
            "unit": "iter/sec",
            "range": "stddev: 0.0000273054825720465",
            "extra": "mean: 1.1330503999985808 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 2186.4980031262703,
            "unit": "iter/sec",
            "range": "stddev: 0.00006970848536891135",
            "extra": "mean: 457.352349999951 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 1066.1428067349748,
            "unit": "iter/sec",
            "range": "stddev: 0.000022406637587527756",
            "extra": "mean: 937.9606500019122 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 4532.218407640158,
            "unit": "iter/sec",
            "range": "stddev: 0.000021503969065291842",
            "extra": "mean: 220.64249999829144 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 4790.824230152991,
            "unit": "iter/sec",
            "range": "stddev: 0.000011017653499944144",
            "extra": "mean: 208.73235000067325 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 2531.592374148945,
            "unit": "iter/sec",
            "range": "stddev: 0.00003910822834670387",
            "extra": "mean: 395.0082999978122 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 1484.9807561323196,
            "unit": "iter/sec",
            "range": "stddev: 0.0000221512501878057",
            "extra": "mean: 673.409400000935 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 931.8083978296814,
            "unit": "iter/sec",
            "range": "stddev: 0.0001263274699852639",
            "extra": "mean: 1.0731820000003722 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 161.7655781081172,
            "unit": "iter/sec",
            "range": "stddev: 0.0000943405646280773",
            "extra": "mean: 6.181784849998451 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 383.4858932888987,
            "unit": "iter/sec",
            "range": "stddev: 0.00014144761833981634",
            "extra": "mean: 2.607657850002454 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 298.9385588591253,
            "unit": "iter/sec",
            "range": "stddev: 0.00007867768667243223",
            "extra": "mean: 3.3451689999992595 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 300.3159473927186,
            "unit": "iter/sec",
            "range": "stddev: 0.00005509125761478966",
            "extra": "mean: 3.3298264999970684 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 1.2750374625291356,
            "unit": "iter/sec",
            "range": "stddev: 0.04511602881242264",
            "extra": "mean: 784.2906811666713 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 78.62206754761111,
            "unit": "iter/sec",
            "range": "stddev: 0.0010293848333551875",
            "extra": "mean: 12.719075333327131 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 13.814601381612619,
            "unit": "iter/sec",
            "range": "stddev: 0.0006660141894117189",
            "extra": "mean: 72.38717733332578 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 14.648258473676206,
            "unit": "iter/sec",
            "range": "stddev: 0.0004988319012334129",
            "extra": "mean: 68.26750100000349 msec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "rocky@users.noreply.github.com",
            "name": "R. Bernstein",
            "username": "rocky"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e8397f8e5a858981816043cb450e02864b01ec74",
          "message": "File extension `.m` to extension `.wl` (#1916)\n\nRename files with extension `.m` to `.wl`; `.m` is ambiguous. It could\nrefer to Objective-C header files.\n\n---------\n\nCo-authored-by: Juan Mauricio Matera <matera@fisica.unlp.edu.ar>",
          "timestamp": "2026-08-27T12:48:09-03:00",
          "tree_id": "5396387cc2040fc9ba497b10ff5c9834dad36fa5",
          "url": "https://github.com/Mathics3/mathics-core/commit/e8397f8e5a858981816043cb450e02864b01ec74"
        },
        "date": 1787845819012,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 9112.630287854736,
            "unit": "iter/sec",
            "range": "stddev: 0.00005581079370036761",
            "extra": "mean: 109.73779999972066 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 9711.06663445032,
            "unit": "iter/sec",
            "range": "stddev: 0.00003790831008200718",
            "extra": "mean: 102.97529999974131 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 4495.385149984428,
            "unit": "iter/sec",
            "range": "stddev: 0.0001529141937967482",
            "extra": "mean: 222.45035000025837 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 2128.1119114440535,
            "unit": "iter/sec",
            "range": "stddev: 0.0009189159480829296",
            "extra": "mean: 469.90010000058646 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 1705.5490635695335,
            "unit": "iter/sec",
            "range": "stddev: 0.000115483849975214",
            "extra": "mean: 586.3214500010372 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 9388.155152558955,
            "unit": "iter/sec",
            "range": "stddev: 0.000029742054013322197",
            "extra": "mean: 106.51719999827947 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 8979.10696485086,
            "unit": "iter/sec",
            "range": "stddev: 0.00003853426385788351",
            "extra": "mean: 111.36965000133614 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 2312.3696979440556,
            "unit": "iter/sec",
            "range": "stddev: 0.00006803274158832665",
            "extra": "mean: 432.45680000438824 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 2152.9920453419486,
            "unit": "iter/sec",
            "range": "stddev: 0.00003363795542480538",
            "extra": "mean: 464.46989999964217 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 2002.024046313679,
            "unit": "iter/sec",
            "range": "stddev: 0.0000989057307642168",
            "extra": "mean: 499.49449999928675 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 2584.0814895332355,
            "unit": "iter/sec",
            "range": "stddev: 0.00005314480615724285",
            "extra": "mean: 386.98469999900453 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 3422.6508293736033,
            "unit": "iter/sec",
            "range": "stddev: 0.00003060710308139395",
            "extra": "mean: 292.1712000002685 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 2839.2603840210045,
            "unit": "iter/sec",
            "range": "stddev: 0.000035460731236327094",
            "extra": "mean: 352.20440000074404 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 5.608156168983456,
            "unit": "iter/sec",
            "range": "stddev: 0.06118416480068604",
            "extra": "mean: 178.31172489999716 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 6.240914759085207,
            "unit": "iter/sec",
            "range": "stddev: 0.0024940520331613062",
            "extra": "mean: 160.23292074999915 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 6.239960570338174,
            "unit": "iter/sec",
            "range": "stddev: 0.002200476603395014",
            "extra": "mean: 160.2574228999984 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 5125.453154224009,
            "unit": "iter/sec",
            "range": "stddev: 0.00004375668230728485",
            "extra": "mean: 195.10469999630686 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 5516.591562778788,
            "unit": "iter/sec",
            "range": "stddev: 0.000024927736744897176",
            "extra": "mean: 181.27135000298722 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 308.00868473583523,
            "unit": "iter/sec",
            "range": "stddev: 0.0002869976759478944",
            "extra": "mean: 3.246661700002562 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 86.63551605826652,
            "unit": "iter/sec",
            "range": "stddev: 0.00047356807655788845",
            "extra": "mean: 11.542610300000433 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 30.93895765466747,
            "unit": "iter/sec",
            "range": "stddev: 0.0009139896250994529",
            "extra": "mean: 32.3217094499995 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 154.93756024065047,
            "unit": "iter/sec",
            "range": "stddev: 0.00036476606406728683",
            "extra": "mean: 6.454212900001721 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 4961.93082616124,
            "unit": "iter/sec",
            "range": "stddev: 0.00004061710222200864",
            "extra": "mean: 201.5344500023275 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x]]",
            "value": 12192.653682349388,
            "unit": "iter/sec",
            "range": "stddev: 0.00001611607323761815",
            "extra": "mean: 82.01659999969024 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 1960.0208663843018,
            "unit": "iter/sec",
            "range": "stddev: 0.00007850713596751737",
            "extra": "mean: 510.1986499994382 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 1248.0914341804585,
            "unit": "iter/sec",
            "range": "stddev: 0.00013493582725357435",
            "extra": "mean: 801.2233499997024 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 2104.5905750639745,
            "unit": "iter/sec",
            "range": "stddev: 0.000059531296644299724",
            "extra": "mean: 475.151799997775 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 1914.4107171135427,
            "unit": "iter/sec",
            "range": "stddev: 0.00011232842434715652",
            "extra": "mean: 522.3539499965568 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1065.380709536182,
            "unit": "iter/sec",
            "range": "stddev: 0.00010093895524614053",
            "extra": "mean: 938.6315999989847 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 803.0124852780011,
            "unit": "iter/sec",
            "range": "stddev: 0.00011651598850610456",
            "extra": "mean: 1.2453106500004196 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 1314.1962700869028,
            "unit": "iter/sec",
            "range": "stddev: 0.00007397765991670624",
            "extra": "mean: 760.9213500003875 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 1453.7503852424945,
            "unit": "iter/sec",
            "range": "stddev: 0.00010712178885154475",
            "extra": "mean: 687.8760000006423 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1062.7453347624455,
            "unit": "iter/sec",
            "range": "stddev: 0.00008062954021376272",
            "extra": "mean: 940.9591999983036 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 808.2039489719538,
            "unit": "iter/sec",
            "range": "stddev: 0.00012081194001909824",
            "extra": "mean: 1.2373114500022098 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 1275.2401101772539,
            "unit": "iter/sec",
            "range": "stddev: 0.00014038349489245043",
            "extra": "mean: 784.1660500005787 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 1473.5399742270968,
            "unit": "iter/sec",
            "range": "stddev: 0.00008248678809866823",
            "extra": "mean: 678.637850000996 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1090.3598072877537,
            "unit": "iter/sec",
            "range": "stddev: 0.00006387227246780071",
            "extra": "mean: 917.1284499998933 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 826.9675097295703,
            "unit": "iter/sec",
            "range": "stddev: 0.00009531449959435554",
            "extra": "mean: 1.2092373499982045 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 1342.0735425414125,
            "unit": "iter/sec",
            "range": "stddev: 0.00006178174310108908",
            "extra": "mean: 745.1156500010825 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 1486.534818954311,
            "unit": "iter/sec",
            "range": "stddev: 0.00008502820256618969",
            "extra": "mean: 672.7054000009502 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 3980.4488314363043,
            "unit": "iter/sec",
            "range": "stddev: 0.00005218027811607171",
            "extra": "mean: 251.22794999958842 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 1194.7383484187512,
            "unit": "iter/sec",
            "range": "stddev: 0.0002520271198719288",
            "extra": "mean: 837.0033500000318 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 39.014576308035686,
            "unit": "iter/sec",
            "range": "stddev: 0.0018694427970263024",
            "extra": "mean: 25.631445849997192 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 29.752384308848466,
            "unit": "iter/sec",
            "range": "stddev: 0.0012771116249949018",
            "extra": "mean: 33.610751649997894 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 29.37778424369923,
            "unit": "iter/sec",
            "range": "stddev: 0.00039413880833169925",
            "extra": "mean: 34.03932684999802 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 1152.2449101193854,
            "unit": "iter/sec",
            "range": "stddev: 0.00008953568568030605",
            "extra": "mean: 867.8710499978592 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 1213.1719660954298,
            "unit": "iter/sec",
            "range": "stddev: 0.00005479391367708973",
            "extra": "mean: 824.2854499997065 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 8.24137779123187,
            "unit": "iter/sec",
            "range": "stddev: 0.0046728890005248375",
            "extra": "mean: 121.33893449999533 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 16.945316007944783,
            "unit": "iter/sec",
            "range": "stddev: 0.0006640439782198809",
            "extra": "mean: 59.0133580000014 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 1129.716346866693,
            "unit": "iter/sec",
            "range": "stddev: 0.0001225203896961434",
            "extra": "mean: 885.1779499991608 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 1199.3399552479166,
            "unit": "iter/sec",
            "range": "stddev: 0.000029217513427296865",
            "extra": "mean: 833.7919500007729 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 3214.9358202542676,
            "unit": "iter/sec",
            "range": "stddev: 0.00005338578445935685",
            "extra": "mean: 311.04819999825395 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 1454.8565293218533,
            "unit": "iter/sec",
            "range": "stddev: 0.00002718818909775348",
            "extra": "mean: 687.3530000007122 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 7093.8814917138425,
            "unit": "iter/sec",
            "range": "stddev: 0.000023556286598770235",
            "extra": "mean: 140.96655000059855 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 7329.003358245534,
            "unit": "iter/sec",
            "range": "stddev: 0.000018546815747454207",
            "extra": "mean: 136.44419999820911 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 3849.515509628516,
            "unit": "iter/sec",
            "range": "stddev: 0.000051209453935061906",
            "extra": "mean: 259.7729499981938 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 2235.5105939763357,
            "unit": "iter/sec",
            "range": "stddev: 0.00004212473092078059",
            "extra": "mean: 447.32509999931835 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 1371.9073435724854,
            "unit": "iter/sec",
            "range": "stddev: 0.00017344427687061785",
            "extra": "mean: 728.912200000309 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 298.8246940899488,
            "unit": "iter/sec",
            "range": "stddev: 0.0000731914074945951",
            "extra": "mean: 3.346443649998321 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 502.2376318773198,
            "unit": "iter/sec",
            "range": "stddev: 0.0001708599039603089",
            "extra": "mean: 1.9910893499996973 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 397.97908607982146,
            "unit": "iter/sec",
            "range": "stddev: 0.00009589269029243917",
            "extra": "mean: 2.512694849998809 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 420.4439880109767,
            "unit": "iter/sec",
            "range": "stddev: 0.00004788576622966809",
            "extra": "mean: 2.3784380999970267 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 1.9857462584181098,
            "unit": "iter/sec",
            "range": "stddev: 0.05890206384189431",
            "extra": "mean: 503.58901383332955 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 101.18045380480949,
            "unit": "iter/sec",
            "range": "stddev: 0.0008438273162814014",
            "extra": "mean: 9.883331833331491 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 21.747660481831726,
            "unit": "iter/sec",
            "range": "stddev: 0.0004019320424763406",
            "extra": "mean: 45.98195749999926 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 22.12038676154269,
            "unit": "iter/sec",
            "range": "stddev: 0.00043795344411795973",
            "extra": "mean: 45.207166166666944 msec\nrounds: 3"
          }
        ]
      }
    ]
  }
}