(* Additions to mathics.builtin.numbers.trig that are either wrong
   or not covered by SymPy.

   These were culled from symja_android_library/rules/LimitRules.m.
 *)


Begin["System`Limit`private`"]
Unprotect[Limit];
Limit[Tan[x_], x_Symbol->Pi/2] = Indeterminate;
Limit[Cot[x_], x_Symbol->0] = Indeterminate;
Limit[x_ Sqrt[2 Pi]^(x_^-1) (Sin[x_]/(x_!))^(x_^-1), x_Symbol->Infinity] = E;
Protect[Limit];
End[]
