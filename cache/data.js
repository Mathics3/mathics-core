window.BENCHMARK_DATA = {
  "lastUpdate": 1788167493838,
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
          "id": "9dc707e3a52b9e653f0e541b276dcf57d9b2c14c",
          "message": "Disable comments on benchmark alerts",
          "timestamp": "2026-08-30T14:07:45-03:00",
          "tree_id": "be422d3a58a084d6cd2c323ecc78454370adcc3a",
          "url": "https://github.com/Mathics3/mathics-core/commit/9dc707e3a52b9e653f0e541b276dcf57d9b2c14c"
        },
        "date": 1788109795256,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000043638103900180646",
            "extra": "mean: 2.3507837457654497 msec\nrounds: 177"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 18537.354736531775,
            "unit": "iter/sec",
            "range": "stddev: 1.8404223455135048e-9",
            "extra": "mean: 126.81333335725262 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 10.651023679686901,
            "unit": "iter/sec",
            "range": "stddev: 0.00137787840041116",
            "extra": "mean: 220.70965350013694 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.5803907753983696,
            "unit": "iter/sec",
            "range": "stddev: 0.00008165951987692145",
            "extra": "mean: 4.050346499997204 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 25.372179909166576,
            "unit": "iter/sec",
            "range": "stddev: 0.000016034017656453928",
            "extra": "mean: 92.65202100021952 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 13.879339462076187,
            "unit": "iter/sec",
            "range": "stddev: 0.000007997255339725929",
            "extra": "mean: 169.37288349987512 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 13.875910441100286,
            "unit": "iter/sec",
            "range": "stddev: 0.000008521487027705173",
            "extra": "mean: 169.41473899993298 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.43646945219048,
            "unit": "iter/sec",
            "range": "stddev: 0.000008775147000742853",
            "extra": "mean: 684.0694435002206 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 20.127689838956663,
            "unit": "iter/sec",
            "range": "stddev: 0.0000027661778230658958",
            "extra": "mean: 116.79352000027166 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 20.15201059331586,
            "unit": "iter/sec",
            "range": "stddev: 0.00000335638022833797",
            "extra": "mean: 116.65256599980012 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 7.364453983925721,
            "unit": "iter/sec",
            "range": "stddev: 0.000007501590388160101",
            "extra": "mean: 319.20679399945584 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 7.367640097293185,
            "unit": "iter/sec",
            "range": "stddev: 0.000004370922509539418",
            "extra": "mean: 319.0687540002273 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 7.120452771376825,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034486890621872384",
            "extra": "mean: 330.1452620000873 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 6.752783266610261,
            "unit": "iter/sec",
            "range": "stddev: 0.000005107965146277171",
            "extra": "mean: 348.12071600003947 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 10.512948147205403,
            "unit": "iter/sec",
            "range": "stddev: 0.000004585454132903973",
            "extra": "mean: 223.60842200009756 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 8.519651424265948,
            "unit": "iter/sec",
            "range": "stddev: 0.000023311877271346154",
            "extra": "mean: 275.92487400011123 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.009520162359519156,
            "unit": "iter/sec",
            "range": "stddev: 0.0022847814493858923",
            "extra": "mean: 246.92685450000909 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.009532129816642402,
            "unit": "iter/sec",
            "range": "stddev: 0.001283149429769945",
            "extra": "mean: 246.6168412500167 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.009502106962244546,
            "unit": "iter/sec",
            "range": "stddev: 0.002559189805335061",
            "extra": "mean: 247.3960517499961 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 16.13495960053246,
            "unit": "iter/sec",
            "range": "stddev: 0.0000043534175720461755",
            "extra": "mean: 145.69505000110894 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 16.142529230488055,
            "unit": "iter/sec",
            "range": "stddev: 0.000006196092037080794",
            "extra": "mean: 145.6267300000036 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5250521718380237,
            "unit": "iter/sec",
            "range": "stddev: 0.0003473389670875648",
            "extra": "mean: 4.477238400016859 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.14492367687179544,
            "unit": "iter/sec",
            "range": "stddev: 0.0006733233195812754",
            "extra": "mean: 16.220839800007525 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.05194065201164001,
            "unit": "iter/sec",
            "range": "stddev: 0.0013898558531459553",
            "extra": "mean: 45.259034200006454 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.26758657824156507,
            "unit": "iter/sec",
            "range": "stddev: 0.0005312677205790499",
            "extra": "mean: 8.785133250006538 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 9.398912991339225,
            "unit": "iter/sec",
            "range": "stddev: 0.00006138051702145878",
            "extra": "mean: 250.11230000018261 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 9.70238966843642,
            "unit": "iter/sec",
            "range": "stddev: 0.00005419296041124642",
            "extra": "mean: 242.2891500032165 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.3196383359265695,
            "unit": "iter/sec",
            "range": "stddev: 0.00005434641674361305",
            "extra": "mean: 708.1445350007698 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.102393360173579,
            "unit": "iter/sec",
            "range": "stddev: 0.00016094348433580278",
            "extra": "mean: 1.1181464850000111 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.8419523897669383,
            "unit": "iter/sec",
            "range": "stddev: 0.000011528790369813278",
            "extra": "mean: 611.8721700005381 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.7239100276392336,
            "unit": "iter/sec",
            "range": "stddev: 0.00001298501265408699",
            "extra": "mean: 631.2676000004558 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.73979450105509,
            "unit": "iter/sec",
            "range": "stddev: 0.00015102044633917905",
            "extra": "mean: 1.3511847199998783 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.4430830631671836,
            "unit": "iter/sec",
            "range": "stddev: 0.000015673453254855883",
            "extra": "mean: 1.6290009949989324 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.321901646015192,
            "unit": "iter/sec",
            "range": "stddev: 0.00001526138930102297",
            "extra": "mean: 1.0124389850017224 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.6565786787132377,
            "unit": "iter/sec",
            "range": "stddev: 0.000011236449575609083",
            "extra": "mean: 884.891445001017 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.9102377990411323,
            "unit": "iter/sec",
            "range": "stddev: 0.000021118973644371765",
            "extra": "mean: 1.2306236149998995 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.4555698432741333,
            "unit": "iter/sec",
            "range": "stddev: 0.000011289718043727924",
            "extra": "mean: 1.6150264150002158 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.324545278218774,
            "unit": "iter/sec",
            "range": "stddev: 0.00001312113807708543",
            "extra": "mean: 1.0112875700002633 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.6550911352007254,
            "unit": "iter/sec",
            "range": "stddev: 0.000010053120901738884",
            "extra": "mean: 885.3872149995823 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.9167923288941862,
            "unit": "iter/sec",
            "range": "stddev: 0.00001283442963525906",
            "extra": "mean: 1.226415460000112 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.4446216419176325,
            "unit": "iter/sec",
            "range": "stddev: 0.00002324565587673457",
            "extra": "mean: 1.6272660450005105 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.324105271632581,
            "unit": "iter/sec",
            "range": "stddev: 0.000014663183324559394",
            "extra": "mean: 1.0114790299985545 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.6436491406484284,
            "unit": "iter/sec",
            "range": "stddev: 0.000019691227790986304",
            "extra": "mean: 889.2192650000652 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 8.766483496233867,
            "unit": "iter/sec",
            "range": "stddev: 0.000005269998406242017",
            "extra": "mean: 268.15583999848513 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.2732219031696177,
            "unit": "iter/sec",
            "range": "stddev: 0.00004953465488287505",
            "extra": "mean: 1.034119785001053 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05673979910694607,
            "unit": "iter/sec",
            "range": "stddev: 0.0024430457239240895",
            "extra": "mean: 41.43094939998946 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.042755138568311125,
            "unit": "iter/sec",
            "range": "stddev: 0.00023831454178233",
            "extra": "mean: 54.982484550004074 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.02755533809632338,
            "unit": "iter/sec",
            "range": "stddev: 0.0005246681420631292",
            "extra": "mean: 85.31137370000579 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.04104467124706387,
            "unit": "iter/sec",
            "range": "stddev: 0.0029476648491023765",
            "extra": "mean: 57.273786689998474 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.2018976678470215,
            "unit": "iter/sec",
            "range": "stddev: 0.000016540765750691888",
            "extra": "mean: 1.0676171649993194 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.1753611237468435,
            "unit": "iter/sec",
            "range": "stddev: 0.000006160792899401337",
            "extra": "mean: 1.080640690000223 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.012229920631570083,
            "unit": "iter/sec",
            "range": "stddev: 0.004529446025961295",
            "extra": "mean: 192.2157810000158 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.024126759840554585,
            "unit": "iter/sec",
            "range": "stddev: 0.00013904017413644506",
            "extra": "mean: 97.43470575000401 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.3019647478074865,
            "unit": "iter/sec",
            "range": "stddev: 0.00002136943675178067",
            "extra": "mean: 1.0212075350000305 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.2887885212593924,
            "unit": "iter/sec",
            "range": "stddev: 0.00001728579500371461",
            "extra": "mean: 1.027086480000321 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 7.651827793906691,
            "unit": "iter/sec",
            "range": "stddev: 0.00001160858147065456",
            "extra": "mean: 307.2185899998203 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.9762503264214315,
            "unit": "iter/sec",
            "range": "stddev: 0.000009432055600537304",
            "extra": "mean: 789.8474549995171 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 17.456092853835745,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018645118081111963",
            "extra": "mean: 134.66838000056214 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 17.513965586077667,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021464990514839406",
            "extra": "mean: 134.22338500163278 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 10.266993849638688,
            "unit": "iter/sec",
            "range": "stddev: 0.000006805194362033611",
            "extra": "mean: 228.96514600017778 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 6.237354006354752,
            "unit": "iter/sec",
            "range": "stddev: 0.000005678673975301929",
            "extra": "mean: 376.88797900045756 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 6.430020365861638,
            "unit": "iter/sec",
            "range": "stddev: 0.000013730108698496473",
            "extra": "mean: 365.5950700010635 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 5.691837748872205,
            "unit": "iter/sec",
            "range": "stddev: 0.000012283913694710418",
            "extra": "mean: 413.00962000036634 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.32665056139570625,
            "unit": "iter/sec",
            "range": "stddev: 0.00005042153627058714",
            "extra": "mean: 7.196631580001167 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.352857783000382,
            "unit": "iter/sec",
            "range": "stddev: 0.000016198112611753784",
            "extra": "mean: 701.1283800000001 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.39426428043078177,
            "unit": "iter/sec",
            "range": "stddev: 0.00009190438858491347",
            "extra": "mean: 5.962456814999655 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 0.9977201316703546,
            "unit": "iter/sec",
            "range": "stddev: 0.00013975687678862046",
            "extra": "mean: 2.3561554700012266 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.8046829757232583,
            "unit": "iter/sec",
            "range": "stddev: 0.00011286280284153126",
            "extra": "mean: 2.9213787500009403 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.8312251856754989,
            "unit": "iter/sec",
            "range": "stddev: 0.00001528068705918759",
            "extra": "mean: 2.8280949449998616 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.0044843047357528065,
            "unit": "iter/sec",
            "range": "stddev: 0.0051515490569948395",
            "extra": "mean: 524.2247983333831 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.15853518708577927,
            "unit": "iter/sec",
            "range": "stddev: 0.002293546511787619",
            "extra": "mean: 14.828151333328302 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.033464408252206375,
            "unit": "iter/sec",
            "range": "stddev: 0.0003831346362356711",
            "extra": "mean: 70.24728266666595 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03492673475549168,
            "unit": "iter/sec",
            "range": "stddev: 0.0014794606329079207",
            "extra": "mean: 67.30614133334711 msec\nrounds: 3"
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
          "id": "a6f3d1807d71e3ffc48356b8f96843ba554fa3f9",
          "message": "has_form now supports iterables with Symbols. (#1923)\n\nIn this PR, the implementation of `has_form` was improved to work with\nsymbols as heads.",
          "timestamp": "2026-08-30T14:48:13-03:00",
          "tree_id": "3398aef955ae95e64fc9d1d2e1a092627c3a5cf3",
          "url": "https://github.com/Mathics3/mathics-core/commit/a6f3d1807d71e3ffc48356b8f96843ba554fa3f9"
        },
        "date": 1788112193047,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000016571055461171416",
            "extra": "mean: 1.821744688372693 msec\nrounds: 215"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 16853.96140486843,
            "unit": "iter/sec",
            "range": "stddev: 2.669281011066219e-9",
            "extra": "mean: 108.09000000714757 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 11.113198937486008,
            "unit": "iter/sec",
            "range": "stddev: 0.0012015348803533087",
            "extra": "mean: 163.92621949992758 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.6028557720643608,
            "unit": "iter/sec",
            "range": "stddev: 0.0000699106352140422",
            "extra": "mean: 3.0218582499998092 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 40.21781392134177,
            "unit": "iter/sec",
            "range": "stddev: 0.000006068516446043167",
            "extra": "mean: 45.296959499978584 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 19.72075522282341,
            "unit": "iter/sec",
            "range": "stddev: 0.000006551492687714649",
            "extra": "mean: 92.37702449976837 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 19.798033155680386,
            "unit": "iter/sec",
            "range": "stddev: 0.000010063343637607683",
            "extra": "mean: 92.01644800003805 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 4.43594536812684,
            "unit": "iter/sec",
            "range": "stddev: 0.000005918136843434769",
            "extra": "mean: 410.677890999807 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 29.06897020234114,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017804789782313646",
            "extra": "mean: 62.669736000003695 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 29.297528821529884,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018705798236428634",
            "extra": "mean: 62.18083100011996 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 9.907840085827596,
            "unit": "iter/sec",
            "range": "stddev: 0.000004770709777311581",
            "extra": "mean: 183.86900400003015 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 9.932511330843884,
            "unit": "iter/sec",
            "range": "stddev: 0.00000368650876331518",
            "extra": "mean: 183.41229400016346 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 9.695953947774363,
            "unit": "iter/sec",
            "range": "stddev: 0.0000025091974574890176",
            "extra": "mean: 187.8871019999906 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 9.198455850438979,
            "unit": "iter/sec",
            "range": "stddev: 0.000002783328072798199",
            "extra": "mean: 198.0489679999664 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 15.182032651150365,
            "unit": "iter/sec",
            "range": "stddev: 0.0000036595001511251323",
            "extra": "mean: 119.99346400000377 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 11.918472610010719,
            "unit": "iter/sec",
            "range": "stddev: 0.00001684561808280476",
            "extra": "mean: 152.85051600005772 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.012301812518333285,
            "unit": "iter/sec",
            "range": "stddev: 0.0011085735704688356",
            "extra": "mean: 148.08750220000206 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.012321272136405714,
            "unit": "iter/sec",
            "range": "stddev: 0.0003499184356425725",
            "extra": "mean: 147.85361999999793 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.012160853412982337,
            "unit": "iter/sec",
            "range": "stddev: 0.0021970445095984303",
            "extra": "mean: 149.8040167499994 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 23.6666905492569,
            "unit": "iter/sec",
            "range": "stddev: 0.000004192100889979896",
            "extra": "mean: 76.97505000038518 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 24.071022485534076,
            "unit": "iter/sec",
            "range": "stddev: 0.000003588289725204833",
            "extra": "mean: 75.68206500025099 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.6328197147487403,
            "unit": "iter/sec",
            "range": "stddev: 0.00030203081933016004",
            "extra": "mean: 2.878773599991291 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.16972582864566746,
            "unit": "iter/sec",
            "range": "stddev: 0.0012647527141149452",
            "extra": "mean: 10.733455849998563 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.06451306632783958,
            "unit": "iter/sec",
            "range": "stddev: 0.0009204324897836165",
            "extra": "mean: 28.238383200002204 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.33514314933688055,
            "unit": "iter/sec",
            "range": "stddev: 0.0003818820708863281",
            "extra": "mean: 5.435721100005253 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 17.645101547915317,
            "unit": "iter/sec",
            "range": "stddev: 0.000018459703168857353",
            "extra": "mean: 103.24364999689806 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 16.16563928285459,
            "unit": "iter/sec",
            "range": "stddev: 0.00001471340541747981",
            "extra": "mean: 112.69240000331138 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 4.4744802787234255,
            "unit": "iter/sec",
            "range": "stddev: 0.000009399679287468664",
            "extra": "mean: 407.14106999985233 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.7937738241558403,
            "unit": "iter/sec",
            "range": "stddev: 0.00001672588802685276",
            "extra": "mean: 652.0730750003167 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 4.871623393230443,
            "unit": "iter/sec",
            "range": "stddev: 0.000009627394832501752",
            "extra": "mean: 373.9502300001618 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 4.692502422748414,
            "unit": "iter/sec",
            "range": "stddev: 0.00000870279671360487",
            "extra": "mean: 388.2245600004808 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 2.420826324776956,
            "unit": "iter/sec",
            "range": "stddev: 0.00001731904303037383",
            "extra": "mean: 752.5301050006306 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.8253684737540756,
            "unit": "iter/sec",
            "range": "stddev: 0.000011957247935958596",
            "extra": "mean: 998.0147650003346 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.8722954309292423,
            "unit": "iter/sec",
            "range": "stddev: 0.000016681665449983035",
            "extra": "mean: 634.2469749998259 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 3.3681909309563105,
            "unit": "iter/sec",
            "range": "stddev: 0.000009441168499165685",
            "extra": "mean: 540.8674050005402 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 2.427089998367759,
            "unit": "iter/sec",
            "range": "stddev: 0.00001144629604076763",
            "extra": "mean: 750.5880250002406 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.7893914969954765,
            "unit": "iter/sec",
            "range": "stddev: 0.00005484400661127694",
            "extra": "mean: 1.0180805549995853 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.7820218669488206,
            "unit": "iter/sec",
            "range": "stddev: 0.00005252031149118501",
            "extra": "mean: 654.8275950004268 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 3.3772094165119624,
            "unit": "iter/sec",
            "range": "stddev: 0.000009256074753173845",
            "extra": "mean: 539.4230749996609 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 2.444371305094431,
            "unit": "iter/sec",
            "range": "stddev: 0.000010575549915565161",
            "extra": "mean: 745.2814899994564 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.8322624612237424,
            "unit": "iter/sec",
            "range": "stddev: 0.000012325668670771512",
            "extra": "mean: 994.259680000198 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.8511530803639054,
            "unit": "iter/sec",
            "range": "stddev: 0.000012071653069503624",
            "extra": "mean: 638.9501500004258 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 3.3673961613840526,
            "unit": "iter/sec",
            "range": "stddev: 0.000013662692768975333",
            "extra": "mean: 540.9950600002844 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 11.238920991164894,
            "unit": "iter/sec",
            "range": "stddev: 0.000005371454191083142",
            "extra": "mean: 162.09249000013415 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.6325777930388234,
            "unit": "iter/sec",
            "range": "stddev: 0.000028649414765853952",
            "extra": "mean: 692.0003250007767 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.07430037800955663,
            "unit": "iter/sec",
            "range": "stddev: 0.0016169699385563986",
            "extra": "mean: 24.518646300001024 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.05527920313870734,
            "unit": "iter/sec",
            "range": "stddev: 0.00021463591043873525",
            "extra": "mean: 32.95533554999963 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.03398321812992179,
            "unit": "iter/sec",
            "range": "stddev: 0.0003342715375035495",
            "extra": "mean: 53.60718580000139 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.053207464932820414,
            "unit": "iter/sec",
            "range": "stddev: 0.0026954990965863904",
            "extra": "mean: 34.23851692000028 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.5666118022840734,
            "unit": "iter/sec",
            "range": "stddev: 0.000018481827868378324",
            "extra": "mean: 709.7858300002713 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.5198253302936413,
            "unit": "iter/sec",
            "range": "stddev: 0.000010742546906903355",
            "extra": "mean: 722.9646699997261 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.015614840594963486,
            "unit": "iter/sec",
            "range": "stddev: 0.0044052519122655094",
            "extra": "mean: 116.66751750000515 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.03134685218199342,
            "unit": "iter/sec",
            "range": "stddev: 0.0003585027845111678",
            "extra": "mean: 58.11571375001279 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.5019584322967012,
            "unit": "iter/sec",
            "range": "stddev: 0.000012538672999699258",
            "extra": "mean: 728.1274799998982 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.402340741055979,
            "unit": "iter/sec",
            "range": "stddev: 0.00004669546120898873",
            "extra": "mean: 758.320690000005 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 9.316464053523143,
            "unit": "iter/sec",
            "range": "stddev: 0.000008584721283215576",
            "extra": "mean: 195.54035500021882 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.2699425223848895,
            "unit": "iter/sec",
            "range": "stddev: 0.000007588790486076818",
            "extra": "mean: 557.1182600004931 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 22.360388633881815,
            "unit": "iter/sec",
            "range": "stddev: 0.0000037055888433611943",
            "extra": "mean: 81.47196000038548 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 22.844582879071705,
            "unit": "iter/sec",
            "range": "stddev: 0.000002971110630963698",
            "extra": "mean: 79.74514999972371 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 13.576033666385841,
            "unit": "iter/sec",
            "range": "stddev: 0.000005434375024416522",
            "extra": "mean: 134.1882860001533 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 8.152734671123167,
            "unit": "iter/sec",
            "range": "stddev: 0.000004124990882783501",
            "extra": "mean: 223.45197800012784 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 8.397479206427594,
            "unit": "iter/sec",
            "range": "stddev: 0.000007530865963229313",
            "extra": "mean: 216.93946999931768 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 7.267839334670306,
            "unit": "iter/sec",
            "range": "stddev: 0.000009882766145072514",
            "extra": "mean: 250.65836000010222 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.4045186043090167,
            "unit": "iter/sec",
            "range": "stddev: 0.000029517770204118103",
            "extra": "mean: 4.503488019999793 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 4.371014701175662,
            "unit": "iter/sec",
            "range": "stddev: 0.000011058669285518725",
            "extra": "mean: 416.7784399999164 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.6065118068650771,
            "unit": "iter/sec",
            "range": "stddev: 0.0000365895389015154",
            "extra": "mean: 3.003642580000019 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.1595249908391696,
            "unit": "iter/sec",
            "range": "stddev: 0.000025846558897410692",
            "extra": "mean: 1.5711129150000147 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.9409739867530174,
            "unit": "iter/sec",
            "range": "stddev: 0.00003756831195048063",
            "extra": "mean: 1.9360202450005204 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.9559912548714115,
            "unit": "iter/sec",
            "range": "stddev: 0.000013165609767614399",
            "extra": "mean: 1.905608110000685 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.005840238513287559,
            "unit": "iter/sec",
            "range": "stddev: 0.003299725237107853",
            "extra": "mean: 311.92984400001933 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.22443990740729244,
            "unit": "iter/sec",
            "range": "stddev: 0.0017222478079965057",
            "extra": "mean: 8.116848333334778 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.044912886456806723,
            "unit": "iter/sec",
            "range": "stddev: 0.00022564455567528345",
            "extra": "mean: 40.56173700001864 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.04416351687572632,
            "unit": "iter/sec",
            "range": "stddev: 0.0009169326929631159",
            "extra": "mean: 41.249991333321155 msec\nrounds: 3"
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
          "id": "573eb54e912ed182c27b8b2b249679312e462a7b",
          "message": "Split order and orderless patterns (#1910)\n\nThis PR is about reorganizing the large module `mathics.core.pattern`\ninto submodules. Also, to split the code in ExpressionPattern into\nspecialized classes that handle the Ordered and Orderless cases.\n\n\nBenchmarks comparisons in https://mathics3.github.io/mathics-core/cache/\n\n---------\n\nCo-authored-by: R. Bernstein <rocky@users.noreply.github.com>",
          "timestamp": "2026-08-30T18:46:03-03:00",
          "tree_id": "3ec093ddb98aa4923bdce4225d721d9528114066",
          "url": "https://github.com/Mathics3/mathics-core/commit/573eb54e912ed182c27b8b2b249679312e462a7b"
        },
        "date": 1788126481383,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.00003064217745976003",
            "extra": "mean: 2.324305041420669 msec\nrounds: 169"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 16111.54399226208,
            "unit": "iter/sec",
            "range": "stddev: 8.523156710677118e-9",
            "extra": "mean: 144.2633333302486 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 36.13874791585011,
            "unit": "iter/sec",
            "range": "stddev: 0.00001406773405182776",
            "extra": "mean: 64.31614749998715 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.5898537860675097,
            "unit": "iter/sec",
            "range": "stddev: 0.00014516830024309665",
            "extra": "mean: 3.940476600000409 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 11.038052168933334,
            "unit": "iter/sec",
            "range": "stddev: 0.001498779226591866",
            "extra": "mean: 210.57202900004768 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 18.990176621993687,
            "unit": "iter/sec",
            "range": "stddev: 0.000008882078584289248",
            "extra": "mean: 122.39512499998283 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 18.830147684166754,
            "unit": "iter/sec",
            "range": "stddev: 0.000008402415018961729",
            "extra": "mean: 123.43530600001884 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 4.062406083414298,
            "unit": "iter/sec",
            "range": "stddev: 0.00002376952573607998",
            "extra": "mean: 572.1498525000186 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 26.161983018179512,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031691268420449186",
            "extra": "mean: 88.84284650003593 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 26.404813927151448,
            "unit": "iter/sec",
            "range": "stddev: 0.000002717143278403094",
            "extra": "mean: 88.02580650002767 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 9.074184762104434,
            "unit": "iter/sec",
            "range": "stddev: 0.00000537584778150705",
            "extra": "mean: 256.1447780000492 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 9.124396361113519,
            "unit": "iter/sec",
            "range": "stddev: 0.000004439087484085151",
            "extra": "mean: 254.73521200004254 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 8.682965253138653,
            "unit": "iter/sec",
            "range": "stddev: 0.000016672581835505068",
            "extra": "mean: 267.68563200002404 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 8.347047562059865,
            "unit": "iter/sec",
            "range": "stddev: 0.000004280336804660142",
            "extra": "mean: 278.458344000029 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 13.67586350608382,
            "unit": "iter/sec",
            "range": "stddev: 0.000004276986424736113",
            "extra": "mean: 169.956730000024 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 11.299431521742065,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034548606009588912",
            "extra": "mean: 205.70106000008082 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.011546389992576693,
            "unit": "iter/sec",
            "range": "stddev: 0.002813263159780921",
            "extra": "mean: 201.30144945000055 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.011583179519880485,
            "unit": "iter/sec",
            "range": "stddev: 0.000820074791107714",
            "extra": "mean: 200.66209259999894 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.01140111480823476,
            "unit": "iter/sec",
            "range": "stddev: 0.0035687619365021407",
            "extra": "mean: 203.86647100000062 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 21.406942688709922,
            "unit": "iter/sec",
            "range": "stddev: 0.000005966273900835465",
            "extra": "mean: 108.57715999989637 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 21.61660816895837,
            "unit": "iter/sec",
            "range": "stddev: 0.000005038247914369715",
            "extra": "mean: 107.52403999987337 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.612171891220685,
            "unit": "iter/sec",
            "range": "stddev: 0.00037146253951396457",
            "extra": "mean: 3.7968176500001505 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.16870911274753267,
            "unit": "iter/sec",
            "range": "stddev: 0.0006063202414575323",
            "extra": "mean: 13.776997599998708 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.06094195652327633,
            "unit": "iter/sec",
            "range": "stddev: 0.0014552836097664699",
            "extra": "mean: 38.13965244999835 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.29593935447893105,
            "unit": "iter/sec",
            "range": "stddev: 0.0006924195823646936",
            "extra": "mean: 7.85399105000124 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 15.93086911165216,
            "unit": "iter/sec",
            "range": "stddev: 0.000025742569319269003",
            "extra": "mean: 145.89945000054172 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 14.654566097984308,
            "unit": "iter/sec",
            "range": "stddev: 0.000022071755320435452",
            "extra": "mean: 158.60619999799042 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 4.184272418245212,
            "unit": "iter/sec",
            "range": "stddev: 0.000013342407846134307",
            "extra": "mean: 555.4860700000575 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.6415838105945753,
            "unit": "iter/sec",
            "range": "stddev: 0.000019648622942777252",
            "extra": "mean: 879.8907050000082 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 4.616287529999045,
            "unit": "iter/sec",
            "range": "stddev: 0.000012278701124257324",
            "extra": "mean: 503.50092500003996 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 4.470880812141133,
            "unit": "iter/sec",
            "range": "stddev: 0.00001686752645722636",
            "extra": "mean: 519.8763150001184 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 2.309998975217727,
            "unit": "iter/sec",
            "range": "stddev: 0.00001666212885097009",
            "extra": "mean: 1.0061931049997952 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.696008450194981,
            "unit": "iter/sec",
            "range": "stddev: 0.00004858721617741056",
            "extra": "mean: 1.370456049999902 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.7246627648620834,
            "unit": "iter/sec",
            "range": "stddev: 0.000015880423136721825",
            "extra": "mean: 853.0615500000495 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 3.1078587665983726,
            "unit": "iter/sec",
            "range": "stddev: 0.000028955449778394762",
            "extra": "mean: 747.8798800000419 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 2.3087474199499374,
            "unit": "iter/sec",
            "range": "stddev: 0.000016007781604518284",
            "extra": "mean: 1.0067385550001262 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.7246853628774597,
            "unit": "iter/sec",
            "range": "stddev: 0.000022235913883199134",
            "extra": "mean: 1.3476690249999024 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.701877917231916,
            "unit": "iter/sec",
            "range": "stddev: 0.000023173483904367585",
            "extra": "mean: 860.2553899999776 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 3.12422916106102,
            "unit": "iter/sec",
            "range": "stddev: 0.000017093213947168918",
            "extra": "mean: 743.96112499997 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 2.2959001759232023,
            "unit": "iter/sec",
            "range": "stddev: 0.000017855034026948686",
            "extra": "mean: 1.0123719950001941 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.7270433175195117,
            "unit": "iter/sec",
            "range": "stddev: 0.000014620268944321575",
            "extra": "mean: 1.3458290350001079 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.717872667480571,
            "unit": "iter/sec",
            "range": "stddev: 0.000022485393505428447",
            "extra": "mean: 855.1927650000124 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 3.0677974593386037,
            "unit": "iter/sec",
            "range": "stddev: 0.00002551282252158933",
            "extra": "mean: 757.6461850000271 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 10.398645997583754,
            "unit": "iter/sec",
            "range": "stddev: 0.00000725989138125694",
            "extra": "mean: 223.51997000001234 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.5913443027026157,
            "unit": "iter/sec",
            "range": "stddev: 0.00004033829015272444",
            "extra": "mean: 896.9495250000392 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.07032131550781659,
            "unit": "iter/sec",
            "range": "stddev: 0.002084494416540822",
            "extra": "mean: 33.052638799999556 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.05177525548449467,
            "unit": "iter/sec",
            "range": "stddev: 0.00018953851306203985",
            "extra": "mean: 44.89219840000089 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.027582155017870612,
            "unit": "iter/sec",
            "range": "stddev: 0.03724150856899568",
            "extra": "mean: 84.26843514999973 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.050900775722562214,
            "unit": "iter/sec",
            "range": "stddev: 0.0001992766667753963",
            "extra": "mean: 45.66345028000036 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.401732601387647,
            "unit": "iter/sec",
            "range": "stddev: 0.000019141302141943645",
            "extra": "mean: 967.7617900001678 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.483837595908989,
            "unit": "iter/sec",
            "range": "stddev: 0.000011970597089634882",
            "extra": "mean: 935.7717450001246 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.014126421831913276,
            "unit": "iter/sec",
            "range": "stddev: 0.0011157119702346464",
            "extra": "mean: 164.53600700000237 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.029180333014453188,
            "unit": "iter/sec",
            "range": "stddev: 0.00039060048262497954",
            "extra": "mean: 79.65313625000192 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.397466995352453,
            "unit": "iter/sec",
            "range": "stddev: 0.000021517651787058595",
            "extra": "mean: 969.4836449996558 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.3848278341759674,
            "unit": "iter/sec",
            "range": "stddev: 0.000018349610015331837",
            "extra": "mean: 974.6217349999142 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 8.566708491173488,
            "unit": "iter/sec",
            "range": "stddev: 0.000011829212816631803",
            "extra": "mean: 271.3183299998434 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.066023757788315,
            "unit": "iter/sec",
            "range": "stddev: 0.000010220914582560918",
            "extra": "mean: 758.0844849999835 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 21.26115564662669,
            "unit": "iter/sec",
            "range": "stddev: 0.000005233598325804702",
            "extra": "mean: 109.32167000007098 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 21.53858381480248,
            "unit": "iter/sec",
            "range": "stddev: 0.000005200244962158491",
            "extra": "mean: 107.91354999966529 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 12.172538598921996,
            "unit": "iter/sec",
            "range": "stddev: 0.0000057656486066820435",
            "extra": "mean: 190.946614999973 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 7.379917836482932,
            "unit": "iter/sec",
            "range": "stddev: 0.000008131302539107399",
            "extra": "mean: 314.94998899992765 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 6.998184448590141,
            "unit": "iter/sec",
            "range": "stddev: 0.000011300016116559739",
            "extra": "mean: 332.12972000029595 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 6.060265317492415,
            "unit": "iter/sec",
            "range": "stddev: 0.000013767985450683676",
            "extra": "mean: 383.5318950000044 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.37182334668093886,
            "unit": "iter/sec",
            "range": "stddev: 0.00006488211682345756",
            "extra": "mean: 6.251100319999949 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.785077689549337,
            "unit": "iter/sec",
            "range": "stddev: 0.000038690762008598314",
            "extra": "mean: 614.0706300000431 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.5554846771631419,
            "unit": "iter/sec",
            "range": "stddev: 0.000028413904247479524",
            "extra": "mean: 4.184282910000121 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.077904266958876,
            "unit": "iter/sec",
            "range": "stddev: 0.00002211793029529939",
            "extra": "mean: 2.1563186199998086 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.8660525555532996,
            "unit": "iter/sec",
            "range": "stddev: 0.00002113494516179298",
            "extra": "mean: 2.683792139999781 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.8768530245243124,
            "unit": "iter/sec",
            "range": "stddev: 0.000022767338853973266",
            "extra": "mean: 2.6507350449998057 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.005436805001717669,
            "unit": "iter/sec",
            "range": "stddev: 0.004384992997666193",
            "extra": "mean: 427.51304133334617 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.202889968235109,
            "unit": "iter/sec",
            "range": "stddev: 0.002168020160284696",
            "extra": "mean: 11.455987999994477 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.041704470832674,
            "unit": "iter/sec",
            "range": "stddev: 0.000776945318866141",
            "extra": "mean: 55.7327546666689 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.04210736238929876,
            "unit": "iter/sec",
            "range": "stddev: 0.0003980699386260756",
            "extra": "mean: 55.199492666664206 msec\nrounds: 3"
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
          "id": "2c6b3d21a651b43769d48f2d243373c733864a9b",
          "message": "Options refactor (#1925)\n\nReorganize the Options Management section and make it more akin to a\nGuide section.\n\nAs such, the location of several Mathics3 Built-in Functions and Mathics3 Options has been moved to more logical places that correspond better with the Wolfram docs.\n\nMoved functions include `Automatic` and `Default` (into Options) and `FormatType` into drawing options.\n\n* Add `is_option_rule()` option.\n* Simplify a ListExpression check.\n\nMove more evaluation code to `mathics.eval.options`\nOptions are `Predefined` and do not need to be `Builtins`.\n\nAll of this is in preparation for adding `CheckArguments`",
          "timestamp": "2026-08-31T05:09:45-04:00",
          "tree_id": "e6cd8f9d3db86ac65a8667ee18c13d6d1bf76cf6",
          "url": "https://github.com/Mathics3/mathics-core/commit/2c6b3d21a651b43769d48f2d243373c733864a9b"
        },
        "date": 1788167492664,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000021681916936852247",
            "extra": "mean: 1.1042973593752947 msec\nrounds: 320"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 18524.231456927475,
            "unit": "iter/sec",
            "range": "stddev: 1.4872879107403797e-9",
            "extra": "mean: 59.61366666914122 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 27.45756749208084,
            "unit": "iter/sec",
            "range": "stddev: 0.000004471629523265278",
            "extra": "mean: 40.21832449993212 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.4848353728520555,
            "unit": "iter/sec",
            "range": "stddev: 0.000054631707887569484",
            "extra": "mean: 2.2776748999959295 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 6.809610322338858,
            "unit": "iter/sec",
            "range": "stddev: 0.001209494000057897",
            "extra": "mean: 162.16748200005782 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 12.665607871187428,
            "unit": "iter/sec",
            "range": "stddev: 0.000005157619227051902",
            "extra": "mean: 87.18865849995439 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 12.489045022717502,
            "unit": "iter/sec",
            "range": "stddev: 0.000004937963333023279",
            "extra": "mean: 88.42128099999513 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.040890787606402,
            "unit": "iter/sec",
            "range": "stddev: 0.000008515938560612017",
            "extra": "mean: 363.14929950000874 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 17.722967060249005,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014458574908165067",
            "extra": "mean: 62.30883099998153 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 17.953978530993375,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013628603017261726",
            "extra": "mean: 61.50711150004894 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 6.409690715029648,
            "unit": "iter/sec",
            "range": "stddev: 0.0000061510448706392765",
            "extra": "mean: 172.28559199992333 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 6.29049797231858,
            "unit": "iter/sec",
            "range": "stddev: 0.000003926985521866633",
            "extra": "mean: 175.55006999998565 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 6.0839472317363175,
            "unit": "iter/sec",
            "range": "stddev: 0.000006640480349920496",
            "extra": "mean: 181.51001599994743 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 6.0095173577933325,
            "unit": "iter/sec",
            "range": "stddev: 0.000006282623660094352",
            "extra": "mean: 183.7580779999257 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 9.142605963499607,
            "unit": "iter/sec",
            "range": "stddev: 0.000010345553117652156",
            "extra": "mean: 120.78584199997522 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 7.661864928712792,
            "unit": "iter/sec",
            "range": "stddev: 0.0000028343399445274666",
            "extra": "mean: 144.12905600005388 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.00831413033070865,
            "unit": "iter/sec",
            "range": "stddev: 0.00796911331987359",
            "extra": "mean: 132.82175229999922 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.008466300640022099,
            "unit": "iter/sec",
            "range": "stddev: 0.0012287766195123607",
            "extra": "mean: 130.43446085000028 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.008304622295127096,
            "unit": "iter/sec",
            "range": "stddev: 0.0030421250664106046",
            "extra": "mean: 132.97382109999916 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 13.123771908822278,
            "unit": "iter/sec",
            "range": "stddev: 0.000002438512822118793",
            "extra": "mean: 84.14481500039983 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 13.085348532295727,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014835222649947791",
            "extra": "mean: 84.39189499995337 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.4545866554542846,
            "unit": "iter/sec",
            "range": "stddev: 0.00021282612724414623",
            "extra": "mean: 2.4292339999988144 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.12871198199933961,
            "unit": "iter/sec",
            "range": "stddev: 0.00033025610962484215",
            "extra": "mean: 8.579600300001289 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.045973865311527716,
            "unit": "iter/sec",
            "range": "stddev: 0.0007021279407796908",
            "extra": "mean: 24.020111249997456 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.2332216661555466,
            "unit": "iter/sec",
            "range": "stddev: 0.0003007155969136569",
            "extra": "mean: 4.734969000001854 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 10.23037491453776,
            "unit": "iter/sec",
            "range": "stddev: 0.000011833040760310615",
            "extra": "mean: 107.94299999759005 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 9.287134091791021,
            "unit": "iter/sec",
            "range": "stddev: 0.000009994459835839632",
            "extra": "mean: 118.90614999856552 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 2.8940080939790653,
            "unit": "iter/sec",
            "range": "stddev: 0.000007417725491685531",
            "extra": "mean: 381.5806049999537 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 1.8542486695047355,
            "unit": "iter/sec",
            "range": "stddev: 0.00000782981681158481",
            "extra": "mean: 595.5497650001007 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.180163105279196,
            "unit": "iter/sec",
            "range": "stddev: 0.000006344806752316151",
            "extra": "mean: 347.24550999982284 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.1420679009634203,
            "unit": "iter/sec",
            "range": "stddev: 0.00000821379731998596",
            "extra": "mean: 351.45560000046316 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.6063307407049299,
            "unit": "iter/sec",
            "range": "stddev: 0.000009688878056391714",
            "extra": "mean: 687.4657450001109 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.2147224107360013,
            "unit": "iter/sec",
            "range": "stddev: 0.000013859261885929921",
            "extra": "mean: 909.0944149998847 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 1.9683455999187118,
            "unit": "iter/sec",
            "range": "stddev: 0.000009773652094588777",
            "extra": "mean: 561.028185000083 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.2136553340728478,
            "unit": "iter/sec",
            "range": "stddev: 0.000009348659758223957",
            "extra": "mean: 498.8569550000932 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.613891087966859,
            "unit": "iter/sec",
            "range": "stddev: 0.000008771626503504121",
            "extra": "mean: 684.2452799999421 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.2290894405234492,
            "unit": "iter/sec",
            "range": "stddev: 0.000011986198716472561",
            "extra": "mean: 898.4678599996698 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 1.9767258446113767,
            "unit": "iter/sec",
            "range": "stddev: 0.000006532924388515769",
            "extra": "mean: 558.6497299995585 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.221806155822398,
            "unit": "iter/sec",
            "range": "stddev: 0.0000065610004658659335",
            "extra": "mean: 497.0268700000702 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.6409082013608287,
            "unit": "iter/sec",
            "range": "stddev: 0.000011787201767848796",
            "extra": "mean: 672.979365000117 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.2438347954060518,
            "unit": "iter/sec",
            "range": "stddev: 0.000006004283487809814",
            "extra": "mean: 887.8167450001229 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 1.99113860850694,
            "unit": "iter/sec",
            "range": "stddev: 0.000010237694923887649",
            "extra": "mean: 554.6059699999262 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.212469815383205,
            "unit": "iter/sec",
            "range": "stddev: 0.000004877015807579343",
            "extra": "mean: 499.1242599999169 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 7.40489027937849,
            "unit": "iter/sec",
            "range": "stddev: 0.000003293351386387812",
            "extra": "mean: 149.1308200002095 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.0658479320059593,
            "unit": "iter/sec",
            "range": "stddev: 0.00002404632346383617",
            "extra": "mean: 534.5491999999297 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.04867396878036677,
            "unit": "iter/sec",
            "range": "stddev: 0.000976923428960662",
            "extra": "mean: 22.687637500000335 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.03567446446999581,
            "unit": "iter/sec",
            "range": "stddev: 0.0003543884248293411",
            "extra": "mean: 30.954840549998153 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.01941164046097312,
            "unit": "iter/sec",
            "range": "stddev: 0.03271380465628568",
            "extra": "mean: 56.88840990000159 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.03569220248484922,
            "unit": "iter/sec",
            "range": "stddev: 0.0004287919834901119",
            "extra": "mean: 30.939456869999873 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 1.9685903630602497,
            "unit": "iter/sec",
            "range": "stddev: 0.000008677482197092582",
            "extra": "mean: 560.9584299999426 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.026462230966572,
            "unit": "iter/sec",
            "range": "stddev: 0.000009052716007381173",
            "extra": "mean: 544.9385349997726 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.010606202282153124,
            "unit": "iter/sec",
            "range": "stddev: 0.0027702357721929136",
            "extra": "mean: 104.11807450000055 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.021235572917153,
            "unit": "iter/sec",
            "range": "stddev: 0.0015878181766456815",
            "extra": "mean: 52.0022400000002 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.092949703766637,
            "unit": "iter/sec",
            "range": "stddev: 0.000011573775711805603",
            "extra": "mean: 527.6272800000469 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.0890495872852597,
            "unit": "iter/sec",
            "range": "stddev: 0.00001033201045251992",
            "extra": "mean: 528.6123250000685 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 6.740125190191934,
            "unit": "iter/sec",
            "range": "stddev: 0.0000061931313430200805",
            "extra": "mean: 163.839295000372 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.5996381364128625,
            "unit": "iter/sec",
            "range": "stddev: 0.0000041479518419270784",
            "extra": "mean: 424.7888750005302 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 16.29491880593349,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017788581732050083",
            "extra": "mean: 67.76943000005531 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 16.488660369989386,
            "unit": "iter/sec",
            "range": "stddev: 0.000001386462286653418",
            "extra": "mean: 66.97314000021493 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 8.341495204956749,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020550002949751503",
            "extra": "mean: 132.38602100005892 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 5.121802222757711,
            "unit": "iter/sec",
            "range": "stddev: 0.000006564751758533417",
            "extra": "mean: 215.60718499995346 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 4.952443265568057,
            "unit": "iter/sec",
            "range": "stddev: 0.000005033076753378163",
            "extra": "mean: 222.98031499985882 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 4.493668713181453,
            "unit": "iter/sec",
            "range": "stddev: 0.0000063201177101921544",
            "extra": "mean: 245.7451649998177 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.2772145833728914,
            "unit": "iter/sec",
            "range": "stddev: 0.00003913254744370512",
            "extra": "mean: 3.9835471349999803 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 2.8476307712720668,
            "unit": "iter/sec",
            "range": "stddev: 0.000009134835966926942",
            "extra": "mean: 387.79513499989093 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.3551940714462615,
            "unit": "iter/sec",
            "range": "stddev: 0.00004439959903255994",
            "extra": "mean: 3.1089971600000865 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 0.8752686411605264,
            "unit": "iter/sec",
            "range": "stddev: 0.0001039416965935668",
            "extra": "mean: 1.261666770000005 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.7066203529072561,
            "unit": "iter/sec",
            "range": "stddev: 0.00001724662145589256",
            "extra": "mean: 1.5627873649999913 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.7170523188351982,
            "unit": "iter/sec",
            "range": "stddev: 0.000016303204861808998",
            "extra": "mean: 1.540051304999821 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.004131154146566436,
            "unit": "iter/sec",
            "range": "stddev: 0.004854607023709344",
            "extra": "mean: 267.3096476666501 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.14958955353759262,
            "unit": "iter/sec",
            "range": "stddev: 0.0016662105339132276",
            "extra": "mean: 7.382182333325697 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03334418852829727,
            "unit": "iter/sec",
            "range": "stddev: 0.0003558360201040385",
            "extra": "mean: 33.11813566667373 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03383608791305707,
            "unit": "iter/sec",
            "range": "stddev: 0.00014541985647300857",
            "extra": "mean: 32.63667366667278 msec\nrounds: 3"
          }
        ]
      }
    ]
  }
}