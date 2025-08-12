(* Kernel/init.m *)

Unprotect["BoolEval`*"]

Get["BoolEval`BoolEval`"]

SetAttributes[
  Evaluate@Names["BoolEval`*"],
  {Protected, ReadProtected}
]
