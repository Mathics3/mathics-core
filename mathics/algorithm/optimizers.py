# -*- coding: utf-8 -*-

from typing import Optional

from mathics.builtin.scoping import dynamic_scoping


from mathics.core.atoms import (
    String,
    Integer,
    Integer0,
    IntegerM1,
    Integer1,
    Integer2,
    Integer3,
    Integer10,
    Number,
    Real,
)
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.evaluators import eval_N
from mathics.core.expression import Expression
from mathics.core.symbols import (
    BaseElement,
    SymbolPlus,
    SymbolTimes,
    SymbolTrue,
)

from mathics.core.systemsymbols import (
    SymbolAutomatic,
    SymbolD,
    SymbolInfinity,
    SymbolLess,
    SymbolLessEqual,
    SymbolLog,
    SymbolNone,
)


def find_minimum_newton1d(f, x0, x, opts, evaluation) -> (Number, bool):
    is_find_maximum = opts.get("_isfindmaximum", False)
    symbol_name = "FindMaximum" if is_find_maximum else "FindMinimum"
    if is_find_maximum:
        f = -f
        # TODO: revert jacobian if given...

    x_name = x.name

    step_monitor = opts.get("System`StepMonitor", None)
    if step_monitor is SymbolNone:
        step_monitor = None
    evaluation_monitor = opts.get("System`EvaluationMonitor", None)
    if evaluation_monitor is SymbolNone:
        evaluation_monitor = None

    acc_goal, prec_goal, maxit_opt = get_accuracy_prec_and_maxit(opts, evaluation)
    maxit = maxit_opt.value if maxit_opt else 100

    curr_val = eval_N(f.replace_vars({x_name: x0}), evaluation)

    # build the quadratic form:
    eps = determine_epsilon(x0, opts, evaluation)
    if not isinstance(curr_val, Number):
        evaluation.message(symbol_name, "nnum", x, x0)
        if is_find_maximum:
            return -x0, False
        else:
            return x0, False
    d1 = dynamic_scoping(
        lambda ev: Expression(SymbolD, f, x).evaluate(ev), {x_name: None}, evaluation
    )
    val_d1 = eval_N(d1.replace_vars({x_name: x0}), evaluation)
    if not isinstance(val_d1, Number):
        d1 = None
        d2 = None
        f2val = eval_N(f.replace_vars({x_name: x0 + eps}), evaluation)
        f1val = eval_N(f.replace_vars({x_name: x0 - eps}), evaluation)
        val_d1 = eval_N((f2val - f1val) / (Integer2 * eps), evaluation)
        val_d2 = eval_N(
            (f2val + f1val - Integer2 * curr_val) / (eps**Integer2), evaluation
        )
    else:
        d2 = dynamic_scoping(
            lambda ev: Expression(SymbolD, d1, x).evaluate(ev),
            {x_name: None},
            evaluation,
        )
        val_d2 = eval_N(d2.replace_vars({x_name: x0}), evaluation)
        if not isinstance(val_d2, Number):
            d2 = None
            df2val = eval_N(d1.replace_vars({x_name: x0 + eps}), evaluation)
            df1val = eval_N(d1.replace_vars({x_name: x0 - eps}), evaluation)
            val_d2 = (df2val - df1val) / (Integer2 * eps)

    def reset_values(x0):
        x_try = [
            eval_N(x0 / Integer3, evaluation),
            eval_N(x0 * Integer2, evaluation),
            eval_N(x0 - offset / Integer2, evaluation),
        ]
        vals = [(u, eval_N(f.replace_vars({x_name: u}), evaluation)) for u in x_try]
        vals = [v for v in vals if isinstance(v[1], Number)]
        v0 = vals[0]
        for v in vals:
            if Expression(SymbolLess, v[1], v0[1]).evaluate(evaluation) is SymbolTrue:
                v0 = v
        return v0

    def reevaluate_coeffs():
        """reevaluates val_d1 and val_d2"""
        if d1:
            val_d1 = eval_N(d1.replace_vars({x_name: x0}), evaluation)
            if d2:
                val_d2 = eval_N(d2.replace_vars({x_name: x0}), evaluation)
            else:
                df2val = eval_N(d1.replace_vars({x_name: x0 + eps}), evaluation)
                df1val = eval_N(d1.replace_vars({x_name: x0 - eps}), evaluation)
                val_d2 = (df2val - df1val) / (Integer2 * eps)
        else:
            f2val = eval_N(f.replace_vars({x_name: x0 + eps}), evaluation)
            f1val = eval_N(f.replace_vars({x_name: x0 - eps}), evaluation)
            val_d1 = eval_N((f2val - f1val) / (Integer2 * eps), evaluation)
            val_d2 = eval_N(
                (f2val + f1val - Integer2 * curr_val) / (eps**Integer2), evaluation
            )
        return (val_d1, val_d2)

    # Main loop
    count = 0

    while count < maxit:
        if step_monitor:
            step_monitor.replace_vars({x_name: x0}).evaluate(evaluation)

        if val_d1.is_zero:
            if is_find_maximum:
                evaluation.message(
                    symbol_name, "fmgz", String("maximum"), String("minimum")
                )
            else:
                evaluation.message(
                    symbol_name, "fmgz", String("minimum"), String("maximum")
                )

            if is_find_maximum:
                return (x0, -curr_val), True
            else:
                return (x0, curr_val), True
        if val_d2.is_zero:
            val_d2 = Integer1

        offset = eval_N(val_d1 / abs(val_d2), evaluation)
        x1 = eval_N(x0 - offset, evaluation)
        new_val = eval_N(f.replace_vars({x_name: x1}), evaluation)
        if (
            Expression(SymbolLessEqual, new_val, curr_val).evaluate(evaluation)
            is SymbolTrue
        ):
            if is_zero(offset, acc_goal, prec_goal, evaluation):
                if is_find_maximum:
                    return (x1, -curr_val), True
                else:
                    return (x1, curr_val), True
            x0 = x1
            curr_val = new_val
        else:
            if is_zero(offset / Integer2, acc_goal, prec_goal, evaluation):
                if is_find_maximum:
                    return (x0, -curr_val), True
                else:
                    return (x0, curr_val), True
            x0, curr_val = reset_values(x0)
        val_d1, val_d2 = reevaluate_coeffs()
        count = count + 1
    else:
        evaluation.message(symbol_name, "maxiter")
    if is_find_maximum:
        return (x0, -curr_val), False
    else:
        return (x0, curr_val), False


def find_root_secant(f, x0, x, opts, evaluation) -> (Number, bool):
    region = opts.get("$$Region", None)
    if not type(region) is list:
        if x0.is_zero:
            region = (Real(-1), Real(1))
        else:
            xmax = 2 * x0.to_python()
            xmin = -2 * x0.to_python()
            if xmin > xmax:
                region = (Real(xmax), Real(xmin))
            else:
                region = (Real(xmin), Real(xmax))

    maxit = opts["System`MaxIterations"]
    x_name = x.get_name()
    if maxit is SymbolAutomatic:
        maxit = 100
    else:
        maxit = maxit.evaluate(evaluation).get_int_value()

    x0 = from_python(region[0])
    x1 = from_python(region[1])
    f0 = dynamic_scoping(lambda ev: f.evaluate(evaluation), {x_name: x0}, evaluation)
    f1 = dynamic_scoping(lambda ev: f.evaluate(evaluation), {x_name: x1}, evaluation)
    if not isinstance(f0, Number):
        return x0, False
    if not isinstance(f1, Number):
        return x0, False
    f0 = f0.to_python(n_evaluation=True)
    f1 = f1.to_python(n_evaluation=True)
    count = 0
    while count < maxit:
        if f0 == f1:
            x1 = Expression(
                SymbolPlus,
                x0,
                Expression(
                    SymbolTimes,
                    Real(0.75),
                    Expression(
                        SymbolPlus, x1, Expression(SymbolTimes, Integer(-1), x0)
                    ),
                ),
            )
            x1 = x1.evaluate(evaluation)
            f1 = dynamic_scoping(
                lambda ev: f.evaluate(evaluation), {x_name: x1}, evaluation
            )
            if not isinstance(f1, Number):
                return x0, False
            f1 = f1.to_python(n_evaluation=True)
            continue

        inv_deltaf = from_python(1.0 / (f1 - f0))
        num = Expression(
            SymbolPlus,
            Expression(SymbolTimes, x0, from_python(f1)),
            Expression(SymbolTimes, x1, from_python(f0), IntegerM1),
        )
        x2 = Expression(SymbolTimes, num, inv_deltaf)
        x2 = x2.evaluate(evaluation)
        f2 = dynamic_scoping(
            lambda ev: f.evaluate(evaluation), {x_name: x2}, evaluation
        )
        if not isinstance(f2, Number):
            return x0, False
        f2 = f2.to_python(n_evaluation=True)
        f1, f0 = f2, f1
        x1, x0 = x2, x1
        if x1 == x0 or abs(f2) == 0:
            break
        count = count + 1
    else:
        evaluation.message("FindRoot", "maxiter")
        return x0, False
    return x0, True


def find_root_newton(f, x0, x, opts, evaluation) -> (Number, bool):
    """
    Look for a root of a f: R->R using the Newton's method.
    """
    absf = abs(f)
    df = opts["System`Jacobian"]
    x_name = x.get_name()

    acc_goal, prec_goal, maxit_opt = get_accuracy_prec_and_maxit(opts, evaluation)
    maxit = maxit_opt.value if maxit_opt else 100

    step_monitor = opts.get("System`StepMonitor", None)
    if step_monitor is SymbolNone:
        step_monitor = None
    evaluation_monitor = opts.get("System`EvaluationMonitor", None)
    if evaluation_monitor is SymbolNone:
        evaluation_monitor = None

    def decreasing(val1, val2):
        """
        Check if val2 has a smaller absolute value than val1
        """
        if not (val1.is_numeric() and val2.is_numeric()):
            return False
        if val2.is_zero:
            return True
        res = eval_N(Expression(SymbolLog, abs(val2 / val1)), evaluation)
        if not res.is_numeric():
            return False
        return res.to_python() < 0

    def new_seed():
        """
        looks for a new starting point, based on how close we are from the target.
        """
        x1 = eval_N(Integer2 * x0, evaluation)
        x2 = eval_N(x0 / Integer3, evaluation)
        x3 = eval_N(x0 - minus / Integer2, evaluation)
        x4 = eval_N(x0 + minus / Integer3, evaluation)
        absf1 = eval_N(absf.replace_vars({x_name: x1}), evaluation)
        absf2 = eval_N(absf.replace_vars({x_name: x2}), evaluation)
        absf3 = eval_N(absf.replace_vars({x_name: x3}), evaluation)
        absf4 = eval_N(absf.replace_vars({x_name: x4}), evaluation)
        if decreasing(absf1, absf2):
            x1, absf1 = x2, absf2
        if decreasing(absf1, absf3):
            x1, absf1 = x3, absf3
        if decreasing(absf1, absf4):
            x1, absf1 = x4, absf4
        return x1, absf1

    def sub(evaluation):
        d_value = eval_N(df, evaluation)
        if d_value == Integer(0):
            return None
        result = eval_N(f / d_value, evaluation)
        if evaluation_monitor:
            dynamic_scoping(
                lambda ev: evaluation_monitor.evaluate(ev), {x_name: x0}, evaluation
            )
        return result

    currval = absf.replace_vars({x_name: x0}).evaluate(evaluation)
    count = 0
    while count < maxit:
        if step_monitor:
            dynamic_scoping(
                lambda ev: step_monitor.evaluate(ev), {x_name: x0}, evaluation
            )
        minus = dynamic_scoping(sub, {x_name: x0}, evaluation)
        if minus is None:
            evaluation.message("FindRoot", "dsing", x, x0)
            return x0, False
        x1 = Expression(
            SymbolPlus, x0, Expression(SymbolTimes, Integer(-1), minus)
        ).evaluate(evaluation)
        if not isinstance(x1, Number):
            evaluation.message("FindRoot", "nnum", x, x0)
            return x0, False

        # Check convergency:
        new_currval = absf.replace_vars({x_name: x1}).evaluate(evaluation)
        if is_zero(new_currval, acc_goal, prec_goal, evaluation):
            return x1, True

        # This step tries to ensure that the new step goes forward to the convergency.
        # If not, tries to restart in a another point closer to x0 than x1.
        if decreasing(new_currval, currval):
            x0, currval = new_seed()
            count = count + 1
            continue
        else:
            currval = new_currval
            x0 = eval_N(x1, evaluation)
            # N required due to bug in sympy arithmetic
            count += 1
    else:
        evaluation.message("FindRoot", "maxiter")
    return x0, True


native_optimizer_messages = {}

native_local_optimizer_methods = {
    "Automatic": find_minimum_newton1d,
    "Newton": find_minimum_newton1d,
}

native_findroot_methods = {
    "Automatic": find_root_newton,
    "Newton": find_root_newton,
    "Secant": find_root_secant,
}
native_findroot_messages = {}


def is_zero(
    val: BaseElement,
    acc_goal: Optional[Real],
    prec_goal: Optional[Real],
    evaluation: Evaluation,
) -> bool:
    """
    Check if val is zero upto the precision and accuracy goals
    """
    if not isinstance(val, Number):
        val = eval_N(val, evaluation)
    if not isinstance(val, Number):
        return False
    if val.is_zero:
        return True
    if not (acc_goal or prec_goal):
        return False

    eps_expr: BaseElement = Integer10 ** (-prec_goal) if prec_goal else Integer0
    if acc_goal:
        eps_expr = eps_expr + Integer10 ** (-acc_goal) / abs(val)
    threeshold_expr = Expression(SymbolLog, eps_expr)
    threeshold: Real = eval_N(threeshold_expr, evaluation)
    return threeshold.to_python() > 0


def determine_epsilon(x0: Real, options: dict, evaluation: Evaluation) -> Real:
    """Determine epsilon  from a reference value, and from the accuracy and the precision goals"""
    acc_goal, prec_goal, maxit = get_accuracy_prec_and_maxit(options, evaluation)
    eps: Real = Real(1e-10)
    if not (acc_goal or prec_goal):
        return eps
    eps = eval_N(
        abs(x0) * Integer10 ** (-prec_goal) if prec_goal else Integer0, evaluation
    )
    if acc_goal:
        eps = eval_N(Integer10 ** (-acc_goal) + eps, evaluation)
    return eps


# comment @mmatera: I moved this method here, because it is going to be used in more than one place
# and I didn't find a better place for it.


def get_accuracy_prec_and_maxit(opts: dict, evaluation: "Evaluation") -> tuple:
    """
    Looks at an opts dictionary and tries to determine the numeric values of
    Accuracy and Precision goals. If not available, returns None.
    """
    # comment @mmatera: I fix the default value for Accuracy
    # and Precision goals to 12 because it ensures that
    # the results of the tests coincides with WMA upto
    # 6 digits. In any case, probably the default value should be
    # determined inside the methods that implements the specific
    # solvers.

    def to_real_or_none(value) -> Optional[Real]:
        if value:
            value = eval_N(value, evaluation)
        if value is SymbolAutomatic:
            value = Real(12.0)
        elif value is SymbolInfinity:
            value = None
        elif not isinstance(value, Number):
            value = None
        return value

    def to_integer_or_none(value) -> Optional[Integer]:
        if value:
            value = eval_N(value, evaluation)
        if value is SymbolAutomatic:
            value = Integer(100)
        elif value is SymbolInfinity:
            value = None
        elif not isinstance(value, Number):
            value = None
        return value

    acc_goal = opts.get("System`AccuracyGoal", None)
    acc_goal = to_real_or_none(acc_goal)
    prec_goal = opts.get("System`PrecisionGoal", None)
    prec_goal = to_real_or_none(prec_goal)
    max_it = opts.get("System`MaxIteration")
    max_it = to_integer_or_none(max_it)
    return acc_goal, prec_goal, max_it
