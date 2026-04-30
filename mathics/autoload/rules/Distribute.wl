(* Distribute coded in WL *)

(* Distribute using Plus form*)

Unprotect[Distribute]

(*Distribute[expr_, targetHead_: Plus] :=
  expr /. f_[args___] /; MemberQ[{args}, _targetHead] :>
    With[{pos = FirstPosition[{args}, _targetHead][[1]]},
      targetHead @@ Map[
        f @@ ReplacePart[{args}, pos -> #] &,
        Extract[{args}, pos]
      ]
    ]
*)
Distribute[expr_, targetHead_: Plus] :=
   expr //. f_[pre___, targetHead[inner___], post___] :>
   targetHead @@ (f[pre, #, post] & /@ {inner})
Protect[Distribute]

Unprotect[FlattenAt]
FlattenAt[expr_, pos_] := MapAt[Flatten[#, 1] &, expr, pos]
protect[Distribute]
