window.BENCHMARK_DATA = {
  "lastUpdate": 1787861891755,
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
      }
    ]
  }
}