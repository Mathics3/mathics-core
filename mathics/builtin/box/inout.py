# -*- coding: utf-8 -*-

from mathics.builtin.base import Builtin

from mathics.core.attributes import hold_all_complete, protected, read_protected


class ButtonBox(Builtin):
    """
    <dl>
    <dt>'ButtonBox[$boxes$]'
        <dd> is a low-level box construct that represents a button in a
    notebook expression.
    </dl>
    """

    attributes = protected | read_protected
    summary_text = "box construct for buttons"


class InterpretationBox(Builtin):
    """
    <dl>
    <dt>'InterpretationBox[{...}]'
        <dd> is a low-level box construct that displays as
    boxes but is interpreted on input as expr.
    </dl>
    """

    attributes = hold_all_complete | protected | read_protected
    summary_text = "box associated to an input expression"


class SubscriptBox(Builtin):
    """
    <dl>
    <dt>'SubscriptBox["symb", "subscript"]'
    <dd>box structure for an expression with a subscript
    </dl>
    """

    summary_text = "box format for subscript"


class SubsuperscriptBox(Builtin):
    """
    <dl>
    <dt>'SubsuperscriptBox["symb", "subscript", "superscript"]'
    <dd>box structure for an expression with a subscript and a superscript
    </dl>
    """

    summary_text = "box format for sub and super script"


class SuperscriptBox(Builtin):
    """
    <dl>
    <dt>'SuperscriptBox["symb", "superscript"]'
    <dd>box structure for an expression with a superscript
    </dl>
    """

    summary_text = "box format for superscript"


class RowBox(Builtin):
    """
    <dl>
    <dt>'RowBox[{...}]'
        <dd>is a box construct that represents a sequence of boxes
        arranged in a horizontal row.
    </dl>
    """

    summary_text = "horizontal arrange of boxes"


class StyleBox(Builtin):
    """
    <dl>
    <dt>'StyleBox[boxes, options]'
        <dd> is a low-level representation of boxes
     to be shown with the specified option settings.
    <dt>'StyleBox[boxes, style]'
        <dd> uses the option setting for the specified style in
    the current notebook.
    </dl>
    """

    attributes = protected | read_protected
    summary_text = "associate boxes with styles"


class TagBox(Builtin):
    """
    <dl>
    <dt>'TagBox[boxes, tag]'
        <dd> is a low-level box construct that displays as
    boxes but is interpreted on input as expr
    </dl>
    """

    attributes = hold_all_complete | protected | read_protected
    summary_text = "box tag with a head"


class TemplateBox(Builtin):
    """
    <dl>
    <dt>'TemplateBox[{$box_1$, $box_2$,...}, tag]'
        <dd>is a low-level box structure that parameterizes the display and evaluation     of the boxes $box_i$ .
    </dl>
    """

    attributes = hold_all_complete | protected | read_protected
    summary_text = "parametrized box"


class TooltipBox(Builtin):
    """
    <dl>
    <dt>'TooltipBox[{...}]'
        <dd>undocumented...
    </dl>
    """

    summary_text = "box for showing tooltips"
