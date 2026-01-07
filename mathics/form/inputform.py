"""
This module builts the string associated to the InputForm.

`InputForm` produces a textual output suitable for being parsed and directly
evaluated in Mathics CLI. Differently from `FullForm`, `InputForm`
show arithmetic expressions using Infix/Prefix/Postfix forms. Apart from that,
the apareance  of the result is almost the same that produce `FullForm`.

On the other hand, internally, there are more differences. In the first place,
InputForm always produces a single `String` object, while `FullForm` produces
a nested   `RowBox` structure.

```
In[1]:= 2+F[x] // FullForm // MakeBoxes // InputForm
Out[1]//InputForm=
TagBox[StyleBox[RowBox[{"Plus", "[", RowBox[{"2", ",", RowBox[{"F", "[", "x", "]"}]}], "]"}], ShowSpecialCharacters -> False, ShowStringCharacters -> True, 
  NumberMarks -> True], FullForm]

In[2]:= 2+F[x] // InputForm // MakeBoxes // InputForm
Out[2]//InputForm= InterpretationBox[StyleBox["2 + F[x]", ShowStringCharacters -> True, NumberMarks -> True], InputForm[2 + F[x]], Editable -> True, AutoDelete -> True]
```
In the case of `FullForm`, we get a `TagBox`, which ensures the content to be interpreted as a `FullForm` boxed expression. In the case of the `InputForm`, we get  an `InterpretationBox`, which keeps the information about the original expression. But the main difference is inside the `StyleBox`: for `InputForm` we have a shallow `String object, while for `FullForm` we have a nested `RowBox` expression.

 
Another important difference between `FullForm` and `InputForm` is that `FullForm` does not take into account `FormatValues`, while `InputForm` does: 



Differently from `FullForm`, which produces a nested `RowBox` 
expression, InputForm produces a single `String` (not boxed), which can be
parsed and interpreted as an expression in the Mathics3 interpreter.
```
In[3]:= Format[F[x_],InputForm]:="-inputform formatted "<>ToString[x]<>"F-"
In[4]:= Format[F[x_],FullForm]:="-fullform formatted "<>ToString[x]<>"F-"

In[5]:= 3 F[r] //InputForm
Out[5]//InputForm= 3*"-inputform formatted rF-"

In[6]:= 3 F[r] //FullForm
Out[6]//FullForm= Times[3, F[r]]
```

On the other hand, neither `InputForm` or `FulLForm` do not take into accout MakeBoxes rules: setting

```
In[7]:= MakeBoxes[InputForm[G[x_]],f_]:=RowBox[{"--mb if G--", MakeBoxes[InputForm[x],f]}]
In[8]:= MakeBoxes[FullForm[G[x_]],f_]:=RowBox[{"--mb ff G--", MakeBoxes[FullForm[x],f]}]
```

Evaluating  `G[3 F[t]]` in any of these forms we get

```
In[9]:= G[3 F[t]]//InputForm
Out[9]//InputForm= G[3*"-inputform formatted tF-"]

In[10]:= G[3 F[t]]//FullForm
Out[10]//FullForm= G[Times[3, F[t]]]
```
In the first case, the `FormatValue` rule for `F` is applied but not the `MakeBoxes` rules for `G`.

"""

from typing import Callable, Dict, List, Optional, Tuple

from mathics.core.atoms import Integer, String
from mathics.core.convert.op import operator_to_ascii, operator_to_unicode
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.parser.operators import OPERATOR_DATA
from mathics.core.symbols import Atom, Symbol
from mathics.core.systemsymbols import (
    SymbolBlank,
    SymbolBlankNullSequence,
    SymbolBlankSequence,
    SymbolInfix,
    SymbolInputForm,
    SymbolLeft,
    SymbolNone,
    SymbolRight,
)
from mathics.eval.makeboxes.formatvalues import do_format  # , format_element
from mathics.eval.makeboxes.precedence import compare_precedence
from mathics.settings import SYSTEM_CHARACTER_ENCODING

SymbolNonAssociative = Symbol("System`NonAssociative")
SymbolPostfix = Symbol("System`Postfix")
SymbolPrefix = Symbol("System`Prefix")


PRECEDENCES = OPERATOR_DATA.get("operator-precedences")
PRECEDENCE_DEFAULT = PRECEDENCES.get("FunctionApply")
PRECEDENCE_PLUS = PRECEDENCES.get("Plus")
PRECEDENCE_TIMES = PRECEDENCES.get("Times")
PRECEDENCE_POWER = PRECEDENCES.get("Power")

EXPR_TO_INPUTFORM_TEXT_MAP: Dict[str, Callable] = {}


# This Exception if the expression should
# be processed by the default routine
class _WrongFormattedExpression(Exception):
    pass


def get_operator_str(head, evaluation, **kwargs) -> str:
    encoding = kwargs["encoding"]
    if isinstance(head, String):
        op_str = head.value
    elif isinstance(head, Symbol):
        op_str = head.short_name
    else:
        return render_input_form(head, evaluation, **kwargs)

    if encoding == "ASCII":
        operator = operator_to_ascii.get(op_str, op_str)
    else:
        operator = operator_to_unicode.get(op_str, op_str)
    return operator


def bracket(expr_str: str) -> str:
    """wrap with parenthesis"""
    return f"[{expr_str}]"


def parenthesize(expr_str: str) -> str:
    """wrap with parenthesis"""
    return f"({expr_str})"


def register_inputform(head_name):
    def _register(func):
        EXPR_TO_INPUTFORM_TEXT_MAP[head_name] = func
        return func

    return _register


def render_input_form(expr, evaluation, **kwargs):
    """
    Build a string with the InputForm of the expression.
    """
    format_expr: Expression = do_format(expr, evaluation, SymbolInputForm)
    while format_expr.has_form("HoldForm", 1):  # type: ignore
        format_expr = format_expr.elements[0]

    lookup_name: str = format_expr.get_head().get_lookup_name()

    try:
        result = EXPR_TO_INPUTFORM_TEXT_MAP[lookup_name](
            format_expr, evaluation, **kwargs
        )
        return result
    except _WrongFormattedExpression as e:
        # If the key is not present, or the execution fails for any reason, use
        # the default
        pass
    except KeyError as e:
        pass
    return _generic_to_inputform_text(format_expr, evaluation, **kwargs)

    return ""


@register_inputform("System`Association")
def _association_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
):
    elements = expr.elements
    result = ", ".join(
        [render_input_form(elem, evaluation, **kwargs) for elem in elements]
    )
    return f"<|{result}|>"


def _generic_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    """
    Default representation of a function
    """
    if isinstance(expr, Atom):
        result = expr.atom_to_boxes(SymbolInputForm, evaluation)
        if isinstance(result, String):
            return result.value
        return result.boxes_to_text(**kwargs)

    expr_head = expr.head
    head = render_input_form(expr_head, evaluation, **kwargs)
    comma = ", "
    elements = [render_input_form(elem, evaluation, **kwargs) for elem in expr.elements]
    result = elements.pop(0) if elements else ""
    while elements:
        result = result + comma + elements.pop(0)

    return head + bracket(result)


@register_inputform("System`List")
def _list_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    elements = tuple(
        render_input_form(element, evaluation, **kwargs) for element in expr.elements
    )
    result = "{"
    if elements:
        first, *rest = elements
        result += first
        for elem in rest:
            result += ", " + elem
    return result + "}"


def collect_in_pre_post_arguments(
    expr: BaseElement, evaluation: Evaluation, **kwargs
) -> Tuple[list, str | List[str], int, Optional[Symbol]]:
    """
    Determine operands, operator(s), precedence, and grouping
    """
    # Processing the second argument, if it is there:
    elements = expr.elements
    # expr at least has to have one element
    if len(elements) < 1:
        raise _WrongFormattedExpression

    target = elements[0]
    if isinstance(target, Atom):
        raise _WrongFormattedExpression

    if not (0 <= len(elements) <= 4):
        raise _WrongFormattedExpression

    head = expr.head
    group = None
    precedence = PRECEDENCE_DEFAULT
    operands = list(target.elements)

    # Just one parameter:
    if len(elements) == 1:
        operator_spec = render_input_form(head, evaluation, **kwargs)
        if head is SymbolInfix:
            operator_spec = [f"~{operator_spec}~"]
        elif head is SymbolPrefix:
            operator_spec = f"{operator_spec}@"
        elif head is SymbolPostfix:
            operator_spec = f"//{operator_spec}"
        return operands, operator_spec, precedence, group

    # At least two parameters: get the operator spec.
    ops = elements[1]
    if head is SymbolInfix:
        # This is not the WMA behaviour, but the Mathics current implementation requires it:
        ops = ops.elements if ops.has_form("List", None) else (ops,)
        operator_spec = [get_operator_str(op, evaluation, **kwargs) for op in ops]
    else:
        operator_spec = get_operator_str(ops, evaluation, **kwargs)

    # At least three arguments: get the precedence
    if len(elements) > 2:
        if isinstance(elements[2], Integer):
            precedence = elements[2].value
        else:
            raise _WrongFormattedExpression

    # Four arguments: get the grouping:
    if len(elements) > 3:
        group = elements[3]
        if group not in (SymbolNone, SymbolLeft, SymbolRight, SymbolNonAssociative):
            raise _WrongFormattedExpression
        if group is SymbolNone:
            group = None

    return operands, operator_spec, precedence, group


@register_inputform("System`Infix")
def _infix_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    """
    Convert Infix[...] into a InputForm string.
    """
    # In WMA, expressions associated to Infix operators are not
    # formatted using this path: in some way, when an expression
    # has a head that matches with a symbol associated to an infix
    # operator, WMA builds its inputform without passing through
    # its "Infix" form.
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    operands, ops_lst, precedence, group = collect_in_pre_post_arguments(
        expr, evaluation, **kwargs
    )
    # Infix needs at least two operands:
    if len(operands) < 2:
        raise _WrongFormattedExpression

    # Process the operands:
    parenthesized = group in (None, SymbolRight, SymbolNonAssociative)
    for index, operand in enumerate(operands):
        operand_txt = str(render_input_form(operand, evaluation, **kwargs))
        cmp_precedence = compare_precedence(operand, precedence)
        if cmp_precedence is not None and (
            cmp_precedence == -1 or (cmp_precedence == 0 and parenthesized)
        ):
            operand_txt = parenthesize(operand_txt)

        if index == 0:
            result = operand_txt
            # After the first element, for lateral
            # associativity, parenthesized is flipped:
            if group in (SymbolLeft, SymbolRight):
                parenthesized = not parenthesized
        else:
            num_ops = len(ops_lst)
            curr_op = ops_lst[index % num_ops]
            if curr_op not in ("*", "**", "/", "^", " "):
                # In the tests, we add spaces just for + and -:
                curr_op = f" {curr_op} "

            result = "".join(
                (
                    result,
                    curr_op,
                    operand_txt,
                )
            )
    return result


@register_inputform("System`Prefix")
def _prefix_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    """
    Convert Prefix[...] into a InputForm string.
    """
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    operands, op_head, precedence, group = collect_in_pre_post_arguments(
        expr, evaluation, **kwargs
    )
    # Prefix works with just one operand:
    if len(operands) != 1:
        raise _WrongFormattedExpression
    operand = operands[0]
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    cmp_precedence = compare_precedence(operand, precedence)
    target_txt = render_input_form(operand, evaluation, **kwargs)
    if cmp_precedence is not None and cmp_precedence != -1:
        target_txt = parenthesize(target_txt)
    return op_head + target_txt


@register_inputform("System`Postfix")
def _postfix_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    """
    Convert Postfix[...] into a InputForm string.
    """
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    operands, op_head, precedence, group = collect_in_pre_post_arguments(
        expr, evaluation, **kwargs
    )
    # Prefix works with just one operand:
    if len(operands) != 1:
        raise _WrongFormattedExpression
    operand = operands[0]
    cmp_precedence = compare_precedence(operand, precedence)
    target_txt = render_input_form(operand, evaluation, **kwargs)
    if cmp_precedence is not None and cmp_precedence != -1:
        target_txt = parenthesize(target_txt)
    return target_txt + op_head


@register_inputform("System`Blank")
@register_inputform("System`BlankSequence")
@register_inputform("System`BlankNullSequence")
def _blanks(expr: Expression, evaluation: Evaluation, **kwargs):
    elements = expr.elements
    if len(elements) > 1:
        return _generic_to_inputform_text(expr, evaluation, **kwargs)
    if elements:
        elem = render_input_form(elements[0], evaluation, **kwargs)
    else:
        elem = ""
    head = expr.head
    if head is SymbolBlank:
        return "_" + elem
    elif head is SymbolBlankSequence:
        return "__" + elem
    elif head is SymbolBlankNullSequence:
        return "___" + elem
    return _generic_to_inputform_text(expr, evaluation, **kwargs)


@register_inputform("System`Pattern")
def _pattern(expr: Expression, evaluation: Evaluation, **kwargs):
    elements = expr.elements
    if len(elements) != 2:
        return _generic_to_inputform_text(expr, evaluation, **kwargs)
    name, pat = (render_input_form(elem, evaluation, **kwargs) for elem in elements)
    return name + pat


@register_inputform("System`Rule")
@register_inputform("System`RuleDelayed")
def _rule_to_inputform_text(expr, evaluation: Evaluation, **kwargs):
    """Rule|RuleDelayed[{...}]"""
    head = expr.head
    elements = expr.elements
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    if len(elements) != 2:
        return _generic_to_inputform_text(expr, evaluation, kwargs)
    pat, rule = (render_input_form(elem, evaluation, **kwargs) for elem in elements)

    op_str = get_operator_str(head, evaluation, **kwargs)
    # In WMA there are spaces between operators.
    return pat + f" {op_str} " + rule


@register_inputform("System`Slot")
def _slot_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
):
    elements = expr.elements
    if len(elements) != 1:
        raise _WrongFormattedExpression
    slot = elements[0]
    if isinstance(slot, Integer):
        slot_value = slot.value
        if slot_value < 0:
            raise _WrongFormattedExpression
        return f"#{slot_value}"
    if isinstance(slot, String):
        return f"#{slot.value}"
    raise _WrongFormattedExpression


@register_inputform("System`SlotSequence")
def _slotsequence_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
):
    elements = expr.elements
    if len(elements) != 1:
        raise _WrongFormattedExpression
    slot = elements[0]
    if isinstance(slot, Integer):
        slot_value = slot.value
        if slot_value < 0:
            raise _WrongFormattedExpression
        return f"##{slot_value}"
    if isinstance(slot, String):
        return f"##{slot.value}"
    raise _WrongFormattedExpression
