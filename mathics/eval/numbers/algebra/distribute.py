"""
Evaluation routines for Distribute[]
"""

from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol


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


def eval_Distribute(expr, operator_symbol, evaluation):
    """
    Recursively distribute operator_symbol over the expression.
    Returns None if no distribution was performed.
    """
    if not isinstance(expr, Expression):
        return None

    # Handle ListExpression: apply distribution to each element.
    if isinstance(expr, ListExpression):
        distributed_elements = []
        for element in expr.elements:
            distributed = eval_Distribute(element, operator_symbol, evaluation)
            if distributed is not None:
                distributed_elements.append(distributed)
            else:
                distributed_elements.append(element)
        return ListExpression(*distributed_elements)

    head = expr.get_head()
    elements = expr.elements

    # Find the first element containing the operator_symbol.
    operator_position = None
    for i, elem in enumerate(elements):
        if contains_operator_symbol(elem, operator_symbol):
            operator_position = i
            break

    if operator_position is None:
        # No element contains operator_symbol.
        return None

    # Get the element at the target position
    target_elem = elements[operator_position]

    # If the element is the operator symbol (e.g., g in f[g[...], g[...]]),
    # distribute over it by distributing the outer function's arguments.
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

        # If we have multiple arguments containing the operator symbol at different positions,
        # we need to create a cartesian product. Check if there are more positions with operator_symbol.
        other_operator_positions = []
        for i, elem in enumerate(elements):
            if i != operator_position and contains_operator_symbol(
                elem, operator_symbol
            ):
                other_operator_positions.append(i)

        # If there are other arguments with the operator symbol, we need to distribute across all of them.
        if other_operator_positions:
            return distribute_across_multiple_positions(
                head, elements, operator_symbol, evaluation
            )

        # Return the combination using the operator symbol.
        return Expression(operator_symbol, *result_parts)

    # If the element contains but is not the operator symbol, recurse into it.
    else:
        recursive_result = eval_Distribute(target_elem, operator_symbol, evaluation)
        if recursive_result is not None:
            new_elements = list(elements)
            new_elements[operator_position] = recursive_result
            new_expr = Expression(head, *new_elements)

            # Try to distribute the modified Expression again.
            second_result = eval_Distribute(new_expr, operator_symbol, evaluation)
            if second_result is not None:
                return second_result
            return new_expr

    return None


# def eval_Distribute_with_replacement(expr, f_symbol, g_symbol, fp_symbol=None, gp_symbol=None, evaluation=None):
#     """
#     Recursively distribute operator_symbol over the expression.
#     Optionally replace outer function head with gp_symbol and inner with fp_symbol.
#     Returns None if no distribution was performed.
#     """
#     if not isinstance(expr, Expression):
#         return None

#     # Default: use operator_symbol for both outer and inner if not specified
#     if fp_symbol is None:
#         fp_symbol = f_symbol
#     if gp_symbol is None:
#         gp_symbol = g_symbol

#     # Handle ListExpression: apply distribution to each element.
#     if isinstance(expr, ListExpression):
#         distributed_elements = []
#         for element in expr.elements:
#             distributed = eval_Distribute_with_replacement(element, f_symbol, g_symbol, fp_symbol, gp_symbol, evaluation)
#             if distributed is not None:
#                 distributed_elements.append(distributed)
#             else:
#                 distributed_elements.append(element)
#         return ListExpression(*distributed_elements)
#     elif isinstance(expr, Expression):
#         head = expr.get_head()
#         element = expr.elements[0]
#         distributed = eval_Distribute_with_replacement(expr, f_symbol, g_symbol, fp_symbol, gp_symbol, evaluation)
#         if distributed is None:
#             return None
#         return Expression(head, distributed)

#     head = expr.get_head()
#     elements = expr.elements

#     # Find the first element containing the operator_symbol.
#     operator_position = None
#     for i, elem in enumerate(elements):
#         if contains_operator_symbol(elem, f_symbol):
#             operator_position = i
#             break

#     if operator_position is None:
#         # No element contains operator_symbol
#         return None

#     # Get the element at the target position
#     target_elem = elements[operator_position]

#     # If the element is the operator symbol (e.g., g in f[g[...], g[...]]),
#     # distribute over it by distributing the outer function's arguments.
#     if is_operator_symbol(target_elem, f_symbol):
#         # Get all components of the operator symbol
#         target_components = target_elem.elements

#         # Create new expressions by replacing the operator position with each component.
#         result_parts = []
#         for component in target_components:
#             # Replace the operator position with this component.
#             new_elements = list(elements)
#             new_elements[operator_position] = component
#             new_expr = Expression(head, *new_elements)

#             # Recursively distribute in the new Expression.
#             recursive_result = eval_Distribute_with_replacement(new_expr, f_symbol, g_symbol, gp_symbol, fp_symbol, evaluation)
#             if recursive_result is not None:
#                 result_parts.append(recursive_result)
#             else:
#                 result_parts.append(new_expr)

#         # If we have multiple arguments containing the operator symbol at different positions,
#         # create a cartesian product. Check if there are more positions with operator_symbol.
#         other_operator_positions = []
#         for i, elem in enumerate(elements):
#             if i != operator_position and contains_operator_symbol(elem, f_symbol):
#                 other_operator_positions.append(i)

#         # If there are other arguments with the operator symbol, distribute across all of them.
#         if other_operator_positions:
#             return distribute_across_multiple_positions_with_replacement(
#                 head, elements, f_symbol, gp_symbol, fp_symbol, evaluation
#             )

#         # Return the combination: use gp_symbol for outer, fp_symbol for inner
#         # The inner expression uses fp_symbol, outer uses gp_symbol
#         inner_expressions = [Expression(fp_symbol, *rp.elements) if isinstance(rp, Expression) and rp.get_head() == head else rp for rp in result_parts]
#         return Expression(gp_symbol, *inner_expressions)

#     # If the element contains but is not the operator symbol, recurse into it.
#     else:
#         recursive_result = eval_Distribute_with_replacement(target_elem, f_symbol, gp_symbol, fp_symbol, evaluation)
#         if recursive_result is not None:
#             new_elements = list(elements)
#             new_elements[operator_position] = recursive_result
#             new_expr = Expression(head, *new_elements)

#             # Try to distribute the modified Expression again.
#             second_result = eval_Distribute_with_replacement(new_expr, f_symbol, gp_symbol, fp_symbol, evaluation)
#             if second_result is not None:
#                 return second_result
#             return new_expr

#     return None


# def distribute_across_multiple_positions_with_replacement(head, elements, f_symbol, gp_symbol, fp_symbol, evaluation):
#     """
#     When multiple arguments contain the f_symbol, distribute across all of them.
#     This creates a cartesian product of the components.
#     """
#     # Find all positions with the f_symbol
#     operator_positions = []
#     for i, elem in enumerate(elements):
#         if contains_operator_symbol(elem, f_symbol):
#             operator_positions.append(i)

#     # Extract the components for each position.
#     position_components = []
#     for pos in operator_positions:
#         elem = elements[pos]
#         if is_operator_symbol(elem, f_symbol):
#             position_components.append((pos, elem.elements))
#         else:
#             position_components.append((pos, [elem]))

#     # Generate cartesian product of all components.
#     result_parts = []

#     # Return the result wrapped in gp_symbol
#     return Expression(gp_symbol, *result_parts)


def distribute_across_multiple_positions(head, elements, operator_symbol, evaluation):
    """
    When multiple arguments contain the operator_symbol, distribute across all of them.
    This creates a cartesian product of the components.
    """
    # Find all positions with the operator_symbol.
    operator_positions = []
    for i, elem in enumerate(elements):
        if contains_operator_symbol(elem, operator_symbol):
            operator_positions.append(i)

    # Extract the components for each position.
    position_components = []
    for pos in operator_positions:
        elem = elements[pos]
        if is_operator_symbol(elem, operator_symbol):
            position_components.append((pos, elem.elements))
        else:
            # Should not happen, but handle gracefully
            position_components.append((pos, [elem]))

    # Generate cartesian product of all components.
    result_parts = []

    def cartesian_product_helper(index, current_elements):
        if index == len(position_components):
            # We've filled all positions, create the expression
            new_expr = Expression(head, *current_elements)
            result_parts.append(new_expr)
            return

        pos, components = position_components[index]
        for component in components:
            new_elements = list(current_elements)
            new_elements[pos] = component
            cartesian_product_helper(index + 1, new_elements)

    cartesian_product_helper(0, list(elements))

    # Return the result wrapped in the operator_symbol
    return Expression(operator_symbol, *result_parts)


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
