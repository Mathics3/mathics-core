(* Adapted from symja_android_library/symja_android_library/rules/Bessel{I,J}.m
   Note: These are not currently covered by SymPy.
 *)


Unprotect[BesselI]
BesselI[1/2,z_] := (Sqrt[2/Pi] Sinh[z]) / Sqrt[z]
BesselI[-1/2,z_] := (Sqrt[2/Pi] Cosh[z]) / Sqrt[z]
Protect[BesselI]

Unprotect[BesselJ]
BesselJ[-1/2,z_] := (Sqrt[2/Pi] Cos[z])/Sqrt[z]
BesselJ[1/2,z_] := (Sqrt[2/Pi] Sin[z])/Sqrt[z]
Protect[BesselJ]
