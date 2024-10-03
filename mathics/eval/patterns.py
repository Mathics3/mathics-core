from mathics.core.evaluation import Evaluation
from mathics.core.pattern import BasePattern, StopGenerator


class _StopGeneratorMatchQ(StopGenerator):
    pass


class Matcher:
    def __init__(self, form, evaluation):
        if isinstance(form, BasePattern):
            self.form = form
        else:
            self.form = BasePattern.create(form, evaluation=evaluation)

    def match(self, expr, evaluation: Evaluation):
        def yield_func(vars, rest):
            raise _StopGeneratorMatchQ(True)

        try:
            self.form.match(
                expr,
                {"yield_func": yield_func, "vars_dict": {}, "evaluation": evaluation},
            )
        except _StopGeneratorMatchQ:
            return True
        return False


def match(expr, form, evaluation: Evaluation):
    return Matcher(form, evaluation).match(expr, evaluation)
