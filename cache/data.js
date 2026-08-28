window.BENCHMARK_DATA = {
  "lastUpdate": 1787944048697,
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
      }
    ]
  }
}