"""
Form Variables

Below are are Built-in variables that contain lists of the forms available according to some criteria.

"""

from mathics.core.attributes import (
    A_LOCKED,
    A_NO_ATTRIBUTES,
    A_PROTECTED,
    A_READ_PROTECTED,
)
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

    Adding a new 'MakeBoxes' rule does not \
    automatically extend the $BoxForms list as happens, for example, in <url>:\$PrintForm:
    /doc/reference-of-built-in-symbols/forms-of-input-and-output/form-variables/\$printforms
    </url> when new 'FormatValues' are defined.

    To see how to add a new form, let us first list the values defined in '\$Boxforms'. \
    This will be useful to compare against later:
    >> $BoxForms
     = ...

    Now we add a rule with our new form 'MyBoxForm':

    >> MakeBoxes[x_Integer, MyBoxForm] := StringJoin[Table["o",{x}]]

    Although a rule involving 'MyBoxForm' has been defined in 'MakeBoxes', the \
    rule is not triggered in boxing.

    >> MyBoxForm[3]
     = MyBoxForm[3]

    And it is not defined in '\$BoxForms' either:

    >> $BoxForms
     = ...

    To have 'MyBoxForm' formatting take effect in boxing via 'MakeBoxes', \
    we first need to add the new form to '\$BoxForms':
    >> AppendTo[$BoxForms, MyBoxForm]
     = ...

    This automatically stores the new form in '\$PrintForms' and \
    '\$OutputForms':
    >> MemberQ[$PrintForms, MyBoxForm]
     = True
    >> MemberQ[$OutputForms, MyBoxForm]
     = True

    We also need to define in 'MyBoxForm' its 'ParentForm':

    >> Unprotect[ParentForm];ParentForm[MyBoxForm]=TraditionalForm
     = TraditionalForm

    Now,
    >> MyBoxForm[3]
     = ooo

    The 'ParentForm' is used when a 'MakeBoxes' rule for a given expression \
    is not available:
    >> MyBoxForm[F[3]]
     = F(3)

    Above, the 'MyBoxForm' rule is not used to format the argument, because \
    the rule used to format the expression propagates 'TradionalForm' (the \
    'ParentForm' of our custom 'BoxForm') to the arguments.

    To fix this, define a rule that propagates the box form to its elements:

    >> MakeBoxes[head_[elements___],MyBoxForm] := RowBox[{MakeBoxes[head,MyBoxForm], "<", RowBox[MakeBoxes[#1, MyBoxForm]&/@{elements}]     ,">"}]
    Now,
    >> MyBoxForm[F[3]]
     = F<ooo>

    Suppose now we want to remove the new BoxForm. We can reset '$BoxForms' \
    to its default values by unset it:
    >> $BoxForms=.; $BoxForms
     = ...

    This does not remove the value from '\$PrintForm' or '\$OutputForm':
    >> {MemberQ[$PrintForms, MyBoxForm], MemberQ[$OutputForms, MyBoxForm]}
     = {True, True}

    To remove 'MyBoxForm', unset in each variable:
    >> $PrintForms=.; $OutputForms=.;
    >> {MemberQ[$PrintForms, MyBoxForm], MemberQ[$OutputForms, MyBoxForm]}
     = {False, False}
    """
    attributes = A_READ_PROTECTED
    messages = {
        "formset": "Cannot set $BoxForms to ``; value must be a list that includes TraditionalForm and StandardForm."
    }
    name = "$BoxForms"
    summary_text = "the list of box forms"

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
    summary_text = "the list of output forms"

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
    summary_text = "sets the parent form of a custom box form"


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
    summary_text = "the list of print forms"

    def evaluate(self, evaluation):
        return ListExpression(*evaluation.definitions.printforms)


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
