(* :Title:  CleanSlate  *)

(* :Author:
        Todd Gayley
        internet: tgayley@mcs.net
*)

(* :Version:  1.1.3  *)

(* :Copyright:
      Copyright 1992-2000, Todd Gayley.
      Permission is hereby granted to modify and/or make copies of
      this file for any purpose other than direct profit, or as part
      of a commercial product, provided this copyright notice is left
      intact.  Sale, other than for the cost of media, is prohibited.
      Permission is hereby granted to reproduce part or all of
      this file, provided that the source is acknowledged.
*)

(* :History:
      Modified May 1993 in several small ways. The major change is that
      now all Unprotecting by the package code is done using string
      arguments to Unprotect, thus circumventing the Unprotect patch
      without having to explicitly remove the patch by altering the
      downvalues of Unprotect.
      V1.1.1, September 1997: fix problem with deleting temporary symbols,
           use Block instead of Module to avoid incrementing $ModuleNumber.
      V1.1.3, August 1998: Handle Experimental` and Developer` contexts.
*)

(* :Context:  Utilities`CleanSlate`  *)

(* :Mathematica Version: 4.0 *)

(* :Warning:
     CleanSlate might be considered a "dangerous" function, given what
     it tries to do. Although it is well-tested, use it at your own
     risk.
*)

(* :Discussion:

PURPOSE

The purpose of CleanSlate is to provide an easy and complete way to accomplish 
two goals: 1) free memory, and 2) clear values of symbols, so that you need not 
worry about tripping over some preexisting definition for a symbol. The basic 
command exported from the package, CleanSlate[], tries to do everything 
possible to return the kernel to the state it was in when the CleanSlate.m 
package was initially read in (usually, this is at the end of the startup 
process, but, as discussed below, it can be read in at other times as well). Of 
course, short of actually restarting, there is no way to do this, but I hope 
that CleanSlate comes as close as possible. I think it will be adequate for 
most user's needs.

BRIEF SUMMARY

There are 3 functions exported from the package: CleanSlate, CleanSlateExcept, 
and ClearInOut.

ClearInOut[] simply clears the In[] and Out[] values, and resets the $Line 
number to 1 (so new input begins as In[1]). It is called internally by 
CleanSlate and CleanSlateExcept. Once this function has been executed, you can 
no longer refer to older input or output (if ClearInOut[] is executed as 
In[32], then you cannot refer to %30, for example). It does not affect the 
values of any symbols, though, so it is a relatively "nondestructive" attempt 
to free memory  By itself, it usually results in only a minimal recovery of 
memory, but in some cases (e.g., graphics) the savings can be large.

CleanSlate and CleanSlateExcept share the same basic purging engine (the 
private function CleanSlateEngine), differing only in the way they calculate 
which contexts to send to this engine. These functions will be discussed in 
much greater detail below, but their basic use is as follows. CleanSlate[] 
tries to purge everything that has happened since the CleanSlate package was 
read in. You can also specify specific contexts for purging with 
CleanSlate["Context1`","Context2`", ...]. Only the listed contexts, along with 
all of their subcontexts, will be affected. Thus, if you don't specify a 
context or contexts, CleanSlate will assume you want the complete job. 
CleanSlateExcept["Context1`","Context2`", ...] allows you to specify a set of 
contexts to be spared from purging. Everything other than what you list will be 
purged. At the end of the process, the functions print a list of the contexts 
purged and the approximate amount of memory freed. The return value is the new 
$ContextPath.

CleanSlate and CleanSlateExcept take one option, Verbose, which can be set to 
True or False. The default is Verbose->True, which specifies that they print 
their usual diagnostic messages.

CleanSlate and CleanSlateExcept have some basic error-checking code built into 
them, to prevent incorrect use. In particular, they catch any invalid 
parameters (such as a misspelled context). For consistency, they take their 
input in the same form as the Mathematica functions that take contexts as 
parameters (Begin and BeginPackage): a sequence (not a list) of strings, each 
specifying a context name.

CleanSlate and Share: Mathematica version 2.1 has a command, Share[], which can 
free significant amounts of memory. Share and CleanSlate do not conflict, and 
in fact they are ideally used together. Run Share after CleanSlate to produce 
the maximum recovery of memory. Share generally executes much more slowly than 
CleanSlate, however, so you might not want to use it routinely.

HOW TO USE IT

CleanSlate.m is designed to be read in at the end of the startup process. This 
is best accomplished by putting it as the last thing in the file init.m. The 
code can be simply pasted into this file, or you can just put <<CleanSlate.m 
into the file. The point at which CleanSlate.m is read in is fundamentally 
important to its operation. In effect, it takes a snapshot of the system at 
this point, so that later when the function is executed, it will not affect 
anything that was initially present. This snapshot consists of two things: the 
contexts on $ContextPath, and any symbols already defined in the Global` 
context. When you execute CleanSlate[], for example, all contexts on the 
current $ContextPath that were not on the initial $ContextPath will be purged 
(along with all of their subcontexts). The exception is the Global` context; it 
is present initially, but it will be purged anyway. However, any symbols that 
were originally defined in the Global` context will be spared. There is no way 
to purge a context that was on the initial path (except Global`) -- any 
attempts to specify such a context will generate an error message.

Although CleanSlate.m is intended to be read in at the start of a session, it 
can actually be read in at any time during a session, or even more than once 
during a session. It will always respect the contexts on the $ContextPath at 
that time, as well as all symbols in the Global` context at that time. This 
allows you to effectively set a "mark" at any point in the session, so that 
executing CleanSlate[] will take you back to that point.

EXAMPLES

  CleanSlate[]                       -- The works
  CleanSlate["Packagename`"]         -- Just strip out this one context
  CleanSlate["Global`"]              -- Get rid of user-defined stuff,
                                          but leave all packages
  CleanSlateExcept["Global`"]        -- Leave all user-defined stuff,
                                          but get rid of all packages
  CleanSlateExcept["Packagename`"]   -- Get rid of everything but this
                                          one package
  CleanSlate[Verbose->False]         -- Same as CleanSlate[], but don't
                                          print diagnostic output
  ClearInOut[]                       -- Just clear In and Out values
  
WHAT IS MEANT BY "PURGING"?

Essentially, "purging" means wiping out all trace of the context's existence. 
This is basically a 3-step process. Step 1 is to map Unprotect, ClearAll, and 
Remove over all symbols in the context (and any subcontexts). Step 2 is to try 
to remove any rules that the context may have defined for System symbols. Step 
3 is to remove the context from $ContextPath and $Packages (if it is present in 
$Packages). The Global` context, however, is not removed from $ContextPath or 
$Packages.

Some packages "overload" System functions (i.e., those in the System` context) 
with additional rules. A good example is the package Algebra`ReIm`, which adds 
new rules for Re, Im, Abs, Conjugate, and Args. To effectively remove this 
package, we would need to remove these additional rules as well. CleanSlate 
uses a clever (I think) scheme that enables it to strip out rules a package 
adds for System functions. The basic mechanism involves substituting my own 
function for Unprotect. In this way, it can intercept all attempts to Unprotect 
system symbols (a necessary prelude to adding rules), noting which symbols are 
being unprotected and which context is doing it. After this information has 
been recorded, the built-in Unprotect is called.

There is more extensive documentation included as a separate file.

I thank Larry Calmer, Jack Lee, Emily Martin, Robby Villegas, Dave Withoff, 
and my beta-testers.

**********)

(*  ================== CODE BEGINS =====================  *)

System`startupPath = $ContextPath;
System`startupGlobals = Flatten[Names[#<>"*"]& /@ Contexts["Global`*"]];
System`startupPackages = $Packages;

BeginPackage["Utilities`CleanSlate`"];

Unprotect[CleanSlate,CleanSlateExcept,ClearInOut];

CleanSlate::usage = "CleanSlate[] purges all symbols and their values in \
all contexts that have been added to the context search path \
($ContextPath), since the CleanSlate package was read in. This includes \
user-defined symbols (in the Global` context) as well as any packages \
that may have been read in. It also removes most, but possibly not all, of \
the additional rules for System symbols that these packages may have \
defined. It also clears the In[] and Out[] values, and resets the $Line \
number, so new input begins as In[1]. \
CleanSlate[\"Context1`\",\"Context2`\"] purges only the listed contexts.";

CleanSlateExcept::usage = "CleanSlateExcept[\"Context1`\",\"Context2`\"] \
purges all symbols and their values in all contexts that have been added to \
the context search path ($ContextPath) since the CleanSlate package was \
read in, except for the listed contexts. It also removes most, but possibly \
not all, of the additional rules for System symbols that purged packages \
may have defined. It also clears the In[] and Out[] values, and resets the \
$Line number, so new input begins as In[1].";

CleanSlate::cntxtpth = "Error in $Contextpath. The $ContextPath is shorter \
than it was when the CleanSlate package was read in. CleanSlate cannot be \
run within a package (i.e., between BeginPackage..EndPackage pairs).";

CleanSlate::notcntxt = "A context you have given is either misspelled, \
incorrectly specified, or is not on $ContextPath.";

CleanSlate::nopurge = "The context `1` cannot be purged, because it was \
present when the CleanSlate package was initally read in.";

CleanSlate::noself = "CleanSlate cannot purge its own context.";

CleanSlate::syntax = "CleanSlate takes arguments of the form \
\"Context1``\", \"Context2``\".";

CleanSlateExcept::syntax = "CleanSlateExcept takes arguments of the form \
\"Context1``\", \"Context2``\".";

ClearInOut::usage = "ClearInOut[] clears the In[] and Out[] values, and \
resets the $Line number, so new input begins as In[1]. This can produce a \
modest recovery of memory, but you will no longer be able to refer to \
output generated previously.";

System`Verbose::usage = "Verbose is an option for CleanSlate and CleanSlateExcept \
that specifies whether they print diagnostic output. It can be set to True or \
False. The default is Verbose->True.";

Options[CleanSlate] = {Verbose->True};
Options[CleanSlateExcept] = {Verbose->True};

(****************   Private`    *******************)

Begin["`Private`"];

initialPath = System`startupPath;
initialGlobals = System`startupGlobals;
initialPackages = System`startupPackages

Remove[System`startupPath];       (*   Clean up these; no longer needed   *)
Remove[System`startupGlobals];
Remove[System`startupPackages];

(*   "Patch" Unprotect, so we can see who is modifying System symbols.

     Actually, this ugly form of patching is no longer needed; it
     persists only for historical reasons. I could
     use the trivial "rule with Condition that fails but performs side
     effect" type of patch. But CleanSlate has been used for years
     as part of the WRI tester. I don't want to touch it now.
*)

alteredSystemSymbols = {};
Unprotect["Unprotect"];
Unprotect[x__Symbol] :=
   Block[ {old, result, pos},
      Scan[ Function[sym,
               If[Context[sym] == "System`", 
                  If[ MemberQ[ alteredSystemSymbols, $Context, {2} ],
                      pos = Flatten[ Position[alteredSystemSymbols, $Context]
                            ] + {0,1};
                      alteredSystemSymbols = 
                         ReplacePart[ alteredSystemSymbols,
                                      (alteredSystemSymbols[[Sequence@@pos]]
                                        ~Union~ {Hold[sym]}),
                                      pos
                         ],
                   (* else *)
                      If[ !StringMatchQ[$Context,"System`*"],
                         alteredSystemSymbols = alteredSystemSymbols ~Union~
                                                 {{$Context,{Hold[sym]}}}
                     ]
                  ]
               ],
               {HoldAll}
            ],
            Hold[x]
      ];
      Unprotect["Unprotect"];
      old = DownValues[Unprotect];
      DownValues[Unprotect] = Select[DownValues[Unprotect],
                                 FreeQ[#,"an unlikely string"]&];
      result = Unprotect[x];
      DownValues[Unprotect] = old;
      Protect[Unprotect];
      result
   ];
Unprotect[{x__Symbol}] := Unprotect[x];
Protect[Unprotect];

(* Note: now that my Unprotect does not intercept string arguments, I could
     avoid the need to fiddle with the downvalues of Unprotect by just
     converting to strings and passing to Unprotect. Here's the code:
     Flatten@ReleaseHold@Map[Function[z,
                                      Unprotect[Evaluate@ToString@HoldForm@z],
                                      {HoldAll}
                             ],Hold@x,{-1}]

*)

(***************    ClearInOut     ***************)

ClearInOut[] := ( Unprotect["In","Out","InString","MessageList"];
                  Clear[In,Out,InString,MessageList];
                  Protect[In,Out,InString,MessageList];
                  $Line=0;
                )

(******************    CleanSlate     ******************)

CleanSlate[opt___?OptionQ] := CleanSlateExcept[opt]

CleanSlate[] := CleanSlateExcept[Verbose -> (Verbose /. Options[CleanSlate])]

CleanSlate[cntxtstopurge__String, opt___?OptionQ] :=
   Block[ { contextsToPurge = {cntxtstopurge}
                                ~ Complement ~ (initialPath
                                                ~ Complement ~ {"Global`"})
                                ~ Complement ~ {"Utilities`CleanSlate`"},
                vbose = Verbose /. {opt} /. Options[CleanSlate]
           },

           If[ !MatchQ[vbose, True | False], 
                 Message[CleanSlate::opttf, Verbose, vbose];
                 vbose = True
           ];
           If[First[#] =!= Verbose,
                 Message[CleanSlate::optx, First[#], InString[$Line]];
           ]& /@ {opt};
           If[ MemberQ[initialPath ~Complement~ {"Global`", "Utilities`CleanSlate`"},#],
               Message[CleanSlate::nopurge,#];
               Abort[];
           ]& /@ {cntxtstopurge};
           If[ MemberQ[ {cntxtstopurge}, "Utilities`CleanSlate`"],
                Message[CleanSlate::noself];
                Abort[];
           ];
           ErrorChecking[cntxtstopurge];
           CleanSlateEngine[contextsToPurge, vbose]
   ]

(****************    CleanSlateExcept     ****************)

CleanSlateExcept[cntxtstospare___String, opt___?OptionQ] :=
   Block[ { contextsToPurge = $ContextPath
                               ~ Complement ~ (initialPath
                                               ~ Complement ~ {"Global`"})
                               ~ Complement ~ {"Utilities`CleanSlate`"}
                               ~ Complement ~ {cntxtstospare},
                vbose = Verbose /. {opt} /. Options[CleanSlateExcept]
           },
           If[ !MatchQ[vbose, True | False], 
                 Message[CleanSlate::opttf, Verbose, vbose];
                 vbose = True
           ];
           If[First[#] =!= Verbose,
                 Message[CleanSlate::optx, First[#], InString[$Line]];
           ]& /@ {opt};
           ErrorChecking[cntxtstospare];
           CleanSlateEngine[contextsToPurge, vbose]
   ]

(****        trap syntax errors:        *****)

CleanSlate[__] := Message[CleanSlate::syntax,"`","`"]

CleanSlateExcept[__] := Message[CleanSlateExcept::syntax,"`","`"]

ErrorChecking[params___String] := (
               If[ Sort[$ContextPath] != $ContextPath ~Union~ {params},
                    Message[CleanSlate::notcntxt]; Abort[]
               ];
               If[ Sort[$ContextPath] != $ContextPath ~Union~ initialPath,
                    Message[CleanSlate::cntxtpth]; Abort[]
               ];
)

(*** Contexts containing kernel functions. Should not be purged. ***)

$AdditionalKernelContexts = {
	"Experimental`", 
	"Developer`",
	"Algebra`SymmetricPolynomials`",
	"NumberTheory`AlgebraicNumberFields`",
	"Optimization`MPSData`",
	"JLink`",
    (* the following Statistics packages include some
       functions defined in the kernel *)
    "HierarchicalClustering`",
    "LinearRegression`" 
	};

(******************    CleanSlateEngine    ******************)
(***             (the main purging function)             ****)

CleanSlateEngine[contextsToPurge_List, vbose_] :=
   Block[ { initialMem = MemoryInUse[],
             memoryFreed,
             systemSymbolsToCheck,
             allPurgedContexts,
             unpurgeableContexts,
             flag,
             protected
           },
       

       (* These contexts, new in 3.5, have some quirks. They will not get
        * purged, though they will be removed from the Context Path if they
        * weren't on it when CleanSlate loaded. *)
       unpurgeableContexts = $AdditionalKernelContexts;

       allPurgedContexts = Flatten[ Contexts[#<>"*"]& /@ contextsToPurge ];
       nonglobalsToPurge = (#<>"*"&) 
           /@ Flatten[ Contexts[#<>"*"]& 
	       /@ (contextsToPurge ~Complement~ Join[ {"Global`"}, unpurgeableContexts] )
	       ];
       globalsToPurge = Flatten[ Names[#<>"*"]& /@  Contexts["Global`*"]
                        ] ~Complement~ initialGlobals;

       (Unprotect[#];ClearAll[#])& /@ nonglobalsToPurge;
       
    (*   Global` context has to be treated a bit differently, because 
         we need to preserve any symbols that may have existed at the 
         time CleanSlate was read in.
    *)

       If[ MemberQ[contextsToPurge, "Global`"],
           (Unprotect[#];ClearAll[#])& /@ globalsToPurge;
           If[Names[#] =!= {}, Remove[#]]& /@ globalsToPurge;
       ];
            
       If[Names[#] =!= {}, Remove[#]]& /@ nonglobalsToPurge;

    (*   Hard-coded hack for Calculus`EllipticIntegrate`  *)

       If[MemberQ[contextsToPurge, "Calculus`EllipticIntegrate`"],
           DownValues[Integrate`TableMatch] =
                   DeleteCases[DownValues[Integrate`TableMatch], z:(x_ :> _) /;
                         StringMatchQ[ToString@FullForm@x,"*Removed[*"] ]
       ];

    (*   Now go after any rules defined for System symbols   *)

       systemSymbolsToCheck = {};
       alteredSystemSymbols =
         Select[ alteredSystemSymbols,
                 If[ MemberQ[ allPurgedContexts, #[[1]] ],
                   systemSymbolsToCheck = systemSymbolsToCheck ~Union~ #[[2]];
                   False,
                   True
                ]&
        ];

       Scan[ Function[sym,
                 protected = Unprotect@Evaluate@ToString@HoldForm@sym;
                 If[ MemberQ[Attributes[sym], ReadProtected],
                       ClearAttributes[sym,ReadProtected];
                       flag=True,
                       flag=False
                 ];
                 DownValues[sym] = DeleteCases[DownValues[sym], z:(x_ :> _) /;
                           StringMatchQ[ToString@FullForm@x,"*Removed[*"] ];
                 UpValues[sym] = DeleteCases[UpValues[sym], z:(x_ :> _) /; 
                           StringMatchQ[ToString@FullForm@x,"*Removed[*"] ];
                 FormatValues[sym] = DeleteCases[FormatValues[sym],z:(x_:>_) /;
                           StringMatchQ[ToString@FullForm@x,"*Removed[*"] ];
                 SubValues[sym] = DeleteCases[SubValues[sym], z:(x_ :> _) /; 
                           StringMatchQ[ToString@FullForm@x,"*Removed[*"] ];
                 If[flag, SetAttributes[sym, {ReadProtected}]];
                 Protect[Evaluate[protected]],
                 {HoldAll}
             ],
             systemSymbolsToCheck, {2}
       ];

   (*   Clean up some potentially large lists that are no longer needed  *)

       Clear[globalsToPurge, nonglobalsToPurge, allPurgedContexts];

       ClearInOut[];

   (*   Print some useful information   *)

       If[ vbose,
            Print["  (CleanSlate) Contexts purged: ", 
	        contextsToPurge ~ Complement ~ unpurgeableContexts ];
            memoryFreed = Quotient[ initialMem - MemoryInUse[], 1024];
            Print["  (CleanSlate) Approximate kernel memory recovered: ",
                    If[ memoryFreed > 0,
                          ToString[memoryFreed]<>" Kb",
                          "0 Kb"
                    ]
            ]
       ];

   (*   Reset $Packages to reflect the removed contexts   *)

       protected = Unprotect["$Packages"];
       $Packages = Select[ $Packages,
                           (! MemberQ[contextsToPurge,#] || #=="Global`")&
                   ];
       $Packages=initialPackages;
       Protect[Evaluate[protected]];

    (*   Reset the $ContextPath to reflect the removed contexts, and 
         return its new value as the result of CleanSlate   *)

       $ContextPath = Select[ $ContextPath,
                              (!MemberQ[contextsToPurge,#] || #=="Global`")&
                      ]
   ]

End[];   (*   Private   *)

Protect[ClearInOut, CleanSlate, CleanSlateExcept];

EndPackage[];   (*   CleanSlate   *)

(*  ================  END OF CODE  ==================  *)
