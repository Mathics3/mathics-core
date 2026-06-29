"""
Evaluation routines for Distribute[]
"""

from mathics.core.expression import Expression
from mathics.core.symbols import Symbol


def eval_Distribute(expr, operator_symbol, evaluation):
    """
    Recursively distribute operator_symbol over the expression.
    Returns None if no distribution was performed.
    """
    if not isinstance(expr, Expression):
        return None

    head = expr.get_head()
    elements = expr.elements

    # Find the first element containing the operator_symbol.
    operator_position = None
    for i, elem in enumerate(elements):
        if contains_operator_symbol(elem, operator_symbol):
            operator_position = i
            break

    if operator_position is None:
        # No element contains operator_symbol, but check if head itself needs distribution.
        return None

    # Get the element at the target position
    target_elem = elements[operator_position]

    # If the element is the operator symbol (e.g., Plus), distribute over it.
    if is_operator_symbol(target_elem, operator_symbol):
        # Get all components of the operator symbol
        target_components = target_elem.elements

        # Create new expressions by replacing the operator position with each component.
        result_parts = []
        for component in target_components:
            # Replace the operator position with this component.
            new_elements = list(elements)
            new_elements[operator_position] = component
            new_expr = Expression(head, *new_elements)

            # Recursively distribute in the new Expression.
            recursive_result = eval_Distribute(new_expr, operator_symbol, evaluation)
            if recursive_result is not None:
                result_parts.append(recursive_result)
            else:
                result_parts.append(new_expr)

        # Return the combination using the operator symbol.
        return Expression(operator_symbol, *result_parts)

    # If the element contains but is not the operator symbol, recurse into it.
    else:
        recursive_result = eval_Distribute(target_elem, operator_symbol, evaluation)
        if recursive_result is not None:
            new_elements = list(elements)
            new_elements[operator_position] = recursive_result
            new_expr = Expression(head, *new_elements)

            # Try to distribute the modified Expression again
            second_result = eval_Distribute(new_expr, operator_symbol, evaluation)
            if second_result is not None:
                return second_result
            return new_expr

    return None


def is_operator_symbol(expr, operator_symbol):
    """
    Check if expr's head is exactly the operator_symbol.
    """
    if not isinstance(expr, Expression):
        return False

    expr_head = expr.get_head()

    if isinstance(operator_symbol, Symbol):
        return (
            isinstance(expr_head, Symbol)
            and expr_head.get_name() == operator_symbol.get_name()
        )

    return expr_head == operator_symbol


def contains_operator_symbol(expr, operator_symbol):
    """
    Check if expr contains operator_symbol anywhere.
    """
    if not isinstance(expr, Expression):
        return False

    # Check if this expression's head is the target
    if is_operator_symbol(expr, operator_symbol):
        return True

    # Recursively check sub-expressions
    for elem in expr.elements:
        if contains_operator_symbol(elem, operator_symbol):
            return True

    return False
