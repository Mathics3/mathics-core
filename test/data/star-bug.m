(*Extracted from Rubi IntegrationUtilityFunctions.m Integration Utility Functions*)

(* If u-v equals 0, EqQ[u,v] returns True; else it returns False. *)

EqQ[args___] := Null /; EqQ[args]

(* Star[u,v] displays as u*v, and returns the product of u and v with u
   distributed over the terms of v." *)

Star[u_,v_] := (
  Message[Star::error];
  0 ) /;
EqQ[u,0]

Star[u_,Star[v_,w_]] :=
  Star[u*v,w]
"OK!"
