window.BENCHMARK_DATA = {
  "lastUpdate": 1787855600944,
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
      }
    ]
  }
}