window.BENCHMARK_DATA = {
  "lastUpdate": 1788625271560,
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
          "id": "25905039ead5eb64330b4aeb20d9f06da88fe965",
          "message": "mypy/cython compiling mathics.core.utils (#1924)\n\nThis PR continues with the baby-step refactor of `mathics.core.pattern`related modules. In this case, auxiliary functions appearing in `mathics.core.utils` were rewritten in a type-safe way, and documented.\n\nThis version also makes sure that the reference benchmarks can run in a finite time when Cython is activated. With the master version, a long sum of terms (which remains unevaluated) consumes all the memory,\nbecause of an unhappy conversion from a generator of permutations into an astronomically large list of permutations.\n\nAlso, docstrings were included.\n\n---------\n\nCo-authored-by: R. Bernstein <rocky@users.noreply.github.com>",
          "timestamp": "2026-08-31T05:18:16-04:00",
          "tree_id": "3378f471ce06ce6bee0fb7ec5e7881a66d6a8e26",
          "url": "https://github.com/Mathics3/mathics-core/commit/25905039ead5eb64330b4aeb20d9f06da88fe965"
        },
        "date": 1788168014580,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000051616655767699035",
            "extra": "mean: 2.3294338235302803 msec\nrounds: 170"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 15947.343791752317,
            "unit": "iter/sec",
            "range": "stddev: 2.038390405792018e-8",
            "extra": "mean: 146.07033333883615 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 40.22346584913405,
            "unit": "iter/sec",
            "range": "stddev: 0.000007877533853796172",
            "extra": "mean: 57.912310000020284 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.5939463642988188,
            "unit": "iter/sec",
            "range": "stddev: 0.00019274612513471527",
            "extra": "mean: 3.921959899999194 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 12.692956702889456,
            "unit": "iter/sec",
            "range": "stddev: 0.0012382918415382305",
            "extra": "mean: 183.5217655000747 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 18.878222556072327,
            "unit": "iter/sec",
            "range": "stddev: 0.000008942991717279637",
            "extra": "mean: 123.39264549993345 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 18.72836131259146,
            "unit": "iter/sec",
            "range": "stddev: 0.000009384779268748465",
            "extra": "mean: 124.38001300007785 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 4.172782900189494,
            "unit": "iter/sec",
            "range": "stddev: 0.0000066895483340990565",
            "extra": "mean: 558.2446725000949 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 27.034793607613565,
            "unit": "iter/sec",
            "range": "stddev: 0.0000030347055376688147",
            "extra": "mean: 86.16429099996026 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 27.194447140434413,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026304918520774812",
            "extra": "mean: 85.65843649995486 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 7.81309653833298,
            "unit": "iter/sec",
            "range": "stddev: 0.0000642960762421666",
            "extra": "mean: 298.1447639999715 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 9.194040439305349,
            "unit": "iter/sec",
            "range": "stddev: 0.000005646385857457631",
            "extra": "mean: 253.3634520000305 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 8.931158048844882,
            "unit": "iter/sec",
            "range": "stddev: 0.00000431869367219274",
            "extra": "mean: 260.8210280000094 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 8.456589058704125,
            "unit": "iter/sec",
            "range": "stddev: 0.000003915433548461097",
            "extra": "mean: 275.4578479999168 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 13.822051998486065,
            "unit": "iter/sec",
            "range": "stddev: 0.00000512345659360324",
            "extra": "mean: 168.53024600004574 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 11.061742963899965,
            "unit": "iter/sec",
            "range": "stddev: 0.00002075225307113544",
            "extra": "mean: 210.58470000002671 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.011420892661802913,
            "unit": "iter/sec",
            "range": "stddev: 0.002749647654605217",
            "extra": "mean: 203.96250034999923 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.011420777422330181,
            "unit": "iter/sec",
            "range": "stddev: 0.0022565559830155712",
            "extra": "mean: 203.9645584000013 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.01138831422157007,
            "unit": "iter/sec",
            "range": "stddev: 0.001807830730489352",
            "extra": "mean: 204.5459739000009 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 21.567489722268917,
            "unit": "iter/sec",
            "range": "stddev: 0.000006373295868132587",
            "extra": "mean: 108.00671999973588 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 21.60314870114326,
            "unit": "iter/sec",
            "range": "stddev: 0.000005138689321652337",
            "extra": "mean: 107.82843999990632 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.6133982716243501,
            "unit": "iter/sec",
            "range": "stddev: 0.00034625122863060376",
            "extra": "mean: 3.7975878499977966 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.1674078166443183,
            "unit": "iter/sec",
            "range": "stddev: 0.0008335551823733816",
            "extra": "mean: 13.914725549999218 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.06120043320550578,
            "unit": "iter/sec",
            "range": "stddev: 0.0011470165143255137",
            "extra": "mean: 38.062374749999606 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.3124979074528802,
            "unit": "iter/sec",
            "range": "stddev: 0.00042882827237146096",
            "extra": "mean: 7.454238149999526 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 15.681517959362901,
            "unit": "iter/sec",
            "range": "stddev: 0.00002726416149356476",
            "extra": "mean: 148.5464500035505 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 14.56100903919608,
            "unit": "iter/sec",
            "range": "stddev: 0.000022888896777287078",
            "extra": "mean: 159.97749999741018 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 4.1809249594638525,
            "unit": "iter/sec",
            "range": "stddev: 0.000014004600527721634",
            "extra": "mean: 557.157530000012 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.6175066158874625,
            "unit": "iter/sec",
            "range": "stddev: 0.000027865199536281478",
            "extra": "mean: 889.9438149998673 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 4.538061279163391,
            "unit": "iter/sec",
            "range": "stddev: 0.000010236664251528199",
            "extra": "mean: 513.3103500003244 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.48206754307087,
            "unit": "iter/sec",
            "range": "stddev: 0.000152435536954686",
            "extra": "mean: 668.9800800003809 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 2.1857979679966606,
            "unit": "iter/sec",
            "range": "stddev: 0.0000658669944348793",
            "extra": "mean: 1.0657132350000609 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.6944963798452195,
            "unit": "iter/sec",
            "range": "stddev: 0.00003589759106430865",
            "extra": "mean: 1.3747056950001024 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.6800771476047838,
            "unit": "iter/sec",
            "range": "stddev: 0.000016685166215762664",
            "extra": "mean: 869.1667050003105 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 3.1006950932677864,
            "unit": "iter/sec",
            "range": "stddev: 0.00002022671842095341",
            "extra": "mean: 751.261815000106 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 2.2557067805141697,
            "unit": "iter/sec",
            "range": "stddev: 0.000025867294122347515",
            "extra": "mean: 1.0326846749998708 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.7077308728169869,
            "unit": "iter/sec",
            "range": "stddev: 0.00000939599787443668",
            "extra": "mean: 1.3640520650000099 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.6503679824248922,
            "unit": "iter/sec",
            "range": "stddev: 0.00003614762636013423",
            "extra": "mean: 878.909584999974 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 3.1361172360514744,
            "unit": "iter/sec",
            "range": "stddev: 0.000019701163308728865",
            "extra": "mean: 742.776384999928 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 2.283764270370838,
            "unit": "iter/sec",
            "range": "stddev: 0.000015837794552630837",
            "extra": "mean: 1.0199974900001507 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.7055034003506988,
            "unit": "iter/sec",
            "range": "stddev: 0.00002802131839416625",
            "extra": "mean: 1.3658335849997627 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.6700373519334466,
            "unit": "iter/sec",
            "range": "stddev: 0.00002147032896067582",
            "extra": "mean: 872.4349199997049 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 3.1140491071897367,
            "unit": "iter/sec",
            "range": "stddev: 0.00001630539757895099",
            "extra": "mean: 748.0401699999106 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 10.521074808491289,
            "unit": "iter/sec",
            "range": "stddev: 0.000006198931521536363",
            "extra": "mean: 221.4064499997903 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.563307275012481,
            "unit": "iter/sec",
            "range": "stddev: 0.000036571015400083924",
            "extra": "mean: 908.7610550002978 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.06995593565393722,
            "unit": "iter/sec",
            "range": "stddev: 0.0019493877163354854",
            "extra": "mean: 33.298587200000895 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.05136264284893141,
            "unit": "iter/sec",
            "range": "stddev: 0.0004678334735089193",
            "extra": "mean: 45.35268620000039 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.027547267100997454,
            "unit": "iter/sec",
            "range": "stddev: 0.0356277335967358",
            "extra": "mean: 84.56134014999748 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.0504608272801985,
            "unit": "iter/sec",
            "range": "stddev: 0.0003330499711244622",
            "extra": "mean: 46.16321113000026 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.445002887490284,
            "unit": "iter/sec",
            "range": "stddev: 0.000023412364963733153",
            "extra": "mean: 952.7325449997193 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.480585167581485,
            "unit": "iter/sec",
            "range": "stddev: 0.000028963564020204575",
            "extra": "mean: 939.0662550003981 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.014472032870373661,
            "unit": "iter/sec",
            "range": "stddev: 0.00576489945854171",
            "extra": "mean: 160.96106499999507 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.029085155367198384,
            "unit": "iter/sec",
            "range": "stddev: 0.0004239554166043035",
            "extra": "mean: 80.09012825000639 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.427929787811104,
            "unit": "iter/sec",
            "range": "stddev: 0.000014975981412586511",
            "extra": "mean: 959.4321199998035 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.404309528105232,
            "unit": "iter/sec",
            "range": "stddev: 0.000020420910450718778",
            "extra": "mean: 968.857709999611 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 8.688136129726693,
            "unit": "iter/sec",
            "range": "stddev: 0.00001199532471084412",
            "extra": "mean: 268.1166350006947 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.1886398129722604,
            "unit": "iter/sec",
            "range": "stddev: 0.000010179493174148397",
            "extra": "mean: 730.5415349998157 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 21.581778768167442,
            "unit": "iter/sec",
            "range": "stddev: 0.000004816645851773",
            "extra": "mean: 107.93521000067585 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 22.075167569624114,
            "unit": "iter/sec",
            "range": "stddev: 0.000004231931257095058",
            "extra": "mean: 105.52281499940364 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 12.295211281772227,
            "unit": "iter/sec",
            "range": "stddev: 0.000005749345533726391",
            "extra": "mean: 189.4586250000998 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 7.513372670666255,
            "unit": "iter/sec",
            "range": "stddev: 0.000009192295925195897",
            "extra": "mean: 310.03837100013243 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 7.056984453921907,
            "unit": "iter/sec",
            "range": "stddev: 0.000016489232199784517",
            "extra": "mean: 330.0891249995175 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 6.085282195718087,
            "unit": "iter/sec",
            "range": "stddev: 0.000010511195929991596",
            "extra": "mean: 382.79799500003264 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.37696962236903386,
            "unit": "iter/sec",
            "range": "stddev: 0.00011261544815291989",
            "extra": "mean: 6.179367475000106 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.7397906170382487,
            "unit": "iter/sec",
            "range": "stddev: 0.000017949251435794403",
            "extra": "mean: 622.8781400000116 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.5615975655849068,
            "unit": "iter/sec",
            "range": "stddev: 0.000037179795299170023",
            "extra": "mean: 4.147870230000308 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.0997293541014161,
            "unit": "iter/sec",
            "range": "stddev: 0.000012263598806216286",
            "extra": "mean: 2.1181882749993974 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.8808797654677853,
            "unit": "iter/sec",
            "range": "stddev: 0.000020621650387470396",
            "extra": "mean: 2.6444401550003254 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.896128291705109,
            "unit": "iter/sec",
            "range": "stddev: 0.000018269852264309175",
            "extra": "mean: 2.5994423400001665 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.005481982288042238,
            "unit": "iter/sec",
            "range": "stddev: 0.004119638623110494",
            "extra": "mean: 424.9254560000016 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.2013042347361487,
            "unit": "iter/sec",
            "range": "stddev: 0.0018162251280708713",
            "extra": "mean: 11.57170800000055 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.042549726511609307,
            "unit": "iter/sec",
            "range": "stddev: 0.0004230727494337311",
            "extra": "mean: 54.74615266668555 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.04260247350696437,
            "unit": "iter/sec",
            "range": "stddev: 0.0011860839603913015",
            "extra": "mean: 54.67837033334414 msec\nrounds: 3"
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
          "id": "6af59769bb44a2bfde7a3e3c0749bc34677d55b2",
          "message": "Add mypy pre-commit hook and sync up benchmark.yml to v6 (#1926)\n\n* `pre-commit-config.yml`: run `mypy` over Python code in the pre-commit\nhook.\n* `workflows.benchmark.yml` : use v6 in checkout and Python setup like\nthe other yml files.",
          "timestamp": "2026-08-31T09:12:20-03:00",
          "tree_id": "63d881f07db1fc5d9a18103c6ac7a098a8c6c733",
          "url": "https://github.com/Mathics3/mathics-core/commit/6af59769bb44a2bfde7a3e3c0749bc34677d55b2"
        },
        "date": 1788178458823,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.0002178820625873522",
            "extra": "mean: 2.398483923973451 msec\nrounds: 171"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 17546.244732061004,
            "unit": "iter/sec",
            "range": "stddev: 2.027245667508413e-9",
            "extra": "mean: 136.6950000184867 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 41.61687607947074,
            "unit": "iter/sec",
            "range": "stddev: 0.000008068565488441666",
            "extra": "mean: 57.63248350004346 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.6158872246761045,
            "unit": "iter/sec",
            "range": "stddev: 0.000055699059806466816",
            "extra": "mean: 3.8943556999981865 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 11.24272851199416,
            "unit": "iter/sec",
            "range": "stddev: 0.0015304366961573135",
            "extra": "mean: 213.33646199983036 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 18.6517901446492,
            "unit": "iter/sec",
            "range": "stddev: 0.000014998699575251033",
            "extra": "mean: 128.59269300011533 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 19.443528672796162,
            "unit": "iter/sec",
            "range": "stddev: 0.000009959786656322992",
            "extra": "mean: 123.35641149999788 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 4.260450076986343,
            "unit": "iter/sec",
            "range": "stddev: 0.000007102615811903998",
            "extra": "mean: 562.9649170000448 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 27.64903029784373,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026438777874717285",
            "extra": "mean: 86.7474879999861 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 27.384327147223036,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031691364718233276",
            "extra": "mean: 87.58600899992075 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 9.456681943731427,
            "unit": "iter/sec",
            "range": "stddev: 0.0000055153938038546345",
            "extra": "mean: 253.6284860001388 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 9.399407660428144,
            "unit": "iter/sec",
            "range": "stddev: 0.000006069014066163063",
            "extra": "mean: 255.17394399980728 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 9.162895218818932,
            "unit": "iter/sec",
            "range": "stddev: 0.000003861562810283702",
            "extra": "mean: 261.7604880002773 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 8.655732974054613,
            "unit": "iter/sec",
            "range": "stddev: 0.000006877572231860494",
            "extra": "mean: 277.0977259999654 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 14.235220115968737,
            "unit": "iter/sec",
            "range": "stddev: 0.000005516903303429207",
            "extra": "mean: 168.48941600017042 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 10.506138573895383,
            "unit": "iter/sec",
            "range": "stddev: 0.000042999136376685125",
            "extra": "mean: 228.29357399996297 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.011864648707753441,
            "unit": "iter/sec",
            "range": "stddev: 0.0014369107574044183",
            "extra": "mean: 202.1538086000021 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.011704843644110589,
            "unit": "iter/sec",
            "range": "stddev: 0.0024240414607354746",
            "extra": "mean: 204.9137944000023 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.011737712953675343,
            "unit": "iter/sec",
            "range": "stddev: 0.00226364758971831",
            "extra": "mean: 204.33997094999938 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 22.33303857401437,
            "unit": "iter/sec",
            "range": "stddev: 0.0000057912426365183424",
            "extra": "mean: 107.39622000045301 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 22.190301769114857,
            "unit": "iter/sec",
            "range": "stddev: 0.00000497828472262003",
            "extra": "mean: 108.08703499975536 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.6342920169300431,
            "unit": "iter/sec",
            "range": "stddev: 0.0003997293869931911",
            "extra": "mean: 3.781356000004621 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.17653999935374412,
            "unit": "iter/sec",
            "range": "stddev: 0.0006256128599885625",
            "extra": "mean: 13.586065099997313 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.06301213073807395,
            "unit": "iter/sec",
            "range": "stddev: 0.0012901531671332548",
            "extra": "mean: 38.06384414999968 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.32596431691875016,
            "unit": "iter/sec",
            "range": "stddev: 0.00037007690069110373",
            "extra": "mean: 7.358118049992868 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 16.438972682275125,
            "unit": "iter/sec",
            "range": "stddev: 0.000026784933525536834",
            "extra": "mean: 145.90229999953408 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 14.993340461407971,
            "unit": "iter/sec",
            "range": "stddev: 0.000019338203939742383",
            "extra": "mean: 159.96995000193692 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 4.285176492474788,
            "unit": "iter/sec",
            "range": "stddev: 0.00001586829993265129",
            "extra": "mean: 559.7164850001946 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.679820437502751,
            "unit": "iter/sec",
            "range": "stddev: 0.000026844689209605984",
            "extra": "mean: 895.0166549996652 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 4.661432865018867,
            "unit": "iter/sec",
            "range": "stddev: 0.000016465211061659777",
            "extra": "mean: 514.5379100002857 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 4.522985342273784,
            "unit": "iter/sec",
            "range": "stddev: 0.000017034563862224148",
            "extra": "mean: 530.2877950003904 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 2.3300723361142657,
            "unit": "iter/sec",
            "range": "stddev: 0.000021049284433048472",
            "extra": "mean: 1.0293602850001093 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.7477824476058559,
            "unit": "iter/sec",
            "range": "stddev: 0.000024647072872632482",
            "extra": "mean: 1.3723011850009925 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.4867355707394894,
            "unit": "iter/sec",
            "range": "stddev: 0.00014965579010422613",
            "extra": "mean: 964.5110450003358 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 3.08415699079583,
            "unit": "iter/sec",
            "range": "stddev: 0.000042615586859349613",
            "extra": "mean: 777.6789349995283 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 2.2821542056580735,
            "unit": "iter/sec",
            "range": "stddev: 0.000037471627536751907",
            "extra": "mean: 1.050973645000397 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.753414259084554,
            "unit": "iter/sec",
            "range": "stddev: 0.000008678017414525709",
            "extra": "mean: 1.3678934749998461 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.7304983212452005,
            "unit": "iter/sec",
            "range": "stddev: 0.000015991871696664042",
            "extra": "mean: 878.4052000001452 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 3.1741453468319105,
            "unit": "iter/sec",
            "range": "stddev: 0.000019932370110428556",
            "extra": "mean: 755.6314100006034 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 2.3196809969670023,
            "unit": "iter/sec",
            "range": "stddev: 0.000027822797884493788",
            "extra": "mean: 1.0339714500008768 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.7432537075504968,
            "unit": "iter/sec",
            "range": "stddev: 0.000019076122407572124",
            "extra": "mean: 1.3758662399999366 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.7518142134845442,
            "unit": "iter/sec",
            "range": "stddev: 0.000018469513762243176",
            "extra": "mean: 871.6009649998568 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 3.1874897901436494,
            "unit": "iter/sec",
            "range": "stddev: 0.000012685437854755503",
            "extra": "mean: 752.4679550002134 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 11.032894063786665,
            "unit": "iter/sec",
            "range": "stddev: 0.00000727540285318614",
            "extra": "mean: 217.39390499959654 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.678947999693887,
            "unit": "iter/sec",
            "range": "stddev: 0.00003604507184828218",
            "extra": "mean: 895.3081300001031 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.07170112729764866,
            "unit": "iter/sec",
            "range": "stddev: 0.0018794308311668173",
            "extra": "mean: 33.45113270000297 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.051534009542645,
            "unit": "iter/sec",
            "range": "stddev: 0.0027202495352688727",
            "extra": "mean: 46.54176814999573 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.028610268722662105,
            "unit": "iter/sec",
            "range": "stddev: 0.03450384878575554",
            "extra": "mean: 83.8329743499969 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.052297897990156904,
            "unit": "iter/sec",
            "range": "stddev: 0.00024925328459523465",
            "extra": "mean: 45.86195652499981 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.510789097389459,
            "unit": "iter/sec",
            "range": "stddev: 0.000023347047452377645",
            "extra": "mean: 955.2709649994995 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.577498820692424,
            "unit": "iter/sec",
            "range": "stddev: 0.000015186094582984238",
            "extra": "mean: 930.5470499998592 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.014915963979161147,
            "unit": "iter/sec",
            "range": "stddev: 0.004918384100579495",
            "extra": "mean: 160.79979324999272 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.027728663171329392,
            "unit": "iter/sec",
            "range": "stddev: 0.00855826504710642",
            "extra": "mean: 86.49836125000832 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.482254528528515,
            "unit": "iter/sec",
            "range": "stddev: 0.00001644937336802437",
            "extra": "mean: 966.252210000107 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.4498631772350343,
            "unit": "iter/sec",
            "range": "stddev: 0.000020177049373952328",
            "extra": "mean: 979.0277050004194 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 8.870370524413623,
            "unit": "iter/sec",
            "range": "stddev: 0.000012537520670657848",
            "extra": "mean: 270.3927550007279 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.2428291187518234,
            "unit": "iter/sec",
            "range": "stddev: 0.000015458440445760027",
            "extra": "mean: 739.6269850002568 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 22.319983833514705,
            "unit": "iter/sec",
            "range": "stddev: 0.000004487117746760558",
            "extra": "mean: 107.45903500037457 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 22.517986099951568,
            "unit": "iter/sec",
            "range": "stddev: 0.000003855005358624448",
            "extra": "mean: 106.51414000022896 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 12.552834646224241,
            "unit": "iter/sec",
            "range": "stddev: 0.000010367085636042502",
            "extra": "mean: 191.07110000010152 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 7.630721058035767,
            "unit": "iter/sec",
            "range": "stddev: 0.0000078044857184979",
            "extra": "mean: 314.31943399996953 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 7.216748541210778,
            "unit": "iter/sec",
            "range": "stddev: 0.000017076202685995087",
            "extra": "mean: 332.3496599995224 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 6.415893106930597,
            "unit": "iter/sec",
            "range": "stddev: 0.000007983890081660807",
            "extra": "mean: 373.8347699999167 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.38638109363138584,
            "unit": "iter/sec",
            "range": "stddev: 0.0000688672979197907",
            "extra": "mean: 6.2075602650000405 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 4.034020694545541,
            "unit": "iter/sec",
            "range": "stddev: 0.00001667496041691568",
            "extra": "mean: 594.5641099998511 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.5818942350279295,
            "unit": "iter/sec",
            "range": "stddev: 0.00006424276018079287",
            "extra": "mean: 4.121855449999998 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.12297173206445,
            "unit": "iter/sec",
            "range": "stddev: 0.00002037357268067098",
            "extra": "mean: 2.135836419999748 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.9048137271047492,
            "unit": "iter/sec",
            "range": "stddev: 0.000020398110639599757",
            "extra": "mean: 2.650804085000118 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.9145161565701735,
            "unit": "iter/sec",
            "range": "stddev: 0.000022860046838647118",
            "extra": "mean: 2.6226807550003173 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.005644463354339129,
            "unit": "iter/sec",
            "range": "stddev: 0.0050373977975110935",
            "extra": "mean: 424.9268306666636 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.20734239248650455,
            "unit": "iter/sec",
            "range": "stddev: 0.001821016348046595",
            "extra": "mean: 11.567744999998316 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.043603909958731576,
            "unit": "iter/sec",
            "range": "stddev: 0.00032905160933065957",
            "extra": "mean: 55.00616633332811 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.04347950480008649,
            "unit": "iter/sec",
            "range": "stddev: 0.0010469438249170325",
            "extra": "mean: 55.16355199999149 msec\nrounds: 3"
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
          "id": "f7f15cbd33e8093c65d41eef651c2d4fe10d3088",
          "message": "Fix remaining makeboxes tests (#1929)\n\nThis is another round of the remaining fixes for MakeBoxes. With this, the number of xfailing tests is reduced to 9.",
          "timestamp": "2026-09-02T07:53:40-04:00",
          "tree_id": "0d09dcff99556e15f8f2f8ad33874d21a7d13b7b",
          "url": "https://github.com/Mathics3/mathics-core/commit/f7f15cbd33e8093c65d41eef651c2d4fe10d3088"
        },
        "date": 1788350128667,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000029595953897602987",
            "extra": "mean: 1.8005343053094578 msec\nrounds: 226"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 17110.57409821804,
            "unit": "iter/sec",
            "range": "stddev: 2.550175749414708e-9",
            "extra": "mean: 105.22933333353042 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 39.018725495813534,
            "unit": "iter/sec",
            "range": "stddev: 0.000006738404518506058",
            "extra": "mean: 46.14539000005635 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.5895034518642065,
            "unit": "iter/sec",
            "range": "stddev: 0.00009376966708670099",
            "extra": "mean: 3.054323599998554 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 11.74593698988622,
            "unit": "iter/sec",
            "range": "stddev: 0.0010634711067948322",
            "extra": "mean: 153.28996799998149 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 18.688507325240607,
            "unit": "iter/sec",
            "range": "stddev: 0.00000711046637851251",
            "extra": "mean: 96.34446850004252 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 18.3652694606915,
            "unit": "iter/sec",
            "range": "stddev: 0.000007079261144986368",
            "extra": "mean: 98.04017900000161 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 4.150256206038197,
            "unit": "iter/sec",
            "range": "stddev: 0.000006534730350903338",
            "extra": "mean: 433.8369044999837 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 26.355447312976928,
            "unit": "iter/sec",
            "range": "stddev: 0.0000027818217853551617",
            "extra": "mean: 68.31734949999912 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 26.75530841743147,
            "unit": "iter/sec",
            "range": "stddev: 0.000002168956704706737",
            "extra": "mean: 67.2963390000163 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 9.105908673420437,
            "unit": "iter/sec",
            "range": "stddev: 0.000004165394943019425",
            "extra": "mean: 197.73252400005958 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 9.028434797230458,
            "unit": "iter/sec",
            "range": "stddev: 0.000004911086904139521",
            "extra": "mean: 199.42928600002574 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 8.828158605982228,
            "unit": "iter/sec",
            "range": "stddev: 0.000003386671346637008",
            "extra": "mean: 203.95355200000154 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 8.313801107290454,
            "unit": "iter/sec",
            "range": "stddev: 0.0000038155043188139935",
            "extra": "mean: 216.57173200000557 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 13.637392994212407,
            "unit": "iter/sec",
            "range": "stddev: 0.00000314270184845063",
            "extra": "mean: 132.02921599997808 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 10.869156700925322,
            "unit": "iter/sec",
            "range": "stddev: 0.000018159657178625707",
            "extra": "mean: 165.65538199998286 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.011430559045671689,
            "unit": "iter/sec",
            "range": "stddev: 0.0006093287539129992",
            "extra": "mean: 157.51935649999993 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.011371032372030593,
            "unit": "iter/sec",
            "range": "stddev: 0.0022502680480468175",
            "extra": "mean: 158.34396090000098 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.011322222710777971,
            "unit": "iter/sec",
            "range": "stddev: 0.0005390159477519906",
            "extra": "mean: 159.0265755499999 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 20.66706345573345,
            "unit": "iter/sec",
            "range": "stddev: 0.000004254271362596231",
            "extra": "mean: 87.12095500001737 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 21.04561833206086,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034426004579470275",
            "extra": "mean: 85.55388000011988 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.610420075704668,
            "unit": "iter/sec",
            "range": "stddev: 0.0002557965471782392",
            "extra": "mean: 2.9496643000001654 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.16771782555244025,
            "unit": "iter/sec",
            "range": "stddev: 0.0005932610157659061",
            "extra": "mean: 10.735497549999451 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.06113679614160455,
            "unit": "iter/sec",
            "range": "stddev: 0.0008757983218127678",
            "extra": "mean: 29.45091039999994 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.3158797644891199,
            "unit": "iter/sec",
            "range": "stddev: 0.00028952864384792354",
            "extra": "mean: 5.700062200000389 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 15.746637497156847,
            "unit": "iter/sec",
            "range": "stddev: 0.000021790925429104736",
            "extra": "mean: 114.34405000017023 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 14.478153564541222,
            "unit": "iter/sec",
            "range": "stddev: 0.000015582172873237",
            "extra": "mean: 124.36214999951291 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 4.150000698512035,
            "unit": "iter/sec",
            "range": "stddev: 0.000009028949316506534",
            "extra": "mean: 433.8636150001207 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.601392100850604,
            "unit": "iter/sec",
            "range": "stddev: 0.00001699339237939282",
            "extra": "mean: 692.1426050001145 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 4.496865036265635,
            "unit": "iter/sec",
            "range": "stddev: 0.000009920481726616906",
            "extra": "mean: 400.39767499997936 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 4.3965919072499124,
            "unit": "iter/sec",
            "range": "stddev: 0.000009051437476192447",
            "extra": "mean: 409.5295499999452 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 2.250548771343286,
            "unit": "iter/sec",
            "range": "stddev: 0.000009355264260472994",
            "extra": "mean: 800.0423399999335 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.6874702703814621,
            "unit": "iter/sec",
            "range": "stddev: 0.000014650444288544835",
            "extra": "mean: 1.0670020899997468 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.6637799446184984,
            "unit": "iter/sec",
            "range": "stddev: 0.000013285203988941247",
            "extra": "mean: 675.9320750000342 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 3.072506618257397,
            "unit": "iter/sec",
            "range": "stddev: 0.00001215090799077905",
            "extra": "mean: 586.0147850000885 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 2.2555348747895207,
            "unit": "iter/sec",
            "range": "stddev: 0.000015195441710115503",
            "extra": "mean: 798.2737600000434 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.7035400579711328,
            "unit": "iter/sec",
            "range": "stddev: 0.00000890086440822189",
            "extra": "mean: 1.0569368750000763 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.6623397340414123,
            "unit": "iter/sec",
            "range": "stddev: 0.000013842206288072735",
            "extra": "mean: 676.2977250000546 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 3.0779644047754897,
            "unit": "iter/sec",
            "range": "stddev: 0.000016508940723378897",
            "extra": "mean: 584.9756749999813 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 2.2662673077240285,
            "unit": "iter/sec",
            "range": "stddev: 0.000012479312395829752",
            "extra": "mean: 794.4933500001383 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.690649302794268,
            "unit": "iter/sec",
            "range": "stddev: 0.000018319035226539925",
            "extra": "mean: 1.064995739999759 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.648188480638404,
            "unit": "iter/sec",
            "range": "stddev: 0.00001633695548679142",
            "extra": "mean: 679.9116900000257 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.7866215575986106,
            "unit": "iter/sec",
            "range": "stddev: 0.00009064694423435394",
            "extra": "mean: 646.1352099999829 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 9.703035409529528,
            "unit": "iter/sec",
            "range": "stddev: 0.00003031758850411918",
            "extra": "mean: 185.56402499996238 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.5666442282277866,
            "unit": "iter/sec",
            "range": "stddev: 0.00003056701547506998",
            "extra": "mean: 701.5130049997964 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.06951995792160438,
            "unit": "iter/sec",
            "range": "stddev: 0.0018388161456310036",
            "extra": "mean: 25.89953100000244 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.051311352555091276,
            "unit": "iter/sec",
            "range": "stddev: 0.0002307223247551219",
            "extra": "mean: 35.09036919999886 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.026678352861180466,
            "unit": "iter/sec",
            "range": "stddev: 0.03094033085756089",
            "extra": "mean: 67.4904599499996 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.050093002851830576,
            "unit": "iter/sec",
            "range": "stddev: 0.0002716689135389335",
            "extra": "mean: 35.94382853499987 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.4128776859678336,
            "unit": "iter/sec",
            "range": "stddev: 0.000017194768800203913",
            "extra": "mean: 746.2186400000803 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.469844388857767,
            "unit": "iter/sec",
            "range": "stddev: 0.000008704658290986402",
            "extra": "mean: 729.0071850000857 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.0142883424893327,
            "unit": "iter/sec",
            "range": "stddev: 0.0038674144736815727",
            "extra": "mean: 126.01421800000168 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.02895039912416636,
            "unit": "iter/sec",
            "range": "stddev: 0.0005261623985209455",
            "extra": "mean: 62.19376450000169 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.366155106113718,
            "unit": "iter/sec",
            "range": "stddev: 0.00001555240152621007",
            "extra": "mean: 760.9536249999849 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.354383984825963,
            "unit": "iter/sec",
            "range": "stddev: 0.00001646114636552964",
            "extra": "mean: 764.7581350000365 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 8.429799033105532,
            "unit": "iter/sec",
            "range": "stddev: 0.000008490813059016979",
            "extra": "mean: 213.59160500011853 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.0765272649479534,
            "unit": "iter/sec",
            "range": "stddev: 0.000008544132853672463",
            "extra": "mean: 585.2489350000668 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 20.69276643065935,
            "unit": "iter/sec",
            "range": "stddev: 0.000003394989311689696",
            "extra": "mean: 87.01273999989212 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 20.90349324106327,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034106335801028847",
            "extra": "mean: 86.13556999996774 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 11.894078784649183,
            "unit": "iter/sec",
            "range": "stddev: 0.000004498636052969171",
            "extra": "mean: 151.38072799999236 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 7.264546387144913,
            "unit": "iter/sec",
            "range": "stddev: 0.000005372879999355809",
            "extra": "mean: 247.85226899997778 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 6.872193192654489,
            "unit": "iter/sec",
            "range": "stddev: 0.000011360820021476655",
            "extra": "mean: 262.0028650000705 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 6.113407456579691,
            "unit": "iter/sec",
            "range": "stddev: 0.000007979998522160764",
            "extra": "mean: 294.52221500001485 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.377305288046379,
            "unit": "iter/sec",
            "range": "stddev: 0.00005539764416126836",
            "extra": "mean: 4.772088710000091 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.871771948114709,
            "unit": "iter/sec",
            "range": "stddev: 0.000013808239195374378",
            "extra": "mean: 465.0414150002291 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.5496436065836767,
            "unit": "iter/sec",
            "range": "stddev: 0.000023578533458126235",
            "extra": "mean: 3.275821430000292 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.0816206154517978,
            "unit": "iter/sec",
            "range": "stddev: 0.000014025501066784971",
            "extra": "mean: 1.6646634500003188 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.8718038468110872,
            "unit": "iter/sec",
            "range": "stddev: 0.000015073559272491031",
            "extra": "mean: 2.065297500000156 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.8842011145103148,
            "unit": "iter/sec",
            "range": "stddev: 0.000022575706389168963",
            "extra": "mean: 2.0363402350002957 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.005461631776321376,
            "unit": "iter/sec",
            "range": "stddev: 0.005890156356519794",
            "extra": "mean: 329.6696626666744 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.21616288578276655,
            "unit": "iter/sec",
            "range": "stddev: 0.0017631732346725848",
            "extra": "mean: 8.329525666672074 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.04280654096785257,
            "unit": "iter/sec",
            "range": "stddev: 0.0003969723652255364",
            "extra": "mean: 42.06213033334431 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.043539717436028906,
            "unit": "iter/sec",
            "range": "stddev: 0.0008359090828742907",
            "extra": "mean: 41.35383533333462 msec\nrounds: 3"
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
          "id": "17e151178ed709ec2b005aa54960a4df8bd99c52",
          "message": "Add check arguments (#1928)\n\nAdd `CheckArguments[]`.\n\nCheckArguments is used in Rubi.\n\nThe association option \"OptionsMode\" and possibly the tag used in some\nfailure messages (which change depending on whether an option was\ndefined or how many arguments are given) may be different too.\n\nHowever, this is good enough for Rubi (the infinite recursion seen\nbefore is now gone).",
          "timestamp": "2026-09-02T15:20:15-03:00",
          "tree_id": "d7eb27d2d2105f94530c0a45df527a580c446cb6",
          "url": "https://github.com/Mathics3/mathics-core/commit/17e151178ed709ec2b005aa54960a4df8bd99c52"
        },
        "date": 1788373338574,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000022883280856494326",
            "extra": "mean: 2.3683618232056443 msec\nrounds: 181"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 17727.745695797053,
            "unit": "iter/sec",
            "range": "stddev: 6.8898168676314726e-9",
            "extra": "mean: 133.5963333322828 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 27.7411627581775,
            "unit": "iter/sec",
            "range": "stddev: 0.000007242106490900607",
            "extra": "mean: 85.37356000002204 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.5964847515098642,
            "unit": "iter/sec",
            "range": "stddev: 0.000029887494730392372",
            "extra": "mean: 3.9705320499990644 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 13.015664427707662,
            "unit": "iter/sec",
            "range": "stddev: 0.0009340549119488548",
            "extra": "mean: 181.96242200005486 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 13.503053806440724,
            "unit": "iter/sec",
            "range": "stddev: 0.000008061720361362213",
            "extra": "mean: 175.39453349996847 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 13.571915238825241,
            "unit": "iter/sec",
            "range": "stddev: 0.00000802422532684952",
            "extra": "mean: 174.5046134999768 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.3599256138806903,
            "unit": "iter/sec",
            "range": "stddev: 0.000009492380004932938",
            "extra": "mean: 704.8851954999691 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 19.297821847970155,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018742324642780852",
            "extra": "mean: 122.72689849993412 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 19.361510094644725,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014254295218044024",
            "extra": "mean: 122.32319750000897 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 7.229650879419175,
            "unit": "iter/sec",
            "range": "stddev: 0.0000054463095234615396",
            "extra": "mean: 327.5900680000632 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 7.234753567126722,
            "unit": "iter/sec",
            "range": "stddev: 0.000005675957979936261",
            "extra": "mean: 327.3590179998678 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 7.131151368196172,
            "unit": "iter/sec",
            "range": "stddev: 0.000003175957098714394",
            "extra": "mean: 332.11492800000997 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 6.5566668770274354,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026190789589517196",
            "extra": "mean: 361.2142980000499 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 10.299741231601297,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031950017051979334",
            "extra": "mean: 229.94381799992425 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 8.708840562182464,
            "unit": "iter/sec",
            "range": "stddev: 0.0000037701101031393187",
            "extra": "mean: 271.9491539999126 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.00948593599996607,
            "unit": "iter/sec",
            "range": "stddev: 0.0028139907002616123",
            "extra": "mean: 249.67086255000197 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.009476534469142456,
            "unit": "iter/sec",
            "range": "stddev: 0.001178003254721866",
            "extra": "mean: 249.91855735000144 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.009458243285914417,
            "unit": "iter/sec",
            "range": "stddev: 0.0015904425320449082",
            "extra": "mean: 250.4018718499978 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 15.743952455248902,
            "unit": "iter/sec",
            "range": "stddev: 0.000003152994264884169",
            "extra": "mean: 150.4299399999809 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 15.767102108879362,
            "unit": "iter/sec",
            "range": "stddev: 0.000003059265903806606",
            "extra": "mean: 150.20907500002068 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5376482906947512,
            "unit": "iter/sec",
            "range": "stddev: 0.0003137440325400951",
            "extra": "mean: 4.4050392499997315 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.15046215131870916,
            "unit": "iter/sec",
            "range": "stddev: 0.0005396762438745927",
            "extra": "mean: 15.740581950001342 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.05432890291213368,
            "unit": "iter/sec",
            "range": "stddev: 0.0013452284538202105",
            "extra": "mean: 43.59303605000093 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.27590057985377026,
            "unit": "iter/sec",
            "range": "stddev: 0.0004010229094441241",
            "extra": "mean: 8.584113250000769 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 12.561854622811461,
            "unit": "iter/sec",
            "range": "stddev: 0.000018099733840253125",
            "extra": "mean: 188.53600000312554 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 11.664936598690014,
            "unit": "iter/sec",
            "range": "stddev: 0.000017015897831631353",
            "extra": "mean: 203.03254999873843 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.388308402474992,
            "unit": "iter/sec",
            "range": "stddev: 0.000012391469459594895",
            "extra": "mean: 698.9805950000516 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.1470473006701876,
            "unit": "iter/sec",
            "range": "stddev: 0.00001230299094034452",
            "extra": "mean: 1.103078550000447 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.716671019967799,
            "unit": "iter/sec",
            "range": "stddev: 0.00000936261181506549",
            "extra": "mean: 637.2266499998602 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.6498403804122685,
            "unit": "iter/sec",
            "range": "stddev: 0.000008034551742602181",
            "extra": "mean: 648.8946299997167 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.8789821598111902,
            "unit": "iter/sec",
            "range": "stddev: 0.000014035432794249148",
            "extra": "mean: 1.2604493399999228 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.411255234015389,
            "unit": "iter/sec",
            "range": "stddev: 0.00002382663777825046",
            "extra": "mean: 1.6781952449997561 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.280793625745058,
            "unit": "iter/sec",
            "range": "stddev: 0.000014543201480896875",
            "extra": "mean: 1.038393740000032 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.597793802207442,
            "unit": "iter/sec",
            "range": "stddev: 0.000013973295308701207",
            "extra": "mean: 911.6819899998063 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.711427062507642,
            "unit": "iter/sec",
            "range": "stddev: 0.0001572980854979743",
            "extra": "mean: 1.383852035000217 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.4198875265395319,
            "unit": "iter/sec",
            "range": "stddev: 0.000010396149370526246",
            "extra": "mean: 1.6679925550002395 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.2693057098994136,
            "unit": "iter/sec",
            "range": "stddev: 0.00001142289733919282",
            "extra": "mean: 1.043650405000136 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.5889423806474814,
            "unit": "iter/sec",
            "range": "stddev: 0.00001565148675586432",
            "extra": "mean: 914.7989699999926 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.8895130091882428,
            "unit": "iter/sec",
            "range": "stddev: 0.00000963571670703185",
            "extra": "mean: 1.253424460000474 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.427240281158012,
            "unit": "iter/sec",
            "range": "stddev: 0.000013861025597030133",
            "extra": "mean: 1.6593995099998438 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.2831812950077057,
            "unit": "iter/sec",
            "range": "stddev: 0.0000154184061586661",
            "extra": "mean: 1.0373078250002268 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.593083623191921,
            "unit": "iter/sec",
            "range": "stddev: 0.000010108628080744022",
            "extra": "mean: 913.3380050005258 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 8.563640631417506,
            "unit": "iter/sec",
            "range": "stddev: 0.000005938939696220137",
            "extra": "mean: 276.56015999980355 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.3779569747171556,
            "unit": "iter/sec",
            "range": "stddev: 0.000029770120577496177",
            "extra": "mean: 995.9649599998953 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05578275379040176,
            "unit": "iter/sec",
            "range": "stddev: 0.0020663130387868532",
            "extra": "mean: 42.45688250000228 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.04185501806229571,
            "unit": "iter/sec",
            "range": "stddev: 0.0002647604022460506",
            "extra": "mean: 56.5848955000007 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.024990275996508157,
            "unit": "iter/sec",
            "range": "stddev: 0.023492613364256253",
            "extra": "mean: 94.77133520000223 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.041358425824651886,
            "unit": "iter/sec",
            "range": "stddev: 0.00011668444538613079",
            "extra": "mean: 57.26431255499989 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.169327192216664,
            "unit": "iter/sec",
            "range": "stddev: 0.0000289617121058754",
            "extra": "mean: 1.0917494749999435 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.243039250121177,
            "unit": "iter/sec",
            "range": "stddev: 0.000008823314439569809",
            "extra": "mean: 1.0558717700003226 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.01206942439932001,
            "unit": "iter/sec",
            "range": "stddev: 0.00407509739218103",
            "extra": "mean: 196.22823299999936 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.023846212739387487,
            "unit": "iter/sec",
            "range": "stddev: 0.00016235772736287462",
            "extra": "mean: 99.31815374999786 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.2978152083160404,
            "unit": "iter/sec",
            "range": "stddev: 0.000012241364794147633",
            "extra": "mean: 1.030701605000388 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.2840634591465547,
            "unit": "iter/sec",
            "range": "stddev: 0.000014748700791905536",
            "extra": "mean: 1.0369071900001359 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 7.450247384670591,
            "unit": "iter/sec",
            "range": "stddev: 0.000009997966710629057",
            "extra": "mean: 317.8903600004901 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.015542028964546,
            "unit": "iter/sec",
            "range": "stddev: 0.00000712494228929592",
            "extra": "mean: 785.3851149999969 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 17.13570660286047,
            "unit": "iter/sec",
            "range": "stddev: 0.000002217920531201009",
            "extra": "mean: 138.21208999985402 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 17.108288697919654,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017397961981270764",
            "extra": "mean: 138.43358999977795 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 9.806683659971418,
            "unit": "iter/sec",
            "range": "stddev: 0.000004376873985056592",
            "extra": "mean: 241.50486599998544 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 6.087722115295293,
            "unit": "iter/sec",
            "range": "stddev: 0.000004523630043616691",
            "extra": "mean: 389.0390820000107 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 5.81929694198228,
            "unit": "iter/sec",
            "range": "stddev: 0.000012498026824930231",
            "extra": "mean: 406.9841849999989 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 5.277503815451109,
            "unit": "iter/sec",
            "range": "stddev: 0.00000902650369874546",
            "extra": "mean: 448.76553500003524 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.3281073664691146,
            "unit": "iter/sec",
            "range": "stddev: 0.000046716872036265455",
            "extra": "mean: 7.21825251499979 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.2177650219718115,
            "unit": "iter/sec",
            "range": "stddev: 0.000012375084686994917",
            "extra": "mean: 736.0269650001783 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.37546133213822547,
            "unit": "iter/sec",
            "range": "stddev: 0.00013716253675699988",
            "extra": "mean: 6.307871465000119 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 0.9966033528760215,
            "unit": "iter/sec",
            "range": "stddev: 0.000013969093263052007",
            "extra": "mean: 2.376433729999974 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.7962568544007764,
            "unit": "iter/sec",
            "range": "stddev: 0.000012497763136943125",
            "extra": "mean: 2.974369149999916 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.8087758730064519,
            "unit": "iter/sec",
            "range": "stddev: 0.000012321511270037064",
            "extra": "mean: 2.928328974999914 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.004582345859375338,
            "unit": "iter/sec",
            "range": "stddev: 0.004620305469396021",
            "extra": "mean: 516.8448423333322 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.19332645301573262,
            "unit": "iter/sec",
            "range": "stddev: 0.0017773102624218102",
            "extra": "mean: 12.250583333326404 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.034971023322311015,
            "unit": "iter/sec",
            "range": "stddev: 0.0004582738128638147",
            "extra": "mean: 67.72354933333229 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03707525126512528,
            "unit": "iter/sec",
            "range": "stddev: 0.0003945701010878421",
            "extra": "mean: 63.879858999996486 msec\nrounds: 3"
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
          "id": "d0e22ae3101075a46ab72b2b256f5180fc87b8d7",
          "message": "Sphere3DBox to SphereBox (#1931)\n\nThis is for compatibility with WMA",
          "timestamp": "2026-09-02T20:27:23-04:00",
          "tree_id": "12017488880cadb5ba93e349f36e003957dee7c4",
          "url": "https://github.com/Mathics3/mathics-core/commit/d0e22ae3101075a46ab72b2b256f5180fc87b8d7"
        },
        "date": 1788395363595,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.00002313216300517574",
            "extra": "mean: 1.668827765216648 msec\nrounds: 230"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 19104.5585346403,
            "unit": "iter/sec",
            "range": "stddev: 2.6121411360789556e-9",
            "extra": "mean: 87.35233332875698 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 11.608351001262474,
            "unit": "iter/sec",
            "range": "stddev: 0.0008381621100639752",
            "extra": "mean: 143.7609669999773 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.6044001012182016,
            "unit": "iter/sec",
            "range": "stddev: 0.00003758725356398049",
            "extra": "mean: 2.7611308499999154 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 27.01994689486155,
            "unit": "iter/sec",
            "range": "stddev: 0.000006029814103225436",
            "extra": "mean: 61.7628069999654 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 13.55435035094177,
            "unit": "iter/sec",
            "range": "stddev: 0.00000684648130574897",
            "extra": "mean: 123.12119150001877 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 13.458477119181183,
            "unit": "iter/sec",
            "range": "stddev: 0.000007586248045111173",
            "extra": "mean: 123.99826150004856 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.309894554443182,
            "unit": "iter/sec",
            "range": "stddev: 0.00001018002200090787",
            "extra": "mean: 504.19363450005505 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 18.805369932505997,
            "unit": "iter/sec",
            "range": "stddev: 0.000002565340899253508",
            "extra": "mean: 88.74208650009052 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 18.098625731308644,
            "unit": "iter/sec",
            "range": "stddev: 0.000012429027164921058",
            "extra": "mean: 92.20743000004461 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 6.8895320199584384,
            "unit": "iter/sec",
            "range": "stddev: 0.00001879740875666647",
            "extra": "mean: 242.22657800009983 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 6.961405676379959,
            "unit": "iter/sec",
            "range": "stddev: 0.000018828644361515876",
            "extra": "mean: 239.72568799990768 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 6.845956606531374,
            "unit": "iter/sec",
            "range": "stddev: 0.000006537142912713908",
            "extra": "mean: 243.76838200004158 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 6.474069379134836,
            "unit": "iter/sec",
            "range": "stddev: 0.000004187961581748448",
            "extra": "mean: 257.77106599986155 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 9.934064134568311,
            "unit": "iter/sec",
            "range": "stddev: 0.000002994033068476882",
            "extra": "mean: 167.99043599985455 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 8.330677700525994,
            "unit": "iter/sec",
            "range": "stddev: 0.000015800913508686486",
            "extra": "mean: 200.32316999987643 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.009183711216731,
            "unit": "iter/sec",
            "range": "stddev: 0.00255707825495402",
            "extra": "mean: 181.71605420000105 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.009214811510705223,
            "unit": "iter/sec",
            "range": "stddev: 0.0005885460245299724",
            "extra": "mean: 181.10275650000034 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.009171831513973385,
            "unit": "iter/sec",
            "range": "stddev: 0.0003637537169553157",
            "extra": "mean: 181.95141969999895 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 15.42458177149758,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034115170246042163",
            "extra": "mean: 108.1927400002769 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 15.476638692994479,
            "unit": "iter/sec",
            "range": "stddev: 0.000002362218064171132",
            "extra": "mean: 107.82882500009805 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5254389931389106,
            "unit": "iter/sec",
            "range": "stddev: 0.00023297265618865413",
            "extra": "mean: 3.17606379999944 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.15153894809817822,
            "unit": "iter/sec",
            "range": "stddev: 0.0003621870706669596",
            "extra": "mean: 11.012533649999057 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.054736342567312975,
            "unit": "iter/sec",
            "range": "stddev: 0.0008638731947969318",
            "extra": "mean: 30.488477799998748 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.27587671439019595,
            "unit": "iter/sec",
            "range": "stddev: 0.000281335010946807",
            "extra": "mean: 6.0491795000004345 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 12.673093212358307,
            "unit": "iter/sec",
            "range": "stddev: 0.000015516117850192294",
            "extra": "mean: 131.6827500005502 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 11.317462600549039,
            "unit": "iter/sec",
            "range": "stddev: 0.0000151478587096411",
            "extra": "mean: 147.4559999991243 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.299063644757175,
            "unit": "iter/sec",
            "range": "stddev: 0.000013757709006620772",
            "extra": "mean: 505.8489150000867 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.0556148570775434,
            "unit": "iter/sec",
            "range": "stddev: 0.000012328135608608528",
            "extra": "mean: 811.8387349998102 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.6030607699612127,
            "unit": "iter/sec",
            "range": "stddev: 0.000011404305099756155",
            "extra": "mean: 463.16947500017136 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.4978919676755527,
            "unit": "iter/sec",
            "range": "stddev: 0.000008578256308535776",
            "extra": "mean: 477.09528499979115 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.7874408856227806,
            "unit": "iter/sec",
            "range": "stddev: 0.000010099062250717682",
            "extra": "mean: 933.6408149997055 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.3437581711771507,
            "unit": "iter/sec",
            "range": "stddev: 0.00000995140665871104",
            "extra": "mean: 1.2419107849999023 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.131798681683065,
            "unit": "iter/sec",
            "range": "stddev: 0.000013144247513748475",
            "extra": "mean: 782.8261550002935 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.4343729687576863,
            "unit": "iter/sec",
            "range": "stddev: 0.000010009649361962141",
            "extra": "mean: 685.5267400000287 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.781473696197817,
            "unit": "iter/sec",
            "range": "stddev: 0.000010504556584369535",
            "extra": "mean: 936.7681199999822 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.3450765166717464,
            "unit": "iter/sec",
            "range": "stddev: 0.000005513345714502718",
            "extra": "mean: 1.2406935550001208 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.1499948357006047,
            "unit": "iter/sec",
            "range": "stddev: 0.00000920152323433549",
            "extra": "mean: 776.2008250000463 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.44164933421475,
            "unit": "iter/sec",
            "range": "stddev: 0.000012457232431920947",
            "extra": "mean: 683.4838000000332 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.78329396294061,
            "unit": "iter/sec",
            "range": "stddev: 0.000010739750396235292",
            "extra": "mean: 935.8119299999146 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.340710109029545,
            "unit": "iter/sec",
            "range": "stddev: 0.000013366054486357363",
            "extra": "mean: 1.2447342300004038 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.144126710764849,
            "unit": "iter/sec",
            "range": "stddev: 0.000012891895189701613",
            "extra": "mean: 778.3251600001506 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.4389382482546336,
            "unit": "iter/sec",
            "range": "stddev: 0.000007694630834167853",
            "extra": "mean: 684.2435500000477 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 8.650524172546499,
            "unit": "iter/sec",
            "range": "stddev: 0.000004061115323668489",
            "extra": "mean: 192.91637499989633 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.473638618832893,
            "unit": "iter/sec",
            "range": "stddev: 0.000022727395385343",
            "extra": "mean: 674.6449350002592 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05539469947026297,
            "unit": "iter/sec",
            "range": "stddev: 0.0014992060861604237",
            "extra": "mean: 30.126127249999968 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.040433871806160565,
            "unit": "iter/sec",
            "range": "stddev: 0.00047696446661996865",
            "extra": "mean: 41.27301420000009 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.023201579648383455,
            "unit": "iter/sec",
            "range": "stddev: 0.022869366443632407",
            "extra": "mean: 71.92733385000025 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.04012980883151882,
            "unit": "iter/sec",
            "range": "stddev: 0.0001400384768768266",
            "extra": "mean: 41.58573922500011 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.2108176778970954,
            "unit": "iter/sec",
            "range": "stddev: 0.00001571133712816656",
            "extra": "mean: 754.8463999998489 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.3224452642963502,
            "unit": "iter/sec",
            "range": "stddev: 0.000004702156548991422",
            "extra": "mean: 718.5649499999158 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.01132638012003489,
            "unit": "iter/sec",
            "range": "stddev: 0.0033559606033096616",
            "extra": "mean: 147.33990450000078 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.023044313073774192,
            "unit": "iter/sec",
            "range": "stddev: 0.0006039526297280853",
            "extra": "mean: 72.41820400000876 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.3779991221819623,
            "unit": "iter/sec",
            "range": "stddev: 0.000013701239251130758",
            "extra": "mean: 701.778125000061 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.3603184306484613,
            "unit": "iter/sec",
            "range": "stddev: 0.000017584545209794995",
            "extra": "mean: 707.03500999997 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 7.674700948218973,
            "unit": "iter/sec",
            "range": "stddev: 0.000008604464617215494",
            "extra": "mean: 217.44531500004882 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.023518270996305,
            "unit": "iter/sec",
            "range": "stddev: 0.000007270618438888864",
            "extra": "mean: 551.9489599997485 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 17.628662803676228,
            "unit": "iter/sec",
            "range": "stddev: 0.000001955317109186358",
            "extra": "mean: 94.6655899997495 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 17.65037207594793,
            "unit": "iter/sec",
            "range": "stddev: 0.000001738860868480974",
            "extra": "mean: 94.54915500000993 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 9.625493690362857,
            "unit": "iter/sec",
            "range": "stddev: 0.000004473139979443944",
            "extra": "mean: 173.37581000001023 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 5.983095895715697,
            "unit": "iter/sec",
            "range": "stddev: 0.0000047030749517976655",
            "extra": "mean: 278.9237869999113 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 5.830084019402118,
            "unit": "iter/sec",
            "range": "stddev: 0.000010808375983379054",
            "extra": "mean: 286.24420499994585 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 5.148266768381954,
            "unit": "iter/sec",
            "range": "stddev: 0.0000074130762626862185",
            "extra": "mean: 324.1533199999935 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.32405119146859324,
            "unit": "iter/sec",
            "range": "stddev: 0.00003935593760534211",
            "extra": "mean: 5.149889305000102 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.1367623981992505,
            "unit": "iter/sec",
            "range": "stddev: 0.00001074305102762121",
            "extra": "mean: 532.022369999936 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.3850876577694765,
            "unit": "iter/sec",
            "range": "stddev: 0.000014966411251400796",
            "extra": "mean: 4.33363087999993 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 0.984411213066992,
            "unit": "iter/sec",
            "range": "stddev: 0.000009148385088786094",
            "extra": "mean: 1.6952547299997889 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.7839624071929586,
            "unit": "iter/sec",
            "range": "stddev: 0.00001223051123456599",
            "extra": "mean: 2.128708915000175 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.7978941630397255,
            "unit": "iter/sec",
            "range": "stddev: 0.000008743158021030947",
            "extra": "mean: 2.091540260000073 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.004320603498153804,
            "unit": "iter/sec",
            "range": "stddev: 0.004317702836393203",
            "extra": "mean: 386.2487650000143 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.1773448957815174,
            "unit": "iter/sec",
            "range": "stddev: 0.0016901876676589675",
            "extra": "mean: 9.41006933333218 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.036080790334676885,
            "unit": "iter/sec",
            "range": "stddev: 0.00020482251803635945",
            "extra": "mean: 46.25252799999657 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03771912241160757,
            "unit": "iter/sec",
            "range": "stddev: 0.0006647069230016897",
            "extra": "mean: 44.243546999998294 msec\nrounds: 3"
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
          "id": "9cebf79b7188b3b350bd30a0cc650aa728ef6ae9",
          "message": "add TagUnset buitlin (#1930)\n\nLooking over the MakeBoxes stuff, I realize that this basic built-in symbol is still missing. `TagUnset` allows surgically removing rules from `UpValues`.",
          "timestamp": "2026-09-03T17:11:29-04:00",
          "tree_id": "cd36347d7db2a1cb9555924587adcd083f918f64",
          "url": "https://github.com/Mathics3/mathics-core/commit/9cebf79b7188b3b350bd30a0cc650aa728ef6ae9"
        },
        "date": 1788470021360,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.00009523506756894628",
            "extra": "mean: 2.2231810418852773 msec\nrounds: 191"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 18238.941373327438,
            "unit": "iter/sec",
            "range": "stddev: 7.542236871013019e-9",
            "extra": "mean: 121.8920000004194 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 27.955893190254056,
            "unit": "iter/sec",
            "range": "stddev: 0.000006945785060146094",
            "extra": "mean: 79.52459350003238 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.6027178468685241,
            "unit": "iter/sec",
            "range": "stddev: 0.00005290768070305923",
            "extra": "mean: 3.688593349999536 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 13.23479113412191,
            "unit": "iter/sec",
            "range": "stddev: 0.0008737405319185505",
            "extra": "mean: 167.980062500078 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 13.073667580595345,
            "unit": "iter/sec",
            "range": "stddev: 0.000018239826403599306",
            "extra": "mean: 170.0502959999568 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 13.839574377450035,
            "unit": "iter/sec",
            "range": "stddev: 0.000007740537482711977",
            "extra": "mean: 160.63940849999625 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.2744506472648425,
            "unit": "iter/sec",
            "range": "stddev: 0.00003083047303645869",
            "extra": "mean: 678.9477935000506 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 18.311365850889462,
            "unit": "iter/sec",
            "range": "stddev: 0.000004293035138083432",
            "extra": "mean: 121.40989699997107 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 18.209397115073347,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031426365126752285",
            "extra": "mean: 122.0897665000109 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 6.907326843785445,
            "unit": "iter/sec",
            "range": "stddev: 0.000009171195780217238",
            "extra": "mean: 321.8583819999026 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 6.813828937872553,
            "unit": "iter/sec",
            "range": "stddev: 0.00000453647805248073",
            "extra": "mean: 326.27485399999046 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 6.895325070190858,
            "unit": "iter/sec",
            "range": "stddev: 0.000009466495018165353",
            "extra": "mean: 322.41859800001293 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 6.353214843243008,
            "unit": "iter/sec",
            "range": "stddev: 0.000011716054818292293",
            "extra": "mean: 349.93008999998665 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 9.712141254660843,
            "unit": "iter/sec",
            "range": "stddev: 0.000003867035631844922",
            "extra": "mean: 228.9074039999548 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 8.177337153555913,
            "unit": "iter/sec",
            "range": "stddev: 0.000007054525516250631",
            "extra": "mean: 271.87102600001367 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.009254535267547583,
            "unit": "iter/sec",
            "range": "stddev: 0.004356676095517175",
            "extra": "mean: 240.22611375000054 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.009263800874560862,
            "unit": "iter/sec",
            "range": "stddev: 0.005437884179843879",
            "extra": "mean: 239.98584080000143 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.00916489352669708,
            "unit": "iter/sec",
            "range": "stddev: 0.005284577825880281",
            "extra": "mean: 242.57576319999927 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 16.084897626005453,
            "unit": "iter/sec",
            "range": "stddev: 0.000004570276672737323",
            "extra": "mean: 138.2154300000593 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 16.063577409041514,
            "unit": "iter/sec",
            "range": "stddev: 0.0000036430558460813364",
            "extra": "mean: 138.39887499990766 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5195561113021487,
            "unit": "iter/sec",
            "range": "stddev: 0.0003582407035814815",
            "extra": "mean: 4.279000850001324 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.14471975692635689,
            "unit": "iter/sec",
            "range": "stddev: 0.000872862487842758",
            "extra": "mean: 15.361973300000642 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.05396813888026914,
            "unit": "iter/sec",
            "range": "stddev: 0.0012800247511347094",
            "extra": "mean: 41.19432479999929 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.27016478793704807,
            "unit": "iter/sec",
            "range": "stddev: 0.0005034948368483116",
            "extra": "mean: 8.228981499999577 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 9.307336212342333,
            "unit": "iter/sec",
            "range": "stddev: 0.000030074306963328058",
            "extra": "mean: 238.8632999995366 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 10.841110169400922,
            "unit": "iter/sec",
            "range": "stddev: 0.000017598782977506974",
            "extra": "mean: 205.06950000012125 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.2528099097625476,
            "unit": "iter/sec",
            "range": "stddev: 0.00002038569858988098",
            "extra": "mean: 683.4647899998458 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.159605306699679,
            "unit": "iter/sec",
            "range": "stddev: 0.000019439529519949388",
            "extra": "mean: 1.029438589999927 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.8006822650140855,
            "unit": "iter/sec",
            "range": "stddev: 0.000012133059752391681",
            "extra": "mean: 584.9426200001062 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.6929311863615943,
            "unit": "iter/sec",
            "range": "stddev: 0.000011207591649287866",
            "extra": "mean: 602.0098750000358 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.8489384771165258,
            "unit": "iter/sec",
            "range": "stddev: 0.000020567842379690543",
            "extra": "mean: 1.2024094199999527 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.1926133697439651,
            "unit": "iter/sec",
            "range": "stddev: 0.00043200588428305293",
            "extra": "mean: 1.8641255400000745 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.241984521225128,
            "unit": "iter/sec",
            "range": "stddev: 0.00004034105174058469",
            "extra": "mean: 991.6130199999883 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.519179892853901,
            "unit": "iter/sec",
            "range": "stddev: 0.000022025414254041928",
            "extra": "mean: 882.5018999999656 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.7852061302400344,
            "unit": "iter/sec",
            "range": "stddev: 0.000026502732313133715",
            "extra": "mean: 1.245335765000064 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.3763054076746721,
            "unit": "iter/sec",
            "range": "stddev: 0.00004833639424199963",
            "extra": "mean: 1.6153253700001358 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.2948089716885884,
            "unit": "iter/sec",
            "range": "stddev: 0.000012813631576675628",
            "extra": "mean: 968.7869750000999 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.5681679623026072,
            "unit": "iter/sec",
            "range": "stddev: 0.000025218172471477965",
            "extra": "mean: 865.6680850001663 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.8570236792711088,
            "unit": "iter/sec",
            "range": "stddev: 0.00002942215436321867",
            "extra": "mean: 1.197174310000122 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.4228632358655404,
            "unit": "iter/sec",
            "range": "stddev: 0.000033401698015001675",
            "extra": "mean: 1.5624699449999468 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.2290683792711516,
            "unit": "iter/sec",
            "range": "stddev: 0.00003305215810611523",
            "extra": "mean: 997.3588350000284 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.48859609961398,
            "unit": "iter/sec",
            "range": "stddev: 0.000024990696135664436",
            "extra": "mean: 893.3474750001125 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 8.631681740923344,
            "unit": "iter/sec",
            "range": "stddev: 0.000003983703115607035",
            "extra": "mean: 257.56059000009657 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.3017571976586866,
            "unit": "iter/sec",
            "range": "stddev: 0.00003332585640594969",
            "extra": "mean: 965.8625350000705 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05546925081905916,
            "unit": "iter/sec",
            "range": "stddev: 0.001763251462839564",
            "extra": "mean: 40.07952170000095 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.04142859124324063,
            "unit": "iter/sec",
            "range": "stddev: 0.0012000447177877521",
            "extra": "mean: 53.66296499999876 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.024758591257211342,
            "unit": "iter/sec",
            "range": "stddev: 0.02482006585741102",
            "extra": "mean: 89.79432710000168 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.04077438887231757,
            "unit": "iter/sec",
            "range": "stddev: 0.0008316800804370559",
            "extra": "mean: 54.5239574 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.173865660278691,
            "unit": "iter/sec",
            "range": "stddev: 0.000020362453351613346",
            "extra": "mean: 1.0226855699998794 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.1824911140522882,
            "unit": "iter/sec",
            "range": "stddev: 0.000025883903626270302",
            "extra": "mean: 1.0186438000003761 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.011997772356927202,
            "unit": "iter/sec",
            "range": "stddev: 0.00675266010317048",
            "extra": "mean: 185.29948524999895 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.024009147462596327,
            "unit": "iter/sec",
            "range": "stddev: 0.0010947519110258539",
            "extra": "mean: 92.5972504999919 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.29260705250996,
            "unit": "iter/sec",
            "range": "stddev: 0.000026408801108490965",
            "extra": "mean: 969.7174399997266 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.2791152828826644,
            "unit": "iter/sec",
            "range": "stddev: 0.000019341878917554873",
            "extra": "mean: 975.4579149999643 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 7.619630119138559,
            "unit": "iter/sec",
            "range": "stddev: 0.000008379624720524793",
            "extra": "mean: 291.7702050000059 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.0366390962865277,
            "unit": "iter/sec",
            "range": "stddev: 0.00000667917003131563",
            "extra": "mean: 732.1189549999474 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 17.47157704434977,
            "unit": "iter/sec",
            "range": "stddev: 0.000002831991627494128",
            "extra": "mean: 127.24558500025294 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 17.401961994692904,
            "unit": "iter/sec",
            "range": "stddev: 0.000003681966913646248",
            "extra": "mean: 127.75461999993355 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 9.696396282073206,
            "unit": "iter/sec",
            "range": "stddev: 0.000008390948382878722",
            "extra": "mean: 229.27910299989662 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 6.0704183375661085,
            "unit": "iter/sec",
            "range": "stddev: 0.000012622500527830341",
            "extra": "mean: 366.23193299996615 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 5.709733596451752,
            "unit": "iter/sec",
            "range": "stddev: 0.000011823900989079778",
            "extra": "mean: 389.3668599997113 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 5.1099828887767025,
            "unit": "iter/sec",
            "range": "stddev: 0.000012722989700828582",
            "extra": "mean: 435.06624000016814 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.3179456845425071,
            "unit": "iter/sec",
            "range": "stddev: 0.0001770722044766262",
            "extra": "mean: 6.9923296649999145 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.1643721929042052,
            "unit": "iter/sec",
            "range": "stddev: 0.000027660989829469067",
            "extra": "mean: 702.5662299999169 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.37611657674445276,
            "unit": "iter/sec",
            "range": "stddev: 0.00008153704506358711",
            "extra": "mean: 5.910882899999876 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.0075007360423676,
            "unit": "iter/sec",
            "range": "stddev: 0.000028752153183299736",
            "extra": "mean: 2.206629694999833 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.7847361675183003,
            "unit": "iter/sec",
            "range": "stddev: 0.00006232812862288337",
            "extra": "mean: 2.8330299199997455 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.8029958189881687,
            "unit": "iter/sec",
            "range": "stddev: 0.00006752227708788243",
            "extra": "mean: 2.7686084900001617 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.004373651417720222,
            "unit": "iter/sec",
            "range": "stddev: 0.006147816036270452",
            "extra": "mean: 508.31235266666874 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.18238210699820162,
            "unit": "iter/sec",
            "range": "stddev: 0.0016734856260780847",
            "extra": "mean: 12.189688333336335 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03393654143199373,
            "unit": "iter/sec",
            "range": "stddev: 0.0007209173430941902",
            "extra": "mean: 65.50994733332989 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.036735995115002314,
            "unit": "iter/sec",
            "range": "stddev: 0.0014305095221388549",
            "extra": "mean: 60.51778466666254 msec\nrounds: 3"
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
          "id": "ca5b7fa999ffc787b4d0ca2960dae18c1eceebf3",
          "message": "Change `get_int_value()` to a function in `mathics.core.atoms.numerics`. Remove it as an method of `Element` (#1934)\n\nChange `get_int_value()` to a function in `mathics.core.atoms.numerics`.\nRemove it as an method of `Element`.\n\n`get_int_value()` is a highly custom kind of function, not a fundamental\nproperty of an element.\n\nThis is part of a long-desired reorganization of `mathics.core` to make\nit comprehensible and logical, and more in line with modern Python\nconventions.\n\n`.int_value` is now a property on methods only where it makes sense.",
          "timestamp": "2026-09-05T10:09:11-03:00",
          "tree_id": "de0c590b2d34eb981c19966a8ac52f0d0b4ecd1c",
          "url": "https://github.com/Mathics3/mathics-core/commit/ca5b7fa999ffc787b4d0ca2960dae18c1eceebf3"
        },
        "date": 1788613889944,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000019835436835980277",
            "extra": "mean: 2.373509631284149 msec\nrounds: 179"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 18804.49503346809,
            "unit": "iter/sec",
            "range": "stddev: 1.6526972907655962e-9",
            "extra": "mean: 126.22033333305654 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 13.500646349191138,
            "unit": "iter/sec",
            "range": "stddev: 0.000911246730395762",
            "extra": "mean: 175.80711100001167 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.5998332632752751,
            "unit": "iter/sec",
            "range": "stddev: 0.000027820091047141124",
            "extra": "mean: 3.95694900000052 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 27.123447103632106,
            "unit": "iter/sec",
            "range": "stddev: 0.0000069584639961854915",
            "extra": "mean: 87.5076690000185 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 12.879093682316812,
            "unit": "iter/sec",
            "range": "stddev: 0.000019155642403166563",
            "extra": "mean: 184.29166599999292 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 13.727670860775621,
            "unit": "iter/sec",
            "range": "stddev: 0.00000836266726862134",
            "extra": "mean: 172.89966050002192 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.357084257472037,
            "unit": "iter/sec",
            "range": "stddev: 0.000005596336093679862",
            "extra": "mean: 707.0152099999589 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 19.387907190829605,
            "unit": "iter/sec",
            "range": "stddev: 0.0000022971624516432127",
            "extra": "mean: 122.42216799999994 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 19.431435088495867,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020693485121363605",
            "extra": "mean: 122.14793300003636 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 7.236103799007003,
            "unit": "iter/sec",
            "range": "stddev: 0.000003538755618845664",
            "extra": "mean: 328.009340000051 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 7.189464571637169,
            "unit": "iter/sec",
            "range": "stddev: 0.000004942092037772781",
            "extra": "mean: 330.1371899999026 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 7.108440918986065,
            "unit": "iter/sec",
            "range": "stddev: 0.000003937209317154407",
            "extra": "mean: 333.9001699999642 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 6.590923269124742,
            "unit": "iter/sec",
            "range": "stddev: 0.0000036147669008234777",
            "extra": "mean: 360.117927999994 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 10.301883731768829,
            "unit": "iter/sec",
            "range": "stddev: 0.0000032495944979970755",
            "extra": "mean: 230.39569199997345 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 8.596266026390921,
            "unit": "iter/sec",
            "range": "stddev: 0.000010569658702992486",
            "extra": "mean: 276.1093739999865 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.009381570727930447,
            "unit": "iter/sec",
            "range": "stddev: 0.0012874847758616074",
            "extra": "mean: 252.99704070000007 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.009399231909227434,
            "unit": "iter/sec",
            "range": "stddev: 0.0007836529036625513",
            "extra": "mean: 252.5216585999992 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.009352445546588008,
            "unit": "iter/sec",
            "range": "stddev: 0.0022056663320913924",
            "extra": "mean: 253.78491855000007 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 15.713782906464203,
            "unit": "iter/sec",
            "range": "stddev: 0.000004567161336575578",
            "extra": "mean: 151.04635500009067 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 15.725752153247212,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024064811351390003",
            "extra": "mean: 150.93138999993982 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5327709436289221,
            "unit": "iter/sec",
            "range": "stddev: 0.0003118087850203205",
            "extra": "mean: 4.455028299999242 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.15093408655914173,
            "unit": "iter/sec",
            "range": "stddev: 0.0005715561621997543",
            "extra": "mean: 15.725471200000385 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.05438624453892104,
            "unit": "iter/sec",
            "range": "stddev: 0.0012861625251526774",
            "extra": "mean: 43.6417268999989 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.27670297384530845,
            "unit": "iter/sec",
            "range": "stddev: 0.00040499096104275724",
            "extra": "mean: 8.5778248000004 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 12.61416815542265,
            "unit": "iter/sec",
            "range": "stddev: 0.000019687700760535275",
            "extra": "mean: 188.1621999991978 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 11.39121591934327,
            "unit": "iter/sec",
            "range": "stddev: 0.000016003772666224956",
            "extra": "mean: 208.3631499999683 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.397144887404794,
            "unit": "iter/sec",
            "range": "stddev: 0.00001554121709574023",
            "extra": "mean: 698.6777749998652 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.1847538665770445,
            "unit": "iter/sec",
            "range": "stddev: 0.000013596985889325105",
            "extra": "mean: 1.0863968099998544 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.6842738820566003,
            "unit": "iter/sec",
            "range": "stddev: 0.000012940386721831182",
            "extra": "mean: 644.2272500000001 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.657399575851391,
            "unit": "iter/sec",
            "range": "stddev: 0.000014835749366244094",
            "extra": "mean: 648.9609850002864 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.9098840931043417,
            "unit": "iter/sec",
            "range": "stddev: 0.000017006141515396386",
            "extra": "mean: 1.2427506150000056 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.431361270324944,
            "unit": "iter/sec",
            "range": "stddev: 0.000014962395298830443",
            "extra": "mean: 1.6582184249999443 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.3162955446687787,
            "unit": "iter/sec",
            "range": "stddev: 0.000011264515649119462",
            "extra": "mean: 1.0247006849998286 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.6166782473098857,
            "unit": "iter/sec",
            "range": "stddev: 0.00001641943881994898",
            "extra": "mean: 907.0697299999608 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.8957383302630229,
            "unit": "iter/sec",
            "range": "stddev: 0.000012458333931293507",
            "extra": "mean: 1.252023864999785 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.4421224481388817,
            "unit": "iter/sec",
            "range": "stddev: 0.000010652047902440943",
            "extra": "mean: 1.64584473000005 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.3201681306987387,
            "unit": "iter/sec",
            "range": "stddev: 0.000013001829287365406",
            "extra": "mean: 1.0229903600000512 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.6157167208955685,
            "unit": "iter/sec",
            "range": "stddev: 0.000013057730693401844",
            "extra": "mean: 907.4031650000336 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.8971041965195177,
            "unit": "iter/sec",
            "range": "stddev: 0.000016438834711371353",
            "extra": "mean: 1.2511224400002163 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.4293944223523853,
            "unit": "iter/sec",
            "range": "stddev: 0.000014839195781420218",
            "extra": "mean: 1.660500134999836 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.298257710133692,
            "unit": "iter/sec",
            "range": "stddev: 0.00001557927299989368",
            "extra": "mean: 1.0327430299999207 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.601328848168679,
            "unit": "iter/sec",
            "range": "stddev: 0.00001003233341391289",
            "extra": "mean: 912.4219850001225 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 8.668333156364236,
            "unit": "iter/sec",
            "range": "stddev: 0.000004978695627670501",
            "extra": "mean: 273.8138449998928 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.3437940840871745,
            "unit": "iter/sec",
            "range": "stddev: 0.000029059440627439125",
            "extra": "mean: 1.0126783950001084 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05618082877518729,
            "unit": "iter/sec",
            "range": "stddev: 0.0020171167290519098",
            "extra": "mean: 42.247679199998345 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.04197017198583911,
            "unit": "iter/sec",
            "range": "stddev: 0.0004781158343765615",
            "extra": "mean: 56.55229699999751 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.024894693866672844,
            "unit": "iter/sec",
            "range": "stddev: 0.02434236096834899",
            "extra": "mean: 95.34198909999958 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.04122623478108217,
            "unit": "iter/sec",
            "range": "stddev: 0.00020663832105307942",
            "extra": "mean: 57.572796640000234 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.17441538572577,
            "unit": "iter/sec",
            "range": "stddev: 0.00001648642111984591",
            "extra": "mean: 1.0915621949997956 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.2289544880270076,
            "unit": "iter/sec",
            "range": "stddev: 0.000008690329196835981",
            "extra": "mean: 1.064853340000269 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.012114595221187274,
            "unit": "iter/sec",
            "range": "stddev: 0.004991294941445046",
            "extra": "mean: 195.9214970000076 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.02406758482263531,
            "unit": "iter/sec",
            "range": "stddev: 0.000489713872381741",
            "extra": "mean: 98.61852150000061 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.2842592590962894,
            "unit": "iter/sec",
            "range": "stddev: 0.000017090540527864364",
            "extra": "mean: 1.0390719099999046 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.282482494708941,
            "unit": "iter/sec",
            "range": "stddev: 0.000014505117410695172",
            "extra": "mean: 1.0398807599997895 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 7.5198873243881685,
            "unit": "iter/sec",
            "range": "stddev: 0.000009090097503187506",
            "extra": "mean: 315.6310100001746 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.971888411538855,
            "unit": "iter/sec",
            "range": "stddev: 0.000007995525728670015",
            "extra": "mean: 798.6536849999482 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 17.04831744553386,
            "unit": "iter/sec",
            "range": "stddev: 0.0000022620997843710262",
            "extra": "mean: 139.2225149999149 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 17.288288386910125,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016125085597734068",
            "extra": "mean: 137.29002999980366 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 9.814138670376463,
            "unit": "iter/sec",
            "range": "stddev: 0.000004771124115274435",
            "extra": "mean: 241.84594400000492 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 6.086822434965578,
            "unit": "iter/sec",
            "range": "stddev: 0.000005151992622775124",
            "extra": "mean: 389.94231499995635 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 5.880216697016696,
            "unit": "iter/sec",
            "range": "stddev: 0.000012667527921902614",
            "extra": "mean: 403.64322500025196 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 5.3389652337459665,
            "unit": "iter/sec",
            "range": "stddev: 0.0000076825576066406",
            "extra": "mean: 444.5636050000701 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.32798318756906586,
            "unit": "iter/sec",
            "range": "stddev: 0.000039548563242024745",
            "extra": "mean: 7.236680785000117 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.2635318668691835,
            "unit": "iter/sec",
            "range": "stddev: 0.000013609095860837334",
            "extra": "mean: 727.282505000062 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.3809511313127641,
            "unit": "iter/sec",
            "range": "stddev: 0.00003175906220883991",
            "extra": "mean: 6.230483219999883 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.001367958126067,
            "unit": "iter/sec",
            "range": "stddev: 0.000009163651169960047",
            "extra": "mean: 2.370267205000119 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.8018030023095848,
            "unit": "iter/sec",
            "range": "stddev: 0.000016297775923401966",
            "extra": "mean: 2.960215444999932 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.8124077497703228,
            "unit": "iter/sec",
            "range": "stddev: 0.00003480534073598955",
            "extra": "mean: 2.921574335000088 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.004564640236551015,
            "unit": "iter/sec",
            "range": "stddev: 0.005341082427800517",
            "extra": "mean: 519.9773713333306 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.1938153566206164,
            "unit": "iter/sec",
            "range": "stddev: 0.0017845328486522675",
            "extra": "mean: 12.246241333343733 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03520892454353528,
            "unit": "iter/sec",
            "range": "stddev: 0.0006863930205385877",
            "extra": "mean: 67.4121593333344 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.037310805920367895,
            "unit": "iter/sec",
            "range": "stddev: 0.0008315923748798668",
            "extra": "mean: 63.614536666667234 msec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "rb@dustyfeet.com",
            "name": "rocky",
            "username": "rocky"
          },
          "committer": {
            "email": "rb@dustyfeet.com",
            "name": "rocky",
            "username": "rocky"
          },
          "distinct": true,
          "id": "0e94a05c39942b3dda561661f61fe244c96b569b",
          "message": "Note that numpy 1.x is no good.\n\nThis was encountered in switching between Mathics3 7.0 and the current version",
          "timestamp": "2026-09-05T10:53:23-04:00",
          "tree_id": "cbedebf069fa90e831984933e86fcce0ac2c8e8d",
          "url": "https://github.com/Mathics3/mathics-core/commit/0e94a05c39942b3dda561661f61fe244c96b569b"
        },
        "date": 1788620178555,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.00003365187379000278",
            "extra": "mean: 2.411402212902566 msec\nrounds: 155"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 15246.856798767967,
            "unit": "iter/sec",
            "range": "stddev: 4.653969311784345e-9",
            "extra": "mean: 158.15733332639562 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 28.67146128547803,
            "unit": "iter/sec",
            "range": "stddev: 0.000007197297401126613",
            "extra": "mean: 84.1046150000011 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.6024528515064751,
            "unit": "iter/sec",
            "range": "stddev: 0.000041196694305012",
            "extra": "mean: 4.00264054999937 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 12.159362069154787,
            "unit": "iter/sec",
            "range": "stddev: 0.0011072298992552095",
            "extra": "mean: 198.31650699995862 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 13.98480881326801,
            "unit": "iter/sec",
            "range": "stddev: 0.000008058001930502444",
            "extra": "mean: 172.43011650003837 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 13.999264751340666,
            "unit": "iter/sec",
            "range": "stddev: 0.000007863446771636052",
            "extra": "mean: 172.2520614999894 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.491134807257945,
            "unit": "iter/sec",
            "range": "stddev: 0.000008367600788824383",
            "extra": "mean: 690.7215979999819 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 19.82505635306869,
            "unit": "iter/sec",
            "range": "stddev: 0.0000025943945606735693",
            "extra": "mean: 121.63406599998439 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 19.743617990462404,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015321491200242954",
            "extra": "mean: 122.13578149999904 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 7.454749329453365,
            "unit": "iter/sec",
            "range": "stddev: 0.000005464023586257698",
            "extra": "mean: 323.4719380000115 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 7.433493530620667,
            "unit": "iter/sec",
            "range": "stddev: 0.000005732514006963359",
            "extra": "mean: 324.39689400001726 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 7.265970628568234,
            "unit": "iter/sec",
            "range": "stddev: 0.000004530935100804505",
            "extra": "mean: 331.8761299999551 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 6.74515448731654,
            "unit": "iter/sec",
            "range": "stddev: 0.0000033303241376029086",
            "extra": "mean: 357.5014059999546 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 10.434729781824148,
            "unit": "iter/sec",
            "range": "stddev: 0.000004238103561598319",
            "extra": "mean: 231.09388199998193 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 8.749175535558374,
            "unit": "iter/sec",
            "range": "stddev: 0.000017605323544841182",
            "extra": "mean: 275.6147939999778 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.00951984970260541,
            "unit": "iter/sec",
            "range": "stddev: 0.003355130534375946",
            "extra": "mean: 253.3025507999994 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.00954516839872269,
            "unit": "iter/sec",
            "range": "stddev: 0.0013545027037365888",
            "extra": "mean: 252.6306621499998 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.009506842097833436,
            "unit": "iter/sec",
            "range": "stddev: 0.0034091643082010533",
            "extra": "mean: 253.6491285000004 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 15.9800629970912,
            "unit": "iter/sec",
            "range": "stddev: 0.00000562208250681446",
            "extra": "mean: 150.900669999956 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 16.26016765543811,
            "unit": "iter/sec",
            "range": "stddev: 0.0000029066216454349674",
            "extra": "mean: 148.30119000009745 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.5480821246700546,
            "unit": "iter/sec",
            "range": "stddev: 0.0003358343170525008",
            "extra": "mean: 4.399709649998584 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.15008457422947477,
            "unit": "iter/sec",
            "range": "stddev: 0.0005603320349761228",
            "extra": "mean: 16.066955750000034 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.05478338032347243,
            "unit": "iter/sec",
            "range": "stddev: 0.001362213983346303",
            "extra": "mean: 44.01703944999866 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.2782186744280821,
            "unit": "iter/sec",
            "range": "stddev: 0.0004970496817851295",
            "extra": "mean: 8.667291000000432 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 12.645613804744002,
            "unit": "iter/sec",
            "range": "stddev: 0.000019096548037036313",
            "extra": "mean: 190.690799998805 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 11.551228953588309,
            "unit": "iter/sec",
            "range": "stddev: 0.000012211559791051362",
            "extra": "mean: 208.75719999935427 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.4341161566327134,
            "unit": "iter/sec",
            "range": "stddev: 0.000014518299077638581",
            "extra": "mean: 702.1900550000737 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.2119203528356226,
            "unit": "iter/sec",
            "range": "stddev: 0.000029032698287093857",
            "extra": "mean: 1.0901849200000413 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.82836815005252,
            "unit": "iter/sec",
            "range": "stddev: 0.000011744492080979667",
            "extra": "mean: 629.8773049999083 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.7227239116881816,
            "unit": "iter/sec",
            "range": "stddev: 0.000015609595406167362",
            "extra": "mean: 647.7520949999871 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.9144509574031747,
            "unit": "iter/sec",
            "range": "stddev: 0.000016413371517870216",
            "extra": "mean: 1.2595789949999412 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.447958708789269,
            "unit": "iter/sec",
            "range": "stddev: 0.000031216165081617295",
            "extra": "mean: 1.6653805100001053 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.3475906380288167,
            "unit": "iter/sec",
            "range": "stddev: 0.000013537892131979291",
            "extra": "mean: 1.0271817300001373 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.647230925497905,
            "unit": "iter/sec",
            "range": "stddev: 0.000014396024282062645",
            "extra": "mean: 910.9149450001297 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.9119159416647664,
            "unit": "iter/sec",
            "range": "stddev: 0.000014151728795192527",
            "extra": "mean: 1.261249075000066 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.4597978835605312,
            "unit": "iter/sec",
            "range": "stddev: 0.000009235505565302703",
            "extra": "mean: 1.6518740299999735 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.339973560576552,
            "unit": "iter/sec",
            "range": "stddev: 0.000028814572731279627",
            "extra": "mean: 1.0305254100001093 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.6740009225849892,
            "unit": "iter/sec",
            "range": "stddev: 0.000013977382261584623",
            "extra": "mean: 901.7955799998134 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.9315707702702642,
            "unit": "iter/sec",
            "range": "stddev: 0.000010907119131807296",
            "extra": "mean: 1.2484151499999996 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.4641052827238636,
            "unit": "iter/sec",
            "range": "stddev: 0.000017815757470308785",
            "extra": "mean: 1.6470142149998424 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.334131693500601,
            "unit": "iter/sec",
            "range": "stddev: 0.000016443623930212",
            "extra": "mean: 1.0331046099999952 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.6615103267010722,
            "unit": "iter/sec",
            "range": "stddev: 0.000011489046701557973",
            "extra": "mean: 906.0277499999358 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 8.50344169876163,
            "unit": "iter/sec",
            "range": "stddev: 0.000010334493471540187",
            "extra": "mean: 283.5795549999176 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.3581750768367167,
            "unit": "iter/sec",
            "range": "stddev: 0.000033845354500704737",
            "extra": "mean: 1.0225713249998591 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05697506330959679,
            "unit": "iter/sec",
            "range": "stddev: 0.0019877986501871466",
            "extra": "mean: 42.32381804999932 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.042555248590862106,
            "unit": "iter/sec",
            "range": "stddev: 0.0004571704328453494",
            "extra": "mean: 56.665212699999756 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.024746800439422272,
            "unit": "iter/sec",
            "range": "stddev: 0.03073160825902154",
            "extra": "mean: 97.44298940000107 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.04193869501804229,
            "unit": "iter/sec",
            "range": "stddev: 0.0002331594525657476",
            "extra": "mean: 57.498265309999894 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.1721255536985757,
            "unit": "iter/sec",
            "range": "stddev: 0.000037390826711792115",
            "extra": "mean: 1.1101578399998857 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.236055326900331,
            "unit": "iter/sec",
            "range": "stddev: 0.00001289321783476478",
            "extra": "mean: 1.078417954999935 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.012318119663605959,
            "unit": "iter/sec",
            "range": "stddev: 0.004671570953486184",
            "extra": "mean: 195.7605770000015 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.02443415005543972,
            "unit": "iter/sec",
            "range": "stddev: 0.0000620599337526258",
            "extra": "mean: 98.6898340000053 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.2786025988686434,
            "unit": "iter/sec",
            "range": "stddev: 0.00003198123011008668",
            "extra": "mean: 1.0582811649999257 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.249751462263986,
            "unit": "iter/sec",
            "range": "stddev: 0.000029582434507751355",
            "extra": "mean: 1.0718527149998633 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 7.526947464466389,
            "unit": "iter/sec",
            "range": "stddev: 0.000013279156185493644",
            "extra": "mean: 320.3692099999955 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.004845833322546,
            "unit": "iter/sec",
            "range": "stddev: 0.000007494336183259868",
            "extra": "mean: 802.504470000116 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 17.27065348748424,
            "unit": "iter/sec",
            "range": "stddev: 0.000004407459950901787",
            "extra": "mean: 139.62425999977768 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 17.375797374652436,
            "unit": "iter/sec",
            "range": "stddev: 0.000002784729961775458",
            "extra": "mean: 138.77937000003726 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 9.962755519571742,
            "unit": "iter/sec",
            "range": "stddev: 0.000006345899741686776",
            "extra": "mean: 242.04169300003286 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 6.164800596488218,
            "unit": "iter/sec",
            "range": "stddev: 0.000005457531919220755",
            "extra": "mean: 391.15656299998136 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 5.925916146013398,
            "unit": "iter/sec",
            "range": "stddev: 0.000014737908577247035",
            "extra": "mean: 406.92479499981005 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 5.308144711248338,
            "unit": "iter/sec",
            "range": "stddev: 0.000008254010128212245",
            "extra": "mean: 454.2834349999225 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.33294644711433113,
            "unit": "iter/sec",
            "range": "stddev: 0.0000648770283660558",
            "extra": "mean: 7.2426128399997936 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.3076399092588,
            "unit": "iter/sec",
            "range": "stddev: 0.000015233775638536124",
            "extra": "mean: 729.0401250004663 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.383196138054933,
            "unit": "iter/sec",
            "range": "stddev: 0.000040349730510694175",
            "extra": "mean: 6.292866690000096 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.0006359318525662,
            "unit": "iter/sec",
            "range": "stddev: 0.000016390012962969562",
            "extra": "mean: 2.4098696999998026 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.8064275153238938,
            "unit": "iter/sec",
            "range": "stddev: 0.000012037881700718695",
            "extra": "mean: 2.99022809500002 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.814314527577358,
            "unit": "iter/sec",
            "range": "stddev: 0.000011836175474702946",
            "extra": "mean: 2.9612663550000202 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.004584731150484363,
            "unit": "iter/sec",
            "range": "stddev: 0.006263242152312793",
            "extra": "mean: 525.9637116666719 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.1855138262759675,
            "unit": "iter/sec",
            "range": "stddev: 0.002382387529627391",
            "extra": "mean: 12.998503999995137 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03499454290691467,
            "unit": "iter/sec",
            "range": "stddev: 0.00043056112890087455",
            "extra": "mean: 68.90795000000101 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03638403442707904,
            "unit": "iter/sec",
            "range": "stddev: 0.0011204755683938779",
            "extra": "mean: 66.276383333341 msec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "rb@dustyfeet.com",
            "name": "rocky",
            "username": "rocky"
          },
          "committer": {
            "email": "rb@dustyfeet.com",
            "name": "rocky",
            "username": "rocky"
          },
          "distinct": true,
          "id": "1e200a23c8198faa62841c1194418ae3b80f53a2",
          "message": "Note that numpy 1.x is no good.\n\nThis was encountered in switching between Mathics3 7.0 and the current version",
          "timestamp": "2026-09-05T10:57:42-04:00",
          "tree_id": "bc8242917e84ecca3e1e8812f09753bce3f37a38",
          "url": "https://github.com/Mathics3/mathics-core/commit/1e200a23c8198faa62841c1194418ae3b80f53a2"
        },
        "date": 1788620400599,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000038396533999537666",
            "extra": "mean: 1.8134345981752318 msec\nrounds: 219"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 16504.023526719877,
            "unit": "iter/sec",
            "range": "stddev: 5.707518909426802e-9",
            "extra": "mean: 109.87833331910224 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 39.33947215046928,
            "unit": "iter/sec",
            "range": "stddev: 0.000008688250491127038",
            "extra": "mean: 46.09707499986371 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.5928199504501338,
            "unit": "iter/sec",
            "range": "stddev: 0.00014966802876223325",
            "extra": "mean: 3.058997250005291 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 10.6192206133648,
            "unit": "iter/sec",
            "range": "stddev: 0.0012350031754651681",
            "extra": "mean: 170.76908599986496 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 18.499815007141866,
            "unit": "iter/sec",
            "range": "stddev: 0.000010840935206963855",
            "extra": "mean: 98.02447200013376 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 19.21099426509515,
            "unit": "iter/sec",
            "range": "stddev: 0.000007422227246167466",
            "extra": "mean: 94.39566599996851 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 4.201392203176063,
            "unit": "iter/sec",
            "range": "stddev: 0.000005959575138213068",
            "extra": "mean: 431.62706800006845 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 26.86048820884704,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018167454461854784",
            "extra": "mean: 67.51309149987605 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 26.925004560733182,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021538493186596155",
            "extra": "mean: 67.35132000014232 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 9.27022342231986,
            "unit": "iter/sec",
            "range": "stddev: 0.000005290511047102029",
            "extra": "mean: 195.61929799976951 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 9.275709301897333,
            "unit": "iter/sec",
            "range": "stddev: 0.000004521905776237566",
            "extra": "mean: 195.50360399978217 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 8.974547493912839,
            "unit": "iter/sec",
            "range": "stddev: 0.0000036812995775549636",
            "extra": "mean: 202.06418199973086 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 8.473851373812172,
            "unit": "iter/sec",
            "range": "stddev: 0.000004490730703821327",
            "extra": "mean: 214.00358800008235 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 13.97603568068428,
            "unit": "iter/sec",
            "range": "stddev: 0.000003426593881907726",
            "extra": "mean: 129.75314599987087 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 11.049181055095897,
            "unit": "iter/sec",
            "range": "stddev: 0.00002120340385796051",
            "extra": "mean: 164.12389200002053 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.011594758403437986,
            "unit": "iter/sec",
            "range": "stddev: 0.000657545635193205",
            "extra": "mean: 156.40124054999944 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.011439112234687026,
            "unit": "iter/sec",
            "range": "stddev: 0.0020130707183721873",
            "extra": "mean: 158.52931249999642 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.0114910169513426,
            "unit": "iter/sec",
            "range": "stddev: 0.0009042401221521998",
            "extra": "mean: 157.81323845000088 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 21.019809908017965,
            "unit": "iter/sec",
            "range": "stddev: 0.000004095858210451126",
            "extra": "mean: 86.27264500063347 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 21.502590194215802,
            "unit": "iter/sec",
            "range": "stddev: 0.000003468472391081571",
            "extra": "mean: 84.33563500005903 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.612999360468054,
            "unit": "iter/sec",
            "range": "stddev: 0.00030566555693249355",
            "extra": "mean: 2.958297700001822 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.1712276665936133,
            "unit": "iter/sec",
            "range": "stddev: 0.0004794287731072945",
            "extra": "mean: 10.590780300003644 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.06203327941813373,
            "unit": "iter/sec",
            "range": "stddev: 0.0009340811300229296",
            "extra": "mean: 29.23325375000445 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.320292611615989,
            "unit": "iter/sec",
            "range": "stddev: 0.00034051254374955093",
            "extra": "mean: 5.661805900004424 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 15.864653468648513,
            "unit": "iter/sec",
            "range": "stddev: 0.00002452244757366564",
            "extra": "mean: 114.30659999973614 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 14.435455411450791,
            "unit": "iter/sec",
            "range": "stddev: 0.000020227738010821452",
            "extra": "mean: 125.62364999837428 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 4.1812686684281015,
            "unit": "iter/sec",
            "range": "stddev: 0.000011026064715040548",
            "extra": "mean: 433.70439500051816 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.6587744740508317,
            "unit": "iter/sec",
            "range": "stddev: 0.0000195655022647471",
            "extra": "mean: 682.0565700002135 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 4.602775240242937,
            "unit": "iter/sec",
            "range": "stddev: 0.00001200617106141909",
            "extra": "mean: 393.9872150002089 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 4.406430622680647,
            "unit": "iter/sec",
            "range": "stddev: 0.00002137620442258318",
            "extra": "mean: 411.5427550001982 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 2.304202903539724,
            "unit": "iter/sec",
            "range": "stddev: 0.000017028406770907885",
            "extra": "mean: 787.0116799998073 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.7103504993664718,
            "unit": "iter/sec",
            "range": "stddev: 0.00003316225493419311",
            "extra": "mean: 1.06027074500048 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.56167337813572,
            "unit": "iter/sec",
            "range": "stddev: 0.00008978649719460707",
            "extra": "mean: 707.9101549999223 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 3.1087608978882524,
            "unit": "iter/sec",
            "range": "stddev: 0.00001578240849283188",
            "extra": "mean: 583.3303549999869 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 2.287805756980284,
            "unit": "iter/sec",
            "range": "stddev: 0.000016033343031234952",
            "extra": "mean: 792.6523450001355 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.711637039231336,
            "unit": "iter/sec",
            "range": "stddev: 0.00001046552925750532",
            "extra": "mean: 1.0594738000000348 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.7230928034531336,
            "unit": "iter/sec",
            "range": "stddev: 0.00001645148550338596",
            "extra": "mean: 665.9466749997024 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 3.1780917780231577,
            "unit": "iter/sec",
            "range": "stddev: 0.000015633934884889766",
            "extra": "mean: 570.6048549998856 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 2.3161765048843694,
            "unit": "iter/sec",
            "range": "stddev: 0.000015076928987581691",
            "extra": "mean: 782.9431799999043 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.7338733156404125,
            "unit": "iter/sec",
            "range": "stddev: 0.000018986664600427118",
            "extra": "mean: 1.0458864449998373 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.733352191166931,
            "unit": "iter/sec",
            "range": "stddev: 0.000012435739895875573",
            "extra": "mean: 663.4471050000457 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 3.1444025958024406,
            "unit": "iter/sec",
            "range": "stddev: 0.000011139245872747392",
            "extra": "mean: 576.71832499949 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 10.590056469925006,
            "unit": "iter/sec",
            "range": "stddev: 0.000005322573304228843",
            "extra": "mean: 171.23937000008027 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.555231626573068,
            "unit": "iter/sec",
            "range": "stddev: 0.00003092345080430614",
            "extra": "mean: 709.6948000003067 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.07155112889045463,
            "unit": "iter/sec",
            "range": "stddev: 0.0015877663724432201",
            "extra": "mean: 25.344598000006613 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.050852867647562514,
            "unit": "iter/sec",
            "range": "stddev: 0.0009867639147534333",
            "extra": "mean: 35.660419599997795 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.0275692307628186,
            "unit": "iter/sec",
            "range": "stddev: 0.02902203272054624",
            "extra": "mean: 65.7774826500031 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.05161688810075733,
            "unit": "iter/sec",
            "range": "stddev: 0.0002694769707296626",
            "extra": "mean: 35.132582860000525 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.4460695861082082,
            "unit": "iter/sec",
            "range": "stddev: 0.000019115830581558754",
            "extra": "mean: 741.3667250000344 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.45978858277091,
            "unit": "iter/sec",
            "range": "stddev: 0.000009687491998980118",
            "extra": "mean: 737.2318949998657 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.014695819287134596,
            "unit": "iter/sec",
            "range": "stddev: 0.0038220832721506696",
            "extra": "mean: 123.39799250000283 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.028419345698112136,
            "unit": "iter/sec",
            "range": "stddev: 0.0034227645164805007",
            "extra": "mean: 63.80986450000137 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.347001951394377,
            "unit": "iter/sec",
            "range": "stddev: 0.0000524884983334829",
            "extra": "mean: 772.6600300003383 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.414520283891011,
            "unit": "iter/sec",
            "range": "stddev: 0.000015275870325024508",
            "extra": "mean: 751.05378499984 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 8.780180711562066,
            "unit": "iter/sec",
            "range": "stddev: 0.00000845063836715944",
            "extra": "mean: 206.53727500018704 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 3.2142590670251296,
            "unit": "iter/sec",
            "range": "stddev: 0.00000709392152129376",
            "extra": "mean: 564.1843299997618 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 21.92242214773317,
            "unit": "iter/sec",
            "range": "stddev: 0.000003903892329526382",
            "extra": "mean: 82.72054000030948 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 22.211466027072866,
            "unit": "iter/sec",
            "range": "stddev: 0.00000347774492176718",
            "extra": "mean: 81.64407500004245 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 12.402025496319034,
            "unit": "iter/sec",
            "range": "stddev: 0.000004421895742065436",
            "extra": "mean: 146.22084100000166 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 7.531884938226643,
            "unit": "iter/sec",
            "range": "stddev: 0.000004154530422327885",
            "extra": "mean: 240.76769799967224 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 7.154146379481448,
            "unit": "iter/sec",
            "range": "stddev: 0.000011218658707514054",
            "extra": "mean: 253.4802199988917 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 6.338859210195176,
            "unit": "iter/sec",
            "range": "stddev: 0.000007270893379907277",
            "extra": "mean: 286.0821699997018 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.3857257788465634,
            "unit": "iter/sec",
            "range": "stddev: 0.00005884501754470892",
            "extra": "mean: 4.701357019999932 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.9706465866281717,
            "unit": "iter/sec",
            "range": "stddev: 0.000012943254835593548",
            "extra": "mean: 456.7101499998216 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.5709978139458247,
            "unit": "iter/sec",
            "range": "stddev: 0.000039300115740912656",
            "extra": "mean: 3.175904624999646 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 1.0970666016766064,
            "unit": "iter/sec",
            "range": "stddev: 0.0000174824633763029",
            "extra": "mean: 1.6529849650001438 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.8856215588657603,
            "unit": "iter/sec",
            "range": "stddev: 0.000027825995905267408",
            "extra": "mean: 2.04764052999991 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.8999647175674401,
            "unit": "iter/sec",
            "range": "stddev: 0.000019026269476002277",
            "extra": "mean: 2.0150063250000017 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.005546873325717866,
            "unit": "iter/sec",
            "range": "stddev: 0.0039411777971710155",
            "extra": "mean: 326.9291529999994 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.22065428594336614,
            "unit": "iter/sec",
            "range": "stddev: 0.0017738963699222073",
            "extra": "mean: 8.218442666645842 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.0434362236992369,
            "unit": "iter/sec",
            "range": "stddev: 0.0002579638520435382",
            "extra": "mean: 41.7493613333401 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.043215668943226496,
            "unit": "iter/sec",
            "range": "stddev: 0.0009591791333170187",
            "extra": "mean: 41.962432666669734 msec\nrounds: 3"
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
          "id": "3120464a4c60d9a9460ac47bf440cb48cbcb2a0b",
          "message": "Simplify and Clarify. Remove duplicate assert fail messages (#1936)\n\nSegregate long tests with mostly no expected messages from tests with no expected messages and the few that do.\n\nDisambiguate duplicate assert fail messages by describing the differences less vaguely.\n\nGo over the wording of some assert messages.\n\nNot done: assert messages should be independent and not rely on\nunderstanding the history of tests that occurred before. This is a fine\nthing to do in a doctest for pedagogical reasons, but not in a pytest.",
          "timestamp": "2026-09-05T12:19:33-04:00",
          "tree_id": "c8b0bfbd819118ba14c89b30c2ee0f7d050a371b",
          "url": "https://github.com/Mathics3/mathics-core/commit/3120464a4c60d9a9460ac47bf440cb48cbcb2a0b"
        },
        "date": 1788625270611,
        "tool": "pytest",
        "benches": [
          {
            "name": "test/timings/test_regressions.py::test_reference_benchmark",
            "value": 1,
            "unit": "iter/sec",
            "range": "stddev: 0.000030411932956454415",
            "extra": "mean: 1.1172098879053318 msec\nrounds: 339"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[reset::reset]",
            "value": 18745.23718984974,
            "unit": "iter/sec",
            "range": "stddev: 1.7134568392387825e-9",
            "extra": "mean: 59.59966665614047 nsec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1 + 2]",
            "value": 7.615618149692995,
            "unit": "iter/sec",
            "range": "stddev: 0.0010723932231891111",
            "extra": "mean: 146.6998300000597 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(*Long Sum*)$u0+$u1+$u2+$u3+$u4+$u5+$u6+...]",
            "value": 0.5209806585564276,
            "unit": "iter/sec",
            "range": "stddev: 0.00003054746270914984",
            "extra": "mean: 2.1444364000018368 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5 * 3]",
            "value": 26.95269973114887,
            "unit": "iter/sec",
            "range": "stddev: 0.000004203642798812868",
            "extra": "mean: 41.45075999990411 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1+2*3]",
            "value": 13.33604557561417,
            "unit": "iter/sec",
            "range": "stddev: 0.0000044051976197125475",
            "extra": "mean: 83.77370049996102 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::(1+2)*3]",
            "value": 13.221690266715589,
            "unit": "iter/sec",
            "range": "stddev: 0.0000046702713851201955",
            "extra": "mean: 84.4982650000361 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::1/2+3/4]",
            "value": 3.140976457611565,
            "unit": "iter/sec",
            "range": "stddev: 0.000009807769407631883",
            "extra": "mean: 355.68871749993036 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::5^3]",
            "value": 18.38105575369742,
            "unit": "iter/sec",
            "range": "stddev: 7.488052079443183e-7",
            "extra": "mean: 60.78050700001825 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[arithmetic::10^100]",
            "value": 18.35650451125742,
            "unit": "iter/sec",
            "range": "stddev: 5.578283982176753e-7",
            "extra": "mean: 60.86179899992317 usec\nrounds: 100"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2]",
            "value": 6.686958048338047,
            "unit": "iter/sec",
            "range": "stddev: 0.0000025354314787681305",
            "extra": "mean: 167.07296199996335 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]:=x^2/;x>4]",
            "value": 6.655732868844655,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023611892792538076",
            "extra": "mean: 167.85678000013604 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[F,x]; F[x_]^:=x^2/;x>4]",
            "value": 6.495232841896011,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011052838301473334",
            "extra": "mean: 172.0045939999295 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u]; u=4;u^2]",
            "value": 6.177430284215186,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015355656217823671",
            "extra": "mean: 180.85349999984146 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z;]",
            "value": 9.58767351141196,
            "unit": "iter/sec",
            "range": "stddev: 0.000001150621622052348",
            "extra": "mean: 116.52565000002824 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[u,z]; u=z/;z>1]",
            "value": 7.926660225110089,
            "unit": "iter/sec",
            "range": "stddev: 0.000006401766281155897",
            "extra": "mean: 140.9433299999705 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...0]",
            "value": 0.009021843156300394,
            "unit": "iter/sec",
            "range": "stddev: 0.0007407558578965641",
            "extra": "mean: 123.8338849999991 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...1]",
            "value": 0.009053893181228357,
            "unit": "iter/sec",
            "range": "stddev: 0.00064948665928443",
            "extra": "mean: 123.39552339999642 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{...2]",
            "value": 0.008877222744930998,
            "unit": "iter/sec",
            "range": "stddev: 0.006108395279744388",
            "extra": "mean: 125.8512847999981 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[OrderlessF, Orderless];]",
            "value": 14.66521627629516,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015507585298790096",
            "extra": "mean: 76.18093499999645 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[assign::SetAttributes[FlatF, Flat];]",
            "value": 14.729397999239382,
            "unit": "iter/sec",
            "range": "stddev: 0.000001005147923185246",
            "extra": "mean: 75.84898500013537 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^5]]",
            "value": 0.4816472915448675,
            "unit": "iter/sec",
            "range": "stddev: 0.00029629568097122",
            "extra": "mean: 2.319560200000126 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c)^5]]",
            "value": 0.13964598704462503,
            "unit": "iter/sec",
            "range": "stddev: 0.0003815827517277838",
            "extra": "mean: 8.000300700000196 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b+c+d)^5]]",
            "value": 0.050429498049742554,
            "unit": "iter/sec",
            "range": "stddev: 0.0007988372896815986",
            "extra": "mean: 22.153896649999183 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Expand[(a+b)^10]]",
            "value": 0.23881092958727404,
            "unit": "iter/sec",
            "range": "stddev: 0.0008049644324165075",
            "extra": "mean: 4.6782192499989605 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[F,x,3]]",
            "value": 11.363187928891874,
            "unit": "iter/sec",
            "range": "stddev: 0.000010689263735336874",
            "extra": "mean: 98.31834999971534 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[symbolic::Nest[FlatF,x,3]]",
            "value": 10.53072506871405,
            "unit": "iter/sec",
            "range": "stddev: 0.000008719519024589565",
            "extra": "mean: 106.09050000027764 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2]]]",
            "value": 3.167754427784848,
            "unit": "iter/sec",
            "range": "stddev: 0.000012072357185912169",
            "extra": "mean: 352.6819749997401 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2]]]",
            "value": 2.050739056915725,
            "unit": "iter/sec",
            "range": "stddev: 0.00001590764885055289",
            "extra": "mean: 544.7840300001872 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[2.]]]",
            "value": 3.575121406984255,
            "unit": "iter/sec",
            "range": "stddev: 0.000005504495014325482",
            "extra": "mean: 312.49565000024404 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NumericQ[Sqrt[-2.]]]",
            "value": 3.5048686181740427,
            "unit": "iter/sec",
            "range": "stddev: 0.000004659186456988903",
            "extra": "mean: 318.75941999999213 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2]]]",
            "value": 1.7659024141528734,
            "unit": "iter/sec",
            "range": "stddev: 0.000014742221172196745",
            "extra": "mean: 632.6566399997091 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2]]]",
            "value": 1.3245662194055725,
            "unit": "iter/sec",
            "range": "stddev: 0.000045651018921198816",
            "extra": "mean: 843.4534049997922 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[2.]]]",
            "value": 2.2295858775568957,
            "unit": "iter/sec",
            "range": "stddev: 0.000007896215518435235",
            "extra": "mean: 501.08403500004783 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Positive[Sqrt[-2.]]]",
            "value": 2.4940258995892064,
            "unit": "iter/sec",
            "range": "stddev: 0.000007203556562799265",
            "extra": "mean: 447.95440500010386 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2]]]",
            "value": 1.8041683330441363,
            "unit": "iter/sec",
            "range": "stddev: 0.000005649585155295476",
            "extra": "mean: 619.2381649999845 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2]]]",
            "value": 1.3726902725066965,
            "unit": "iter/sec",
            "range": "stddev: 0.000004574060121291948",
            "extra": "mean: 813.8834449997034 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[2.]]]",
            "value": 2.2085487911006108,
            "unit": "iter/sec",
            "range": "stddev: 0.000009869801506808282",
            "extra": "mean: 505.85701000002814 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::Negative[Sqrt[-2.]]]",
            "value": 2.482432976775428,
            "unit": "iter/sec",
            "range": "stddev: 0.000007223528163202346",
            "extra": "mean: 450.0463450000325 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2]]]",
            "value": 1.8139019594590504,
            "unit": "iter/sec",
            "range": "stddev: 0.000007271443813578745",
            "extra": "mean: 615.9152550000613 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2]]]",
            "value": 1.3721109783619334,
            "unit": "iter/sec",
            "range": "stddev: 0.000009300517743805454",
            "extra": "mean: 814.227059999979 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[2.]]]",
            "value": 2.2270227642382845,
            "unit": "iter/sec",
            "range": "stddev: 0.000009683554895062208",
            "extra": "mean: 501.66074000031807 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[numeric::NonNegative[Sqrt[-2.]]]",
            "value": 2.4845511697684626,
            "unit": "iter/sec",
            "range": "stddev: 0.000005222188518668771",
            "extra": "mean: 449.66266000045607 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[100]]",
            "value": 8.256438085039989,
            "unit": "iter/sec",
            "range": "stddev: 0.000002558302204844457",
            "extra": "mean: 135.31378500005076 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Range[1000]]",
            "value": 2.3606060925189065,
            "unit": "iter/sec",
            "range": "stddev: 0.000017654327722442964",
            "extra": "mean: 473.2724749995043 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i, {i, 1, 100}]]",
            "value": 0.05363308515018859,
            "unit": "iter/sec",
            "range": "stddev: 0.0011112796750989324",
            "extra": "mean: 20.830610149999984 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i^2, {i, 1, 100}]]",
            "value": 0.039918984398755936,
            "unit": "iter/sec",
            "range": "stddev: 0.00011140189537006325",
            "extra": "mean: 27.986931649998326 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Table[i*j, {i, 1., 10.},{j, 1., 10.}]]",
            "value": 0.021630487137896066,
            "unit": "iter/sec",
            "range": "stddev: 0.02921067720908984",
            "extra": "mean: 51.64977934999939 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@Table[i^2, {i, 1, 100}]]",
            "value": 0.03944795857574544,
            "unit": "iter/sec",
            "range": "stddev: 0.00006039819506052556",
            "extra": "mean: 28.321107814999777 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Total[Range[100]]]",
            "value": 2.1167902697202026,
            "unit": "iter/sec",
            "range": "stddev: 0.000010040943040584488",
            "extra": "mean: 527.7848749999237 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[Range[1000]]]",
            "value": 2.2278651070430078,
            "unit": "iter/sec",
            "range": "stddev: 0.000003251900525192383",
            "extra": "mean: 501.47106500006083 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::nonuniformTable=Table[If[i==0,1,1./(1.+i...]",
            "value": 0.01129335860668735,
            "unit": "iter/sec",
            "range": "stddev: 0.0028325863268340436",
            "extra": "mean: 98.92627399999299 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::uniformTable=Table[1./(1.+i^2),{i,0,100}...]",
            "value": 0.022975189747854396,
            "unit": "iter/sec",
            "range": "stddev: 0.00022067317716369377",
            "extra": "mean: 48.62679699999717 msec\nrounds: 2"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@uniformTable]",
            "value": 2.0819226088927127,
            "unit": "iter/sec",
            "range": "stddev: 0.00002516140695618588",
            "extra": "mean: 536.6241200000843 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Plus@@nonuniformTable]",
            "value": 2.210125064444981,
            "unit": "iter/sec",
            "range": "stddev: 0.000010601763615244973",
            "extra": "mean: 505.4962299999488 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[uniformTable,{__Real}]]",
            "value": 7.2010427877904375,
            "unit": "iter/sec",
            "range": "stddev: 0.000005012042192179586",
            "extra": "mean: 155.14556999988827 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::MatchQ[nonuniformTable,{__Real}]]",
            "value": 2.7497264275439925,
            "unit": "iter/sec",
            "range": "stddev: 0.000003408785216511717",
            "extra": "mean: 406.2985600000957 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[nonuniformTable]]",
            "value": 17.0110395355906,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013698881202340199",
            "extra": "mean: 65.67558000014628 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[list::Length[uniformTable]]",
            "value": 17.197248678633372,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012876663990688766",
            "extra": "mean: 64.96445499990955 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[x, x->y]]",
            "value": 8.859763297053115,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020425866912076313",
            "extra": "mean: 126.09929299995315 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Replace[{x,y}, {x->a, y->b}]]",
            "value": 5.459085068790122,
            "unit": "iter/sec",
            "range": "stddev: 0.000004504133689393059",
            "extra": "mean: 204.6514889999571 usec\nrounds: 50"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[FlatF[FlatF[FlatF[FlatF[FlatF[FlatF...]",
            "value": 5.3193795031366475,
            "unit": "iter/sec",
            "range": "stddev: 0.000008794639886348909",
            "extra": "mean: 210.02635499996813 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...0]",
            "value": 4.859433952305949,
            "unit": "iter/sec",
            "range": "stddev: 0.000005422641490775029",
            "extra": "mean: 229.90535500028386 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Hold[OrderlessF[$u0,$u1,$u2,$u3,$u4,$u5,...1]",
            "value": 0.29910464369014406,
            "unit": "iter/sec",
            "range": "stddev: 0.000027181080115867543",
            "extra": "mean: 3.7351806850003295 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Cases[{1,2,3,4}, x_Integer /; x>2]]",
            "value": 3.0028473656967467,
            "unit": "iter/sec",
            "range": "stddev: 0.0000074879510525169485",
            "extra": "mean: 372.05017499985615 usec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Select[Range[100], PrimeQ]]",
            "value": 0.37572340906147583,
            "unit": "iter/sec",
            "range": "stddev: 0.000029970763894026355",
            "extra": "mean: 2.9734902350003267 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::Range[100]/.{a__Integer}->a[[1]]]",
            "value": 0.9382913196975663,
            "unit": "iter/sec",
            "range": "stddev: 0.0000368461938952785",
            "extra": "mean: 1.1906855199997324 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::F@@Join[Range[100],a->1]/.F[a__Integer,O...]",
            "value": 0.7465449217873366,
            "unit": "iter/sec",
            "range": "stddev: 0.000016199725133030565",
            "extra": "mean: 1.4965072499998655 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[pattern::OrderlessF@@Join[Range[100],a->1]/.F[a__...]",
            "value": 0.766638398947927,
            "unit": "iter/sec",
            "range": "stddev: 0.000007704538004046232",
            "extra": "mean: 1.4572840200001735 msec\nrounds: 10"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[Sin[2 Pi x],{x,0,3}];]",
            "value": 0.0043647087852979145,
            "unit": "iter/sec",
            "range": "stddev: 0.0027150303895875066",
            "extra": "mean: 255.96435933332867 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot[If[x>1,x,-x],{x,0,3}];]",
            "value": 0.1608824119492872,
            "unit": "iter/sec",
            "range": "stddev: 0.0018431667409756262",
            "extra": "mean: 6.944263666667894 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=DensityPlot[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03398568310218091,
            "unit": "iter/sec",
            "range": "stddev: 0.00017086203041103887",
            "extra": "mean: 32.8729566666747 msec\nrounds: 3"
          },
          {
            "name": "test/timings/test_regressions.py::test_regression_benchmark[plot::p=Plot3D[x*y,{x,0,3},{y,0,3}];]",
            "value": 0.03641939278031027,
            "unit": "iter/sec",
            "range": "stddev: 0.0005533638528719356",
            "extra": "mean: 30.676235999995544 msec\nrounds: 3"
          }
        ]
      }
    ]
  }
}