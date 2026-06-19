(*Rules for Elements*)


System`Integers::usage="Represents the set of the Integers numbers";
System`Primes::usage="Represents the set of the prime numbers";
System`Rationals::usage="Represents the set of the Rational numbers";
System`Reals::usage="Represents the field of the Real numbers";
System`Complexes::usage="Represents the field of the Complex numbers";
System`Algebraics::usage="Represents the set of the algebraic numbers";
System`Booleans::usage="Represents the set of boolean values";

Begin["internals`elements`"]
Unprotect[Element]


Element[_Integer, Reals]:=True;

(*Booleans*)
Element[True|False, Booleans]:=True;
Element[E|I|EulerGamma|Khinchin|MachinePrecision|Pi, Booleans]:=False;
Element[_Integer|_Rational|_Real|_Complex, Booleans]:=False;



(*Integers*)
Element[True|False|E|I|EulerGamma|Khinchin|MachinePrecision|Pi, Integers]:=False;
Element[_Integer, Integers]:=True;
Element[_Rational|_Complex, Integers]:=False;
Element[x_Real/;(FractionalPart[x]!=0.), Integers]:=False;




(*Rationals*)
Element[True|False|E|I|EulerGamma|Khinchin|MachinePrecision|Pi, Rationals]:=False;
Element[_Integer|_Rational, Rationals]:=True;
Element[_Complex, Rationals]:=False;






(*Reals*)
Element[True|False|I, Reals]:=False;
Element[E|EulerGamma|Khinchin|MachinePrecision|Pi, Reals]:=True;
Element[_Rational, Reals]:=True;
Element[_Real, Reals]:=True;
Element[_Complex, Reals]:=False;



(*Complex*)
Element[True|False, Complexes]:=False;
Element[E|EulerGamma|I|Khinchin|MachinePrecision|Pi, Complexes]:=True;
Element[_Integer|_Rational|_Real|_Complex, Complexes]:=True;



(*Elementary inexact functions*)
Element[f:(Sin[_]|Cos[_]|Tan[_]|Cot[_]|Sec[_]|Cosec[_]|Sinh[_]|Cosh[_]|Tanh[_]|Coth[_]|Sech[_]|Cosech[_]|
	 Log[_]|Exp[_]| ArcSin[_]|ArcCos[_]|ArcTan[_]|ArcCot[_]|ArcSec[_]|ArcCosec[_]|
	 ArcSinh[_]|ArcCosh[_]|ArcTanh[_]|ArcCoth[_]|ArcSech[_]|ArcCosech[_]), domain:Reals|Complexes]:=Element[f[[1]], domain];





(*Primes*)
Element[True|False|E|I|EulerGamma|Khinchin|MachinePrecision|Pi, Primes]:=False;
Element[z_Integer, Primes]:=PrimeQ[z];
Element[_Rational|_Complex, Primes]:=False;
Element[x_Real/;(FractionalPart[x]!=0.), Primes]:=False;
(*TODO: Check this condition. Probably this need to be implemented in Python...*)
Element[x_, Primes]:=If[Element[x, Algebraics]===True, False, HoldForm[Element[x, Primes]]];


(*General Algebraic*)

Element[z:(_Plus|_Times), domain:(Integers|Rationals|Reals|Complexes|Algebraics)]:=Element[Alternatives@@z, domain];
Element[z:(_Plus|_Times), Booleans]:=False;
Element[_Times, Primes]:=False;



Element[z_Power, Algebraics]:=Element[Alternatives@@z, Algebraics];
Element[z:(_Integer|_Rational|_Complex), Algebraics]:=True;
Element[I, Algebraics]:=True;
Element[True|False|E|EulerGamma|Khinchin|MachinePrecision|Pi, Algebraics]:=False;
Element[z_DirectedInfinity, domain:(Booleans|Integers|Rationals|Reals|Complexes)]:=False;
Element[z_Power, Integers]:= (Element[Alternatives@@z, Integers] && z[[2]]>=0);
Element[z_Power/;Element[Alternatives@@z, Integers], Integers]:= (z[[2]]>=0);

Element[z_Power, Complexes]:= Element[z, Algebraics];
Element[Power[b_,p_], Rationals]:=Element[b, Rationals] && Element[p, Integers] ;




Element[Sin[_]|Cos[_]|Tan[_]|Cot[_]|Sec[_]|Cosec[_]|
         Sinh[_]|Cosh[_]|Tanh[_]|Coth[_]|Sech[_]|Cosech[_]|
	 Log[_]|Exp[_]|
	 ArcSin[_]|ArcCos[_]|ArcTan[_]|ArcCot[_]|ArcSec[_]|ArcCosec[_]|
	 ArcSinh[_]|ArcCosh[_]|ArcTanh[_]|ArcCoth[_]|ArcSech[_]|ArcCosech[_]
	 , Integers|Primes|Rationals|Algebraics|Booleans]:=False;



Element[Power[b_Real|b_Rational|b_Integer, _Real|_Rational], Reals]:= (b>=0);
Element[Power[_Real|_Rational|_Integer, p_Integer], Reals]= True;
Element[Power[b_/;(Element[b, Reals]), p_/;Element[p, Reals]], Reals]:=(Element[p, Integers] || b>=0);

Protect[Element]
End[]
