from mathics.core.evaluation import Evaluation
from mathics.core.pattern import Pattern, StopGenerator


class _StopGeneratorMatchQ(StopGenerator):
    pass


class Matcher:
    def __init__(self, form):
        if isinstance(form, Pattern):
            self.form = form
        else:
            self.form = Pattern.create(form)

    def match(self, expr, evaluation: Evaluation):
        def yield_func(vars, rest):
            raise _StopGeneratorMatchQ(True)

        try:
            self.form.match(yield_func, expr, {}, evaluation)
        except _StopGeneratorMatchQ:
            return True
        return False


def match(expr, form, evaluation: Evaluation):
    return Matcher(form).match(expr, evaluation)
