"""
Form variables

"""

from mathics.builtin.base import Predefined
from mathics.core.attributes import A_LOCKED, A_PROTECTED
from mathics.core.list import ListExpression


class PrintForms_(Predefined):
    r"""
    <dl>
      <dt>'$PrintForms'
      <dd>contains the list of basic print forms. It is updated automatically when new 'PrintForms' are defined by setting format values.
    </dl>

    >> $PrintForms
     = ...

    Suppose now that we want to add a new format 'MyForm'. Initially, it does not belong to '$PrintForms':
    >> MemberQ[$PrintForms, MyForm]
     = False
    Now, let's define a format rule:
    >> Format[MyForm[F[x_]]]:= "F<<" <> ToString[x] <> ">>"
    >> Format[F[x_], MyForm]:= MyForm[F[x]]
    Now, the new format belongs to the '$PrintForms' list
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
      <dt>'$OutputForms'
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
