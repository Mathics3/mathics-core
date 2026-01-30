"""
Form Variables

Below are are Built-in variables that contain lists of the forms available according to some criteria.

"""

from mathics.core.attributes import A_LOCKED, A_PROTECTED
from mathics.core.builtin import Builtin, Predefined
from mathics.core.list import ListExpression

sort_order = "mathics.builtin.forms.form-variables"


class BoxForms_(Predefined):
    r"""
    <dl>
      <dt>'\$BoxForms'
      <dd>contains the current list of general-purpose "BoxForms" formatters.
    </dl>

    Elements of '\$BoxForms' are valid forms to be used as a second parameter \
    in 'MakeBoxes' expressions. 
    
    >> $BoxForms
     = ...
    
    ## TODO: The rest describes how this works in WMA, but is not already implemented here.
    ##
    ## Differently from <url>:\$PrintForm':
    ## /doc/reference-of-built-in-symbols/forms-of-input-and-output/form-variables/\$printforms
    ## </url>, elements are not automatically appended to '$BoxForms' by setting 'MakeBoxes' values.
    ## To do that, explicit assignment to '$BoxForms' is required:
    ##
    ## >> AppendTo[$BoxForms, MyBoxForm]
    ## = ...
    ##
    ## On the other hand, to use a custom 'BoxForm' in a 'MakeBoxes' construction, a 'ParentForm' \
    ## must be associated to the new form:
    ##
    ## >> Unprotect[ParentForm]; ParentForm[MyBoxForm] = TraditionalForm
    ## = ...
    ##
    ## Now we can define MakeBoxes rules. For example,
    ## 
    ## >> MakeBoxes[F[x_], MyBoxForm] := RowBox[{MakeBoxes[F, MyBoxForm], "<", MakeBoxes[x, MyBoxForm] ,">"}]
    ## >> MyBoxForm[F[3]]
    ##  = F < a > 
    ##
    """

    attributes = A_LOCKED | A_PROTECTED
    name = "$BoxForms"
    summary_text = "contains a list of box forms"

    def evaluate(self, evaluation):
        return ListExpression(*evaluation.definitions.boxforms)


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


class ParentForm(Builtin):
    r"""
    <dl>
      <dt>'ParentForm'[$Form$]
      <dd>Return the parent form of the Box Form $Form$.
    </dl>
    
    'ParentForm' is used to set and retrieve the parent form of a user-defined \
    box form. 'MakeBoxes'

    ## TODO: This is how this works in WMA: 
    ## MakeBoxes can not be evaluated with a second argument not in '\$BoxForms'
    ## >> MakeBoxes[F[x], MyForm]
    ##  | MakeBoxes::boxfmt: MyForm in MakeBoxes[F[x], MyForm] is not a box formatting type. A box formatting type is any member of $BoxForms.
    ##  = MakeBoxes[F[x], MyForm]
    ##
    ## Append the custom format to $BoxForms is not enough:
    ## >> AppendTo[$BoxForms, MyForm];
    ## >> MakeBoxes[F[x], MyForm]
    ##  | ParentForm::deflt: The ParentForm of ParentForm[MyForm] is not defined on $BoxForms.
    ##  = MakeBoxes[F[x], MyForm]
    ##
    ## Setting 'ParentForm' for this new form
    ## >> Unprotect[ParentForm];ParentForm[MyForm]=TraditionalForm;
    ## >> MakeBoxes[F[x], MyForm]
    ##  = RowBox[{F, (, x, )}]
    ##  
    ## >> MyForm[F[x]]
    ##  = F(x)
    """

    attributes = A_PROTECTED
    messages = {"deflt": "The ParentForm of `` is not defined on $BoxForms."}
    summary_text = "Associated ParentForm to a custom BoxForm"
