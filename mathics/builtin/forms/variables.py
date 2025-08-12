"""
Form Variables

"""

from mathics.core.attributes import A_LOCKED, A_NO_ATTRIBUTES, A_PROTECTED
from mathics.core.builtin import Predefined
from mathics.core.list import ListExpression


class Use2DOutputForm_(Predefined):
    r"""
    <dl>
      <dt>'$Use2DOutputForm'
      <dd>internal variable that controls if 'OutputForm[expr]' is shown \
          in one line (standard Mathics behavior) or \
          or in a prettyform-like multiline output (the standard way in WMA).
          The default value is 'False', keeping the standard Mathics behavior.
    </dl>

    >> $Use2DOutputForm
     = False
    >> OutputForm[a^b]
     = a ^ b
    >> $Use2DOutputForm = True; OutputForm[a ^ b]
     =  
     .  b
     . a 

    Notice that without the 'OutputForm' wrapper, we fall back to the normal
    behavior:
    >> a ^ b
     = Superscript[a, b]
    Setting the variable back to False go back to the normal behavior:
    >> $Use2DOutputForm = False; OutputForm[a ^ b]
     = a ^ b
    """

    attributes = A_NO_ATTRIBUTES
    name = "$Use2DOutputForm"
    rules = {
        "$Use2DOutputForm": "False",
    }
    summary_text = "use the 2D OutputForm"


class PrintForms_(Predefined):
    r"""
    <dl>
      <dt>'\$PrintForms'
      <dd>contains the list of basic print forms. It is updated automatically when new 'PrintForms' are defined by setting format values.
    </dl>

    >> $PrintForms
     = ...

    Suppose now that we want to add a new format 'MyForm'. Initially, it does not belong to '\$PrintForms':
    >> MemberQ[$PrintForms, MyForm]
     = False

    Now, let's define a format rule:
    >> Format[F[x_], MyForm] := "F<<" <> ToString[x] <> ">>"

    Now, the new format belongs to the '\$PrintForms' list
    >> MemberQ[$PrintForms, MyForm]
     = True

    """

    attributes = A_LOCKED | A_PROTECTED
    name = "$PrintForms"
    summary_text = "list common print forms"

    def evaluate(self, evaluation):
        return ListExpression(*evaluation.definitions.printforms)


class OutputForms_(Predefined):
    r"""
    <dl>
      <dt>'\$OutputForms'
      <dd>contains the list of all output forms. It is updated automatically when new 'OutputForms' are defined by setting format values.
    </dl>

    >> $OutputForms
     = ...
    """

    attributes = A_LOCKED | A_PROTECTED
    name = "$OutputForms"
    summary_text = "list all output forms"

    def evaluate(self, evaluation):
        return ListExpression(*evaluation.definitions.outputforms)
