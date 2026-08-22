from contextlib import contextmanager

from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.core.systemsymbols import SymbolAnd


def get_assumptions(
    evaluation: Evaluation, explicit_assumptions=None
) -> Symbol | Expression:
    """
    Combines explicit assumptions with active evaluation assumptions.

    Parameters:
        evaluation: The current Evaluation object containing evaluation.assumptions.
        explicit_assumptions: An optional explicit assumption Expression or Symbol.

    Returns:
        The merged assumption Expression/Symbol.
    """
    # Resolve explicit assumptions or default to $Assumptions
    if explicit_assumptions is not None:
        assum_opt = explicit_assumptions
    else:
        assum_opt = Symbol("$Assumptions")

    # Evaluate explicit assumption expression
    assum_eval = (
        assum_opt.evaluate(evaluation) if hasattr(assum_opt, "evaluate") else assum_opt
    )

    # Retrieve current active assumptions from the evaluation state
    active_assumptions = getattr(evaluation, "assumptions", SymbolTrue)

    if active_assumptions in (None, SymbolTrue):
        return assum_eval
    elif assum_eval in (None, SymbolTrue):
        return active_assumptions
    else:
        # Pure merging logic
        return Expression(SymbolAnd, active_assumptions, assum_eval)


@contextmanager
def with_assumptions(evaluation, new_assumptions):
    """
    Context manager to temporarily modify evaluation.assumptions.

    Parameters:
        evaluation: The Evaluation state instance to modify temporarily.
        new_assumptions: The new assumption Expression/Symbol to apply.
    """
    old_assumptions = getattr(evaluation, "assumptions", Symbol("System`True"))

    try:
        # Determine updated assumptions using pure condition checks
        if new_assumptions is None or new_assumptions is SymbolTrue:
            updated = old_assumptions
        elif (
            old_assumptions is None
            or getattr(old_assumptions, "name", None) == "System`True"
        ):
            updated = new_assumptions
        else:
            updated = Expression(SymbolAnd, old_assumptions, new_assumptions)

        evaluation.assumptions = updated
        yield updated

    finally:
        # Guarantee restoration of prior evaluation state
        evaluation.assumptions = old_assumptions
