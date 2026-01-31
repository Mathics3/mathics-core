(**************************************************************************************
Run the format tests in WMA.

Notice that some of the tests that produce meaninful outputs in Mathics3,
fails miserably to produce an output in WMA. Also, the results of these tests
in the Notebook interface, the CLI (math) and wolframscript are not fully consistent.

****************************************************************************************)

ISMATHICSINTERPRETER=(StringTake[$Version, 8]==="Mathics3");

If[ISMATHICSINTERPRETER,
  (*Mathics Interpreter*)
  STRIPMATHML[strg_]:= Module[
     {start=(StringPosition[strg,"<math display=\"block\">"][[1]][[2]]+1),
     end=(StringPosition[strg,"</math>"][[1]][[1]]-1)
     },
     StringTrim[StringTake[strg, {start, end}]]
     ],
  (*WMA interpreter*)
  STRIPMATHML[strg_]:= Module[
     {semanticpos, start, end},
      semanticpos = StringPosition[strg,"<semantics>"];
      (*If have a field <semantics> use it as a reference.*)
      If[Length[semanticpos]>0,
         start=(semanticpos[[1]][[2]]+1);
	 end=(StringPosition[strg,"<annotation"][[1]][[1]]-1);,
	 (*Otherwise, strip <math>...</math>*)
	 start=StringPosition[strg,"<math>"][[1]][[2]]+1;
	 end=StringPosition[strg,"</math>"][[1]][[1]]-1;
      ];
      StringTrim[StringTake[strg, {start, end}]]
   ]
]



Print["Read json"];
data = Import["format_tests-WMA.json"];
Print["Found ", Length[data], " expressions to test."];

Print["Run the tests"];

Do[key = ToExpression[tests[[1]]];
 fields = tests[[2]];
 mesg = ("msg" /. fields);
 text = ("text" /. fields);
 latex = ("latex" /. fields);
 mathml = ("mathml" /. fields);
 Print[Head[key], "  msg:", mesg, "<<", key, ">>"];
 (*text*)
 If[Head[text]===List,
   Print["    text", "\n    -----", "\n"];
   Do[form = ToExpression[subtest[[1]]]; expr = form[key];
      result = ToString[expr, CharacterEncoding->"ASCII"];
      expected = subtest[[2]];
      If[result != expected,
         Print["      * ", FullForm[expr], " //", form, "(text)    [Failed]\n        result:", "<<" <> result <> ">>(", StringLength[result],
    ")\n        expected: ", "<<" <> expected <> ">> (", StringLength[expected],")\n"],
         Print["      * ", FullForm[expr], " //", form, "(text)    [OK]"]];,
 {subtest, text}]
 ];
 (*LaTeX*)
 If[Head[latex]===List,
   Print["    latex", "\n    -----", "\n"];
   Do[form = ToExpression[subtest[[1]]]; expr = form[key];
      result = ToString[expr, TeXForm, CharacterEncoding->"ASCII"];
      expected = subtest[[2]];
      If[result != subtest[[2]],
        Print["      * ", key, " //", form, "(latex)    [Failed]\n        result:",
        "<<" <> result <> ">>", "\n        expected: ",
        "<<" <> expected <> ">>\n"],
      Print["      * ", key, " //",  form, "(latex)    [OK]"]];,
   {subtest, latex}]
   ];
(*MathML*)
 If[Head[mathml]===List,
 Print["    mathml", "\n    ------", "\n"];
 Do[form = ToExpression[subtest[[1]]]; expr = form[key];
  result = STRIPMATHML[ToString[expr, MathMLForm, CharacterEncoding->"ASCII"]];
  expected = subtest[[2]];
  If[result != subtest[[2]],
   Print["      * ", key, " //",  form, "(mathml)    [Failed]\n        result:",
    "<<" <> result <> ">>", "\n        expected: ",
    "<<" <> expected <> ">>\n"],
   Print["      * ", key, " //",  form, "(mathml)    [OK]"]];, {subtest, mathml}]];
  , {tests, data}
  ]
