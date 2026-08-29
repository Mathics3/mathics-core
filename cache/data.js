window.BENCHMARK_DATA = {
  "lastUpdate": 1788044657822,
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
          "id": "5204e5d9ae3d907c2da549f38af37698f13356bd",
          "message": "More on benchmarks (#1922)\n\n* Few more benchmarks.\n* Avoid count parsing.\n* adjust number of iterations/rounds to reduce fluctuations.\n* Improve setup / clear cache on rounds.",
          "timestamp": "2026-08-28T13:58:00-03:00",
          "tree_id": "aaa1316b8c67fc0616efbc94c29a80399feb8f69",
          "url": "https://github.com/Mathics3/mathics-core/commit/5204e5d9ae3d907c2da549f38af37698f13356bd"
        },
        "date": 1787944047657,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.00004364510775584946",
            "extra": "mean: 1.9912103134331784 msec\nrounds: 201"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 19497.58448781091,
            "unit": "iter/sec",
            "range": "stddev: 7.661873119686408e-10",
            "extra": "mean: 102.12600000159 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 10.28415894239823,
            "unit": "iter/sec",
            "range": "stddev: 0.0012527524690265626",
            "extra": "mean: 193.61916950000335 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.6047529850094703,
            "unit": "iter/sec",
            "range": "stddev: 0.00010098808135384059",
            "extra": "mean: 3.2926010500005987 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 28.07167600442122,
            "unit": "iter/sec",
            "range": "stddev: 0.000007200906378934886",
            "extra": "mean: 70.93307550000105 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 14.011119561728387,
            "unit": "iter/sec",
            "range": "stddev: 0.000007793463546800143",
            "extra": "mean: 142.1164315000354 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 14.000059808133429,
            "unit": "iter/sec",
            "range": "stddev: 0.000007695447873266882",
            "extra": "mean: 142.22870050000583 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.640741876691805,
            "unit": "iter/sec",
            "range": "stddev: 0.00000876401716089436",
            "extra": "mean: 546.9243305000546 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 23.518194734126954,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019092577753278076",
            "extra": "mean: 84.66680099998314 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 23.565755130630496,
            "unit": "iter/sec",
            "range": "stddev: 0.0000022561836113549594",
            "extra": "mean: 84.4959264999332 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 7.356816061550586,
            "unit": "iter/sec",
            "range": "stddev: 0.000006861672223455825",
            "extra": "mean: 270.6619679999847 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 7.108456192512296,
            "unit": "iter/sec",
            "range": "stddev: 0.00001652097680421519",
            "extra": "mean: 280.11853200004566 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 7.147958336325435,
            "unit": "iter/sec",
            "range": "stddev: 0.0000049693342559166144",
            "extra": "mean: 278.5704979999651 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 7.140939633455506,
            "unit": "iter/sec",
            "range": "stddev: 0.000006850603853241462",
            "extra": "mean: 278.84430000000293 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 10.332641422695648,
            "unit": "iter/sec",
            "range": "stddev: 0.000017542820120495193",
            "extra": "mean: 192.71067599999017 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 8.80388696773784,
            "unit": "iter/sec",
            "range": "stddev: 0.000005912008065244446",
            "extra": "mean: 226.17399799997884 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.009553031739073146,
            "unit": "iter/sec",
            "range": "stddev: 0.001189817489458372",
            "extra": "mean: 208.43752725000044 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.00937020289282101,
            "unit": "iter/sec",
            "range": "stddev: 0.006568385957768112",
            "extra": "mean: 212.50450349999852 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.009612538538790077,
            "unit": "iter/sec",
            "range": "stddev: 0.001201582030536726",
            "extra": "mean: 207.14718649999924 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 16.11255093760256,
            "unit": "iter/sec",
            "range": "stddev: 0.00000440509456501541",
            "extra": "mean: 123.58131999981481 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 16.120513274685077,
            "unit": "iter/sec",
            "range": "stddev: 0.000003704138694797488",
            "extra": "mean: 123.52028000002237 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5235876055402381,
            "unit": "iter/sec",
            "range": "stddev: 0.0003024470427073502",
            "extra": "mean: 3.8030127000020286 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.1463598453401643,
            "unit": "iter/sec",
            "range": "stddev: 0.0005595531183419463",
            "extra": "mean: 13.60489489999992 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.052947867236298574,
            "unit": "iter/sec",
            "range": "stddev: 0.0011195924236073066",
            "extra": "mean: 37.60699754999948 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.27301994070215896,
            "unit": "iter/sec",
            "range": "stddev: 0.0005265721606526691",
            "extra": "mean: 7.293277949999322 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 12.794259790738929,
            "unit": "iter/sec",
            "range": "stddev: 0.000020250786806299086",
            "extra": "mean: 155.63309999961916 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 11.717257965367791,
            "unit": "iter/sec",
            "range": "stddev: 0.000018260934221116958",
            "extra": "mean: 169.9382500000013 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.580749094573436,
            "unit": "iter/sec",
            "range": "stddev: 0.00000956309462267201",
            "extra": "mean: 556.087639999916 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.2344577402265955,
            "unit": "iter/sec",
            "range": "stddev: 0.000017436649922505886",
            "extra": "mean: 891.1380500001087 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.9441188548144677,
            "unit": "iter/sec",
            "range": "stddev: 0.000013007469931433964",
            "extra": "mean: 504.8555549999633 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.692709063440356,
            "unit": "iter/sec",
            "range": "stddev: 0.000019731549802453146",
            "extra": "mean: 539.2275099999466 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.7738579312522387,
            "unit": "iter/sec",
            "range": "stddev: 0.000025091046803212152",
            "extra": "mean: 1.122530885000188 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.3562857119116127,
            "unit": "iter/sec",
            "range": "stddev: 0.000016931581951253145",
            "extra": "mean: 1.4681348450000797 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.312038054510838,
            "unit": "iter/sec",
            "range": "stddev: 0.000018709772113715503",
            "extra": "mean: 861.2359600000019 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.672740372514133,
            "unit": "iter/sec",
            "range": "stddev: 0.000012636692733104661",
            "extra": "mean: 745.0070100000515 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.7732807896534328,
            "unit": "iter/sec",
            "range": "stddev: 0.000017229743724960676",
            "extra": "mean: 1.1228962299999523 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.357616960560506,
            "unit": "iter/sec",
            "range": "stddev: 0.000016833132004056496",
            "extra": "mean: 1.466695225000052 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.3369722247892835,
            "unit": "iter/sec",
            "range": "stddev: 0.000013913540935554376",
            "extra": "mean: 852.0470599999186 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.6895029480449137,
            "unit": "iter/sec",
            "range": "stddev: 0.000011727819849122119",
            "extra": "mean: 740.363685000105 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.769745557761524,
            "unit": "iter/sec",
            "range": "stddev: 0.000017760730650181873",
            "extra": "mean: 1.1251393200002013 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.3430127866795878,
            "unit": "iter/sec",
            "range": "stddev: 0.000018911985975056563",
            "extra": "mean: 1.482644344999997 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.3150180319323805,
            "unit": "iter/sec",
            "range": "stddev: 0.000018888287289717802",
            "extra": "mean: 860.1273450000236 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.669120774271967,
            "unit": "iter/sec",
            "range": "stddev: 0.000019785223727421576",
            "extra": "mean: 746.0173150000315 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 8.905506183219325,
            "unit": "iter/sec",
            "range": "stddev: 0.000005180309927979522",
            "extra": "mean: 223.59316500001114 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.4547148790866316,
            "unit": "iter/sec",
            "range": "stddev: 0.00003147142747693181",
            "extra": "mean: 811.1778399999281 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05768138586312224,
            "unit": "iter/sec",
            "range": "stddev: 0.002001015420499378",
            "extra": "mean: 34.52084729999925 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.044262276660981106,
            "unit": "iter/sec",
            "range": "stddev: 0.00026021421576961337",
            "extra": "mean: 44.98662209999935 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.026896274947324775,
            "unit": "iter/sec",
            "range": "stddev: 0.0009064660188843113",
            "extra": "mean: 74.03294014999773 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.04256232558541273,
            "unit": "iter/sec",
            "range": "stddev: 0.00289108614746567",
            "extra": "mean: 46.78340024999997 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.2972449164357145,
            "unit": "iter/sec",
            "range": "stddev: 0.000021250312860442978",
            "extra": "mean: 866.7818999998644 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.333486306560839,
            "unit": "iter/sec",
            "range": "stddev: 0.000007454170564288202",
            "extra": "mean: 853.3199049999496 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.011989085842527471,
            "unit": "iter/sec",
            "range": "stddev: 0.00474227243920571",
            "extra": "mean: 166.08524950000714 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.024777949924307884,
            "unit": "iter/sec",
            "range": "stddev: 0.0007537429482816892",
            "extra": "mean: 80.36218974999798 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.421910574605902,
            "unit": "iter/sec",
            "range": "stddev: 0.000018375281857887666",
            "extra": "mean: 822.1650849999662 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.4422278502694006,
            "unit": "iter/sec",
            "range": "stddev: 0.000023698612516217125",
            "extra": "mean: 815.3253649996373 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 7.963218827524578,
            "unit": "iter/sec",
            "range": "stddev: 0.000015608768591991714",
            "extra": "mean: 250.0509350001323 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.0231317625025684,
            "unit": "iter/sec",
            "range": "stddev: 0.000014318721507016422",
            "extra": "mean: 658.6581299998784 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 18.344432002095843,
            "unit": "iter/sec",
            "range": "stddev: 0.0000025962584687879517",
            "extra": "mean: 108.54575999985627 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 18.468137627837212,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020526821460553562",
            "extra": "mean: 107.81868500004066 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 10.396494264281813,
            "unit": "iter/sec",
            "range": "stddev: 0.000007399184245721172",
            "extra": "mean: 191.52709200005802 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 6.344973543486371,
            "unit": "iter/sec",
            "range": "stddev: 0.000007784811160506649",
            "extra": "mean: 313.8248409998994 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 6.457318514547812,
            "unit": "iter/sec",
            "range": "stddev: 0.000018445878112911026",
            "extra": "mean: 308.36488999995026 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 5.719766127445402,
            "unit": "iter/sec",
            "range": "stddev: 0.000012937509293929712",
            "extra": "mean: 348.12792500005685 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.33629345280718576,
            "unit": "iter/sec",
            "range": "stddev: 0.000035195628496383786",
            "extra": "mean: 5.92104989500001 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.386601154108032,
            "unit": "iter/sec",
            "range": "stddev: 0.000013919436217506685",
            "extra": "mean: 587.9671750001592 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.4082729045729951,
            "unit": "iter/sec",
            "range": "stddev: 0.000014031912728695326",
            "extra": "mean: 4.877155184999964 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.0413890586559191,
            "unit": "iter/sec",
            "range": "stddev: 0.000024839498568502178",
            "extra": "mean: 1.91207147500009 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.8258990143071101,
            "unit": "iter/sec",
            "range": "stddev: 0.000013763620925789667",
            "extra": "mean: 2.4109610000003556 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.8418884348657304,
            "unit": "iter/sec",
            "range": "stddev: 0.000015494003647905126",
            "extra": "mean: 2.3651712400001657 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.0030817866695990606,
            "unit": "iter/sec",
            "range": "stddev: 0.008865950875472022",
            "extra": "mean: 646.1220476666654 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.17187008420684113,
            "unit": "iter/sec",
            "range": "stddev: 0.001761517071376294",
            "extra": "mean: 11.585555000001099 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03414635199684389,
            "unit": "iter/sec",
            "range": "stddev: 0.0003508734947398726",
            "extra": "mean: 58.31399833332777 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.0362340738422506,
            "unit": "iter/sec",
            "range": "stddev: 0.0006439455844015897",
            "extra": "mean: 54.954083333332925 msec\nrounds: 3"
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
        "date": 1787944182015,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000012426851154500541",
            "extra": "mean: 2.3129683023247654 msec\nrounds: 172"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 16629.013595481578,
            "unit": "iter/sec",
            "range": "stddev: 1.0137367770705076e-8",
            "extra": "mean: 139.09233335122434 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 10.43576669296641,
            "unit": "iter/sec",
            "range": "stddev: 0.001665574871349418",
            "extra": "mean: 221.63855999997392 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.5937606560415201,
            "unit": "iter/sec",
            "range": "stddev: 0.00010575724232573882",
            "extra": "mean: 3.8954556500002013 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 41.32399060662434,
            "unit": "iter/sec",
            "range": "stddev: 0.00000773142031584644",
            "extra": "mean: 55.97156199996789 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 19.875530233661195,
            "unit": "iter/sec",
            "range": "stddev: 0.000008636385912405176",
            "extra": "mean: 116.37265899993565 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 19.849935284712828,
            "unit": "iter/sec",
            "range": "stddev: 0.000008462820653163595",
            "extra": "mean: 116.52271250002855 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 4.666206875226898,
            "unit": "iter/sec",
            "range": "stddev: 0.000009000872088534546",
            "extra": "mean: 495.6849029999972 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 34.43567364231254,
            "unit": "iter/sec",
            "range": "stddev: 0.000002964214024054338",
            "extra": "mean: 67.16779599986467 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 34.78876948576346,
            "unit": "iter/sec",
            "range": "stddev: 0.000002222681249056885",
            "extra": "mean: 66.48606249989086 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 9.466756618563815,
            "unit": "iter/sec",
            "range": "stddev: 0.000008984263372538036",
            "extra": "mean: 244.3253159999017 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 9.526039798274129,
            "unit": "iter/sec",
            "range": "stddev: 0.000004900980483573526",
            "extra": "mean: 242.80481200003123 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 9.035914491511747,
            "unit": "iter/sec",
            "range": "stddev: 0.000003675282647021862",
            "extra": "mean: 255.97501000009967 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 9.310689730150406,
            "unit": "iter/sec",
            "range": "stddev: 0.000004149971520238657",
            "extra": "mean: 248.42072600000623 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 13.79908536956565,
            "unit": "iter/sec",
            "range": "stddev: 0.00002224419082743032",
            "extra": "mean: 167.61750799992114 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 11.508971210882963,
            "unit": "iter/sec",
            "range": "stddev: 0.000003086824220493813",
            "extra": "mean: 200.97089999995885 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.012093839246749418,
            "unit": "iter/sec",
            "range": "stddev: 0.0018602967211776404",
            "extra": "mean: 191.25178159999479 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.01211153441365699,
            "unit": "iter/sec",
            "range": "stddev: 0.0009372951872541714",
            "extra": "mean: 190.9723593499976 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.012011830692204453,
            "unit": "iter/sec",
            "range": "stddev: 0.004448316495084578",
            "extra": "mean: 192.55751780000168 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 22.218425410839444,
            "unit": "iter/sec",
            "range": "stddev: 0.000005242539109118777",
            "extra": "mean: 104.10135999990189 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 22.34180917656283,
            "unit": "iter/sec",
            "range": "stddev: 0.0000040086959855443936",
            "extra": "mean: 103.52645499949631 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.6160080753624964,
            "unit": "iter/sec",
            "range": "stddev: 0.0003305089637709258",
            "extra": "mean: 3.7547694500005946 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.1660795344841825,
            "unit": "iter/sec",
            "range": "stddev: 0.000517970127398637",
            "extra": "mean: 13.926871299997856 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.05902426794661539,
            "unit": "iter/sec",
            "range": "stddev: 0.0011539465051936505",
            "extra": "mean: 39.18673424999923 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.3018807818507237,
            "unit": "iter/sec",
            "range": "stddev: 0.00045878342389134194",
            "extra": "mean: 7.661860049999802 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 16.52461921486666,
            "unit": "iter/sec",
            "range": "stddev: 0.000029003318213511402",
            "extra": "mean: 139.97104999816656 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 15.413104532292767,
            "unit": "iter/sec",
            "range": "stddev: 0.00002268878186503388",
            "extra": "mean: 150.06505000201287 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 4.509059878787592,
            "unit": "iter/sec",
            "range": "stddev: 0.000014822503413764465",
            "extra": "mean: 512.9602099998465 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.8156740096795856,
            "unit": "iter/sec",
            "range": "stddev: 0.00003055388940462833",
            "extra": "mean: 821.4616800003682 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 5.010611794389738,
            "unit": "iter/sec",
            "range": "stddev: 0.000012500257523604343",
            "extra": "mean: 461.61394999998606 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 4.816858925576778,
            "unit": "iter/sec",
            "range": "stddev: 0.000015626408877551106",
            "extra": "mean: 480.1818649998779 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 2.2745472081491247,
            "unit": "iter/sec",
            "range": "stddev: 0.00002459123257132765",
            "extra": "mean: 1.0168917549998466 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.7251952668849755,
            "unit": "iter/sec",
            "range": "stddev: 0.000028396549278510707",
            "extra": "mean: 1.3406994249996274 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.8811680127748827,
            "unit": "iter/sec",
            "range": "stddev: 0.000020654299495852193",
            "extra": "mean: 802.7884150001796 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 3.410156658043133,
            "unit": "iter/sec",
            "range": "stddev: 0.000011033277165431056",
            "extra": "mean: 678.2586649998734 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 2.2710119359169556,
            "unit": "iter/sec",
            "range": "stddev: 0.000030353675622359954",
            "extra": "mean: 1.0184747449999065 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.7341874862272513,
            "unit": "iter/sec",
            "range": "stddev: 0.000023172535765878576",
            "extra": "mean: 1.3337475449996816 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.8794554867895066,
            "unit": "iter/sec",
            "range": "stddev: 0.000017803020299742446",
            "extra": "mean: 803.2658649999291 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 3.403912083568786,
            "unit": "iter/sec",
            "range": "stddev: 0.000013832913386115878",
            "extra": "mean: 679.502949999744 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 2.2910631837530344,
            "unit": "iter/sec",
            "range": "stddev: 0.000015729844259374506",
            "extra": "mean: 1.0095611149998263 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.7441873639776708,
            "unit": "iter/sec",
            "range": "stddev: 0.000020161328138631476",
            "extra": "mean: 1.3261008249996564 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.9048138207350838,
            "unit": "iter/sec",
            "range": "stddev: 0.000014305302770909724",
            "extra": "mean: 796.2535449998143 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 3.2375811792259235,
            "unit": "iter/sec",
            "range": "stddev: 0.00008188019051119644",
            "extra": "mean: 714.412450000026 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 10.892218944332209,
            "unit": "iter/sec",
            "range": "stddev: 0.000006753700099215589",
            "extra": "mean: 212.35051500028135 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.5710769139645273,
            "unit": "iter/sec",
            "range": "stddev: 0.00003647694294458466",
            "extra": "mean: 899.6106999997268 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.0740289212338564,
            "unit": "iter/sec",
            "range": "stddev: 0.00204834200969866",
            "extra": "mean: 31.244117350003364 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.057048124093544664,
            "unit": "iter/sec",
            "range": "stddev: 0.00023839594453213664",
            "extra": "mean: 40.54416054999592 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.03348275569827243,
            "unit": "iter/sec",
            "range": "stddev: 0.00037108071427200556",
            "extra": "mean: 69.07938890000338 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.05361803918942829,
            "unit": "iter/sec",
            "range": "stddev: 0.0039058186087867824",
            "extra": "mean: 43.13787556000008 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.489707911629707,
            "unit": "iter/sec",
            "range": "stddev: 0.000022722324856294914",
            "extra": "mean: 929.0119099998151 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.455593468249361,
            "unit": "iter/sec",
            "range": "stddev: 0.000011152715815076254",
            "extra": "mean: 941.918249999958 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.015550115182349116,
            "unit": "iter/sec",
            "range": "stddev: 0.0050810777036686145",
            "extra": "mean: 148.74284049999886 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.028887862348821066,
            "unit": "iter/sec",
            "range": "stddev: 0.007281190248749445",
            "extra": "mean: 80.0671324999982 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.163036497401352,
            "unit": "iter/sec",
            "range": "stddev: 0.0002071941374008817",
            "extra": "mean: 1.0693154300001595 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.44576191137992,
            "unit": "iter/sec",
            "range": "stddev: 0.000021677568969426528",
            "extra": "mean: 945.704604999662 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 8.88894214594925,
            "unit": "iter/sec",
            "range": "stddev: 0.000018058720661771058",
            "extra": "mean: 260.20737500005 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.14327833477671,
            "unit": "iter/sec",
            "range": "stddev: 0.0000153527923740174",
            "extra": "mean: 735.845845000256 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 21.96037642783256,
            "unit": "iter/sec",
            "range": "stddev: 0.000005100547834341448",
            "extra": "mean: 105.32462000028886 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 22.238633249693454,
            "unit": "iter/sec",
            "range": "stddev: 0.000004297684380375026",
            "extra": "mean: 104.00676500012196 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 13.21017637710388,
            "unit": "iter/sec",
            "range": "stddev: 0.00000754714142997062",
            "extra": "mean: 175.0898879998033 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 7.90286872334366,
            "unit": "iter/sec",
            "range": "stddev: 0.000009424765703679518",
            "extra": "mean: 292.67451900000196 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 8.03143289071959,
            "unit": "iter/sec",
            "range": "stddev: 0.000015126775407405055",
            "extra": "mean: 287.98949500000504 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 6.829903203402754,
            "unit": "iter/sec",
            "range": "stddev: 0.000013184022873328265",
            "extra": "mean: 338.6531599997511 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.3802629528748326,
            "unit": "iter/sec",
            "range": "stddev: 0.0002436585559598081",
            "extra": "mean: 6.082549680000255 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 4.173190429989583,
            "unit": "iter/sec",
            "range": "stddev: 0.000017970886601078587",
            "extra": "mean: 554.2446099998699 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.5723154387320357,
            "unit": "iter/sec",
            "range": "stddev: 0.00015458057328818063",
            "extra": "mean: 4.04142216999972 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.1157131396049287,
            "unit": "iter/sec",
            "range": "stddev: 0.00009368038956993806",
            "extra": "mean: 2.0730851149998837 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.9130146246616245,
            "unit": "iter/sec",
            "range": "stddev: 0.000019475296033383532",
            "extra": "mean: 2.533331055000332 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.926260707035002,
            "unit": "iter/sec",
            "range": "stddev: 0.00001570282957726229",
            "extra": "mean: 2.4971029050003324 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.003951670649934411,
            "unit": "iter/sec",
            "range": "stddev: 0.007851924581743972",
            "extra": "mean: 585.314037333338 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.16807470193210045,
            "unit": "iter/sec",
            "range": "stddev: 0.00297123441366523",
            "extra": "mean: 13.761549333338507 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.040303531788251995,
            "unit": "iter/sec",
            "range": "stddev: 0.0013370577486902999",
            "extra": "mean: 57.38872500000033 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.041737651362393616,
            "unit": "iter/sec",
            "range": "stddev: 0.0006495185894491275",
            "extra": "mean: 55.416829333353235 msec\nrounds: 3"
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
        "date": 1787944421630,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000026406046217248315",
            "extra": "mean: 1.9385997386955833 msec\nrounds: 199"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 19631.257227362497,
            "unit": "iter/sec",
            "range": "stddev: 2.886261658063335e-9",
            "extra": "mean: 98.750666666092 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 9.507914072675554,
            "unit": "iter/sec",
            "range": "stddev: 0.0013735671336277617",
            "extra": "mean: 203.8932749999134 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.6124234336174449,
            "unit": "iter/sec",
            "range": "stddev: 0.00009441791408004813",
            "extra": "mean: 3.1654564999982426 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 28.137198057123854,
            "unit": "iter/sec",
            "range": "stddev: 0.000006812331490472484",
            "extra": "mean: 68.89810900004534 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 14.027772204629203,
            "unit": "iter/sec",
            "range": "stddev: 0.000007910762843930542",
            "extra": "mean: 138.1972640000413 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 13.554692449865417,
            "unit": "iter/sec",
            "range": "stddev: 0.0000122013569668814",
            "extra": "mean: 143.02056250009798 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.6306697202614497,
            "unit": "iter/sec",
            "range": "stddev: 0.0000212718851378931",
            "extra": "mean: 533.9510030000696 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 23.66034796640188,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015858220506363594",
            "extra": "mean: 81.93454049992965 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 23.795515880045773,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013114464344165436",
            "extra": "mean: 81.46912000009365 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 7.357242860439641,
            "unit": "iter/sec",
            "range": "stddev: 0.000006145601037668843",
            "extra": "mean: 263.4954119999975 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 7.3659778042553405,
            "unit": "iter/sec",
            "range": "stddev: 0.000005501010776725791",
            "extra": "mean: 263.1829460001427 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 7.1290554357537905,
            "unit": "iter/sec",
            "range": "stddev: 0.000005211301651626455",
            "extra": "mean: 271.9293960000755 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 7.105420277806549,
            "unit": "iter/sec",
            "range": "stddev: 0.000004502724427570014",
            "extra": "mean: 272.83392999999023 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 10.293560527433938,
            "unit": "iter/sec",
            "range": "stddev: 0.000017637173535311406",
            "extra": "mean: 188.33130999996683 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 8.74458867582785,
            "unit": "iter/sec",
            "range": "stddev: 0.000004893617706309046",
            "extra": "mean: 221.69135799998685 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.009624449280126034,
            "unit": "iter/sec",
            "range": "stddev: 0.0012210241820165121",
            "extra": "mean: 201.4244849000022 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.009637810942365694,
            "unit": "iter/sec",
            "range": "stddev: 0.0007745216163410343",
            "extra": "mean: 201.14523415000036 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.009601991284141439,
            "unit": "iter/sec",
            "range": "stddev: 0.0007911579125157214",
            "extra": "mean: 201.89559450000303 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 16.199971643788306,
            "unit": "iter/sec",
            "range": "stddev: 0.0000035207270552939586",
            "extra": "mean: 119.6668599996542 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 16.26164235054319,
            "unit": "iter/sec",
            "range": "stddev: 0.000002971178168626242",
            "extra": "mean: 119.21303500017189 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5291776762316982,
            "unit": "iter/sec",
            "range": "stddev: 0.00030191201234798943",
            "extra": "mean: 3.6634193500006518 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.1472825237703294,
            "unit": "iter/sec",
            "range": "stddev: 0.00046058714608567756",
            "extra": "mean: 13.162455999997746 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.05284168236353958,
            "unit": "iter/sec",
            "range": "stddev: 0.0010510882898098859",
            "extra": "mean: 36.686942049998095 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.26633746366592415,
            "unit": "iter/sec",
            "range": "stddev: 0.0005995099715516795",
            "extra": "mean: 7.278734700001621 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 13.005922564218999,
            "unit": "iter/sec",
            "range": "stddev: 0.000018770016957781226",
            "extra": "mean: 149.0551499998105 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 11.832880462001867,
            "unit": "iter/sec",
            "range": "stddev: 0.0000166380872043921",
            "extra": "mean: 163.83159999975305 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.601523524348952,
            "unit": "iter/sec",
            "range": "stddev: 0.000011374890949379064",
            "extra": "mean: 538.2721299997684 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.249780685167963,
            "unit": "iter/sec",
            "range": "stddev: 0.000020323551985265332",
            "extra": "mean: 861.6838749999545 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.9728027508215726,
            "unit": "iter/sec",
            "range": "stddev: 0.000010409388533062204",
            "extra": "mean: 487.96777999982055 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.834004736552121,
            "unit": "iter/sec",
            "range": "stddev: 0.000015749128568070447",
            "extra": "mean: 505.63310999947925 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.682249894989014,
            "unit": "iter/sec",
            "range": "stddev: 0.00005347418869852858",
            "extra": "mean: 1.1523851149999587 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.296703849536544,
            "unit": "iter/sec",
            "range": "stddev: 0.000050356909933165326",
            "extra": "mean: 1.4950211950002767 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.2029375137018765,
            "unit": "iter/sec",
            "range": "stddev: 0.000020509240265896157",
            "extra": "mean: 880.0066850002963 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.589871950340803,
            "unit": "iter/sec",
            "range": "stddev: 0.000023688302633369788",
            "extra": "mean: 748.5311149999063 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.7535367563438944,
            "unit": "iter/sec",
            "range": "stddev: 0.000018869132314290507",
            "extra": "mean: 1.1055369850002705 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.3220652874171117,
            "unit": "iter/sec",
            "range": "stddev: 0.000020146531184413776",
            "extra": "mean: 1.4663419099997554 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.251142485964323,
            "unit": "iter/sec",
            "range": "stddev: 0.000022691489664149695",
            "extra": "mean: 861.1626100002923 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.580338023521597,
            "unit": "iter/sec",
            "range": "stddev: 0.00002678834357541215",
            "extra": "mean: 751.2968150001598 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.6960908462069286,
            "unit": "iter/sec",
            "range": "stddev: 0.00003519575826491572",
            "extra": "mean: 1.1429810750001934 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.3325649136031557,
            "unit": "iter/sec",
            "range": "stddev: 0.00004280230658227922",
            "extra": "mean: 1.454788220000296 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.298924538379217,
            "unit": "iter/sec",
            "range": "stddev: 0.00001116674768271221",
            "extra": "mean: 843.2637550001232 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.6129063190612087,
            "unit": "iter/sec",
            "range": "stddev: 0.00002359764172176566",
            "extra": "mean: 741.9323550000456 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 8.932785382790277,
            "unit": "iter/sec",
            "range": "stddev: 0.000004417381640886358",
            "extra": "mean: 217.0207449997008 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.4576976857699777,
            "unit": "iter/sec",
            "range": "stddev: 0.000027973851654205605",
            "extra": "mean: 788.7868999999625 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05741559360746269,
            "unit": "iter/sec",
            "range": "stddev: 0.0019546434061872807",
            "extra": "mean: 33.76434200000347 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.04428468696734483,
            "unit": "iter/sec",
            "range": "stddev: 0.00014538168116095057",
            "extra": "mean: 43.77584830000245 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.027138211536597276,
            "unit": "iter/sec",
            "range": "stddev: 0.0007008849932775797",
            "extra": "mean: 71.43432189999999 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.04242751858224661,
            "unit": "iter/sec",
            "range": "stddev: 0.002982824124593693",
            "extra": "mean: 45.69203675999972 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.2946845909932705,
            "unit": "iter/sec",
            "range": "stddev: 0.000018402919535020804",
            "extra": "mean: 844.8218749995817 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.326675774855424,
            "unit": "iter/sec",
            "range": "stddev: 0.000005199894452239561",
            "extra": "mean: 833.2057949999695 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.012055933079932617,
            "unit": "iter/sec",
            "range": "stddev: 0.004624172525266449",
            "extra": "mean: 160.80047275000453 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.024623833391299307,
            "unit": "iter/sec",
            "range": "stddev: 0.0009932492074612544",
            "extra": "mean: 78.72859225000184 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.4088683080185644,
            "unit": "iter/sec",
            "range": "stddev: 0.00001990641651503102",
            "extra": "mean: 804.7761400000297 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.4134078113985096,
            "unit": "iter/sec",
            "range": "stddev: 0.000016706843980333394",
            "extra": "mean: 803.2623949999618 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 7.903147089348357,
            "unit": "iter/sec",
            "range": "stddev: 0.000018206271245733375",
            "extra": "mean: 245.2946549999524 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.9559612170020357,
            "unit": "iter/sec",
            "range": "stddev: 0.000014095859166789593",
            "extra": "mean: 655.8271900000534 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 17.94281879165806,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026997356873485428",
            "extra": "mean: 108.04320999980632 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 18.10171255886697,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020469123019592118",
            "extra": "mean: 107.09482500018909 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 10.428487987954798,
            "unit": "iter/sec",
            "range": "stddev: 0.00000654103917146918",
            "extra": "mean: 185.89461299995946 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 6.231013706211447,
            "unit": "iter/sec",
            "range": "stddev: 0.000011312636613609486",
            "extra": "mean: 311.12108400003535 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 6.554382938017636,
            "unit": "iter/sec",
            "range": "stddev: 0.00001496876829101925",
            "extra": "mean: 295.77150999998025 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 5.667968011250662,
            "unit": "iter/sec",
            "range": "stddev: 0.00001253506763355148",
            "extra": "mean: 342.0272900001464 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.3262086589114437,
            "unit": "iter/sec",
            "range": "stddev: 0.00024034829994920651",
            "extra": "mean: 5.942821214999867 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.3566965493888294,
            "unit": "iter/sec",
            "range": "stddev: 0.000013777046415448388",
            "extra": "mean: 577.5320200000067 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.40234479853597077,
            "unit": "iter/sec",
            "range": "stddev: 0.000013036205734571269",
            "extra": "mean: 4.818254755000311 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.0439379035515226,
            "unit": "iter/sec",
            "range": "stddev: 0.000014863740327052537",
            "extra": "mean: 1.8570067549998726 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.8205957152754114,
            "unit": "iter/sec",
            "range": "stddev: 0.000016172845234921944",
            "extra": "mean: 2.362429760000566 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.8344742380476777,
            "unit": "iter/sec",
            "range": "stddev: 0.000017968890463511434",
            "extra": "mean: 2.323139109999488 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.0030574593618258937,
            "unit": "iter/sec",
            "range": "stddev: 0.01452263534450055",
            "extra": "mean: 634.055766333347 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.17079549916252243,
            "unit": "iter/sec",
            "range": "stddev: 0.0018075158446292261",
            "extra": "mean: 11.35041466667038 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03363783692362972,
            "unit": "iter/sec",
            "range": "stddev: 0.0012069801028872357",
            "extra": "mean: 57.631521999970424 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.0362100181841199,
            "unit": "iter/sec",
            "range": "stddev: 0.0008390472507790638",
            "extra": "mean: 53.53766266667511 msec\nrounds: 3"
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
        "date": 1787969997123,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000018408782128998618",
            "extra": "mean: 1.811306105504971 msec\nrounds: 218"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 19.278094116891197,
            "unit": "iter/sec",
            "range": "stddev: 0.000025463464657683586",
            "extra": "mean: 93.95669999960887 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 18.932507302447043,
            "unit": "iter/sec",
            "range": "stddev: 0.000025765400922239884",
            "extra": "mean: 95.67174999958183 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 10.112246537986138,
            "unit": "iter/sec",
            "range": "stddev: 0.00005773626122095479",
            "extra": "mean: 179.1200500008472 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 10.112509061289321,
            "unit": "iter/sec",
            "range": "stddev: 0.00004919164225794717",
            "extra": "mean: 179.11539999886372 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.326434469303831,
            "unit": "iter/sec",
            "range": "stddev: 0.00007128739235173774",
            "extra": "mean: 544.5188000003043 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 17.481430740238718,
            "unit": "iter/sec",
            "range": "stddev: 0.000020869437635523574",
            "extra": "mean: 103.61315000011473 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 16.78528617084499,
            "unit": "iter/sec",
            "range": "stddev: 0.000037629237085827975",
            "extra": "mean: 107.91034999755311 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 4.55185353777638,
            "unit": "iter/sec",
            "range": "stddev: 0.00003905764506370172",
            "extra": "mean: 397.92715000004364 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 4.020969230578249,
            "unit": "iter/sec",
            "range": "stddev: 0.000025544228337488028",
            "extra": "mean: 450.46505000101433 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 3.8366078373378407,
            "unit": "iter/sec",
            "range": "stddev: 0.00006097554569835148",
            "extra": "mean: 472.1113499996932 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 4.863009292671532,
            "unit": "iter/sec",
            "range": "stddev: 0.00003691115949141587",
            "extra": "mean: 372.4660999999685 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 6.383655618240095,
            "unit": "iter/sec",
            "range": "stddev: 0.00002341527859140055",
            "extra": "mean: 283.7411999998096 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 5.2346090081363945,
            "unit": "iter/sec",
            "range": "stddev: 0.000023048666348701555",
            "extra": "mean: 346.02510000070197 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.011245273852509102,
            "unit": "iter/sec",
            "range": "stddev: 0.03820692477019952",
            "extra": "mean: 161.07265409999982 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.01209008478841707,
            "unit": "iter/sec",
            "range": "stddev: 0.000894215746625046",
            "extra": "mean: 149.8174857500004 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.012070040748378036,
            "unit": "iter/sec",
            "range": "stddev: 0.0013811896084949323",
            "extra": "mean: 150.06627924999947 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 9.249040047010777,
            "unit": "iter/sec",
            "range": "stddev: 0.000051158680580955925",
            "extra": "mean: 195.83720000113658 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 9.408759188729734,
            "unit": "iter/sec",
            "range": "stddev: 0.000025785006688255277",
            "extra": "mean: 192.51274999945167 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5748598069474696,
            "unit": "iter/sec",
            "range": "stddev: 0.00028797100253012806",
            "extra": "mean: 3.1508657999992806 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.1618158666006172,
            "unit": "iter/sec",
            "range": "stddev: 0.0003918545397935284",
            "extra": "mean: 11.193624850000106 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.057615488219641395,
            "unit": "iter/sec",
            "range": "stddev: 0.0009182408481204594",
            "extra": "mean: 31.437833150001634 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.3005701330582184,
            "unit": "iter/sec",
            "range": "stddev: 0.0003529442861807742",
            "extra": "mean: 6.026234499999816 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 9.376375090582536,
            "unit": "iter/sec",
            "range": "stddev: 0.000024714652484280226",
            "extra": "mean: 193.17764999868814 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x]]",
            "value": 23.045559841480088,
            "unit": "iter/sec",
            "range": "stddev: 0.0000126087822737098",
            "extra": "mean: 78.59675000148059 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.7188111619044806,
            "unit": "iter/sec",
            "range": "stddev: 0.000049891914833564365",
            "extra": "mean: 487.0659000005162 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.370778703884051,
            "unit": "iter/sec",
            "range": "stddev: 0.00009291143059239513",
            "extra": "mean: 764.0131499989877 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.922020851634481,
            "unit": "iter/sec",
            "range": "stddev: 0.00004232814586972972",
            "extra": "mean: 461.8297999996912 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.675509034379092,
            "unit": "iter/sec",
            "range": "stddev: 0.00006150105499323182",
            "extra": "mean: 492.80415000012573 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 2.0008788742215935,
            "unit": "iter/sec",
            "range": "stddev: 0.00006926162892010449",
            "extra": "mean: 905.2552500008915 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.5437553890233071,
            "unit": "iter/sec",
            "range": "stddev: 0.0000627345110974033",
            "extra": "mean: 1.1733116000009147 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.4575664590931976,
            "unit": "iter/sec",
            "range": "stddev: 0.00004470709851436912",
            "extra": "mean: 737.0324000000039 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.742332936538242,
            "unit": "iter/sec",
            "range": "stddev: 0.00006613934722927177",
            "extra": "mean: 660.4982500014955 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 2.013208803171383,
            "unit": "iter/sec",
            "range": "stddev: 0.00003663184108644595",
            "extra": "mean: 899.7109999974384 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.5523224492782266,
            "unit": "iter/sec",
            "range": "stddev: 0.00005805730302233934",
            "extra": "mean: 1.166836249998937 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.44091597109082,
            "unit": "iter/sec",
            "range": "stddev: 0.00003742932498935785",
            "extra": "mean: 742.0599999989008 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.7017148671973317,
            "unit": "iter/sec",
            "range": "stddev: 0.00005903536304414648",
            "extra": "mean: 670.4283000019018 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 2.028045452458868,
            "unit": "iter/sec",
            "range": "stddev: 0.000045932131650767877",
            "extra": "mean: 893.1289499990669 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.5462261240355328,
            "unit": "iter/sec",
            "range": "stddev: 0.00005659799047438764",
            "extra": "mean: 1.171436749999799 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.474237284750577,
            "unit": "iter/sec",
            "range": "stddev: 0.00003693845460252502",
            "extra": "mean: 732.0664499999907 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.7730617327640377,
            "unit": "iter/sec",
            "range": "stddev: 0.00005530680754806463",
            "extra": "mean: 653.1791500002271 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 7.604136629263886,
            "unit": "iter/sec",
            "range": "stddev: 0.000038106729459469646",
            "extra": "mean: 238.2001000000855 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.21562688189447,
            "unit": "iter/sec",
            "range": "stddev: 0.00021979880548456357",
            "extra": "mean: 817.5140499993461 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.07339440764396844,
            "unit": "iter/sec",
            "range": "stddev: 0.00164244231609015",
            "extra": "mean: 24.679075200000256 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.05549185308417163,
            "unit": "iter/sec",
            "range": "stddev: 0.0011607522112445973",
            "extra": "mean: 32.64093744999883 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.05470135523124549,
            "unit": "iter/sec",
            "range": "stddev: 0.00013192582420362638",
            "extra": "mean: 33.11263675000049 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.2014841712651276,
            "unit": "iter/sec",
            "range": "stddev: 0.00004235553399400698",
            "extra": "mean: 822.7658999992116 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.23164407843175,
            "unit": "iter/sec",
            "range": "stddev: 0.00003414800603423827",
            "extra": "mean: 811.6465000000517 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.015304516104557079,
            "unit": "iter/sec",
            "range": "stddev: 0.0036518101914724075",
            "extra": "mean: 118.35108625000146 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.03138338357415518,
            "unit": "iter/sec",
            "range": "stddev: 0.00005245459524110151",
            "extra": "mean: 57.71544999999989 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.148791035381673,
            "unit": "iter/sec",
            "range": "stddev: 0.0000771759331019351",
            "extra": "mean: 842.9419499989876 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.2092560913534274,
            "unit": "iter/sec",
            "range": "stddev: 0.00002254949314026939",
            "extra": "mean: 819.8715000013124 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 6.000290209611504,
            "unit": "iter/sec",
            "range": "stddev: 0.000045942743370297286",
            "extra": "mean: 301.86975000034977 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.6822533480793647,
            "unit": "iter/sec",
            "range": "stddev: 0.000020107874973377164",
            "extra": "mean: 675.2926999986641 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 13.350094455765452,
            "unit": "iter/sec",
            "range": "stddev: 0.000015678403126846193",
            "extra": "mean: 135.6773999994232 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 13.658267024234908,
            "unit": "iter/sec",
            "range": "stddev: 0.000014030153801318304",
            "extra": "mean: 132.61609999943857 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 7.227123368802792,
            "unit": "iter/sec",
            "range": "stddev: 0.00003452451360615189",
            "extra": "mean: 250.62615000095437 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 4.244960325952002,
            "unit": "iter/sec",
            "range": "stddev: 0.00002589091430104634",
            "extra": "mean: 426.69564999968657 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 2.6769768360987536,
            "unit": "iter/sec",
            "range": "stddev: 0.0001140981538886871",
            "extra": "mean: 676.6237500002603 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.5497406656563261,
            "unit": "iter/sec",
            "range": "stddev: 0.00005004102990276271",
            "extra": "mean: 3.2948373999992953 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 0.9804897676882371,
            "unit": "iter/sec",
            "range": "stddev: 0.00012657790301870108",
            "extra": "mean: 1.8473482999986857 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.775040612369647,
            "unit": "iter/sec",
            "range": "stddev: 0.00008456965532877848",
            "extra": "mean: 2.3370467000006556 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.7866833607775807,
            "unit": "iter/sec",
            "range": "stddev: 0.000033657491121292214",
            "extra": "mean: 2.3024589000009144 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.0037271542614014273,
            "unit": "iter/sec",
            "range": "stddev: 0.04726415141301321",
            "extra": "mean: 485.97562066666694 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.2247621371161826,
            "unit": "iter/sec",
            "range": "stddev: 0.0008852220771868895",
            "extra": "mean: 8.058768833331934 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.04147616957125842,
            "unit": "iter/sec",
            "range": "stddev: 0.0002803716799837346",
            "extra": "mean: 43.67100733333255 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.04328623985318597,
            "unit": "iter/sec",
            "range": "stddev: 0.00039389028255199817",
            "extra": "mean: 41.84484749999958 msec\nrounds: 3"
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
            "email": "matera@fisica.unlp.edu.ar",
            "name": "Juan Mauricio Matera",
            "username": "mmatera"
          },
          "distinct": false,
          "id": "b5a31748ba9c8731fec639ae278ac0ff3ef830b8",
          "message": "fill symbols and numbers cache",
          "timestamp": "2026-08-28T13:51:55-03:00",
          "tree_id": "aaa1316b8c67fc0616efbc94c29a80399feb8f69",
          "url": "https://github.com/Mathics3/mathics-core/commit/b5a31748ba9c8731fec639ae278ac0ff3ef830b8"
        },
        "date": 1787970361886,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000039922354056970104",
            "extra": "mean: 1.294645435714565 msec\nrounds: 280"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 18791.3913652205,
            "unit": "iter/sec",
            "range": "stddev: 5.361502070194848e-9",
            "extra": "mean: 68.8956666673827 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 8.699323023201295,
            "unit": "iter/sec",
            "range": "stddev: 0.0010238230114166615",
            "extra": "mean: 148.82140049998327 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.5780716556039667,
            "unit": "iter/sec",
            "range": "stddev: 0.00006925607567438564",
            "extra": "mean: 2.239593350000746 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 26.542247003896943,
            "unit": "iter/sec",
            "range": "stddev: 0.000004919136373467504",
            "extra": "mean: 48.77678350007386 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 13.404968766882003,
            "unit": "iter/sec",
            "range": "stddev: 0.000005731331966524834",
            "extra": "mean: 96.57951899993122 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 13.43144050451988,
            "unit": "iter/sec",
            "range": "stddev: 0.000005445754900464836",
            "extra": "mean: 96.38917250006784 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.5839706988715987,
            "unit": "iter/sec",
            "range": "stddev: 0.000005296521797097236",
            "extra": "mean: 361.2321485000365 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 22.568265967408685,
            "unit": "iter/sec",
            "range": "stddev: 9.991479892313827e-7",
            "extra": "mean: 57.36574699997732 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 22.604955146438854,
            "unit": "iter/sec",
            "range": "stddev: 7.996089980865385e-7",
            "extra": "mean: 57.272639000061076 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 7.0436939052901195,
            "unit": "iter/sec",
            "range": "stddev: 0.00000450651541380833",
            "extra": "mean: 183.80205800002614 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 7.046877386600832,
            "unit": "iter/sec",
            "range": "stddev: 0.000003308324501944295",
            "extra": "mean: 183.71902400008366 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 6.833325963535331,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021617633421752867",
            "extra": "mean: 189.46051200003922 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 6.82697969300554,
            "unit": "iter/sec",
            "range": "stddev: 0.0000035772057141344428",
            "extra": "mean: 189.63663200008796 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 9.782815927854886,
            "unit": "iter/sec",
            "range": "stddev: 0.0000153706370478495",
            "extra": "mean: 132.33872999984442 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 8.432212320802392,
            "unit": "iter/sec",
            "range": "stddev: 0.00000329612834277548",
            "extra": "mean: 153.53567800002568 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.009335642100828928,
            "unit": "iter/sec",
            "range": "stddev: 0.0015632801863695897",
            "extra": "mean: 138.67770654999845 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.009178550015869202,
            "unit": "iter/sec",
            "range": "stddev: 0.002052037513801853",
            "extra": "mean: 141.05119364999865 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.009002500470198002,
            "unit": "iter/sec",
            "range": "stddev: 0.007685872990827289",
            "extra": "mean: 143.80953824999807 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 15.575705011282336,
            "unit": "iter/sec",
            "range": "stddev: 0.000002055027957025876",
            "extra": "mean: 83.11954000006949 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 15.550093610932985,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016063834243417077",
            "extra": "mean: 83.25644000009902 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5186057029183583,
            "unit": "iter/sec",
            "range": "stddev: 0.00022576695015981275",
            "extra": "mean: 2.4963964499988833 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.1408041203275767,
            "unit": "iter/sec",
            "range": "stddev: 0.0003179395852225752",
            "extra": "mean: 9.194655900002147 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.0509112656420091,
            "unit": "iter/sec",
            "range": "stddev: 0.0008136445146023901",
            "extra": "mean: 25.42944905000155 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.2619580663506742,
            "unit": "iter/sec",
            "range": "stddev: 0.0003415119069247141",
            "extra": "mean: 4.942185800003074 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 12.14819637337817,
            "unit": "iter/sec",
            "range": "stddev: 0.00001575814317255103",
            "extra": "mean: 106.57100000059927 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 11.27229334880921,
            "unit": "iter/sec",
            "range": "stddev: 0.000011165684106693519",
            "extra": "mean: 114.85200000151963 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.491696839477175,
            "unit": "iter/sec",
            "range": "stddev: 0.000008198653206552416",
            "extra": "mean: 370.778304999817 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.2103318610157805,
            "unit": "iter/sec",
            "range": "stddev: 0.00001491113157217203",
            "extra": "mean: 585.7244600001366 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.8816227435368975,
            "unit": "iter/sec",
            "range": "stddev: 0.000009441228268567766",
            "extra": "mean: 333.5320100002548 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.786797436108587,
            "unit": "iter/sec",
            "range": "stddev: 0.000008433060067029108",
            "extra": "mean: 341.88399500052924 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.7499766925298887,
            "unit": "iter/sec",
            "range": "stddev: 0.000014828023376759066",
            "extra": "mean: 739.8072449998949 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.32230024789009,
            "unit": "iter/sec",
            "range": "stddev: 0.000021772611068066808",
            "extra": "mean: 979.0858299999173 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.2796046430112105,
            "unit": "iter/sec",
            "range": "stddev: 0.00001644236344322661",
            "extra": "mean: 567.9254250001975 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.6387521698523657,
            "unit": "iter/sec",
            "range": "stddev: 0.000009044732985116606",
            "extra": "mean: 490.6278999997938 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.7551639721471588,
            "unit": "iter/sec",
            "range": "stddev: 0.000011089254097992538",
            "extra": "mean: 737.6207899999088 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.3500705362226584,
            "unit": "iter/sec",
            "range": "stddev: 0.0000064461079548178965",
            "extra": "mean: 958.9465149997523 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.2946620877972097,
            "unit": "iter/sec",
            "range": "stddev: 0.000013164530452405342",
            "extra": "mean: 564.1987300001006 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.641025174076928,
            "unit": "iter/sec",
            "range": "stddev: 0.00000875794466894474",
            "extra": "mean: 490.20564000002764 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.7585017055104444,
            "unit": "iter/sec",
            "range": "stddev: 0.000009708240067344695",
            "extra": "mean: 736.2207449999403 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.346201136212963,
            "unit": "iter/sec",
            "range": "stddev: 0.000010165826555614646",
            "extra": "mean: 961.702825000259 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.2264768885836275,
            "unit": "iter/sec",
            "range": "stddev: 0.000020176100748359574",
            "extra": "mean: 581.4771500000404 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.285410912363432,
            "unit": "iter/sec",
            "range": "stddev: 0.00004648069444365857",
            "extra": "mean: 566.4825649999727 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 7.5688117304471465,
            "unit": "iter/sec",
            "range": "stddev: 0.000005478558281509373",
            "extra": "mean: 171.05002500017008 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.1887584868290157,
            "unit": "iter/sec",
            "range": "stddev: 0.000040458184694545287",
            "extra": "mean: 591.4976200001831 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05323308971289797,
            "unit": "iter/sec",
            "range": "stddev: 0.0015733335121421671",
            "extra": "mean: 24.32031359999911 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.03934865226453334,
            "unit": "iter/sec",
            "range": "stddev: 0.002339649210377242",
            "extra": "mean: 32.90190035000222 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.026307619716430877,
            "unit": "iter/sec",
            "range": "stddev: 0.0005465096274114931",
            "extra": "mean: 49.21180439999944 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.040101952029700225,
            "unit": "iter/sec",
            "range": "stddev: 0.0022965412228440913",
            "extra": "mean: 32.28385078999963 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.127072856095187,
            "unit": "iter/sec",
            "range": "stddev: 0.000016072723120162604",
            "extra": "mean: 608.6511950000784 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.1883467319187804,
            "unit": "iter/sec",
            "range": "stddev: 0.000010799208941078052",
            "extra": "mean: 591.6089150001369 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.011257508018922389,
            "unit": "iter/sec",
            "range": "stddev: 0.0019880749094796676",
            "extra": "mean: 115.00284375000547 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.024443153503879662,
            "unit": "iter/sec",
            "range": "stddev: 0.0002720310497843569",
            "extra": "mean: 52.96556499999383 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.2994696285453684,
            "unit": "iter/sec",
            "range": "stddev: 0.000019527421032902835",
            "extra": "mean: 563.0191500000591 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.3151254505724927,
            "unit": "iter/sec",
            "range": "stddev: 0.000012406548205026636",
            "extra": "mean: 559.2117850004286 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 7.4024756810808245,
            "unit": "iter/sec",
            "range": "stddev: 0.000011125009756600819",
            "extra": "mean: 174.89357499997027 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.8238107240664183,
            "unit": "iter/sec",
            "range": "stddev: 0.000011032662413358458",
            "extra": "mean: 458.474579999546 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 17.159792617350142,
            "unit": "iter/sec",
            "range": "stddev: 0.00000247191858685117",
            "extra": "mean: 75.44644999995853 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 17.533243883158203,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014507280381223357",
            "extra": "mean: 73.83947000008106 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 9.868870410235555,
            "unit": "iter/sec",
            "range": "stddev: 0.000004834795880844701",
            "extra": "mean: 131.1847640001247 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 5.8622181203494,
            "unit": "iter/sec",
            "range": "stddev: 0.000010196201896920794",
            "extra": "mean: 220.84566099997005 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 6.272601318515435,
            "unit": "iter/sec",
            "range": "stddev: 0.000011152547380872424",
            "extra": "mean: 206.39689500001168 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 4.664736146617792,
            "unit": "iter/sec",
            "range": "stddev: 0.00007053869140207337",
            "extra": "mean: 277.538834999973 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.3121353389834583,
            "unit": "iter/sec",
            "range": "stddev: 0.0001939435118818741",
            "extra": "mean: 4.147705415000047 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.2666751263041034,
            "unit": "iter/sec",
            "range": "stddev: 0.000016086680495126423",
            "extra": "mean: 396.31900499983885 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.37902054603940755,
            "unit": "iter/sec",
            "range": "stddev: 0.00003827367096021278",
            "extra": "mean: 3.415765844999754 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.0113010177945538,
            "unit": "iter/sec",
            "range": "stddev: 0.000021379964334281556",
            "extra": "mean: 1.2801781200002438 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.7936388344802183,
            "unit": "iter/sec",
            "range": "stddev: 0.000015231622024164991",
            "extra": "mean: 1.6312778299999309 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.8088340544711651,
            "unit": "iter/sec",
            "range": "stddev: 0.00001815903813036383",
            "extra": "mean: 1.6006317100001866 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.003002516029207959,
            "unit": "iter/sec",
            "range": "stddev: 0.0038676140357895785",
            "extra": "mean: 431.1868523333355 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.15796118333670295,
            "unit": "iter/sec",
            "range": "stddev: 0.001852369292543131",
            "extra": "mean: 8.195972000000515 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.032573333236903715,
            "unit": "iter/sec",
            "range": "stddev: 0.0006416788948846209",
            "extra": "mean: 39.74556200001681 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.035191215403226325,
            "unit": "iter/sec",
            "range": "stddev: 0.0007439147878060973",
            "extra": "mean: 36.788880999997296 msec\nrounds: 3"
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
          "id": "6a47e26181124c1f0d05be7765407cd27fa7f47c",
          "message": "Move the `get_float_value()` method from the `BaseElement` class and move it to the `Number` and `Numeric` classes. (#1920)\n\n* Remove get_float_value from the `BaseElement` class and add it to the `Rational`, `Number`, and `Numeric` classes.\n* Go over the `Power` built-in, e.g., add `eval_Power()`, and handle the rcase when the base is zero more correctly.\n* Use SymPy's zero detection instead of Python's float zero test for better accuracy. Similarly, replace improper SymPy \"x - y\" with `sympy.Add(x, -y)`.\n* Go over some comments and make the code more stringent for `mypy`. Better type checking and accuracy.",
          "timestamp": "2026-08-29T19:02:11-04:00",
          "tree_id": "865fd243c735c1d5522c3051bb2f71c9fa2972da",
          "url": "https://github.com/Mathics3/mathics-core/commit/6a47e26181124c1f0d05be7765407cd27fa7f47c"
        },
        "date": 1788044656810,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.00001854559528532173",
            "extra": "mean: 2.3344758757055497 msec\nrounds: 177"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 18484.163201561336,
            "unit": "iter/sec",
            "range": "stddev: 1.634604548231955e-9",
            "extra": "mean: 126.29600000006272 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 12.82286651733776,
            "unit": "iter/sec",
            "range": "stddev: 0.0010094676754424227",
            "extra": "mean: 182.05569499995278 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.586974105576824,
            "unit": "iter/sec",
            "range": "stddev: 0.00006366395659534011",
            "extra": "mean: 3.9771360499990753 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 27.6490662724397,
            "unit": "iter/sec",
            "range": "stddev: 0.000006816471489650624",
            "extra": "mean: 84.43235850002395 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 14.118171018371125,
            "unit": "iter/sec",
            "range": "stddev: 0.00001099835653199827",
            "extra": "mean: 165.35257100001388 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 14.06021500748127,
            "unit": "iter/sec",
            "range": "stddev: 0.0000075327365892604215",
            "extra": "mean: 166.03415200005145 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.416844524259467,
            "unit": "iter/sec",
            "range": "stddev: 0.00003550229053610965",
            "extra": "mean: 683.2256659999772 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 19.77377438150444,
            "unit": "iter/sec",
            "range": "stddev: 0.000007337029617229565",
            "extra": "mean: 118.05919450002023 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 20.03277312918817,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016206209531125689",
            "extra": "mean: 116.53283650001356 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 7.378245089565024,
            "unit": "iter/sec",
            "range": "stddev: 0.0000072787091859945175",
            "extra": "mean: 316.3998820000131 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 7.399636361107494,
            "unit": "iter/sec",
            "range": "stddev: 0.000004713258061889815",
            "extra": "mean: 315.4852160000132 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 7.193561958071403,
            "unit": "iter/sec",
            "range": "stddev: 0.000002613877122852005",
            "extra": "mean: 324.5229400000085 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 6.779622341149247,
            "unit": "iter/sec",
            "range": "stddev: 0.000004447021229210178",
            "extra": "mean: 344.337156000023 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 10.645626579578467,
            "unit": "iter/sec",
            "range": "stddev: 0.000004422317568722874",
            "extra": "mean: 219.28966400002992 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 8.753641097507844,
            "unit": "iter/sec",
            "range": "stddev: 0.00000859258969526569",
            "extra": "mean: 266.6862679999724 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.009647753167050827,
            "unit": "iter/sec",
            "range": "stddev: 0.0009478617183734316",
            "extra": "mean: 241.97093719999927 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.009636933873836417,
            "unit": "iter/sec",
            "range": "stddev: 0.0010225034500579518",
            "extra": "mean: 242.24259565000068 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.009640506189518951,
            "unit": "iter/sec",
            "range": "stddev: 0.0012739440804702775",
            "extra": "mean: 242.15283200000073 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 16.406468254246114,
            "unit": "iter/sec",
            "range": "stddev: 0.0000051437154835364225",
            "extra": "mean: 142.28997000017785 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 16.515040537653583,
            "unit": "iter/sec",
            "range": "stddev: 0.000002941910512206765",
            "extra": "mean: 141.3545349999623 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5288089522076371,
            "unit": "iter/sec",
            "range": "stddev: 0.00032727776443037615",
            "extra": "mean: 4.414592199999134 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.1460867156054024,
            "unit": "iter/sec",
            "range": "stddev: 0.0006271726756193812",
            "extra": "mean: 15.98006955000102 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.052535759211668503,
            "unit": "iter/sec",
            "range": "stddev: 0.0013060008261705607",
            "extra": "mean: 44.43594059999896 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.268861196626984,
            "unit": "iter/sec",
            "range": "stddev: 0.0005049068562920599",
            "extra": "mean: 8.682829299998929 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 12.632968170412274,
            "unit": "iter/sec",
            "range": "stddev: 0.00001379253043393069",
            "extra": "mean: 184.79235000157246 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 11.67655374647062,
            "unit": "iter/sec",
            "range": "stddev: 0.000011409771175533365",
            "extra": "mean: 199.9285000003681 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.4802056034965907,
            "unit": "iter/sec",
            "range": "stddev: 0.000008751339497631694",
            "extra": "mean: 670.7867700000493 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.20561584669674,
            "unit": "iter/sec",
            "range": "stddev: 0.000015729245950557875",
            "extra": "mean: 1.0584236049998452 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.7914260114814278,
            "unit": "iter/sec",
            "range": "stddev: 0.000011971457310670402",
            "extra": "mean: 615.7250250001312 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.695469282047406,
            "unit": "iter/sec",
            "range": "stddev: 0.000017657069836327057",
            "extra": "mean: 631.7129699998958 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.9244243707198336,
            "unit": "iter/sec",
            "range": "stddev: 0.000015167005705120017",
            "extra": "mean: 1.2130774850000137 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.4523179030799116,
            "unit": "iter/sec",
            "range": "stddev: 0.000010269929215615866",
            "extra": "mean: 1.6074138249999237 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.317124735915411,
            "unit": "iter/sec",
            "range": "stddev: 0.00001355305568021384",
            "extra": "mean: 1.00748822000007 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.6010421888283255,
            "unit": "iter/sec",
            "range": "stddev: 0.00006525636018043352",
            "extra": "mean: 897.5155750000141 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.9194567131546085,
            "unit": "iter/sec",
            "range": "stddev: 0.00001664628223252467",
            "extra": "mean: 1.216216995000039 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.4595324340658289,
            "unit": "iter/sec",
            "range": "stddev: 0.000009926975294305075",
            "extra": "mean: 1.5994683100000628 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.3095034230474494,
            "unit": "iter/sec",
            "range": "stddev: 0.000011374367539573894",
            "extra": "mean: 1.0108129099999985 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.6532069536511007,
            "unit": "iter/sec",
            "range": "stddev: 0.000012435143299671468",
            "extra": "mean: 879.8695000000123 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.9084766216271245,
            "unit": "iter/sec",
            "range": "stddev: 0.000019160989130273178",
            "extra": "mean: 1.223214290000172 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.447635292585478,
            "unit": "iter/sec",
            "range": "stddev: 0.00001740665982047247",
            "extra": "mean: 1.6126132650000358 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.2974815972782494,
            "unit": "iter/sec",
            "range": "stddev: 0.000016973136124151242",
            "extra": "mean: 1.0161020999998982 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.6559452167050344,
            "unit": "iter/sec",
            "range": "stddev: 0.00001100695239267285",
            "extra": "mean: 878.9623599999175 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 8.705904624832076,
            "unit": "iter/sec",
            "range": "stddev: 0.000004811219504880943",
            "extra": "mean: 268.14857000005077 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.3613186972936404,
            "unit": "iter/sec",
            "range": "stddev: 0.00003337286895185795",
            "extra": "mean: 988.632275000043 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05749741293955947,
            "unit": "iter/sec",
            "range": "stddev: 0.0020935112362548444",
            "extra": "mean: 40.60140719999907 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.043019663672453995,
            "unit": "iter/sec",
            "range": "stddev: 0.00023894618124528684",
            "extra": "mean: 54.265321399998356 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.027853912135457893,
            "unit": "iter/sec",
            "range": "stddev: 0.0005442018376664351",
            "extra": "mean: 83.81141810000088 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.041660974039597426,
            "unit": "iter/sec",
            "range": "stddev: 0.0023985280909546345",
            "extra": "mean: 56.03507669999999 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.207101791130831,
            "unit": "iter/sec",
            "range": "stddev: 0.000022299689675644903",
            "extra": "mean: 1.057711015000109 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.239114658157327,
            "unit": "iter/sec",
            "range": "stddev: 0.000008718275739596548",
            "extra": "mean: 1.0425888049996956 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.01242171526845882,
            "unit": "iter/sec",
            "range": "stddev: 0.004535985703061996",
            "extra": "mean: 187.93506574999697 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.02455070136047897,
            "unit": "iter/sec",
            "range": "stddev: 0.000009404520194173009",
            "extra": "mean: 95.08795050000174 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.286993152352457,
            "unit": "iter/sec",
            "range": "stddev: 0.000016956381872774025",
            "extra": "mean: 1.020762074999766 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.289759146437411,
            "unit": "iter/sec",
            "range": "stddev: 0.000016059976657485747",
            "extra": "mean: 1.0195290099999 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 7.661511594953817,
            "unit": "iter/sec",
            "range": "stddev: 0.00000993733816120722",
            "extra": "mean: 304.7017350000658 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.9796314408692335,
            "unit": "iter/sec",
            "range": "stddev: 0.000007110429074570633",
            "extra": "mean: 783.4780650000539 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 17.187993017029175,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024074414815002645",
            "extra": "mean: 135.82015499963518 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 17.38436495128535,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012185454424545398",
            "extra": "mean: 134.2859449998457 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 10.2564412081017,
            "unit": "iter/sec",
            "range": "stddev: 0.000005483557897247871",
            "extra": "mean: 227.61071099998276 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 6.214786844077923,
            "unit": "iter/sec",
            "range": "stddev: 0.000005651061682971577",
            "extra": "mean: 375.632493000154 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 6.350643144818796,
            "unit": "iter/sec",
            "range": "stddev: 0.00001445136089826336",
            "extra": "mean: 367.5967650001155 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 5.671768109447929,
            "unit": "iter/sec",
            "range": "stddev: 0.000011155201398624314",
            "extra": "mean: 411.59579000009217 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.3320792954554967,
            "unit": "iter/sec",
            "range": "stddev: 0.00003697418951956786",
            "extra": "mean: 7.029874815000028 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.4141667926912986,
            "unit": "iter/sec",
            "range": "stddev: 0.000015394309905703258",
            "extra": "mean: 683.7615200004166 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.3918262178276688,
            "unit": "iter/sec",
            "range": "stddev: 0.00004306141251324529",
            "extra": "mean: 5.957936885000095 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.034002440091883,
            "unit": "iter/sec",
            "range": "stddev: 0.000011323155425328107",
            "extra": "mean: 2.257708284999893 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.8204717942238992,
            "unit": "iter/sec",
            "range": "stddev: 0.0000079145223808601",
            "extra": "mean: 2.8452847399998404 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.8339913924609688,
            "unit": "iter/sec",
            "range": "stddev: 0.000011993413961004361",
            "extra": "mean: 2.7991606349999643 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.004567258593507821,
            "unit": "iter/sec",
            "range": "stddev: 0.005509779306983352",
            "extra": "mean: 511.1328443333415 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.189879156795848,
            "unit": "iter/sec",
            "range": "stddev: 0.0016109528249842768",
            "extra": "mean: 12.294534666674886 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03413462778377052,
            "unit": "iter/sec",
            "range": "stddev: 0.0004999131788743777",
            "extra": "mean: 68.39025433332797 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.036037694284943945,
            "unit": "iter/sec",
            "range": "stddev: 0.0007645444737875498",
            "extra": "mean: 64.7787246666572 msec\nrounds: 3"
          }
        ]
      }
    ]
  }
}