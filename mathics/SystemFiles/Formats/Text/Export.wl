(* ::Package:: *)

(* Text Exporter *)

Begin["System`Convert`TextDump`"]

Options[TextExport] = {
    "CharacterEncoding" :> $CharacterEncoding
};

TextExport[filename_, expr_, opt:OptionsPattern[]] :=
    Module[{strm, data},
        strm = OpenWrite[filename, CharacterEncoding -> OptionValue["CharacterEncoding"]];
        If[strm === $Failed, Return[$Failed]];
        data = ToString[expr, opt];
        WriteString[strm, data];
        Close[strm];
  ]

ImportExport`RegisterExport[
    "Text",
	System`Convert`TextDump`TextExport,
	FunctionChannels -> {"FileNames"},
	Options -> {"CharacterEncoding", "ByteOrderMark"},
	DefaultElement -> "Plaintext",
	BinaryFormat -> True
]


End[]
