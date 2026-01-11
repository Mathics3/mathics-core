"""

Common routines and objects used in rendering PrintForms.

"""
from typing import Final, FrozenSet, List, Optional, Tuple

from mathics.core.atoms import Integer, String
from mathics.core.convert.op import operator_to_ascii, operator_to_unicode
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.parser.operators import OPERATOR_DATA, operator_to_string
from mathics.core.symbols import Atom, Symbol
from mathics.core.systemsymbols import (
    SymbolBlank,
    SymbolBlankNullSequence,
    SymbolBlankSequence,
    SymbolInfix,
    SymbolLeft,
    SymbolNonAssociative,
    SymbolNone,
    SymbolPostfix,
    SymbolPrefix,
    SymbolRight,
)


# This Exception if the expression should
# be processed by the default routine
class _WrongFormattedExpression(Exception):
    pass


ARITHMETIC_OPERATOR_STRINGS: Final[FrozenSet[str]] = frozenset(
    [
        *operator_to_string["Divide"],
        *operator_to_string["NonCommutativeMultiply"],
        *operator_to_string["Power"],
        *operator_to_string["Times"],
        " ",
    ]
)

PRECEDENCES: Final = OPERATOR_DATA.get("operator-precedences")
PRECEDENCE_BOX_GROUP: Final[int] = PRECEDENCES.get("BoxGroup", 670)
PRECEDENCE_PLUS: Final[int] = PRECEDENCES.get("Plus", 310)
PRECEDENCE_TIMES: Final[int] = PRECEDENCES.get("Times", 400)
PRECEDENCE_POWER: Final[int] = PRECEDENCES.get("Power", 590)


BLANKS_TO_STRINGS = {
    SymbolBlank: "_",
    SymbolBlankSequence: "__",
    SymbolBlankNullSequence: "___",
}


def square_bracket(expr_str: str) -> str:
    """Wrap `expr_str` with square parenthesis"""
    return f"[{expr_str}]"


def collect_in_pre_post_arguments(
    expr: Expression, evaluation: Evaluation, **kwargs
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
    precedence = PRECEDENCE_BOX_GROUP
    operands = list(target.elements)

    # Just one parameter:
    if len(elements) == 1:
        render_function = kwargs["_render_function"]
        operator_spec = render_function(head, evaluation, **kwargs)
        if head is SymbolInfix:
            operator_spec = [
                f"{operator_to_string['Infix']}{operator_spec}{operator_to_string['Infix']}"
            ]
        elif head is SymbolPrefix:
            operator_spec = f"{operator_spec}{operator_to_string['Prefix']}"
        elif head is SymbolPostfix:
            operator_spec = f"{operator_to_string['Postfix']}{operator_spec}"
        return operands, operator_spec, precedence, group

    # At least two parameters: get the operator spec.
    ops = elements[1]
    if head is SymbolInfix:
        # This is not the WMA behaviour, but the Mathics3 current implementation requires it:
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


def get_operator_str(head, evaluation, **kwargs) -> str:
    encoding = kwargs["encoding"]
    if isinstance(head, String):
        op_str = head.value
    elif isinstance(head, Symbol):
        op_str = head.short_name
    else:
        render_function = kwargs["_render_function"]
        return render_function(head, evaluation, **kwargs)

    if encoding == "ASCII":
        operator = operator_to_ascii.get(op_str, op_str)
    else:
        operator = operator_to_unicode.get(op_str, op_str)
    return operator


def parenthesize(expr_str: str) -> str:
    """Wrap `expr_str` with parenthesis"""
    return f"({expr_str})"


def text_cells_to_grid(cells: List, **kwargs):
    """
    Build from a tabulated grid from a list or
    a list of lists of elements.
    """
    if not cells:
        return ""
    cells = [[row] if isinstance(row, str) else row for row in cells]
    for row in cells:
        assert all(isinstance(field, str) for field in row)

    def normalize_rows(rows):
        """
        Split each field in each row in a list of lines, and then
        make that the number of lines on each field inside the same
        row are the same.
        """
        rows = [[field.split("\n") for field in row] for row in rows]
        max_cols = max(len(row) for row in rows)
        new_rows = []
        heights = []
        # TODO: implement vertical aligments
        for row in rows:
            max_height = max(len(field) for field in row)
            new_row = []
            for field in row:
                height = len(field)
                if height < max_height:
                    field = field + [""] * (max_height - height)
                new_row.append(field)
            num_cols = len(new_row)
            if num_cols < max_cols:
                blank_field = [""] * max_height
                new_row.extend([blank_field] * (max_cols - num_cols))
            new_rows.append(new_row)
            heights.append(max_height)
        return new_rows, heights

    def normalize_cols(rows):
        """
        Ensure that all the lines of fields on the same line
        have the same width.
        """
        # TODO: implement horizontal alignments
        col_widths = [0] * len(rows[0])
        for row in rows:
            for col, cell in enumerate(row):
                for line in cell:
                    col_widths[col] = max(col_widths[col], len(line))
        rows = [
            [
                [line.ljust(col_widths[col]) for line in cell]
                for col, cell in enumerate(row)
            ]
            for row in rows
        ]
        return rows, col_widths

    cells, heights = normalize_rows(cells)
    cells, col_widths = normalize_cols(cells)
    row_sep = "\n\n"
    col_sep = "   "
    result = ""
    for row_idx, row in enumerate(cells):
        if row_idx != 0:
            result += row_sep
        new_lines = [""] * heights[row_idx]
        for field_no, field in enumerate(row):
            for l_no, line in enumerate(field):
                if field_no:
                    new_lines[l_no] += col_sep + line
                else:
                    new_lines[l_no] += line

        # TODO: Remove me at the end...
        new_lines = [line.rstrip() for line in new_lines]
        new_text_row = "\n".join(new_lines)
        result = result + new_text_row

    return result + "\n"
