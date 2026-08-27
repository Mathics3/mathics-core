(* -*- wolfram -*- *)
(* Additions to mathics.builtin.numbers.trig that are either wrong
   or not covered by SymPy.

   These were culled from symja_android_library/rules/LimitRules.m.
 *)


Begin["System`Limit`private`"]
Unprotect[Limit];

(* We have the following Indeterminate rules on Limit to prevent them
   from coming out Infinity. Other cases like:
     Limit[Tan[x], x->Infinity] or
     Limit[Cot[x], x->Infinity]
   SymPy matches WMA.
 *)
Limit[Tan[x_], x_Symbol->Pi/2] = Indeterminate;
Limit[Cot[x_], x_Symbol->0] = Indeterminate;

Limit[x_ Sqrt[2 Pi]^(x_^-1) (Sin[x_]/(x_!))^(x_^-1), x_Symbol->Infinity] = E;
Protect[Limit];
End[]
