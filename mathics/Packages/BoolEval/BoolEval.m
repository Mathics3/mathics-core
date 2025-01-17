(* Mathematica Package *)
(* :Context: BoolEval` *)
(* :Author: szhorvat *)
(* :Date: 2014-05-30 *)

BeginPackage["BoolEval`"]
(* Exported symbols added here with SymbolName::usage *)

BoolEval::usage =
    "BoolEval[array > value] replaces elements of the numerical array 'array' which are greater than 'value' with 1, and the rest with 0.\n" <>
    "BoolEval[condition] takes a condition expressed in terms of >, >=, <, <=, ==, != and logical operators, and evaluates it for each element of the arrays appearing in the condition. The result is returned as a Boolean array of 0s and 1s.";

BoolPick::usage =
    "BoolPick[array, condition] will return the elements of a numerical array for which condition is True.";

BoolCount::usage =
    "BoolCount[condition] counts the number of elements satisfying the array condition.";

Begin["`Private`"] (* Begin Private Context *)

greaterEq[a_, b_] := UnitStep@Subtract[a, b]
lessEq[a_, b_] := UnitStep@Subtract[b, a]
greater[a_, b_] := Subtract[1, lessEq[a, b]]
less[a_, b_] := Subtract[1, greaterEq[a, b]]
unequal[a_, b_] := Unitize@Subtract[a, b]
equal[a_, b_] := Subtract[1, unequal[a, b]]

equal[a_, b_, c__] := equal[a, b] equal[b, c]
less[a_, b_, c__] := less[a, b] less[b, c]
greater[a_, b_, c__] := greater[a, b] greater[b, c]
lessEq[a_, b_, c__] := lessEq[a, b] lessEq[b, c]
greaterEq[a_, b_, c__] := greaterEq[a, b] greaterEq[b, c]

unequal[a__] := Times @@ (unequal @@@ Subsets[{a}, {2}])

rules = Dispatch[{
    (* Do not descend into the innards of Image/Audio, so they are safe to use. *)
    (* Note that options within these may contain True/False,
       which must not be converted to 1/0. *)
    im_Image :> im, au_System`Audio :> au,

    (* Relational operators *)
    Less -> less, LessEqual -> lessEq,
    Greater -> greater, GreaterEqual -> greaterEq,
    Equal -> equal, Unequal -> unequal,

    (* Boolean operators *)
    Or -> (Unitize@Plus[##]&), And -> Times, Not -> (Subtract[1, #] &),
    Nor -> (Subtract[1, Unitize@Plus[##]]&), Nand -> (Subtract[1, Times[##]]&),
    Xor -> (Mod[Plus[##], 2]&), Xnor -> (Subtract[1, Mod[Plus[##], 2]]&),

    (* Boolean values *)
    True -> 1, False -> 0
  }];

(* Convert Inequality expressions to canonical form, e.g. a < b > c  ->  a < b && b > c *)
ineq = Dispatch[{
    HoldPattern@Inequality[a_, op_, b_] :> op[a, b],
    HoldPattern@Inequality[a_, op_, b_, rest__] :> op[a, b] && Inequality[b, rest]
  }];

SyntaxInformation[BoolEval] = {"ArgumentsPattern" -> {_}};
SetAttributes[BoolEval, HoldAll]
BoolEval[condition_] := First[Hold[condition] //. ineq /. rules]

SyntaxInformation[BoolPick] = {"ArgumentsPattern" -> {_, _}};
SetAttributes[BoolPick, HoldRest]
BoolPick[array_, condition_] :=
    Pick[array,
      BoolEval[condition],
      1
    ]

SyntaxInformation[BoolCount] = {"ArgumentsPattern" -> {_}};
SetAttributes[BoolCount, HoldAll]
BoolCount[condition_] := Total[BoolEval[condition], Infinity]

End[] (* End Private Context *)

EndPackage[]
