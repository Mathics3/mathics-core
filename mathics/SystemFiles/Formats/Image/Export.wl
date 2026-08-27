(* ::Package:: *)

(* Image Exporter *)

Begin["System`Convert`Image`"]

RegisterImageExport[type_] := ImportExport`RegisterExport[
    type,
	System`ImageExport,
        FunctionChannels -> {"FileNames"},
	Options -> {},
	BinaryFormat -> True
];

(* FIXME: RegisterImageImport should work with MIME types, not psuedo-canonicalized file extensions. *)
RegisterImageExport[#]& /@ {"BMP", "GIF", "JPEG2000", "JPEG", "JPG", "PCX", "PNG", "PPM", "PBM", "PGM", "TIFF"};

End[]
