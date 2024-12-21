from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import MessageException
from mathics.core.subexpression import SubExpression


def eval_Part(list_of_list, indices, evaluation: Evaluation, assign_rhs=None):
    """
    eval_part takes the first element of `list_of_list`, and builds
    a subexpression composed of the expressions at the index positions
    listed in `indices`.

    `assign_rhs`, when not empty, indicates where to the store parts of the composed list.

    list_of_list: a list of `Expression`s with a unique element.

    indices: a list of part specification `Expression`s, including
    `Integer` indices,  `Span` `Expression`s, `List` of `Integer`s
    and

    assign_rhs: None or an `Expression` object.
    """
    walk_list = list_of_list[0]
    indices = [index.evaluate(evaluation) for index in indices]
    if assign_rhs is not None:
        try:
            result = SubExpression(walk_list, indices)
            result.replace(assign_rhs.copy())
            result = result.to_expression()
        except MessageException as e:
            e.message(evaluation)
            return False
        if isinstance(result, Expression):
            result.clear_cache()
        return result
    else:
        try:
            result = parts(walk_list, _part_selectors(indices), evaluation)
        except MessageException as e:
            e.message(evaluation)
            return False
        return result
