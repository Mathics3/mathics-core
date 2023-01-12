(* Adapted from symja_android_library/symja_android_library/rules/ArcCosh.m *)
(**
ArcCosh[Undefined]=Undefined
ArcCosh[0] = I Pi/2,
ArcCosh[1/2] = I Pi/3,
ArcCosh[-1/2] = 2/3 I Pi,
ArcCosh[Sqrt[2]/2] = 1/4 I Pi,
ArcCosh[-Sqrt[2]/2] = 3/4 I Pi,
ArcCosh[Sqrt[3]/2] = 1/6 I Pi,
ArcCosh[-Sqrt[3]/2] = 5/6 I Pi,
ArcCosh[1] = 0,
ArcCosh[-1] = PI I,
ArcCosh[I]=Log[I*[1+Sqrt[2]]],
ArcCosh[Infinity] = Infinity,
Begin["System`"]

ArcCosh[-Infinity] = Infinity
ArcCosh[I Infinity] = Infinity
ArcCosh[-I Infinity] = Infinity
ArcCosh[ComplexInfinity] = Infinity
End[]
 **)
