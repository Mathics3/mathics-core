(* Additions to mathics.builtin.numbers.trig that are either wrong
   or not covered by SymPy.

   These were culled from symja_android_library/rules/LimitRules.m.
 *)

Unprotect[Limit];
(*****
 Fixme  Uncommenting any of the below causes:

  G[x_Real]=x^2; a={G[x]}; {x=1.; a, x=.; a} == {{1.}, {G[x]}}

To be false when it should be true.
 Huh?
 ****)

Limit[Tan[Sysetm`Limit`x_], System`Limit`x_Symbol->Pi/2] = Indeterminate;
Limit[Cot[System`Limit`x_], System`Limit`x_Symbol->0] = Indeterminate;
Limit[System`Limit`x_ Sqrt[2 Pi]^(System`Limit`x_^-1) (Sin[System`Limit`x_]/(System`Limit`x_!))^(System`Limitx_^-1), System`Limit`x_Symbol->Infinity] = E;
Protect[Limit];
