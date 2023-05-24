(* Additions to mathics.builtin.numbers.trig that are either wrong
   or not covered by SymPy
 *)

Unprotect[ArcCos];
ArcCos[I Infinity] := -I Infinity;
ArcCos[-I Infinity] := I Infinity;
Protect[ArcCos];
