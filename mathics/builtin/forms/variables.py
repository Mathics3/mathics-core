"""
Form Variables

Below are are Built-in variables that contain lists of the forms available according to some criteria.

"""

from mathics.core.attributes import A_LOCKED, A_PROTECTED
from mathics.core.builtin import Predefined
from mathics.core.list import ListExpression

sort_order = "mathics.builtin.forms.form-variables"


class PrintForms_(Predefined):
    r"""
    <dl>
      <dt>'\$PrintForms'
      <dd>contains the current list of general-purpose "Forms" formatters.

      It is updated automatically when new forms are defined \
      via setting <url>:Format:/doc/reference-of-built-in-symbols/layout/format/</url>\
      in the the left-hand-side of a delayed assignment.
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
    summary_text = "contains a list of print forms"

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
    summary_text = "contains a list all output forms"

    def evaluate(self, evaluation):
        return ListExpression(*evaluation.definitions.outputforms)
