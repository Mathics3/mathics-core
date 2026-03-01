(* ::Package:: *)

(**************************************************************************************
Run the format tests in WMA.

Notice that some of the tests that produce meaningful outputs in Mathics3,
fails miserably to produce an output in WMA. Also, the results of these tests
in the Notebook interface, the CLI (math) and wolframscript are not fully consistent.

****************************************************************************************)


Print["Read json"];
data = Import["makeboxes_tests.json"];
Print["Found ", Length[data], " expressions to test."];


Do[
title=testsblock[[1]];
Print["\n",title, "\n",StringJoin[Table["=",{StringLength[title]}]]];
 Do[
   case = tests[[1]];
   Print["\n  ", case,"\n","  ",StringJoin[Table["=",{StringLength[case]}]]];
   Do[
      form = caseform[[1]];
      rul = caseform[[2]];
      expr = "expr"/.rul;
      result = ToExpression[expr];
      expect = ToExpression["expect"/.rul];
      If[SameQ[result, expect],
        Print["    ", expr, " //", form, "   [OK]"],
        Print["    ", expr, " //", form, "   [Failed]"];
        Print["      expr    = ", expr ];
        Print["      result  = ", result];
        Print["      expected= ",expect];
      ],
      {caseform, tests[[2]]}
   ],
   {tests, testsblock[[2]]}],
  {testsblock, data}
];
Print["Done"]
