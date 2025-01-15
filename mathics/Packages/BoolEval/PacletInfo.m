(* Paclet Info File *)

Paclet[
    Name -> "BoolEval",
    Version -> "1.0.1",
    MathematicaVersion -> "10.0+",
    Description -> "Fast vectorized comparison and Boolean operations.",
    Creator -> "Szabolcs Horv\[AAcute]t <szhorvat@gmail.com>",
    URL -> "http://szhorvat.net/mathematica/BoolEval",
    Extensions -> 
        {
            {"Kernel",
              Symbols -> {"BoolEval`BoolEval", "BoolEval`BoolPick", "BoolEval`BoolCount"},
              Root -> ".", Context -> "BoolEval`"
            },
            {"Documentation", Language -> All, MainPage -> "Guides/BoolEval"}
        }
]
