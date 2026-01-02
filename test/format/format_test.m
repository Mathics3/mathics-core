(**************************************************************************************
Run the format tests in WMA.

Notice that some of the tests that produce meaninful outputs in Mathics, 
fails miserably to produce an output in WMA. Also, the results of these tests
in the Notebook interface, the CLI (math) and wolframscript are not fully consistent.

****************************************************************************************)


Print["Read json"];
data = Import["format_tests.json"];
Print["Found ", Length[data], " expressions to test."];

Print["Run the tests"];

Do[key = ToExpression[tests[[1]]];
 fields = tests[[2]];
 mesg = ("msg" /. fields);
 text = ("text" /. fields);
 latex = ("latex" /. fields);
 mathml = ("mathml" /. fields);
 Print[Head[key], "  msg:", mesg, "<<", key, ">>"];
 If[Head[text]===List,
 Print["    text", "\n    -----", "\n"];
 Do[form = ToExpression[subtest[[1]]]; expr = form[key];
  result = ToString[expr];
  expected = subtest[[2]];
  If[result != subtest[[2]], 
   Print["      * ", form, "(text)    [Failed]\n        result:", "<<" <> result <> ">>", 
    "\n        expected: ", "<<" <> expected <> ">>\n"], 
   Print["      * ", form, "(text)    [OK]"]];, {subtest, text}]];
   (*LaTeX*)
 If[Head[latex]===List,
   Print["    latex", "\n    -----", "\n"];
   Do[form = ToExpression[subtest[[1]]]; expr = form[key];
      result = ToString[expr, TeXForm];
      expected = subtest[[2]];
      If[result != subtest[[2]], 
        Print["      * ", form, "(latex)    [Failed]\n        result:", 
        "<<" <> result <> ">>", "\n        expected: ", 
        "<<" <> expected <> ">>\n"], 
      Print["      * ", form, "(latex)    [OK]"]];,
   {subtest, latex}]
   ];
   
(*MathML*)
 If[Head[mathml]===List, 
 Print["    mathml", "\n    ------", "\n"];
 Do[form = ToExpression[subtest[[1]]]; expr = form[key];
  result = ToString[expr, MathMLForm];
  expected = subtest[[2]];
  If[result != subtest[[2]], 
   Print["      * ", form, "(mathml)    [Failed]\n        result:", 
    "<<" <> result <> ">>", "\n        expected: ", 
    "<<" <> expected <> ">>\n"], 
   Print["      * ", form, "(mathml)    [OK]"]];, {subtest, mathml}]];
  , {tests, data}
  ]
