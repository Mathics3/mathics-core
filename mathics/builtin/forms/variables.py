"""
Form Variables

Below are are Built-in variables that contain lists of the forms available according to some criteria.

"""

from mathics.core.attributes import A_LOCKED, A_PROTECTED, A_READ_PROTECTED
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
    
    Differently from <url>:\$PrintForm':
    /doc/reference-of-built-in-symbols/forms-of-input-and-output/form-variables/\$printforms
    </url> which is updated when new 'FormatValues' are defined, it is not \
    enough to add a 'MakeBoxes' rule to extend $BoxForms:
    >> MakeBoxes[x_Integer, MyBoxForm]:=StringJoin[Table["o",{x}]]
    >> MyBoxForm[3]
     = MyBoxForm[3]
    >> $BoxForms
     = ...

    To extend the available box form, and make the rule available, \
    we start by adding the new form to '\$BoxForms':
    >> AppendTo[$BoxForms, MyBoxForm]
     = ...
    Automatically this stores the new form in '\$PrintForms' and \
    '\$OutputForms':
    >> MemberQ[$PrintForms, MyBoxForm]
     = True
    >> MemberQ[$OutputForms, MyBoxForm]
     = True

    Still, this is not enough:
    >> MyBoxForm[F[3]]
     | The ParentForm of ParentForm[MyBoxForm] is not defined on $BoxForms.
     = F[3]
    To complete the extension, we need to establish what is the \
    'ParentForm'  of the new box form:
    >> Unprotect[ParentForm];ParentForm[MyBoxForm]=TraditionalForm
     = TraditionalForm
    Now,
    >> MyBoxForm[3]
     = ooo

    The 'ParentForm' is used when a 'MakeBoxes' rule for a given expression \
    is not available:
    >> MyBoxForm[F[3, g[x]]]
     = F(3, g(x))

    Notice that our rule is not used to format the argument. This is because \
    the rule used to format the expression propagates 'TratidionalForm' (the \
    'ParentForm' of our custom 'BoxForm') to the arguments.

    To make available for nested expressions, we need to define a rule that \
    propagates the box form to their elements:

    >> MakeBoxes[head_[elements___],MyBoxForm]:=RowBox[{MakeBoxes[head,MyBoxForm], "<", RowBox[MakeBoxes[#1, MyBoxForm]&/@{elements}]     ,">"}]
    Now,
    >> MyBoxForm[F[3]]
     = F<ooo>    

    Suppose now we want to remove the new BoxForm. We can reset '$BoxForms' \
    to its default values by unset it:
    >> $BoxForms=.; $BoxForms
     = ...
    Notice that this do not clean automatically the other variables:
    >> {MemberQ[$PrintForms, MyBoxForm], MemberQ[$OutputForms, MyBoxForm]}
     = {True, True}
    To reset them too, unset their values:
    >> $PrintForms=.; $OutputForms=.; 
    >> {MemberQ[$PrintForms, MyBoxForm], MemberQ[$OutputForms, MyBoxForm]}
     = {False, False}
    """
    attributes = A_READ_PROTECTED
    messages = {
        "formset": "Cannot set $BoxForms to ``; value must be a list that includes TraditionalForm and StandardForm."
    }
    name = "$BoxForms"
    summary_text = "the list of box formats"

    def evaluate(self, evaluation):
        return ListExpression(*evaluation.definitions.boxforms)


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
    box form. See <url>:\$BoxForms':
    /doc/reference-of-built-in-symbols/forms-of-input-and-output/form-variables/\$boxforms
    </url> for a usage example.
    """

    attributes = A_PROTECTED
    messages = {"deflt": "The ParentForm of `` is not defined on $BoxForms."}
    summary_text = "Associated ParentForm to a custom BoxForm"


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
