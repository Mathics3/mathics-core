(* Image Exporter *)
(* FIXME: There is no RegisterImageImport builtin in WMA. Rewrite in Python. *)

Begin["System`Convert`Image`"]

RegisterImageExport[type_] := ImportExport`RegisterExport[
    type,
	System`ImageExport,
        FunctionChannels -> {"FileNames"},
	Options -> {},
	BinaryFormat -> True
];

(* FIXME: RegisterImageImport shoudl work with MIME types, not psuedo-canonicalized file extensions. *)
RegisterImageExport[#]& /@ {"BMP", "GIF", "JPEG2000", "JPEG", "JPG", "PCX", "PNG", "PPM", "PBM", "PGM", "TIFF"};

End[]
