window.BENCHMARK_DATA = {
  "lastUpdate": 1787936410039,
  "repoUrl": "https://github.com/Mathics3/mathics-core",
  "entries": {
    "Mathics3 Core Benchmarks": [
      {
        "commit": {
          "author": {
            "name": "Juan Mauricio Matera",
            "username": "mmatera",
            "email": "matera@fisica.unlp.edu.ar"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "2d571ec11f080fbf3ea8796e8abcbef7a6a9623f",
          "message": "Add check benchmarks (#1919)\n\nThis should normalize the benchmarks to prevent server fluctuations from\naffecting the comparisons.",
          "timestamp": "2026-08-27T17:49:59Z",
          "url": "https://github.com/Mathics3/mathics-core/commit/2d571ec11f080fbf3ea8796e8abcbef7a6a9623f"
        },
        "date": 1787853723453,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000016268271035213232",
            "extra": "mean: 2.3326964244190127 msec\nrounds: 172"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 19.182688306243037,
            "unit": "iter/sec",
            "range": "stddev: 0.00003418053548482601",
            "extra": "mean: 121.60424999763109 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 18.952992610372434,
            "unit": "iter/sec",
            "range": "stddev: 0.00003737358378018145",
            "extra": "mean: 123.07799999575764 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 10.01236975937216,
            "unit": "iter/sec",
            "range": "stddev: 0.00007736962063857189",
            "extra": "mean: 232.98144999444048 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 5.969376986189221,
            "unit": "iter/sec",
            "range": "stddev: 0.000561832834512325",
            "extra": "mean: 390.77720000193494 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.3168364643371064,
            "unit": "iter/sec",
            "range": "stddev: 0.00009082359505113022",
            "extra": "mean: 703.2895499975211 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 17.716939609582887,
            "unit": "iter/sec",
            "range": "stddev: 0.000025274013491720665",
            "extra": "mean: 131.66474999763977 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 17.18354588042352,
            "unit": "iter/sec",
            "range": "stddev: 0.000033822543687646725",
            "extra": "mean: 135.75174999687079 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 4.520703221518185,
            "unit": "iter/sec",
            "range": "stddev: 0.00004903596804022091",
            "extra": "mean: 516.0030000013194 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 4.028288072348808,
            "unit": "iter/sec",
            "range": "stddev: 0.00003228575544452693",
            "extra": "mean: 579.0788500036115 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 3.8452292832038784,
            "unit": "iter/sec",
            "range": "stddev: 0.00007630711917855837",
            "extra": "mean: 606.6468999932795 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 4.875662625487088,
            "unit": "iter/sec",
            "range": "stddev: 0.00004424745694769888",
            "extra": "mean: 478.43680000028144 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 6.421082456310819,
            "unit": "iter/sec",
            "range": "stddev: 0.00002791108884820269",
            "extra": "mean: 363.28710000077535 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 5.283180504477854,
            "unit": "iter/sec",
            "range": "stddev: 0.00003166728524678175",
            "extra": "mean: 441.53260000143746 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.011320356595026265,
            "unit": "iter/sec",
            "range": "stddev: 0.04469787927365823",
            "extra": "mean: 206.06209749999493 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.012113903945483973,
            "unit": "iter/sec",
            "range": "stddev: 0.00217213504361906",
            "extra": "mean: 192.56355630000144 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.012115728138649197,
            "unit": "iter/sec",
            "range": "stddev: 0.0005043125289835436",
            "extra": "mean: 192.5345631500022 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 9.699863566441262,
            "unit": "iter/sec",
            "range": "stddev: 0.00003925325948155473",
            "extra": "mean: 240.48754999910216 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 10.121181119174022,
            "unit": "iter/sec",
            "range": "stddev: 0.00002569199101498835",
            "extra": "mean: 230.47669999698428 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5852767861181709,
            "unit": "iter/sec",
            "range": "stddev: 0.00031708170039260387",
            "extra": "mean: 3.9856295000021187 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.1638981615079899,
            "unit": "iter/sec",
            "range": "stddev: 0.0005052817174695929",
            "extra": "mean: 14.232596649995344 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.059188269970123636,
            "unit": "iter/sec",
            "range": "stddev: 0.0011691617714723026",
            "extra": "mean: 39.41146489999596 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.30237476020188325,
            "unit": "iter/sec",
            "range": "stddev: 0.0003792948296836701",
            "extra": "mean: 7.714587099999903 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 9.199965863034187,
            "unit": "iter/sec",
            "range": "stddev: 0.00003462592540914841",
            "extra": "mean: 253.55490000151804 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x]]",
            "value": 22.849668934145893,
            "unit": "iter/sec",
            "range": "stddev: 0.000019364089029108216",
            "extra": "mean: 102.08885000224655 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.7453793607838226,
            "unit": "iter/sec",
            "range": "stddev: 0.000055704668290602464",
            "extra": "mean: 622.8198000030716 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.375218657679227,
            "unit": "iter/sec",
            "range": "stddev: 0.00010673460501920505",
            "extra": "mean: 982.097549999139 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.9889342249980673,
            "unit": "iter/sec",
            "range": "stddev: 0.0000504626569729321",
            "extra": "mean: 584.7919000018464 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.6924584730863206,
            "unit": "iter/sec",
            "range": "stddev: 0.00007910451032491723",
            "extra": "mean: 631.7461500032096 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 2.0325035733878623,
            "unit": "iter/sec",
            "range": "stddev: 0.00008946305853698312",
            "extra": "mean: 1.147696100002804 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.555540782760476,
            "unit": "iter/sec",
            "range": "stddev: 0.00008549956934271246",
            "extra": "mean: 1.4996047999972006 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.4671661057097882,
            "unit": "iter/sec",
            "range": "stddev: 0.000056836881491546195",
            "extra": "mean: 945.4962999939198 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.781495442616949,
            "unit": "iter/sec",
            "range": "stddev: 0.00008580003717884338",
            "extra": "mean: 838.648300003797 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.9690021379721967,
            "unit": "iter/sec",
            "range": "stddev: 0.00013581971628820667",
            "extra": "mean: 1.1847099499959768 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.560127309328225,
            "unit": "iter/sec",
            "range": "stddev: 0.00006901572019719296",
            "extra": "mean: 1.4951961999969399 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.5066687618584416,
            "unit": "iter/sec",
            "range": "stddev: 0.00004906627315252518",
            "extra": "mean: 930.5961999899637 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.7847041760933897,
            "unit": "iter/sec",
            "range": "stddev: 0.00006804635792652885",
            "extra": "mean: 837.6819500057309 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 2.0553530450661484,
            "unit": "iter/sec",
            "range": "stddev: 0.00005372464748938342",
            "extra": "mean: 1.1349370999880648 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.5833103912980417,
            "unit": "iter/sec",
            "range": "stddev: 0.00008184407593352521",
            "extra": "mean: 1.473303299997042 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.5083988525115575,
            "unit": "iter/sec",
            "range": "stddev: 0.00005020428871081257",
            "extra": "mean: 929.9543499963647 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.810874528785008,
            "unit": "iter/sec",
            "range": "stddev: 0.00007125916881352626",
            "extra": "mean: 829.8828000079084 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 7.93509865275187,
            "unit": "iter/sec",
            "range": "stddev: 0.000047577085043429976",
            "extra": "mean: 293.97195000342435 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.2317559976319674,
            "unit": "iter/sec",
            "range": "stddev: 0.00026796827826048415",
            "extra": "mean: 1.0452291500030242 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.07369641461587245,
            "unit": "iter/sec",
            "range": "stddev: 0.0021232040994152894",
            "extra": "mean: 31.6527803500037 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.056221461523659824,
            "unit": "iter/sec",
            "range": "stddev: 0.0017051250586662251",
            "extra": "mean: 41.49120925000034 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.055611600586672055,
            "unit": "iter/sec",
            "range": "stddev: 0.00017804832517992835",
            "extra": "mean: 41.9462198500014 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.1820438612566955,
            "unit": "iter/sec",
            "range": "stddev: 0.000060949625955373643",
            "extra": "mean: 1.0690419499979953 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.222438685423517,
            "unit": "iter/sec",
            "range": "stddev: 0.00004185404901828124",
            "extra": "mean: 1.0496111500032157 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.015671457941080935,
            "unit": "iter/sec",
            "range": "stddev: 0.006421246225882383",
            "extra": "mean: 148.8499942499999 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.03206069229360784,
            "unit": "iter/sec",
            "range": "stddev: 0.000005201477480690975",
            "extra": "mean: 72.75876650000157 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.1897881148238043,
            "unit": "iter/sec",
            "range": "stddev: 0.00008581058173046887",
            "extra": "mean: 1.0652612499939096 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.255410716481137,
            "unit": "iter/sec",
            "range": "stddev: 0.000030447317388625217",
            "extra": "mean: 1.0342667999992727 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 6.122879383538186,
            "unit": "iter/sec",
            "range": "stddev: 0.00004923426492974115",
            "extra": "mean: 380.98030000242034 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.7244673348714077,
            "unit": "iter/sec",
            "range": "stddev: 0.000024794478011117186",
            "extra": "mean: 856.2027500062186 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 13.401479837712344,
            "unit": "iter/sec",
            "range": "stddev: 0.000022579067478333304",
            "extra": "mean: 174.06260000143448 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 13.67681934450233,
            "unit": "iter/sec",
            "range": "stddev: 0.00001557521175753392",
            "extra": "mean: 170.55839999500222 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 7.3330409514509745,
            "unit": "iter/sec",
            "range": "stddev: 0.00004058622484971296",
            "extra": "mean: 318.10764999988805 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 4.2905028669724405,
            "unit": "iter/sec",
            "range": "stddev: 0.000033951841791465256",
            "extra": "mean: 543.6883500010481 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 2.706440105641884,
            "unit": "iter/sec",
            "range": "stddev: 0.00014157823709593783",
            "extra": "mean: 861.9058000050472 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.5613983686401939,
            "unit": "iter/sec",
            "range": "stddev: 0.00007622888695851746",
            "extra": "mean: 4.155153549999113 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 0.9832290317781758,
            "unit": "iter/sec",
            "range": "stddev: 0.00014264067612711028",
            "extra": "mean: 2.372485299991922 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.7714613639101187,
            "unit": "iter/sec",
            "range": "stddev: 0.00008374667245173284",
            "extra": "mean: 3.0237372000016194 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.7886466303111191,
            "unit": "iter/sec",
            "range": "stddev: 0.000040092584727153295",
            "extra": "mean: 2.9578474500027596 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.0037521068719486256,
            "unit": "iter/sec",
            "range": "stddev: 0.05935291287544773",
            "extra": "mean: 621.7030868333305 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.22547699950540973,
            "unit": "iter/sec",
            "range": "stddev: 0.0010089486903115778",
            "extra": "mean: 10.345606999986027 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.0417146599584571,
            "unit": "iter/sec",
            "range": "stddev: 0.00028316867296877173",
            "extra": "mean: 55.92030300000298 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.043005044764509726,
            "unit": "iter/sec",
            "range": "stddev: 0.0001781854916916471",
            "extra": "mean: 54.24239033333341 msec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Juan Mauricio Matera",
            "username": "mmatera",
            "email": "matera@fisica.unlp.edu.ar"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "2d571ec11f080fbf3ea8796e8abcbef7a6a9623f",
          "message": "Add check benchmarks (#1919)\n\nThis should normalize the benchmarks to prevent server fluctuations from\naffecting the comparisons.",
          "timestamp": "2026-08-27T17:49:59Z",
          "url": "https://github.com/Mathics3/mathics-core/commit/2d571ec11f080fbf3ea8796e8abcbef7a6a9623f"
        },
        "date": 1787855599746,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.00004134549232191498",
            "extra": "mean: 1.7964758590913086 msec\nrounds: 220"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 17.71289014955689,
            "unit": "iter/sec",
            "range": "stddev: 0.00003339563451126093",
            "extra": "mean: 101.42194999929188 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 17.598369341182327,
            "unit": "iter/sec",
            "range": "stddev: 0.00003295677238231007",
            "extra": "mean: 102.08194999563602 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 8.825224116883243,
            "unit": "iter/sec",
            "range": "stddev: 0.00010559879507837547",
            "extra": "mean: 203.56150000253592 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 9.529931011690238,
            "unit": "iter/sec",
            "range": "stddev: 0.00006268379900317963",
            "extra": "mean: 188.5087999994539 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.2951749920827273,
            "unit": "iter/sec",
            "range": "stddev: 0.00007414921005803971",
            "extra": "mean: 545.1837500004331 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 17.343974388034333,
            "unit": "iter/sec",
            "range": "stddev: 0.0000226284742281686",
            "extra": "mean: 103.5792499976651 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 16.98587131975195,
            "unit": "iter/sec",
            "range": "stddev: 0.00003276686492429498",
            "extra": "mean: 105.76294999964375 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 4.398755842000071,
            "unit": "iter/sec",
            "range": "stddev: 0.00004670683007123199",
            "extra": "mean: 408.40544999980466 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 3.989913388025438,
            "unit": "iter/sec",
            "range": "stddev: 0.000027709716666396243",
            "extra": "mean: 450.2543500024103 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 3.790706028417245,
            "unit": "iter/sec",
            "range": "stddev: 0.00006374165643773042",
            "extra": "mean: 473.9158999996107 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 4.7986114933897275,
            "unit": "iter/sec",
            "range": "stddev: 0.000037818985301371704",
            "extra": "mean: 374.3741000008072 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 6.371906410630565,
            "unit": "iter/sec",
            "range": "stddev: 0.000019751887185305317",
            "extra": "mean: 281.9369499988511 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 5.037997525635815,
            "unit": "iter/sec",
            "range": "stddev: 0.00002356570763678887",
            "extra": "mean: 356.5853000026209 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.010936844775193346,
            "unit": "iter/sec",
            "range": "stddev: 0.04705080917361797",
            "extra": "mean: 164.25906155000263 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.011797931589779312,
            "unit": "iter/sec",
            "range": "stddev: 0.002065340956946597",
            "extra": "mean: 152.27040819999473 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.011831373701125846,
            "unit": "iter/sec",
            "range": "stddev: 0.0012369583163618018",
            "extra": "mean: 151.84000644999998 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 9.655069727207445,
            "unit": "iter/sec",
            "range": "stddev: 0.00003482622414059952",
            "extra": "mean: 186.06555000104663 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 10.03692654795841,
            "unit": "iter/sec",
            "range": "stddev: 0.000018410467324001147",
            "extra": "mean: 178.9866499976256 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5755946323585157,
            "unit": "iter/sec",
            "range": "stddev: 0.0002833689442487278",
            "extra": "mean: 3.121078200000227 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.16140959388401938,
            "unit": "iter/sec",
            "range": "stddev: 0.0004190369404519215",
            "extra": "mean: 11.12991995000101 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.058464310550454764,
            "unit": "iter/sec",
            "range": "stddev: 0.0010618621621471553",
            "extra": "mean: 30.727735299998926 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.29628024253870405,
            "unit": "iter/sec",
            "range": "stddev: 0.0003405379489142203",
            "extra": "mean: 6.063434549999158 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 7.99971438022838,
            "unit": "iter/sec",
            "range": "stddev: 0.00004927055685165242",
            "extra": "mean: 224.56750000117154 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x]]",
            "value": 22.10377976765794,
            "unit": "iter/sec",
            "range": "stddev: 0.000018361384808144712",
            "extra": "mean: 81.27459999940356 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.576391950525451,
            "unit": "iter/sec",
            "range": "stddev: 0.00005385731757442026",
            "extra": "mean: 502.3151500012091 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.323100873906651,
            "unit": "iter/sec",
            "range": "stddev: 0.00010608178667630755",
            "extra": "mean: 773.309449998294 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.88354202187393,
            "unit": "iter/sec",
            "range": "stddev: 0.00004502532919531484",
            "extra": "mean: 462.58694999892214 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.5931148455903945,
            "unit": "iter/sec",
            "range": "stddev: 0.00006521582968051615",
            "extra": "mean: 499.9773000008645 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.9735662261678077,
            "unit": "iter/sec",
            "range": "stddev: 0.00006908119699113159",
            "extra": "mean: 910.2688499993405 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.4992824037471648,
            "unit": "iter/sec",
            "range": "stddev: 0.00009197427326958156",
            "extra": "mean: 1.1982238000001644 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.373667382685315,
            "unit": "iter/sec",
            "range": "stddev: 0.00006004238181123225",
            "extra": "mean: 756.8355499998347 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.650020008692847,
            "unit": "iter/sec",
            "range": "stddev: 0.00009174835699934562",
            "extra": "mean: 677.9102999971087 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.9652278093291102,
            "unit": "iter/sec",
            "range": "stddev: 0.00006010558330203075",
            "extra": "mean: 914.131099999338 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.4884369793927932,
            "unit": "iter/sec",
            "range": "stddev: 0.00013338175871348954",
            "extra": "mean: 1.2069546000020637 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.4087152808589254,
            "unit": "iter/sec",
            "range": "stddev: 0.000053013047206543574",
            "extra": "mean: 745.8232499985229 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.668383712474604,
            "unit": "iter/sec",
            "range": "stddev: 0.00007791371092098267",
            "extra": "mean: 673.2449500020721 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.980835376966649,
            "unit": "iter/sec",
            "range": "stddev: 0.000057776902815310226",
            "extra": "mean: 906.9283999977529 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.4992016396504013,
            "unit": "iter/sec",
            "range": "stddev: 0.00008702095305369571",
            "extra": "mean: 1.1982883499982222 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.4463854242407868,
            "unit": "iter/sec",
            "range": "stddev: 0.00005261427815179042",
            "extra": "mean: 734.3388499990056 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.6953124175222953,
            "unit": "iter/sec",
            "range": "stddev: 0.00007132321970591661",
            "extra": "mean: 666.5186000006429 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 7.6796135010155036,
            "unit": "iter/sec",
            "range": "stddev: 0.00004746950415072403",
            "extra": "mean: 233.92789999832075 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.0927560127524543,
            "unit": "iter/sec",
            "range": "stddev: 0.00035383134769148593",
            "extra": "mean: 858.4258500007991 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.07180197347893717,
            "unit": "iter/sec",
            "range": "stddev: 0.0017571167927507966",
            "extra": "mean: 25.0198674499984 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.05489227150221281,
            "unit": "iter/sec",
            "range": "stddev: 0.0013582722434809904",
            "extra": "mean: 32.72730040000056 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.053800235704537916,
            "unit": "iter/sec",
            "range": "stddev: 0.0002791393349033363",
            "extra": "mean: 33.391598300001135 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.1519181935330574,
            "unit": "iter/sec",
            "range": "stddev: 0.00007131075125983385",
            "extra": "mean: 834.8253500017222 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.1504501720520035,
            "unit": "iter/sec",
            "range": "stddev: 0.000045407126806751596",
            "extra": "mean: 835.3952499987827 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.015053551290692017,
            "unit": "iter/sec",
            "range": "stddev: 0.00631688645737694",
            "extra": "mean: 119.3390067499962 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.0309874363203731,
            "unit": "iter/sec",
            "range": "stddev: 0.0004424437840521535",
            "extra": "mean: 57.97433000000041 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.099764597731541,
            "unit": "iter/sec",
            "range": "stddev: 0.0001098637547129827",
            "extra": "mean: 855.5605999987392 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.2115902416504802,
            "unit": "iter/sec",
            "range": "stddev: 0.00002656928766336935",
            "extra": "mean: 812.3005000015837 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 6.03773410724289,
            "unit": "iter/sec",
            "range": "stddev: 0.0000424444021046278",
            "extra": "mean: 297.5413999990906 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.7254840952520607,
            "unit": "iter/sec",
            "range": "stddev: 0.00002223426036705335",
            "extra": "mean: 659.1400999994335 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 13.229342059781622,
            "unit": "iter/sec",
            "range": "stddev: 0.000019171401582446136",
            "extra": "mean: 135.79479999634714 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 13.440775132076807,
            "unit": "iter/sec",
            "range": "stddev: 0.000012926324943763972",
            "extra": "mean: 133.6586499988357 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 7.264677237506715,
            "unit": "iter/sec",
            "range": "stddev: 0.000036203271012185186",
            "extra": "mean: 247.2891500005403 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 4.165884573841926,
            "unit": "iter/sec",
            "range": "stddev: 0.000027935693581270165",
            "extra": "mean: 431.2351500018963 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 2.6271503131740115,
            "unit": "iter/sec",
            "range": "stddev: 0.000146059262739881",
            "extra": "mean: 683.8115999997285 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.5584435622453527,
            "unit": "iter/sec",
            "range": "stddev: 0.000045631046010994315",
            "extra": "mean: 3.2169336000009707 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 0.9590353011378288,
            "unit": "iter/sec",
            "range": "stddev: 0.00016608918522232518",
            "extra": "mean: 1.8732113999973876 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.7515135196622721,
            "unit": "iter/sec",
            "range": "stddev: 0.0000819941572700087",
            "extra": "mean: 2.3904770999976677 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.7759795568400294,
            "unit": "iter/sec",
            "range": "stddev: 0.00003055854139987118",
            "extra": "mean: 2.3151071999976125 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.0035805439125601237,
            "unit": "iter/sec",
            "range": "stddev: 0.06525474451893067",
            "extra": "mean: 501.7326704999997 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.18086191996903148,
            "unit": "iter/sec",
            "range": "stddev: 0.0008168391951492467",
            "extra": "mean: 9.932858500003286 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.039311627394275746,
            "unit": "iter/sec",
            "range": "stddev: 0.0003143265678544189",
            "extra": "mean: 45.69833349999897 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.040257704140319615,
            "unit": "iter/sec",
            "range": "stddev: 0.000900661886293462",
            "extra": "mean: 44.62439916666957 msec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Juan Mauricio Matera",
            "username": "mmatera",
            "email": "matera@fisica.unlp.edu.ar"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "2d571ec11f080fbf3ea8796e8abcbef7a6a9623f",
          "message": "Add check benchmarks (#1919)\n\nThis should normalize the benchmarks to prevent server fluctuations from\naffecting the comparisons.",
          "timestamp": "2026-08-27T17:49:59Z",
          "url": "https://github.com/Mathics3/mathics-core/commit/2d571ec11f080fbf3ea8796e8abcbef7a6a9623f"
        },
        "date": 1787855601302,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.00010429144092334243",
            "extra": "mean: 2.3936251676299154 msec\nrounds: 173"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 15.56327809566886,
            "unit": "iter/sec",
            "range": "stddev: 0.000030526320947139625",
            "extra": "mean: 153.7995499994338 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 15.876330730855976,
            "unit": "iter/sec",
            "range": "stddev: 0.00002633285172215951",
            "extra": "mean: 150.76689999773407 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 5.217697888601389,
            "unit": "iter/sec",
            "range": "stddev: 0.0006086842372632446",
            "extra": "mean: 458.751199999341 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 8.36830052719797,
            "unit": "iter/sec",
            "range": "stddev: 0.00005942047704517907",
            "extra": "mean: 286.0347999991575 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 2.7579388191608833,
            "unit": "iter/sec",
            "range": "stddev: 0.00009071804591505806",
            "extra": "mean: 867.9036500012671 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 14.39827799724291,
            "unit": "iter/sec",
            "range": "stddev: 0.000018642143679637238",
            "extra": "mean: 166.24384999985864 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 13.693131811227778,
            "unit": "iter/sec",
            "range": "stddev: 0.00003753659903771337",
            "extra": "mean: 174.80479999960608 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 3.7620910562785492,
            "unit": "iter/sec",
            "range": "stddev: 0.00005036390273763079",
            "extra": "mean: 636.2486000000445 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 3.487194561551041,
            "unit": "iter/sec",
            "range": "stddev: 0.00002570532594444467",
            "extra": "mean: 686.4042500012602 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 3.342899238584931,
            "unit": "iter/sec",
            "range": "stddev: 0.00007424251720680156",
            "extra": "mean: 716.0326999994027 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 4.1100405910892945,
            "unit": "iter/sec",
            "range": "stddev: 0.000036265860327501615",
            "extra": "mean: 582.3847999991472 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 5.242059833723386,
            "unit": "iter/sec",
            "range": "stddev: 0.000044436088676842365",
            "extra": "mean: 456.6192000005742 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 4.471216691319734,
            "unit": "iter/sec",
            "range": "stddev: 0.000022390922815861325",
            "extra": "mean: 535.3409000008469 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.008931547867191154,
            "unit": "iter/sec",
            "range": "stddev: 0.046444051033727264",
            "extra": "mean: 267.9966790999998 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.009479982394468078,
            "unit": "iter/sec",
            "range": "stddev: 0.000991353522882819",
            "extra": "mean: 252.49257520000086 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.00946902633570609,
            "unit": "iter/sec",
            "range": "stddev: 0.0014651732313206666",
            "extra": "mean: 252.78471964999838 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 8.049573388608472,
            "unit": "iter/sec",
            "range": "stddev: 0.00003198109649146555",
            "extra": "mean: 297.3605000008206 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 8.390932754542922,
            "unit": "iter/sec",
            "range": "stddev: 0.000018772621840785586",
            "extra": "mean: 285.26329999891686 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.4942530814361164,
            "unit": "iter/sec",
            "range": "stddev: 0.0003237826369121662",
            "extra": "mean: 4.84291399999961 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.1381348848169775,
            "unit": "iter/sec",
            "range": "stddev: 0.000630813558702119",
            "extra": "mean: 17.32817289999815 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.049924573673213374,
            "unit": "iter/sec",
            "range": "stddev: 0.0013504474657443824",
            "extra": "mean: 47.94482939999938 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.2550695640553063,
            "unit": "iter/sec",
            "range": "stddev: 0.00045855156737824163",
            "extra": "mean: 9.384205349999775 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 7.696832269209271,
            "unit": "iter/sec",
            "range": "stddev: 0.000022073168047526595",
            "extra": "mean: 310.98835000022973 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x]]",
            "value": 18.08810503913397,
            "unit": "iter/sec",
            "range": "stddev: 0.000015480340002736758",
            "extra": "mean: 132.33145000270952 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.0138692023009157,
            "unit": "iter/sec",
            "range": "stddev: 0.00004096863310967452",
            "extra": "mean: 794.2034000024023 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 1.9441037609235878,
            "unit": "iter/sec",
            "range": "stddev: 0.00010798126234194051",
            "extra": "mean: 1.231222949999733 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.3043243974647987,
            "unit": "iter/sec",
            "range": "stddev: 0.000038565639965587896",
            "extra": "mean: 724.3916999996713 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 2.9992651246546576,
            "unit": "iter/sec",
            "range": "stddev: 0.00008529229866642294",
            "extra": "mean: 798.0705500003182 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.6534671379823873,
            "unit": "iter/sec",
            "range": "stddev: 0.00007135002168532996",
            "extra": "mean: 1.4476400000006606 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.2894095306756284,
            "unit": "iter/sec",
            "range": "stddev: 0.00008774892196215113",
            "extra": "mean: 1.8563731000000416 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.106153626456901,
            "unit": "iter/sec",
            "range": "stddev: 0.000055029517499270756",
            "extra": "mean: 1.1364912500027913 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.3335214718125448,
            "unit": "iter/sec",
            "range": "stddev: 0.00007516578393869153",
            "extra": "mean: 1.0257566500001758 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.6772191889116261,
            "unit": "iter/sec",
            "range": "stddev: 0.00003617124937517437",
            "extra": "mean: 1.4271391500017216 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.308219725275234,
            "unit": "iter/sec",
            "range": "stddev: 0.00007544975278116117",
            "extra": "mean: 1.8296813000020506 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.146155997276581,
            "unit": "iter/sec",
            "range": "stddev: 0.000028555431410001927",
            "extra": "mean: 1.115308100001755 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.32828623809811,
            "unit": "iter/sec",
            "range": "stddev: 0.00007743707864332158",
            "extra": "mean: 1.028063100001475 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.6716069672870686,
            "unit": "iter/sec",
            "range": "stddev: 0.00003762933858111498",
            "extra": "mean: 1.4319305999990206 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.2946402977878446,
            "unit": "iter/sec",
            "range": "stddev: 0.00007273696848955027",
            "extra": "mean: 1.8488727499985202 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.114746746922297,
            "unit": "iter/sec",
            "range": "stddev: 0.00003902390692110912",
            "extra": "mean: 1.1318732000006548 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.3440457863965034,
            "unit": "iter/sec",
            "range": "stddev: 0.0000761153729158793",
            "extra": "mean: 1.0211511999983713 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 6.76183829785237,
            "unit": "iter/sec",
            "range": "stddev: 0.000040595930483231264",
            "extra": "mean: 353.9903000032041 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.054716260860435,
            "unit": "iter/sec",
            "range": "stddev: 0.00026265680525953326",
            "extra": "mean: 1.16494195000314 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05689754959846144,
            "unit": "iter/sec",
            "range": "stddev: 0.002278112140712996",
            "extra": "mean: 42.0690378499998 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.043179434895339965,
            "unit": "iter/sec",
            "range": "stddev: 0.002175664830903548",
            "extra": "mean: 55.43437919999832 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.04306747731229842,
            "unit": "iter/sec",
            "range": "stddev: 0.0004181910186185297",
            "extra": "mean: 55.57848560000025 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.003635374369983,
            "unit": "iter/sec",
            "range": "stddev: 0.00005005144175228046",
            "extra": "mean: 1.1946410999968293 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 1.9877697041811146,
            "unit": "iter/sec",
            "range": "stddev: 0.000028006267548165025",
            "extra": "mean: 1.204176299998494 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.012554974735948441,
            "unit": "iter/sec",
            "range": "stddev: 0.005732027478511287",
            "extra": "mean: 190.65153200000395 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.025413591259637453,
            "unit": "iter/sec",
            "range": "stddev: 0.00011577883592763647",
            "extra": "mean: 94.18681300000031 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.0685119700198507,
            "unit": "iter/sec",
            "range": "stddev: 0.0001077604311503009",
            "extra": "mean: 1.1571725000010247 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.120698295327817,
            "unit": "iter/sec",
            "range": "stddev: 0.000014790354387264421",
            "extra": "mean: 1.1286966999989545 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 5.278518342424135,
            "unit": "iter/sec",
            "range": "stddev: 0.00004034923653758426",
            "extra": "mean: 453.46535000021504 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.553431553747526,
            "unit": "iter/sec",
            "range": "stddev: 0.00001909314658485129",
            "extra": "mean: 937.4150500008227 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 11.486521822771849,
            "unit": "iter/sec",
            "range": "stddev: 0.000017072189721232545",
            "extra": "mean: 208.3855500004006 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 11.565443130788957,
            "unit": "iter/sec",
            "range": "stddev: 0.000012309150878368711",
            "extra": "mean: 206.96354999643063 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 6.090978628355693,
            "unit": "iter/sec",
            "range": "stddev: 0.000034319174072991604",
            "extra": "mean: 392.97874999704163 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 3.5866420082217014,
            "unit": "iter/sec",
            "range": "stddev: 0.0000254671645560246",
            "extra": "mean: 667.3721999973736 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 2.264114319194166,
            "unit": "iter/sec",
            "range": "stddev: 0.00014386138590036083",
            "extra": "mean: 1.0572015500002863 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.3797832845752817,
            "unit": "iter/sec",
            "range": "stddev: 0.00008569166980775931",
            "extra": "mean: 6.3026079999985996 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 0.9116106377438322,
            "unit": "iter/sec",
            "range": "stddev: 0.00013607432650753192",
            "extra": "mean: 2.625709999999515 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.7056893297392933,
            "unit": "iter/sec",
            "range": "stddev: 0.00008288238005800737",
            "extra": "mean: 3.3918964999998025 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.7207320531305372,
            "unit": "iter/sec",
            "range": "stddev: 0.00003205924902123075",
            "extra": "mean: 3.321102700002143 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.003017441857931781,
            "unit": "iter/sec",
            "range": "stddev: 0.04856690560342426",
            "extra": "mean: 793.2630619999941 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.18243370509804233,
            "unit": "iter/sec",
            "range": "stddev: 0.0009319391580406917",
            "extra": "mean: 13.120520500000529 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03266460587029091,
            "unit": "iter/sec",
            "range": "stddev: 0.0005866524071299629",
            "extra": "mean: 73.27886266666894 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03530262303498732,
            "unit": "iter/sec",
            "range": "stddev: 0.00013702302005647065",
            "extra": "mean: 67.80304016666605 msec\nrounds: 3"
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
          "id": "740def2d634bd7a9530667e002364209a5478f9f",
          "message": "Add check benchmarks (#1921)\n\nSkip when benchmarks are not required",
          "timestamp": "2026-08-27T17:09:37-03:00",
          "tree_id": "c07163fea95bfc69c9b4e6f4ba5bffa5d9ce319f",
          "url": "https://github.com/Mathics3/mathics-core/commit/740def2d634bd7a9530667e002364209a5478f9f"
        },
        "date": 1787861890907,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000014612451703961842",
            "extra": "mean: 2.299582773003676 msec\nrounds: 163"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 18.42892755047848,
            "unit": "iter/sec",
            "range": "stddev: 0.00003695414585417829",
            "extra": "mean: 124.78114999936452 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 18.66190760918551,
            "unit": "iter/sec",
            "range": "stddev: 0.00003485716292534222",
            "extra": "mean: 123.22335000050089 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 9.477931981135386,
            "unit": "iter/sec",
            "range": "stddev: 0.00009665495529283073",
            "extra": "mean: 242.6249499976052 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 9.923974060028662,
            "unit": "iter/sec",
            "range": "stddev: 0.00006262286050327123",
            "extra": "mean: 231.71995000126344 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.260201921085807,
            "unit": "iter/sec",
            "range": "stddev: 0.00009096217939619434",
            "extra": "mean: 705.3498000018976 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 16.862498573687045,
            "unit": "iter/sec",
            "range": "stddev: 0.00002785907541200552",
            "extra": "mean: 136.37260000081142 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 16.62863879334612,
            "unit": "iter/sec",
            "range": "stddev: 0.00004528161841086853",
            "extra": "mean: 138.29049999714016 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 4.417711152794135,
            "unit": "iter/sec",
            "range": "stddev: 0.0000656126708627364",
            "extra": "mean: 520.5371500011324 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 3.937769172672134,
            "unit": "iter/sec",
            "range": "stddev: 0.000030185076909516224",
            "extra": "mean: 583.9811000001305 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 3.721546685164401,
            "unit": "iter/sec",
            "range": "stddev: 0.00008146449026199573",
            "extra": "mean: 617.9105000001073 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 4.770408914788881,
            "unit": "iter/sec",
            "range": "stddev: 0.00004706919120007467",
            "extra": "mean: 482.051500003422 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 6.260007513377419,
            "unit": "iter/sec",
            "range": "stddev: 0.000028280851619688967",
            "extra": "mean: 367.3450500002673 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 5.138504522206033,
            "unit": "iter/sec",
            "range": "stddev: 0.000029487219658217143",
            "extra": "mean: 447.519850000333 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.010892625878298628,
            "unit": "iter/sec",
            "range": "stddev: 0.04665864009700473",
            "extra": "mean: 211.11372029999984 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.011710539367555532,
            "unit": "iter/sec",
            "range": "stddev: 0.0026192932319749197",
            "extra": "mean: 196.3686471499983 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.011696718429366449,
            "unit": "iter/sec",
            "range": "stddev: 0.0010844315918266667",
            "extra": "mean: 196.60067794999776 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 9.446599050963624,
            "unit": "iter/sec",
            "range": "stddev: 0.000039806358571559636",
            "extra": "mean: 243.42970000077457 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 9.835473035272495,
            "unit": "iter/sec",
            "range": "stddev: 0.000027662267825508282",
            "extra": "mean: 233.80499999916537 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5750062597670363,
            "unit": "iter/sec",
            "range": "stddev: 0.00031465206565474445",
            "extra": "mean: 3.999230850000401 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.16052272029915574,
            "unit": "iter/sec",
            "range": "stddev: 0.00045257318045873173",
            "extra": "mean: 14.325590599997895 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.05767580630602183,
            "unit": "iter/sec",
            "range": "stddev: 0.0012551472638964755",
            "extra": "mean: 39.870838750000814 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.29330923760474775,
            "unit": "iter/sec",
            "range": "stddev: 0.00043868585333155187",
            "extra": "mean: 7.840130749998764 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 9.246055532159703,
            "unit": "iter/sec",
            "range": "stddev: 0.00003533020559303458",
            "extra": "mean: 248.709600002428 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x]]",
            "value": 22.628298898870355,
            "unit": "iter/sec",
            "range": "stddev: 0.000020083946455879002",
            "extra": "mean: 101.6242000019929 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.6712697410595596,
            "unit": "iter/sec",
            "range": "stddev: 0.00005421822270954622",
            "extra": "mean: 626.3725999986036 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.3218007812095616,
            "unit": "iter/sec",
            "range": "stddev: 0.00011101272486076707",
            "extra": "mean: 990.4307000041968 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.9029764203152397,
            "unit": "iter/sec",
            "range": "stddev: 0.000051883928733435905",
            "extra": "mean: 589.1869499990321 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.5829264904035,
            "unit": "iter/sec",
            "range": "stddev: 0.00009918130553275316",
            "extra": "mean: 641.8169000014018 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.98859865570029,
            "unit": "iter/sec",
            "range": "stddev: 0.00009149278266704536",
            "extra": "mean: 1.1563835499998731 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.5356871450131044,
            "unit": "iter/sec",
            "range": "stddev: 0.00010089440626604651",
            "extra": "mean: 1.4974291999976685 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.429535595068942,
            "unit": "iter/sec",
            "range": "stddev: 0.00005835925116831084",
            "extra": "mean: 946.5112499981387 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.730733183484991,
            "unit": "iter/sec",
            "range": "stddev: 0.00009190561452179084",
            "extra": "mean: 842.1118500010039 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.9965588474015437,
            "unit": "iter/sec",
            "range": "stddev: 0.00005674694108768973",
            "extra": "mean: 1.1517730999997866 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.5356725823522688,
            "unit": "iter/sec",
            "range": "stddev: 0.00007967139374220898",
            "extra": "mean: 1.497443399999554 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.4019248266924507,
            "unit": "iter/sec",
            "range": "stddev: 0.00006113569855442939",
            "extra": "mean: 957.391650000261 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.7291263887759776,
            "unit": "iter/sec",
            "range": "stddev: 0.00007322553663858671",
            "extra": "mean: 842.6076500015256 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 2.0172041477962583,
            "unit": "iter/sec",
            "range": "stddev: 0.000052913092261703126",
            "extra": "mean: 1.139985149998779 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.5325025105131465,
            "unit": "iter/sec",
            "range": "stddev: 0.00008110423068226984",
            "extra": "mean: 1.500540950000584 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.4545370855827358,
            "unit": "iter/sec",
            "range": "stddev: 0.00004778036806462643",
            "extra": "mean: 936.8702499997994 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.6578491429389963,
            "unit": "iter/sec",
            "range": "stddev: 0.00007621751894271171",
            "extra": "mean: 865.2043999987313 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 7.648027059762375,
            "unit": "iter/sec",
            "range": "stddev: 0.000050496858325562466",
            "extra": "mean: 300.67659999559737 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.170075079346789,
            "unit": "iter/sec",
            "range": "stddev: 0.00027604379656363316",
            "extra": "mean: 1.0596789000018703 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.071814880942521,
            "unit": "iter/sec",
            "range": "stddev: 0.001993493185165064",
            "extra": "mean: 32.020978700002445 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.05449831344642373,
            "unit": "iter/sec",
            "range": "stddev: 0.0014605853531871496",
            "extra": "mean: 42.19548509999953 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.052690489084639636,
            "unit": "iter/sec",
            "range": "stddev: 0.0016299904001203492",
            "extra": "mean: 43.643223150002086 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.1662687526318103,
            "unit": "iter/sec",
            "range": "stddev: 0.00005535166873661391",
            "extra": "mean: 1.0615408500029844 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.146921617547906,
            "unit": "iter/sec",
            "range": "stddev: 0.000042896463156202264",
            "extra": "mean: 1.0711069999985057 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.015257315738184687,
            "unit": "iter/sec",
            "range": "stddev: 0.00495991283540276",
            "extra": "mean: 150.72000949999875 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.030938334111179758,
            "unit": "iter/sec",
            "range": "stddev: 0.00006474163622737219",
            "extra": "mean: 74.32794425000111 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.0867201066819816,
            "unit": "iter/sec",
            "range": "stddev: 0.00009474971096077803",
            "extra": "mean: 1.102008249999642 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.1611486662658446,
            "unit": "iter/sec",
            "range": "stddev: 0.000023856202380508185",
            "extra": "mean: 1.064055800000574 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 5.890017702789123,
            "unit": "iter/sec",
            "range": "stddev: 0.000046562819561051205",
            "extra": "mean: 390.4203499956793 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.618272932297843,
            "unit": "iter/sec",
            "range": "stddev: 0.00002659192145035758",
            "extra": "mean: 878.2822999990003 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 12.961369087359854,
            "unit": "iter/sec",
            "range": "stddev: 0.000019651784206276107",
            "extra": "mean: 177.41819999912423 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 13.166731212524757,
            "unit": "iter/sec",
            "range": "stddev: 0.000016433456963990973",
            "extra": "mean: 174.65100000038092 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 7.050772852743231,
            "unit": "iter/sec",
            "range": "stddev: 0.0000437732909964359",
            "extra": "mean: 326.1462000025972 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 4.143716041615563,
            "unit": "iter/sec",
            "range": "stddev: 0.00003255541226763171",
            "extra": "mean: 554.956649999383 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 2.617090405524992,
            "unit": "iter/sec",
            "range": "stddev: 0.0001434861880584514",
            "extra": "mean: 878.6791500014601 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.5403010796054637,
            "unit": "iter/sec",
            "range": "stddev: 0.00007345655362065225",
            "extra": "mean: 4.256113600000333 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 0.9526914763297268,
            "unit": "iter/sec",
            "range": "stddev: 0.00015584995060883384",
            "extra": "mean: 2.4137748999947917 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.7449624912994574,
            "unit": "iter/sec",
            "range": "stddev: 0.00010171207506855688",
            "extra": "mean: 3.0868436999995197 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.7770740923877026,
            "unit": "iter/sec",
            "range": "stddev: 0.00003885035431408402",
            "extra": "mean: 2.9592838000013444 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.0036377292052881234,
            "unit": "iter/sec",
            "range": "stddev: 0.051700281990304055",
            "extra": "mean: 632.1478711666609 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.21674262682203918,
            "unit": "iter/sec",
            "range": "stddev: 0.0011506053862940153",
            "extra": "mean: 10.609739333332868 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.04069818162167565,
            "unit": "iter/sec",
            "range": "stddev: 0.000309061992838494",
            "extra": "mean: 56.50332966667312 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.04197171715498704,
            "unit": "iter/sec",
            "range": "stddev: 0.00034413718566108227",
            "extra": "mean: 54.788865666661 msec\nrounds: 3"
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
          "id": "b0efda5870bf27e5c47469175b6299efc98cb105",
          "message": "replace string-arg-parameter has_form() with symbol. Part 1 (#1918)\n\nStart to replace the string first argument of `has_form` with a symbol\nfirst argument.\n\n---------\n\nCo-authored-by: Juan Mauricio Matera <matera@fisica.unlp.edu.ar>",
          "timestamp": "2026-08-27T16:47:36-04:00",
          "tree_id": "2b9af3d551ace2ddaf23f8534e38e984f9f34a38",
          "url": "https://github.com/Mathics3/mathics-core/commit/b0efda5870bf27e5c47469175b6299efc98cb105"
        },
        "date": 1787863779759,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000022036300486267132",
            "extra": "mean: 2.3509247999996723 msec\nrounds: 175"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 15.332601571198229,
            "unit": "iter/sec",
            "range": "stddev: 0.0000285484992915954",
            "extra": "mean: 153.32849999936116 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 15.297975507221295,
            "unit": "iter/sec",
            "range": "stddev: 0.000026104060649169853",
            "extra": "mean: 153.6755500026743 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 7.874101449502251,
            "unit": "iter/sec",
            "range": "stddev: 0.00010102389700155088",
            "extra": "mean: 298.56420000129447 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 5.516700461723858,
            "unit": "iter/sec",
            "range": "stddev: 0.0005011389713494788",
            "extra": "mean: 426.14690000135624 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 2.671237268385376,
            "unit": "iter/sec",
            "range": "stddev: 0.00006819741905654618",
            "extra": "mean: 880.0883500029499 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 14.163097714871807,
            "unit": "iter/sec",
            "range": "stddev: 0.000016783235877790633",
            "extra": "mean: 165.9894500008363 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 13.867312530913269,
            "unit": "iter/sec",
            "range": "stddev: 0.00003064774717101114",
            "extra": "mean: 169.52994999996918 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 3.7474653587642046,
            "unit": "iter/sec",
            "range": "stddev: 0.000033760685327955385",
            "extra": "mean: 627.3372999970661 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 3.393466148980408,
            "unit": "iter/sec",
            "range": "stddev: 0.000025824268743437276",
            "extra": "mean: 692.7798000006646 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 3.261130437451705,
            "unit": "iter/sec",
            "range": "stddev: 0.00006575733699059511",
            "extra": "mean: 720.8926000018323 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 3.975950060049794,
            "unit": "iter/sec",
            "range": "stddev: 0.00002995986092807624",
            "extra": "mean: 591.2863000020252 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 5.222885144299988,
            "unit": "iter/sec",
            "range": "stddev: 0.00002209971567220852",
            "extra": "mean: 450.11994999839544 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 4.25137324111315,
            "unit": "iter/sec",
            "range": "stddev: 0.00002375636351186048",
            "extra": "mean: 552.9800999980239 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.008833818986092463,
            "unit": "iter/sec",
            "range": "stddev: 0.03414779327988325",
            "extra": "mean: 266.1277986000002 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.009383619820647006,
            "unit": "iter/sec",
            "range": "stddev: 0.0054754908204987665",
            "extra": "mean: 250.53495825000027 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.009273067444003228,
            "unit": "iter/sec",
            "range": "stddev: 0.007340853336504069",
            "extra": "mean: 253.5218054000012 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 7.518460313341029,
            "unit": "iter/sec",
            "range": "stddev: 0.00002721444630626682",
            "extra": "mean: 312.68700000026683 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 7.693525434377052,
            "unit": "iter/sec",
            "range": "stddev: 0.00002138373118095584",
            "extra": "mean: 305.57184999935316 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.4558185794102625,
            "unit": "iter/sec",
            "range": "stddev: 0.00044271670696092964",
            "extra": "mean: 5.1575888000030545 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.1373272197380682,
            "unit": "iter/sec",
            "range": "stddev: 0.0006734487192824737",
            "extra": "mean: 17.11914654999731 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.04604245818198368,
            "unit": "iter/sec",
            "range": "stddev: 0.0015186298254604887",
            "extra": "mean: 51.05993234999744 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.2370439167849057,
            "unit": "iter/sec",
            "range": "stddev: 0.0004798818107335881",
            "extra": "mean: 9.91767614999759 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 7.284187199954009,
            "unit": "iter/sec",
            "range": "stddev: 0.000018903520154982426",
            "extra": "mean: 322.7436000017292 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x]]",
            "value": 17.115540877255913,
            "unit": "iter/sec",
            "range": "stddev: 0.000010381199456660148",
            "extra": "mean: 137.3561499960374 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 2.854099381440821,
            "unit": "iter/sec",
            "range": "stddev: 0.000041516297540580316",
            "extra": "mean: 823.7010999991412 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 1.850176624330252,
            "unit": "iter/sec",
            "range": "stddev: 0.00009810924724750505",
            "extra": "mean: 1.270648849998679 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.113536948739888,
            "unit": "iter/sec",
            "range": "stddev: 0.00004343849317344015",
            "extra": "mean: 755.0656500001196 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 2.932106955855184,
            "unit": "iter/sec",
            "range": "stddev: 0.00006734986937020435",
            "extra": "mean: 801.7868500004965 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.5560092902863674,
            "unit": "iter/sec",
            "range": "stddev: 0.0000645652322032875",
            "extra": "mean: 1.5108681000015167 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.220739125883412,
            "unit": "iter/sec",
            "range": "stddev: 0.00006745773805942548",
            "extra": "mean: 1.9258207999996557 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.0160972203325693,
            "unit": "iter/sec",
            "range": "stddev: 0.000032925165338624106",
            "extra": "mean: 1.1660770999981196 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.2053139823571026,
            "unit": "iter/sec",
            "range": "stddev: 0.00007146886905728198",
            "extra": "mean: 1.0660272500004453 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.5843522186271448,
            "unit": "iter/sec",
            "range": "stddev: 0.000029739465823684192",
            "extra": "mean: 1.4838397500000156 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.2257002049438646,
            "unit": "iter/sec",
            "range": "stddev: 0.00006407770102339073",
            "extra": "mean: 1.9180259499975705 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 1.9870430674242912,
            "unit": "iter/sec",
            "range": "stddev: 0.000031942763492415625",
            "extra": "mean: 1.1831272500032242 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.174940973577577,
            "unit": "iter/sec",
            "range": "stddev: 0.000051592535534749776",
            "extra": "mean: 1.080914300001723 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.572982956173753,
            "unit": "iter/sec",
            "range": "stddev: 0.00003596675375584525",
            "extra": "mean: 1.494564700000467 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.2224772554612455,
            "unit": "iter/sec",
            "range": "stddev: 0.00006568443701054993",
            "extra": "mean: 1.9230826500020726 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.0048159761379485,
            "unit": "iter/sec",
            "range": "stddev: 0.00002247951015531382",
            "extra": "mean: 1.1726387000010163 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.169914643292516,
            "unit": "iter/sec",
            "range": "stddev: 0.00008621643803257304",
            "extra": "mean: 1.0834181000006993 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 6.248773462901472,
            "unit": "iter/sec",
            "range": "stddev: 0.00004198926272220086",
            "extra": "mean: 376.2217999991435 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 1.9405813931744622,
            "unit": "iter/sec",
            "range": "stddev: 0.00026479288701762577",
            "extra": "mean: 1.211453850000055 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05551474282002797,
            "unit": "iter/sec",
            "range": "stddev: 0.002812080988543816",
            "extra": "mean: 42.34775629999916 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.04289448551663564,
            "unit": "iter/sec",
            "range": "stddev: 0.0019124351579879778",
            "extra": "mean: 54.80715694999816 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.04261171664787025,
            "unit": "iter/sec",
            "range": "stddev: 0.0006103001628439122",
            "extra": "mean: 55.170854050001594 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 1.9460525552834866,
            "unit": "iter/sec",
            "range": "stddev: 0.00006848577086500154",
            "extra": "mean: 1.2080479499985586 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 1.979168563503754,
            "unit": "iter/sec",
            "range": "stddev: 0.00002487238605591227",
            "extra": "mean: 1.1878345499980014 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.012446773203782827,
            "unit": "iter/sec",
            "range": "stddev: 0.004953897831541942",
            "extra": "mean: 188.87825475000852 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.02494335682199914,
            "unit": "iter/sec",
            "range": "stddev: 0.0012592461615327781",
            "extra": "mean: 94.25053800001137 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 1.8950582940426757,
            "unit": "iter/sec",
            "range": "stddev: 0.00022434514826583736",
            "extra": "mean: 1.2405554000054053 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.0836946124259694,
            "unit": "iter/sec",
            "range": "stddev: 0.000017244873348739847",
            "extra": "mean: 1.1282482499979096 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 5.258846654036972,
            "unit": "iter/sec",
            "range": "stddev: 0.00003435931439770687",
            "extra": "mean: 447.0418999943604 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.5240547644236018,
            "unit": "iter/sec",
            "range": "stddev: 0.000017729885801580326",
            "extra": "mean: 931.4079999910518 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 11.192843968333646,
            "unit": "iter/sec",
            "range": "stddev: 0.000013223565368603103",
            "extra": "mean: 210.0382000008949 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 11.440791644590933,
            "unit": "iter/sec",
            "range": "stddev: 0.000013665445157109585",
            "extra": "mean: 205.48619999658513 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 5.9736664939375155,
            "unit": "iter/sec",
            "range": "stddev: 0.00003181720975589607",
            "extra": "mean: 393.5480499933419 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 3.4349844116876493,
            "unit": "iter/sec",
            "range": "stddev: 0.00002514855184610445",
            "extra": "mean: 684.4062499965275 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 2.161474281106772,
            "unit": "iter/sec",
            "range": "stddev: 0.00016421098964138612",
            "extra": "mean: 1.0876487499984933 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.3744369499003422,
            "unit": "iter/sec",
            "range": "stddev: 0.0001230517503567953",
            "extra": "mean: 6.278559849997123 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 0.8947531837066935,
            "unit": "iter/sec",
            "range": "stddev: 0.00013160108813500837",
            "extra": "mean: 2.627456199999756 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.700791578497935,
            "unit": "iter/sec",
            "range": "stddev: 0.00006456808141481695",
            "extra": "mean: 3.3546704500054148 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.703558565515668,
            "unit": "iter/sec",
            "range": "stddev: 0.0000825915321859556",
            "extra": "mean: 3.3414770499973656 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.0029362172262966313,
            "unit": "iter/sec",
            "range": "stddev: 0.04117357732329996",
            "extra": "mean: 800.6644668333441 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.1893502094609902,
            "unit": "iter/sec",
            "range": "stddev: 0.0010292372266806225",
            "extra": "mean: 12.415749666672582 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03259455599338437,
            "unit": "iter/sec",
            "range": "stddev: 0.0014807377459465567",
            "extra": "mean: 72.12630233333546 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03579286168240597,
            "unit": "iter/sec",
            "range": "stddev: 0.0008180609004107239",
            "extra": "mean: 65.68138700000266 msec\nrounds: 3"
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
          "id": "5204e5d9ae3d907c2da549f38af37698f13356bd",
          "message": "More on benchmarks (#1922)\n\n* Few more benchmarks.\n* Avoid count parsing.\n* adjust number of iterations/rounds to reduce fluctuations.\n* Improve setup / clear cache on rounds.",
          "timestamp": "2026-08-28T13:58:00-03:00",
          "tree_id": "aaa1316b8c67fc0616efbc94c29a80399feb8f69",
          "url": "https://github.com/Mathics3/mathics-core/commit/5204e5d9ae3d907c2da549f38af37698f13356bd"
        },
        "date": 1787936408937,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.00013345515048191498",
            "extra": "mean: 2.3728537411772894 msec\nrounds: 170"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 19011.67698075845,
            "unit": "iter/sec",
            "range": "stddev: 2.7248237261979205e-9",
            "extra": "mean: 124.81033333244794 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 11.597980692893506,
            "unit": "iter/sec",
            "range": "stddev: 0.001197168777687187",
            "extra": "mean: 204.5919720000242 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.5895834730279814,
            "unit": "iter/sec",
            "range": "stddev: 0.00009004911016521726",
            "extra": "mean: 4.024627300000105 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 27.38145912946864,
            "unit": "iter/sec",
            "range": "stddev: 0.000007124601774421018",
            "extra": "mean: 86.65914150000731 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 13.81852278659118,
            "unit": "iter/sec",
            "range": "stddev: 0.000008429155845544852",
            "extra": "mean: 171.71544149999818 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 13.412617857622447,
            "unit": "iter/sec",
            "range": "stddev: 0.00004814504296265119",
            "extra": "mean: 176.91205149998268 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.6354150376211787,
            "unit": "iter/sec",
            "range": "stddev: 0.000010323666758095493",
            "extra": "mean: 652.7050464999888 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 23.371289374643073,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024907813413054696",
            "extra": "mean: 101.52857650000868 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 23.484522769584643,
            "unit": "iter/sec",
            "range": "stddev: 0.000001640816629835359",
            "extra": "mean: 101.03904449999845 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 7.44913080983727,
            "unit": "iter/sec",
            "range": "stddev: 0.00000734644924179977",
            "extra": "mean: 318.5410220000051 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 7.459008027769094,
            "unit": "iter/sec",
            "range": "stddev: 0.000004421439802191646",
            "extra": "mean: 318.11920999996346 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 7.176351087092131,
            "unit": "iter/sec",
            "range": "stddev: 0.000005956311775232608",
            "extra": "mean: 330.6490600000416 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 7.1142320141522495,
            "unit": "iter/sec",
            "range": "stddev: 0.0000058028913250999445",
            "extra": "mean: 333.53617600002394 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 10.181246720935274,
            "unit": "iter/sec",
            "range": "stddev: 0.000025882022181916647",
            "extra": "mean: 233.06121600001006 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 8.842276561787656,
            "unit": "iter/sec",
            "range": "stddev: 0.000003382028678290418",
            "extra": "mean: 268.3532599999978 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.009433068547338351,
            "unit": "iter/sec",
            "range": "stddev: 0.004860105900169545",
            "extra": "mean: 251.54632654999816 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.009503850551674381,
            "unit": "iter/sec",
            "range": "stddev: 0.001197431468530734",
            "extra": "mean: 249.67288030000034 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.00948812496307111,
            "unit": "iter/sec",
            "range": "stddev: 0.0016401052003787197",
            "extra": "mean: 250.08668734999944 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 16.371918264237625,
            "unit": "iter/sec",
            "range": "stddev: 0.000004231455503123019",
            "extra": "mean: 144.93437499993433 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 16.4117097689921,
            "unit": "iter/sec",
            "range": "stddev: 0.000003260067356109594",
            "extra": "mean: 144.5829699999024 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5165464097342571,
            "unit": "iter/sec",
            "range": "stddev: 0.000308218512840436",
            "extra": "mean: 4.593689350000574 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.14129464167584344,
            "unit": "iter/sec",
            "range": "stddev: 0.0005897339364639395",
            "extra": "mean: 16.793656950000013 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.050546710884094445,
            "unit": "iter/sec",
            "range": "stddev: 0.0013036518835719613",
            "extra": "mean: 46.94378130000061 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.23227058255908062,
            "unit": "iter/sec",
            "range": "stddev: 0.0014265351333929517",
            "extra": "mean: 10.215903000000992 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 13.00020019894528,
            "unit": "iter/sec",
            "range": "stddev: 0.000019532512676320862",
            "extra": "mean: 182.52439999884018 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 11.851214592949276,
            "unit": "iter/sec",
            "range": "stddev: 0.000015466775996502144",
            "extra": "mean: 200.22030000106383 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.625747922387656,
            "unit": "iter/sec",
            "range": "stddev: 0.000013079309432483974",
            "extra": "mean: 654.4453149999185 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.272391712594003,
            "unit": "iter/sec",
            "range": "stddev: 0.00001829627758427191",
            "extra": "mean: 1.044209820000006 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.9248583650427484,
            "unit": "iter/sec",
            "range": "stddev: 0.00004709988159415272",
            "extra": "mean: 604.570539999969 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.918031352022521,
            "unit": "iter/sec",
            "range": "stddev: 0.000011867527545729636",
            "extra": "mean: 605.6239800001606 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.8356083841088326,
            "unit": "iter/sec",
            "range": "stddev: 0.000021137908080603887",
            "extra": "mean: 1.2926797249998856 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.4120278231955903,
            "unit": "iter/sec",
            "range": "stddev: 0.000011604528340226825",
            "extra": "mean: 1.6804582049999794 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.385025240486969,
            "unit": "iter/sec",
            "range": "stddev: 0.000023767500963296228",
            "extra": "mean: 994.8967000000409 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.7562777789956066,
            "unit": "iter/sec",
            "range": "stddev: 0.000011049182140160896",
            "extra": "mean: 860.8906399999937 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.834775384154868,
            "unit": "iter/sec",
            "range": "stddev: 0.000016509130544253552",
            "extra": "mean: 1.2932666099999324 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.4198399974321492,
            "unit": "iter/sec",
            "range": "stddev: 0.00001044828050614309",
            "extra": "mean: 1.6712120699999389 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.399106843485903,
            "unit": "iter/sec",
            "range": "stddev: 0.000020327447045640625",
            "extra": "mean: 989.0571350000953 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.767381418956931,
            "unit": "iter/sec",
            "range": "stddev: 0.000008477527894593397",
            "extra": "mean: 857.4364650000632 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.8508968428193715,
            "unit": "iter/sec",
            "range": "stddev: 0.000013521743758848566",
            "extra": "mean: 1.282002155000086 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.4142869134291103,
            "unit": "iter/sec",
            "range": "stddev: 0.000015489965250926602",
            "extra": "mean: 1.6777739500000166 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.422628175410026,
            "unit": "iter/sec",
            "range": "stddev: 0.000014481655130362009",
            "extra": "mean: 979.4543649999811 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.7473629059010483,
            "unit": "iter/sec",
            "range": "stddev: 0.000014062978269529415",
            "extra": "mean: 863.6841299999531 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 8.86514975780133,
            "unit": "iter/sec",
            "range": "stddev: 0.0000055006741684355105",
            "extra": "mean: 267.6608749997911 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.365243381378408,
            "unit": "iter/sec",
            "range": "stddev: 0.000034796180549762644",
            "extra": "mean: 1.0032175799999266 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05693841458134652,
            "unit": "iter/sec",
            "range": "stddev: 0.0021961858552293325",
            "extra": "mean: 41.674039549999264 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.044289979030813144,
            "unit": "iter/sec",
            "range": "stddev: 0.0002750874269516664",
            "extra": "mean: 53.57540900000117 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.02746515567860302,
            "unit": "iter/sec",
            "range": "stddev: 0.000572004250326034",
            "extra": "mean: 86.39505884999892 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.042999599930154404,
            "unit": "iter/sec",
            "range": "stddev: 0.0026383138894685554",
            "extra": "mean: 55.18315856500038 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.228919911673602,
            "unit": "iter/sec",
            "range": "stddev: 0.000015903511225966653",
            "extra": "mean: 1.064575595000008 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.2175304985095963,
            "unit": "iter/sec",
            "range": "stddev: 0.000009251698143626989",
            "extra": "mean: 1.0700433400000975 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.012704462925545074,
            "unit": "iter/sec",
            "range": "stddev: 0.005085248926571798",
            "extra": "mean: 186.77324299999754 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.025355338666303677,
            "unit": "iter/sec",
            "range": "stddev: 0.0002810859056751915",
            "extra": "mean: 93.58398924999278 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.319500475269647,
            "unit": "iter/sec",
            "range": "stddev: 0.00001481458605274226",
            "extra": "mean: 1.0230020500002013 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.3158343900064127,
            "unit": "iter/sec",
            "range": "stddev: 0.0000143508388006027",
            "extra": "mean: 1.0246215149999216 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 7.672177123747381,
            "unit": "iter/sec",
            "range": "stddev: 0.000014834669231552823",
            "extra": "mean: 309.28036500000644 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.0108730891702256,
            "unit": "iter/sec",
            "range": "stddev: 0.00000911727337301007",
            "extra": "mean: 788.0949050002073 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 17.259460383371263,
            "unit": "iter/sec",
            "range": "stddev: 0.000002313053701399923",
            "extra": "mean: 137.48133999968104 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 17.597800007260556,
            "unit": "iter/sec",
            "range": "stddev: 0.000002713285178811947",
            "extra": "mean: 134.8380899997892 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 10.274212384491376,
            "unit": "iter/sec",
            "range": "stddev: 0.000006603482801853248",
            "extra": "mean: 230.95237399988378 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 6.267890849607113,
            "unit": "iter/sec",
            "range": "stddev: 0.000006314798699733589",
            "extra": "mean: 378.57292000003895 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 6.3713946250983975,
            "unit": "iter/sec",
            "range": "stddev: 0.00002204930289287771",
            "extra": "mean: 372.4229749998642 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 5.756250395246327,
            "unit": "iter/sec",
            "range": "stddev: 0.000013905944704679776",
            "extra": "mean: 412.2221199996545 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.33652155435236,
            "unit": "iter/sec",
            "range": "stddev: 0.000026139368110260713",
            "extra": "mean: 7.05111964000011 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.4138434145242647,
            "unit": "iter/sec",
            "range": "stddev: 0.000014656092903093667",
            "extra": "mean: 695.0681250000912 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.3985078434754637,
            "unit": "iter/sec",
            "range": "stddev: 0.000039442942418965186",
            "extra": "mean: 5.954346394999845 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.0379241612393995,
            "unit": "iter/sec",
            "range": "stddev: 0.000016203159855293584",
            "extra": "mean: 2.2861532949997354 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.82992053509929,
            "unit": "iter/sec",
            "range": "stddev: 0.000011153828041949122",
            "extra": "mean: 2.8591336650001153 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.8414298762617431,
            "unit": "iter/sec",
            "range": "stddev: 0.000016164085911214493",
            "extra": "mean: 2.8200255400001595 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.0031457871775979755,
            "unit": "iter/sec",
            "range": "stddev: 0.009188904950106",
            "extra": "mean: 754.2957000000001 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.1910543382887058,
            "unit": "iter/sec",
            "range": "stddev: 0.001994865514470296",
            "extra": "mean: 12.419784666661826 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03314280604361583,
            "unit": "iter/sec",
            "range": "stddev: 0.0003000264931588419",
            "extra": "mean: 71.59483533333362 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03601172456761889,
            "unit": "iter/sec",
            "range": "stddev: 0.0006220607756963386",
            "extra": "mean: 65.8911443333352 msec\nrounds: 3"
          }
        ]
      }
    ]
  }
}