(*Extended rules for handling expressions with Bessel functions*)

Begin["internals`bessel`"]

Unprotect[HankelH1];
(*HankelH1[x_Integer?NegativeQ, z_]:=-HankelH1[-x, z];*)
(*Limit cases*)
HankelH1[nu_, 0] := DirectedInfinity[];
Protect[HankelH1];


Unprotect[HankelH2];
(*HankelH2[x_Integer?NegativeQ, z_]:=-HankelH2[-x, z];*)
(*Limit cases*)
HankelH2[nu_,0] := DirectedInfinity[];
Protect[HankelH2];


Unprotect[BesselI]
(*Rayleigh's formulas for half-integer indices*)
BesselI[nu_/;(nu>0 && IntegerQ[2*nu]), z_]:=Module[{u,f,k= nu-1/2},f=Sinh[u]/u;While[k>0, k=k-1;f = (-D[f, u]/u)]; (Sqrt[2/Pi z] * ((-u)^(nu-1/2)*f))/.u->z];
BesselI[nu_/;(nu<0 && IntegerQ[2*nu]), z_]:=Module[{u,f,k=-nu-1/2},f=Cosh[u]/u;While[k>0, k=k-1;f = (-D[f, u]/u)]; (Sqrt[2/Pi z] * ((-u)^(-nu-1/2)*f))/.u->z];
(*Limit cases*)
BesselI[0, 0] := 1;
BesselI[nu_Integer,0]:=0;
BesselI[nu_Rational, 0] := If[nu>0, 0, DirectedInfinity[]];
BesselI[nu_Real, 0] := If[nu>0, 0, DirectedInfinity[]];
BesselI[nu_, DirectedInfinity[z___]] := 0;
Protect[BesselI]

Unprotect[BesselK]
(*Rayleigh's formulas for half-integer indices*)
BesselK[nu_/;(nu>0 && IntegerQ[2*nu]), z_]:=Module[{u,f,k= nu-1/2},f=Exp[-u]/u;While[k>0, k=k-1;f = (D[f, u]/u)]; (Sqrt[Pi/2 z] * ((-u)^(nu-1/2)*f))/.u->z];
BesselK[nu_/;(nu<0 && IntegerQ[2*nu]), z_]:=Module[{u,f,k=-nu-1/2},f=Exp[-u]/u;While[k>0, k=k-1;f = (D[f, u]/u)]; (Sqrt[Pi/2 z] * ((-u)^(-nu-1/2)*f))/.u->z];
(*Limit cases*)
BesselK[0, 0] = DirectedInfinity[-1];
BesselK[nu_?NumericQ, 0] = DirectedInfinity[];
Protect[BesselK]


Unprotect[BesselJ]
(*Rayleigh's formulas for half-integer indices*)
BesselJ[nu_/;(nu>0 && IntegerQ[2*nu]), z_]:=Module[{u,f,k= nu-1/2},f=Sin[u]/u;While[k>0, k=k-1;f = (D[f, u]/u)]; (Sqrt[2/Pi z] * ((-u)^(nu-1/2)*f))/.u->z];
BesselJ[nu_/;(nu<0 && IntegerQ[2*nu]), z_]:=Module[{u,f,k=-nu-1/2},f=Cos[u]/u;While[k>0, k=k-1;f = (-D[f, u]/u)]; (Sqrt[2/Pi z] * ((-u)^(-nu-1/2)*f))/.u->z];
(*Limit cases*)
BesselJ[0, 0] := 1;
BesselJ[nu_Integer,0]:=0;
BesselJ[nu_Rational, 0] := If[nu>0, 0, DirectedInfinity[]];
BesselJ[nu_Real, 0] := If[nu>0, 0, DirectedInfinity[]];
BesselJ[nu_, DirectedInfinity[z___]] := 0;
Protect[BesselJ]


Unprotect[BesselY]
(*Rayleigh's formulas for half-integer indices*)
BesselY[nu_/;(nu>0 && IntegerQ[2*nu]), z_]:=Module[{u,f,k= nu-1/2},f=Cos[u]/u;While[k>0, k=k-1;f = (D[f, u]/u)]; (-Sqrt[2/Pi z] * ((-u)^(nu-1/2)*f))/.u->z];
BesselY[nu_/;(nu<0 && IntegerQ[2*nu]), z_]:=Module[{u,f,k=-nu-1/2},f=Sin[u]/u;While[k>0, k=k-1;f = (D[f, u]/u)]; (Sqrt[2/Pi z] * ((u)^(-nu-1/2)*f))/.u->z];
(*Limit cases*)
BesselY[0, 0] = DirectedInfinity[-1];
BesselY[nu_, 0] = DirectedInfinity[];
Protect[BesselY]





Unprotect[Integrate];
(*  See https://dlmf.nist.gov/10.9 *)
Integrate[Cos[z_Integer Sin[Theta_]], {Theta_, 0, Pi}]:= Pi BesselJ[0, Abs[z]];
Integrate[Cos[z_Rational Sin[Theta_]], {Theta_, 0, Pi}]:= Pi BesselJ[0, Abs[z]];
Integrate[Cos[z_Real Sin[Theta_]], {Theta_, 0, Pi}]:= Pi BesselJ[0, Abs[z]];


(* This rule needs to implement Elements*)
Integrate[Cos[z_ Sin[Theta_]], {Theta_, 0, Pi}]:= ConditionalExpression[Pi BesselJ[0, Abs[z]], Element[z, Reals]];

Protect[Integrate];

(*TODO: extend me with series expansions, integrals, etc*)
End[]
