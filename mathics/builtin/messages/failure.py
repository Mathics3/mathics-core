from mathics.builtin.base import Builtin, Predefined


class Aborted(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Aborted.html</url>

    <dl>
      <dt>'$Aborted'
      <dd>is returned by a calculation that has been aborted.
    </dl>
    """

    summary_text = "return value for aborted evaluations"
    name = "$Aborted"


class Failed(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/$Failed.html</url>
    <dl>
      <dt>'$Failed'
      <dd>is returned by some functions in the event of an error.
    </dl>

    #> Get["nonexistent_file.m"]
     : Cannot open nonexistent_file.m.
     = $Failed
    """

    summary_text = "retrieved result for failed evaluations"
    name = "$Failed"


class Failure(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Failure.html</url>

    <dl>
      <dt>Failure[$tag$, $assoc$]
      <dd> represents a failure of a type indicated by $tag$, with details given by the association $assoc$.
    </dl>
    """

    summary_text = "a failure at the level of the interpreter"


#    rules = {'Failure /: MakeBoxes[Failure[tag_, assoc_Association], StandardForm]' :
# 		'With[{msg = assoc["MessageTemplate"], msgParam = assoc["MessageParameters"], type = assoc["Type"]}, ToBoxes @ Interpretation["Failure" @ Panel @ Grid[{{Style["\[WarningSign]", "Message", FontSize -> 35], Style["Message:", FontColor->GrayLevel[0.5]], ToString[StringForm[msg, Sequence @@ msgParam], StandardForm]}, {SpanFromAbove, Style["Tag:", FontColor->GrayLevel[0.5]], ToString[tag, StandardForm]},{SpanFromAbove,Style["Type:", FontColor->GrayLevel[0.5]],ToString[type, StandardForm]}},Alignment -> {Left, Top}], Failure[tag, assoc]] /; msg =!= Missing["KeyAbsent", "MessageTemplate"] && msgParam =!= Missing["KeyAbsent", "MessageParameters"] && msgParam =!= Missing["KeyAbsent", "Type"]]',
#     }


class Missing(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Missing.html</url>

    <dl>
      <dd>'Missing[]'
      <dt> represents a data that is misssing.
    </dl>
    >> ElementData["Meitnerium","MeltingPoint"]
     = Missing[NotAvailable]
    """

    summary_text = "symbolic representation of missing data"
