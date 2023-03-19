(* Adapted from symja_android_library/symja_android_library/rules/Bessel{I,J}.m
   Note: These are not currently covered by SymPy.
 *)


Unprotect[BesselI]
BesselI[nu_/;(nu>0 && IntegerQ[2*nu]),z_]:=Module[{u,f,k= nu-1/2},f=Sinh[u]/u;While[k>0, k=k-1;f = (-D[f, u]/u)]; (Sqrt[2/Pi z] * ((-u)^(nu-1/2)*f))/.u->z];
BesselI[nu_/;(nu<0 && IntegerQ[2*nu]),z_]:=Module[{u,f,k=-nu-1/2},f=Cosh[u]/u;While[k>0, k=k-1;f = (-D[f, u]/u)]; (Sqrt[2/Pi z] * ((-u)^(-nu-1/2)*f))/.u->z];
Protect[BesselI]

Unprotect[BesselK]
BesselK[nu_/;(nu>0 && IntegerQ[2*nu]),z_]:=Module[{u,f,k= nu-1/2},f=Exp[-u]/u;While[k>0, k=k-1;f = (D[f, u]/u)]; (Sqrt[Pi/2 z] * ((-u)^(nu-1/2)*f))/.u->z];
BesselK[nu_/;(nu<0 && IntegerQ[2*nu]),z_]:=Module[{u,f,k=-nu-1/2},f=Exp[-u]/u;While[k>0, k=k-1;f = (D[f, u]/u)]; (Sqrt[Pi/2 z] * ((-u)^(-nu-1/2)*f))/.u->z];
Protect[BesselK]


Unprotect[BesselJ]
BesselJ[nu_/;(nu>0 && IntegerQ[2*nu]),z_]:=Module[{u,f,k= nu-1/2},f=Sin[u]/u;While[k>0, k=k-1;f = (D[f, u]/u)]; (Sqrt[2/Pi z] * ((-u)^(nu-1/2)*f))/.u->z];
BesselJ[nu_/;(nu<0 && IntegerQ[2*nu]),z_]:=Module[{u,f,k=-nu-1/2},f=Cos[u]/u;While[k>0, k=k-1;f = (-D[f, u]/u)]; (Sqrt[2/Pi z] * ((-u)^(-nu-1/2)*f))/.u->z];
Protect[BesselJ]


Unprotect[BesselY]
BesselY[nu_/;(nu>0 && IntegerQ[2*nu]),z_]:=Module[{u,f,k= nu-1/2},f=Cos[u]/u;While[k>0, k=k-1;f = (D[f, u]/u)]; (-Sqrt[2/Pi z] * ((-u)^(nu-1/2)*f))/.u->z];
BesselY[nu_/;(nu<0 && IntegerQ[2*nu]),z_]:=Module[{u,f,k=-nu-1/2},f=Sin[u]/u;While[k>0, k=k-1;f = (D[f, u]/u)]; (Sqrt[2/Pi z] * ((u)^(-nu-1/2)*f))/.u->z];
Protect[BesselY]
